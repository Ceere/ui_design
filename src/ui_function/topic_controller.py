"""
Topic Controller - 管理ROS topic订阅和消息处理
"""

from ros.ros_topic import RosTopic

def handle_topic_click(topic):
  
    topic_instance = RosTopic(topic['name'], topic['type'])
    topic_instance.subscribe()

