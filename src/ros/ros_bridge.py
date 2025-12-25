"""
ROS桥接器 - 管理ROS连接
提供ROS连接的基础功能，一个桥接器可以对应多个topic和service
"""
import roslibpy
import logging
from typing import Optional, List, Dict, Any


class RosBridge:
    
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, ros_host: str = "localhost", ros_port: int = 9090):
        """初始化ROS桥接器
        
        Args:
            ros_host: ROS主机地址
            ros_port: ROS端口号
        """
        # 确保只初始化一次
        if not RosBridge._initialized:
            self.ros_host = ros_host
            self.ros_port = ros_port
            self.ros_client = None
            RosBridge._initialized = True
    
    def update_host_port(self, ros_host: str, ros_port: int = 9090) -> bool:
        """更新主机和端口，如果需要则重新连接
        
        Args:
            ros_host: 新的ROS主机地址
            ros_port: 新的ROS端口号
            
        Returns:
            bool: 是否需要重新连接
        """
        if self.ros_host != ros_host or self.ros_port != ros_port:
            self.ros_host = ros_host
            self.ros_port = ros_port
            # 如果已经连接，需要断开重新连接
            if self.ros_client is not None:
                self.disconnect_ros_bridge()
                return True
        return False
    
    def connect_ros_bridge(self, ros_host: str = None, ros_port: int = None) -> bool:
        """连接ROS桥接器
        
        Args:
            ros_host: 可选的ROS主机地址（如果提供则更新）
            ros_port: 可选的ROS端口号（如果提供则更新）
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 更新主机和端口（如果需要）
            need_reconnect = False
            if ros_host is not None or ros_port is not None:
                new_host = ros_host if ros_host is not None else self.ros_host
                new_port = ros_port if ros_port is not None else self.ros_port
                need_reconnect = self.update_host_port(new_host, new_port)
            
            # 如果客户端不存在或者需要重新连接，创建新的连接
            if self.ros_client is None or need_reconnect:
                if self.ros_client is not None:
                    self.disconnect_ros_bridge()
                
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
    
    def get_available_topics(self) -> List[Dict[str, str]]:
        """获取ROS系统中所有可用的topic
        
        Returns:
            List[Dict[str, str]]: topic信息列表，每个元素包含name和type
        """
        if not self.ros_is_connected:
            logging.warning("ROS未连接，无法获取topic列表")
            return []
        
        try:
            # 使用roslibpy官方API获取topic列表
            topic_names = self.ros_client.get_topics()
            topic_list = []
            
            for topic_name in topic_names:
                try:
                    # 获取每个topic的类型
                    topic_type = self.ros_client.get_topic_type(topic_name)
                    topic_list.append({
                        'name': topic_name,
                        'type': topic_type if topic_type else 'unknown'
                    })
                except Exception as e:
                    logging.warning(f"获取topic {topic_name} 类型失败: {e}")
                    topic_list.append({
                        'name': topic_name,
                        'type': 'unknown'
                    })
            
            logging.info(f"获取到 {len(topic_list)} 个topic")
            return topic_list
            
        except Exception as e:
            logging.error(f"获取topic列表失败: {e}")
            return []
    
    def get_ros_client(self):
        """获取ROS客户端实例
        
        Returns:
            roslibpy.Ros: ROS客户端实例
        """
        return self.ros_client

def get_ros_bridge():
    ros_bridge = RosBridge()
    return ros_bridge
