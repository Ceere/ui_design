"""
ROS连接管理器 - 整合ROS bridge和topic管理
提供统一的接口管理ROS连接和topic订阅
"""
import logging
from typing import Dict, List, Optional, Callable, Any
from ..src.ros.ros_bridge import RosBridge
from .ros_topic import RosTopic


class ROSManager:
    """ROS连接管理器类"""
    
    def __init__(self):
        """初始化ROS管理器"""
        self.ros_bridge = None
        self.topics: Dict[str, RosTopic] = {}
        self.topic_configs: Dict[str, Dict] = {}
        self.ui_callbacks: Dict[str, Dict] = {}
        self.notify_callback = None
    
    def connect(self, host: str = "localhost", port: int = 9090) -> bool:
        """连接到ROS
        
        Args:
            host: ROS主机地址
            port: ROS端口号
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 创建或更新ROS桥接器
            if self.ros_bridge is None:
                self.ros_bridge = RosBridge(host, port)
            else:
                # 如果已有连接，先断开
                if self.ros_bridge.ros_is_connected:
                    self.disconnect()
                self.ros_bridge.ros_host = host
                self.ros_bridge.ros_port = port
            
            # 连接ROS
            if self.ros_bridge.connect_ros_bridge():
                self._notify(f"✅ 成功连接到 ROS {host}:{port}", 'positive')
                return True
            else:
                self._notify(f"❌ 连接ROS失败 {host}:{port}", 'negative')
                return False
                
        except Exception as e:
            self._notify(f"❌ 连接异常: {str(e)}", 'negative')
            logging.error(f"连接异常: {e}")
            return False
    
    def disconnect(self):
        """断开ROS连接"""
        try:
            # 取消订阅所有topic
            for topic_name in list(self.topics.keys()):
                self.unsubscribe_topic(topic_name)
            
            # 断开ROS连接
            if self.ros_bridge:
                self.ros_bridge.disconnect_ros_bridge()
                self._notify("✅ 已断开ROS连接", 'info')
            
            # 清理资源
            self.topics.clear()
            self.ui_callbacks.clear()
            
        except Exception as e:
            self._notify(f"❌ 断开连接异常: {str(e)}", 'negative')
            logging.error(f"断开连接异常: {e}")
    
    @property
    def is_connected(self) -> bool:
        """检查是否已连接ROS
        
        Returns:
            bool: 连接状态
        """
        return self.ros_bridge is not None and self.ros_bridge.ros_is_connected
    
    def add_topic(self, topic_name: str, msg_type: str) -> bool:
        """添加topic配置
        
        Args:
            topic_name: topic名称
            msg_type: 消息类型
            
        Returns:
            bool: 添加是否成功
        """
        if topic_name in self.topic_configs:
            self._notify(f"⚠️ Topic {topic_name} 已存在", 'warning')
            return False
        
        self.topic_configs[topic_name] = {
            'topic_name': topic_name,
            'msg_type': msg_type,
            'subscribed': False,
            'frame_count': 0,
            'latest_message': None
        }
        
        self._notify(f"✅ 添加Topic {topic_name}", 'positive')
        return True
    
    def remove_topic(self, topic_name: str) -> bool:
        """移除topic配置
        
        Args:
            topic_name: topic名称
            
        Returns:
            bool: 移除是否成功
        """
        if topic_name not in self.topic_configs:
            return False
        
        # 如果已订阅，先取消订阅
        if topic_name in self.topics:
            self.unsubscribe_topic(topic_name)
        
        # 移除配置
        del self.topic_configs[topic_name]
        
        # 移除UI回调
        if topic_name in self.ui_callbacks:
            del self.ui_callbacks[topic_name]
        
        self._notify(f"✅ 移除Topic {topic_name}", 'info')
        return True
    
    def subscribe_topic(self, topic_name: str) -> bool:
        """订阅topic
        
        Args:
            topic_name: topic名称
            
        Returns:
            bool: 订阅是否成功
        """
        if not self.is_connected:
            self._notify("❌ 请先连接ROS", 'warning')
            return False
        
        if topic_name not in self.topic_configs:
            self._notify(f"❌ Topic {topic_name} 未配置", 'warning')
            return False
        
        # 如果已经订阅，直接返回成功
        if topic_name in self.topics and self.topics[topic_name].is_subscribed:
            return True
        
        try:
            config = self.topic_configs[topic_name]
            
            # 创建消息回调函数
            def create_callback(tn):
                def callback(msg):
                    # 更新最新消息
                    config['latest_message'] = msg
                    config['frame_count'] += 1
                    
                    # 调用UI回调
                    if tn in self.ui_callbacks:
                        callbacks = self.ui_callbacks[tn]
                        
                        # 处理图像消息
                        if 'image_callback' in callbacks and hasattr(msg, 'data'):
                            try:
                                import base64
                                img_base64 = base64.b64encode(bytes(msg.data)).decode('utf-8')
                                callbacks['image_callback'](img_base64)
                            except Exception as e:
                                logging.error(f"处理图像消息失败: {e}")
                        
                        # 处理文本消息
                        if 'message_callback' in callbacks:
                            try:
                                callbacks['message_callback'](str(msg))
                            except Exception as e:
                                logging.error(f"处理文本消息失败: {e}")
                
                return callback
            
            # 创建ROS topic
            topic = RosTopic(
                topic_name=topic_name,
                topic_message_type=config['msg_type'],
                ros_bridge=self.ros_bridge,
                msg_callback=create_callback(topic_name)
            )
            
            # 订阅topic
            if topic.subscribe():
                self.topics[topic_name] = topic
                config['subscribed'] = True
                self._notify(f"✅ 已订阅 {topic_name}", 'positive')
                return True
            else:
                self._notify(f"❌ 订阅 {topic_name} 失败", 'negative')
                return False
                
        except Exception as e:
            self._notify(f"❌ 订阅异常: {str(e)}", 'negative')
            logging.error(f"订阅异常: {e}")
            return False
    
    def unsubscribe_topic(self, topic_name: str) -> bool:
        """取消订阅topic
        
        Args:
            topic_name: topic名称
            
        Returns:
            bool: 取消订阅是否成功
        """
        if topic_name not in self.topics:
            return False
        
        try:
            topic = self.topics[topic_name]
            if topic.unsubscribe():
                # 更新状态
                if topic_name in self.topic_configs:
                    self.topic_configs[topic_name]['subscribed'] = False
                
                # 移除topic实例
                del self.topics[topic_name]
                
                self._notify(f"✅ 已取消订阅 {topic_name}", 'info')
                return True
            else:
                return False
                
        except Exception as e:
            self._notify(f"❌ 取消订阅异常: {str(e)}", 'negative')
            logging.error(f"取消订阅异常: {e}")
            return False
    
    def get_topic_list(self) -> List[str]:
        """获取已配置的topic列表
        
        Returns:
            List[str]: topic名称列表
        """
        return list(self.topic_configs.keys())
    
    def get_available_topics(self) -> List[Dict[str, str]]:
        """获取ROS系统中所有可用的topic
        
        Returns:
            List[Dict[str, str]]: topic信息列表
        """
        if not self.is_connected or self.ros_bridge is None:
            return []
        
        return self.ros_bridge.get_available_topics()
    
    def get_topic_type(self, topic_name: str) -> str:
        """获取指定topic的消息类型
        
        Args:
            topic_name: topic名称
            
        Returns:
            str: topic类型
        """
        if not self.is_connected or self.ros_bridge is None:
            return 'unknown'
        
        return self.ros_bridge.get_topic_type(topic_name)
    
    def register_ui_callbacks(self, topic_name: str, 
                             image_callback: Optional[Callable] = None,
                             message_callback: Optional[Callable] = None):
        """注册UI回调函数
        
        Args:
            topic_name: topic名称
            image_callback: 图像回调函数
            message_callback: 消息回调函数
        """
        if topic_name not in self.ui_callbacks:
            self.ui_callbacks[topic_name] = {}
        
        if image_callback:
            self.ui_callbacks[topic_name]['image_callback'] = image_callback
        
        if message_callback:
            self.ui_callbacks[topic_name]['message_callback'] = message_callback
    
    def get_latest_message(self, topic_name: str) -> Optional[Any]:
        """获取指定topic的最新消息
        
        Args:
            topic_name: topic名称
            
        Returns:
            Optional[Any]: 最新消息，如果没有则返回None
        """
        if topic_name in self.topic_configs:
            return self.topic_configs[topic_name].get('latest_message')
        return None
    
    def set_notify_callback(self, callback: Callable):
        """设置通知回调函数
        
        Args:
            callback: 通知回调函数
        """
        self.notify_callback = callback
    
    def _notify(self, message: str, type: str = 'info'):
        """发送通知
        
        Args:
            message: 消息内容
            type: 消息类型
        """
        if self.notify_callback:
            try:
                self.notify_callback(message, type)
            except Exception as e:
                logging.error(f"通知回调异常: {e}")
        else:
            logging.info(f"[{type}] {message}")
