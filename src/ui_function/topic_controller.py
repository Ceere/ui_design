"""
Topic Controller - 管理ROS topic订阅和消息处理
使用单例模式的RosTopic实例
"""

from ros.ros_topic import RosTopic

def handle_topic_click(topic):
    """处理topic点击事件，使用单例模式更新topic并订阅"""
    
    # 获取单例实例
    topic_instance = RosTopic.get_instance()
    
    # 使用update_topic方法，如果topic有变化会自动取消旧订阅并重新订阅
    success = topic_instance.update_topic(topic['name'], topic['type'])
    
    if success:
        print(f"成功处理topic点击: {topic['name']}")
    else:
        print(f"处理topic点击失败: {topic['name']}")
