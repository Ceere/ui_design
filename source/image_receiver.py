"""
ROS桥接器和Topic订阅器 - 对象式编程实现
提供ROS连接和topic订阅的基础功能
"""
import roslibpy
import logging
from typing import Optional, Callable


class RosBridge:
    """ROS桥接器类 - 管理ROS连接"""
    
    def __init__(self, ros_host: str = "localhost", ros_port: int = 9090):
        """初始化ROS桥接器
        
        Args:
            ros_host: ROS主机地址
            ros_port: ROS端口号
        """
        self.ros_host = ros_host
        self.ros_port = ros_port
        self.ros_client = None
    
    def connect_ros_bridge(self) -> bool:
        """连接ROS桥接器
        
        Returns:
            bool: 连接是否成功
        """
        try:
            if self.ros_client is None:
                self.ros_client = roslibpy.Ros(self.ros_host, self.ros_port)
                self.ros_client.run()
            
            # 等待连接建立
            import time
            for _ in range(10):
                if self.ros_client.is_connected:
                    logging.info(f"Connected to ROS at {self.ros_host}:{self.ros_port}")
                    return True
                time.sleep(0.1)
            
            logging.error("Failed to connect to ROS")
            return False
        except Exception as e:
            logging.error(f"Connection error: {e}")
            return False
    
    def disconnect_ros_bridge(self):
        """断开ROS桥接器连接"""
        if self.ros_client:
            try:
                self.ros_client.close()
            except Exception as e:
                logging.error(f"Disconnect error: {e}")
            finally:
                self.ros_client = None
    
    @property
    def ros_is_connected(self) -> bool:
        """检查是否已连接
        
        Returns:
            bool: 连接状态
        """
        return self.ros_client is not None and self.ros_client.is_connected
    
    def get_available_topics(self) -> list:
        """获取ROS系统中所有可用的topic
        
        Returns:
            list: topic信息列表，每个元素包含name和type
        """
        if not self.ros_is_connected:
            logging.warning("ROS未连接，无法获取topic列表")
            return []
        
        try:
            # 使用roslibpy官方API获取topic列表
            # 方法1: 使用get_topics_and_types()获取名称和类型
            try:
                topic_types = self.ros_client.get_topics_and_types()
                topic_list = []
                for topic_name, topic_type in topic_types:
                    topic_list.append({
                        'name': topic_name,
                        'type': topic_type
                    })
                return topic_list
            except Exception as e1:
                logging.warning(f"get_topics_and_types()失败: {e1}")
                
                # 方法2: 使用get_topics()获取名称
                try:
                    topic_names = self.ros_client.get_topics()
                    topic_list = []
                    for topic_name in topic_names:
                        topic_list.append({
                            'name': topic_name,
                            'type': 'unknown'
                        })
                    return topic_list
                except Exception as e2:
                    logging.error(f"get_topics()也失败: {e2}")
                    return []
        except Exception as e:
            logging.error(f"获取topic列表失败: {e}")
            return []
    
    def get_topic_type(self, topic_name: str) -> str:
        """获取指定topic的消息类型
        
        Args:
            topic_name: topic名称
            
        Returns:
            str: topic类型，失败返回'unknown'
        """
        if not self.ros_is_connected:
            return 'unknown'
        
        try:
            # 尝试获取topic类型
            if hasattr(self.ros_client, 'get_topic_type'):
                topic_type = self.ros_client.get_topic_type(topic_name)
                if topic_type:
                    return topic_type
            
            # 从topic列表中查找
            topics = self.get_available_topics()
            for topic in topics:
                if topic['name'] == topic_name:
                    return topic['type']
            
            return 'unknown'
        except Exception as e:
            logging.warning(f"获取topic {topic_name} 类型失败: {e}")
            return 'unknown'


class RosTopic:
    """ROS Topic订阅器类 - 管理topic订阅"""
    
    def __init__(
        self,
        topic_name: str,
        topic_message_type: str,
        ros_bridge_client: Optional[RosBridge] = None,
        msg_callback: Optional[Callable] = None,
    ):
        """初始化Topic订阅器
        
        Args:
            topic_name: topic名称
            topic_message_type: 消息类型
            ros_bridge_client: ROS桥接器客户端
            msg_callback: 消息回调函数
        """
        self.topic_name = topic_name
        self.topic_message_type = topic_message_type
        self.ros_bridge_client = ros_bridge_client
        self.msg_callback = msg_callback
        self.listener = None
        self.frame_count = 0
    
    def subscribe(self) -> bool:
        """订阅topic
        
        Returns:
            bool: 订阅是否成功
        """
        if not self.ros_bridge_client or not self.ros_bridge_client.ros_client:
            logging.warning("ROS client not available")
            return False
        
        try:
            self.listener = roslibpy.Topic(
                self.ros_bridge_client.ros_client,
                self.topic_name,
                self.topic_message_type,
                queue_size=1
            )
            
            # 使用提供的回调或默认回调
            callback = self.msg_callback if self.msg_callback else self._default_callback
            self.listener.subscribe(callback)
            
            logging.info(f"Subscribed to {self.topic_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to subscribe to {self.topic_name}: {e}")
            return False
    
    def unsubscribe(self) -> bool:
        """取消订阅topic
        
        Returns:
            bool: 取消订阅是否成功
        """
        if self.listener:
            try:
                self.listener.unsubscribe()
                self.listener = None
                logging.info(f"Unsubscribed from {self.topic_name}")
                return True
            except Exception as e:
                logging.error(f"Failed to unsubscribe from {self.topic_name}: {e}")
                return False
        return False
    
    def _default_callback(self, msg):
        """默认回调函数
        
        Args:
            msg: 接收到的消息
        """
        self.frame_count += 1
        logging.debug(f"Received message {self.frame_count} from {self.topic_name}")
    
    def get_message(self):
        """获取消息（向后兼容）
        
        Returns:
            None: 现在使用回调机制，此方法主要用于向后兼容
        """
        # 注意：现在使用回调机制，这个方法主要用于向后兼容
        return None
