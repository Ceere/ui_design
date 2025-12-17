"""
ROS管理器 - 对象式编程实现
管理ROS连接、topic订阅和消息处理
一次只能存在一个ROS连接，但topic可以独立连接/断开
"""
import base64
import cv2
import numpy as np
import logging
from typing import Optional, Dict, List, Any, Callable
from image_receiver import RosBridge, RosTopic
from ros_services import ServiceManager
from text_message_handler import TextTopicManager


class ROSManager:
    """ROS管理器类 - 单例模式，确保一次只有一个ROS连接"""
    
    def __init__(self):
        """初始化ROS管理器"""
        self.host = "localhost"
        self.port = 9090
        self.bridge = None
        self.is_connected = False
        self.topics: Dict[str, RosTopic] = {}
        self.topic_configs: Dict[str, dict] = {}
        self.ui_notify = None
        self.image_callbacks: Dict[str, Callable] = {}
        self.message_callbacks: Dict[str, Callable] = {}
        
    def set_notify_callback(self, callback: Callable):
        """设置UI通知回调函数
        
        Args:
            callback: 通知回调函数，接收消息和类型参数
        """
        self.ui_notify = callback
    
    def _notify(self, message: str, type: str = 'info'):
        """内部通知方法"""
        if self.ui_notify:
            self.ui_notify(message, type)
    
    def connect(self, host: str, port: int) -> bool:
        """连接到ROS系统
        
        Args:
            host: ROS主机地址
            port: ROS端口号
            
        Returns:
            bool: 连接是否成功
        """
        self.host = host
        self.port = port
        
        try:
            # 确保只有一个连接
            if self.bridge is None:
                self.bridge = RosBridge(ros_host=self.host, ros_port=self.port)
            
            # 尝试连接
            if self.bridge.connect_ros_bridge():
                self.is_connected = True
                self._notify(f"✅ ROS连接成功: {host}:{port}", 'positive')
                logging.info(f"ROS连接成功: {host}:{port}")
                return True
            else:
                self.is_connected = False
                self._notify(f"❌ ROS连接失败: 无法连接到 {host}:{port}", 'negative')
                logging.warning(f"ROS连接失败: 无法连接到 {host}:{port}")
                return False
        except Exception as e:
            logging.error(f"ROS连接异常: {e}")
            self.is_connected = False
            self._notify(f"❌ ROS连接异常: {str(e)}", 'negative')
            return False
    
    def disconnect(self):
        """断开ROS系统连接"""
        # 取消所有订阅
        for topic_name in list(self.topics.keys()):
            self.unsubscribe_topic(topic_name)
        
        # 断开连接
        if self.bridge is not None:
            try:
                self.bridge.disconnect_ros_bridge()
            except Exception as e:
                logging.error(f"断开连接时出错: {e}")
            finally:
                self.bridge = None
                self.is_connected = False
        
        self._notify("🛑 ROS 连接已断开", 'info')
    
    def add_topic(self, topic_name: str, msg_type: str = "sensor_msgs/Image") -> bool:
        """添加topic配置
        
        Args:
            topic_name: topic名称
            msg_type: 消息类型
            
        Returns:
            bool: 添加是否成功
        """
        if topic_name not in self.topic_configs:
            self.topic_configs[topic_name] = {
                'topic_name': topic_name,
                'msg_type': msg_type,
                'frame_count': 0,
                'subscribed': False
            }
            self._notify(f"✅ 添加 Topic {topic_name} 成功", 'positive')
            return True
        else:
            self._notify(f"Topic {topic_name} 已存在", 'warning')
            return False
    
    def remove_topic(self, topic_name: str) -> bool:
        """移除topic配置
        
        Args:
            topic_name: topic名称
            
        Returns:
            bool: 移除是否成功
        """
        # 先取消订阅
        self.unsubscribe_topic(topic_name)
        
        # 移除配置
        if topic_name in self.topic_configs:
            del self.topic_configs[topic_name]
            self._notify(f"✅ 删除 Topic {topic_name} 成功", 'positive')
            return True
        else:
            self._notify(f"Topic {topic_name} 不存在", 'warning')
            return False
    
    def subscribe_topic(self, topic_name: str) -> bool:
        """订阅topic
        
        Args:
            topic_name: topic名称
            
        Returns:
            bool: 订阅是否成功
        """
        if not self.is_connected:
            logging.warning("ROS 未连接，无法订阅 topic")
            self._notify("❌ ROS 未连接", 'negative')
            return False
            
        if topic_name not in self.topic_configs:
            logging.warning(f"Topic {topic_name} 未配置")
            self._notify(f"❌ Topic {topic_name} 未配置", 'negative')
            return False
            
        if topic_name in self.topics:
            logging.warning(f"Topic {topic_name} 已订阅")
            return True
            
        try:
            config = self.topic_configs[topic_name]
            
            # 创建 topic 订阅
            topic = RosTopic(
                topic_name=config['topic_name'],
                topic_message_type=config['msg_type'],
                ros_bridge_client=self.bridge if self.bridge else None
            )
            
            # 设置回调函数
            def message_callback(msg):
                config['frame_count'] += 1
                processed = self._process_message(topic_name, msg)
                if processed:
                    self._trigger_callbacks(topic_name, processed)
            
            # 修改 RosTopic 以支持回调
            topic.msg_callback = message_callback
            
            if topic.subscribe():
                self.topics[topic_name] = topic
                self.topic_configs[topic_name]['subscribed'] = True
                self._notify(f"✅ 订阅 {topic_name} 成功", 'positive')
                return True
            else:
                self._notify(f"❌ 订阅 {topic_name} 失败", 'negative')
                return False
        except Exception as e:
            logging.error(f"订阅 topic {topic_name} 失败: {e}")
            self._notify(f"❌ 订阅 {topic_name} 失败", 'negative')
            return False
    
    def unsubscribe_topic(self, topic_name: str) -> bool:
        """取消订阅topic
        
        Args:
            topic_name: topic名称
            
        Returns:
            bool: 取消订阅是否成功
        """
        if topic_name in self.topics:
            topic = self.topics[topic_name]
            if topic.unsubscribe():
                del self.topics[topic_name]
                if topic_name in self.topic_configs:
                    self.topic_configs[topic_name]['subscribed'] = False
                self._notify(f"取消订阅 {topic_name}", 'info')
                return True
        return False
    
    def get_topic_list(self) -> List[str]:
        """获取所有已配置的topic名称
        
        Returns:
            List[str]: topic名称列表
        """
        return list(self.topic_configs.keys())
    
    def get_available_topics(self) -> List[Dict]:
        """获取ROS系统中所有可用的topic
        
        Returns:
            List[Dict]: topic信息列表，每个元素包含name和type
        """
        if not self.is_connected or not self.bridge:
            logging.warning("ROS未连接或桥接器未初始化，无法获取topic列表")
            return []
        
        # 使用RosBridge对象的方法获取topic列表
        return self.bridge.get_available_topics()
    
    def get_topic_type(self, topic_name: str) -> Optional[str]:
        """获取指定topic的消息类型
        
        Args:
            topic_name: topic名称
            
        Returns:
            Optional[str]: 消息类型，失败返回None
        """
        # 首先检查已配置的topic
        if topic_name in self.topic_configs:
            return self.topic_configs[topic_name]['msg_type']
        
        # 然后从ROS系统获取
        if self.is_connected and self.bridge:
            return self.bridge.get_topic_type(topic_name)
        
        return None
    
    def _process_message(self, topic_name: str, msg: Any) -> Optional[str]:
        """处理接收到的消息
        
        Args:
            topic_name: topic名称
            msg: 原始消息
            
        Returns:
            Optional[str]: 处理后的消息，失败返回None
        """
        try:
            if 'data' in msg and 'encoding' in msg:  # 图像消息
                return self._process_image_message(msg)
            else:  # 普通消息
                return str(msg)
        except Exception as e:
            logging.error(f"消息处理错误: {e}")
            return None
    
    def _process_image_message(self, msg: Dict) -> Optional[str]:
        """处理图像消息，返回base64编码的图像
        
        Args:
            msg: 图像消息字典
            
        Returns:
            Optional[str]: base64编码的图像字符串，失败返回None
        """
        try:
            image_bytes = base64.b64decode(msg['data'])
            img_array = np.frombuffer(image_bytes, dtype=np.uint8)
            
            if msg['encoding'] == 'bgr8':
                img = img_array.reshape((msg['height'], msg['width'], 3))
            elif msg['encoding'] == 'rgb8':
                img = img_array.reshape((msg['height'], msg['width'], 3))
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            else:
                logging.warning(f"不支持的编码格式: {msg['encoding']}")
                return None
            
            # 转换为 base64 PNG
            _, buffer = cv2.imencode('.png', img)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            logging.error(f"图像处理错误: {e}")
            return None
    
    def _trigger_callbacks(self, topic_name: str, data: str):
        """触发回调函数
        
        Args:
            topic_name: topic名称
            data: 处理后的数据
        """
        # 触发图像回调
        if topic_name in self.image_callbacks:
            try:
                self.image_callbacks[topic_name](data)
            except Exception as e:
                logging.error(f"图像回调错误: {e}")
        
        # 触发消息回调
        if topic_name in self.message_callbacks:
            try:
                self.message_callbacks[topic_name](data)
            except Exception as e:
                logging.error(f"消息回调错误: {e}")
    
    def register_ui_callbacks(self, topic_name: str, 
                             image_callback: Optional[Callable] = None,
                             message_callback: Optional[Callable] = None):
        """注册 UI 回调函数
        
        Args:
            topic_name: topic名称
            image_callback: 图像回调函数
            message_callback: 消息回调函数
        """
        if image_callback:
            self.image_callbacks[topic_name] = image_callback
        if message_callback:
            self.message_callbacks[topic_name] = message_callback
    
    def check_messages(self):
        """检查并处理所有 topic 的新消息（向后兼容）"""
        # 注意：现在使用回调机制，这个方法主要用于向后兼容
        pass
