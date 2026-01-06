"""
ROS Topic订阅器 - 管理topic订阅
提供topic订阅和消息接收功能，只保留最新一帧数据
单例模式实现，确保只有一个topic订阅器实例
"""
import roslibpy
import logging
from ros.ros_bridge import get_ros_bridge


class RosTopic:
    """ROS Topic订阅器类 - 管理topic订阅，只保留最新一帧数据"""
    
    # 类变量保存最新消息和相关信息
    cls_latest_message = None
    cls_current_topic_name = None
    cls_current_topic_type = None
    
    # 单例模式相关变量
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, topic_name: str = None, topic_message_type: str = None):
        """初始化Topic订阅器
        
        Args:
            topic_name: topic名称（可选）
            topic_message_type: 消息类型（可选）
        """
        # 确保只初始化一次
        if not RosTopic._initialized:
            self.topic_name = topic_name
            self.topic_message_type = topic_message_type
            self.ros_bridge = get_ros_bridge()
            self.listener = None
            self.is_subscribed = False
            RosTopic._initialized = True
    
    def update_topic(self, topic_name: str, topic_message_type: str) -> bool:
        """更新topic信息，如果已订阅则取消订阅并重新订阅
        
        Args:
            topic_name: 新的topic名称
            topic_message_type: 新的消息类型
            
        Returns:
            bool: 操作是否成功
        """
        # 如果topic信息没有变化，直接返回成功
        if self.topic_name == topic_name and self.topic_message_type == topic_message_type:
            return True
        
        # 如果已经订阅了其他topic，先取消订阅
        if self.is_subscribed:
            logging.info(f"取消订阅当前topic: {self.topic_name}")
            self.unsubscribe()
        
        # 更新topic信息
        self.topic_name = topic_name
        self.topic_message_type = topic_message_type
        
        # 如果之前已经订阅过，重新订阅新的topic
        if self.topic_name and self.topic_message_type:
            logging.info(f"更新topic信息，准备订阅新的topic: {self.topic_name}")
            return self.subscribe()
        
        return True

    def message_handler(self, message):
        """消息处理函数
        
        Args:
            message: 接收到的消息
        """
        
        # 更新最新消息和相关信息
        RosTopic.cls_latest_message = message
        RosTopic.cls_current_topic_name = self.topic_name
        RosTopic.cls_current_topic_type = self.topic_message_type
        print(f"接收到{self.topic_name}消息")

    def subscribe(self) -> bool:
        """订阅当前设置的topic
        
        Returns:
            bool: 订阅是否成功
        """
        # 检查是否有有效的topic信息
        if not self.topic_name or not self.topic_message_type:
            logging.error("无法订阅: topic名称或类型未设置")
            return False
        
        # 检查ROS bridge是否已连接
        if not self.ros_bridge or not self.ros_bridge.ros_client:
            logging.error(f"无法订阅 {self.topic_name}: ROS bridge未连接")
            return False
        
        if not self.ros_bridge.ros_is_connected:
            logging.error(f"无法订阅 {self.topic_name}: ROS bridge未连接")
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
                queue_size=1
            )
            
            # 订阅topic，传递消息处理函数
            self.listener.subscribe(self.message_handler)
            
            self.is_subscribed = True
            logging.info(f"成功订阅 {self.topic_name}")
            return True
        except Exception as e:
            logging.error(f"订阅 {self.topic_name} 失败: {e}")
            return False
    
    def unsubscribe(self) -> bool:
        """取消订阅当前topic
        
        Returns:
            bool: 取消订阅是否成功
        """
        if self.listener and self.is_subscribed:
            try:
                self.listener.unsubscribe()
                self.listener = None
                self.is_subscribed = False
                logging.info(f"取消订阅 {self.topic_name}")
                return True
            except Exception as e:
                logging.error(f"取消订阅 {self.topic_name} 失败: {e}")
                return False
        return False
    
    def get_latest_message(self):
        """获取最新消息"""
        return RosTopic.cls_latest_message
    
    @classmethod
    def get_current_topic_info(cls):
        """获取当前topic的信息
        
        Returns:
            dict: 包含topic名称和类型的字典
        """
        return {
            'name': cls.cls_current_topic_name,
            'type': cls.cls_current_topic_type
        }
    
    @classmethod
    def get_instance(cls):
        """获取单例实例
        
        Returns:
            RosTopic: 单例实例
        """
        if not cls._instance:
            cls._instance = RosTopic()
        return cls._instance

    def __del__(self):
        """析构函数，确保取消订阅"""
        self.unsubscribe()
