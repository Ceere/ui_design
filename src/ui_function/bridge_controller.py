"""
Topic Controller
处理ROS topic列表的业务逻辑，与UI分离
"""
from ros.ros_bridge import get_ros_bridge
from typing import List, Dict, Optional


class BridgeController:
    """ROS Topic控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.ros_bridge = get_ros_bridge()
        
    def get_all_topics(self) -> List[Dict[str, str]]:
        """获取所有ROS topic
        
        Returns:
            List[Dict[str, str]]: topic列表，每个元素包含name和type
        """
        if not self.ros_bridge.ros_is_connected:
            return []
        
        try:
            topics = self.ros_bridge.get_available_topics()
            return topics if topics else []
        except Exception as e:
            print(f"获取topic列表失败: {e}")
            return []
    
    def get_topic_count(self) -> int:
        """获取topic数量
        
        Returns:
            int: topic数量
        """
        topics = self.get_all_topics()
        return len(topics)
    
    