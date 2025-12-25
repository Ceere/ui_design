"""
Topic Controller
处理ROS topic列表的业务逻辑，与UI分离
"""
from ros.ros_bridge import get_ros_bridge
from typing import List, Dict, Optional


class TopicController:
    """ROS Topic控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.ros_bridge = get_ros_bridge()
    
    def get_topic_status(self) -> Dict[str, str]:
        """获取topic连接状态
        
        Returns:
            Dict[str, str]: 包含状态信息的字典
        """
        if self.ros_bridge.ros_is_connected:
            return {
                'status': '已连接',
                'status_class': 'text-green-500',
                'message': 'Topic状态: 已连接'
            }
        else:
            return {
                'status': '未连接',
                'status_class': 'text-red-500',
                'message': 'Topic状态: 未连接'
            }
    
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
    
    def format_topic_display(self, topics: List[Dict[str, str]]) -> Dict[str, any]:
        """格式化topic显示信息
        
        Args:
            topics: topic列表
            
        Returns:
            Dict[str, any]: 格式化后的显示信息
        """
        if not topics:
            return {
                'has_topics': False,
                'count': 0,
                'message': '未找到任何topic',
                'topics': []
            }
        
        # 处理所有topic
        formatted_topics = []
        for topic in topics:
            topic_name = topic.get('name', '未知')
            topic_type = topic.get('type', '未知')
            
            formatted_topics.append({
                'name': topic_name,
                'type': topic_type,
                'display_name': topic_name,
                'display_type': topic_type
            })
        
        return {
            'has_topics': True,
            'count': len(topics),
            'message': f'发现 {len(topics)} 个topic',
            'topics': formatted_topics
        }
