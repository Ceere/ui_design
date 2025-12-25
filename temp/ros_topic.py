"""
ROS Topic订阅器 - 管理topic订阅
提供topic订阅和消息接收功能，只保留最新一帧数据
"""
import roslibpy
import logging
from typing import Optional, Callable, Any, Dict
from ..src.ros.ros_bridge import RosBridge


class RosTopic:
    """ROS Topic订阅器类 - 管理topic订阅，只保留最新一帧数据"""
    
    def __init__(
        self,
        topic_name: str,
        topic_message_type: str,
        ros_bridge: Optional[RosBridge] = None,
        msg_callback: Optional[Callable] = None,
    ):
        """初始化Topic订阅器
        
        Args:
            topic_name: topic名称
            topic_message_type: 消息类型
            ros_bridge: ROS桥接器
            msg_callback: 消息回调函数
        """
        self.topic_name = topic_name
        self.topic_message_type = topic_message_type
        self.ros_bridge = ros_bridge
        self.msg_callback = msg_callback
        self.listener = None
        self.frame_count = 0
        self.is_subscribed = False
        self.latest_message = None  # 存储最新一帧数据
        self.message_timestamp = None  # 消息时间戳
    
    def subscribe(self) -> bool:
        """订阅topic
        
        Returns:
            bool: 订阅是否成功
        """
        if not self.ros_bridge or not self.ros_bridge.ros_client:
            logging.warning("ROS client not available")
            return False
        
        if self.is_subscribed:
            logging.warning(f"Topic {self.topic_name} 已经订阅")
            return True
        
        try:
            # 设置queue_size=1确保只保留最新消息
            self.listener = roslibpy.Topic(
                self.ros_bridge.ros_client,
                self.topic_name,
                self.topic_message_type,
                queue_size=1  # 只保留最新一帧数据
            )
            
            # 使用包装的回调函数
            callback = self._wrapped_callback if self.msg_callback else self._default_callback
            self.listener.subscribe(callback)
            
            self.is_subscribed = True
            logging.info(f"Subscribed to {self.topic_name} (queue_size=1, 只保留最新消息)")
            return True
        except Exception as e:
            logging.error(f"Failed to subscribe to {self.topic_name}: {e}")
            return False
    
    def unsubscribe(self) -> bool:
        """取消订阅topic
        
        Returns:
            bool: 取消订阅是否成功
        """
        if self.listener and self.is_subscribed:
            try:
                self.listener.unsubscribe()
                self.listener = None
                self.is_subscribed = False
                logging.info(f"Unsubscribed from {self.topic_name}")
                return True
            except Exception as e:
                logging.error(f"Failed to unsubscribe from {self.topic_name}: {e}")
                return False
        return False
    
    def _wrapped_callback(self, msg):
        """包装的回调函数，更新最新消息并调用用户回调
        
        Args:
            msg: 接收到的消息
        """
        import time
        
        # 更新最新消息
        self.latest_message = msg
        self.frame_count += 1
        self.message_timestamp = time.time()
        
        # 调用用户回调
        if self.msg_callback:
            try:
                self.msg_callback(msg)
            except Exception as e:
                logging.error(f"Error in user callback for {self.topic_name}: {e}")
        
        logging.debug(f"Received message {self.frame_count} from {self.topic_name}")
    
    def _default_callback(self, msg):
        """默认回调函数
        
        Args:
            msg: 接收到的消息
        """
        import time
        
        # 更新最新消息
        self.latest_message = msg
        self.frame_count += 1
        self.message_timestamp = time.time()
        
        logging.debug(f"Received message {self.frame_count} from {self.topic_name}")
    
    def get_latest_message(self) -> Optional[Any]:
        """获取最新一帧数据
        
        Returns:
            Optional[Any]: 最新消息，如果没有则返回None
        """
        return self.latest_message
    
    def get_message_info(self) -> Dict[str, Any]:
        """获取消息信息
        
        Returns:
            Dict[str, Any]: 消息信息字典
        """
        return {
            'frame_count': self.frame_count,
            'timestamp': self.message_timestamp,
            'has_message': self.latest_message is not None
        }
    
    def set_callback(self, callback: Callable):
        """设置消息回调函数
        
        Args:
            callback: 消息回调函数
        """
        self.msg_callback = callback
        # 如果已经订阅，需要重新订阅以应用新的回调
        if self.is_subscribed:
            self.unsubscribe()
            self.subscribe()
    
    def clear_message(self):
        """清空最新消息"""
        self.latest_message = None
        self.message_timestamp = None
    
    def __del__(self):
        """析构函数，确保取消订阅"""
        self.unsubscribe()
