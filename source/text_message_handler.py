"""
文字消息处理模块 - 混合式编程实现
处理ROS文字topic消息，结合对象式和函数式编程
"""
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from nicegui import ui


class TextMessageProcessor:
    """文字消息处理器类 - 对象式编程实现"""
    
    def __init__(self):
        """初始化文字消息处理器"""
        self.message_history: Dict[str, list] = {}
        self.max_history = 100  # 每个topic最大保存消息数
    
    def process_message(self, topic_name: str, msg: Any) -> Dict:
        """处理文字消息
        
        Args:
            topic_name: topic名称
            msg: 原始消息
            
        Returns:
            Dict: 处理后的消息记录
        """
        try:
            # 尝试解析JSON消息
            if isinstance(msg, str):
                try:
                    parsed = json.loads(msg)
                    msg_type = "json"
                    content = parsed
                except:
                    msg_type = "text"
                    content = msg
            elif isinstance(msg, dict):
                msg_type = "dict"
                content = msg
            else:
                msg_type = "other"
                content = str(msg)
            
            # 创建消息记录
            message_record = {
                'timestamp': datetime.now().isoformat(),
                'type': msg_type,
                'content': content,
                'topic': topic_name
            }
            
            # 保存到历史
            if topic_name not in self.message_history:
                self.message_history[topic_name] = []
            
            self.message_history[topic_name].append(message_record)
            
            # 限制历史记录大小
            if len(self.message_history[topic_name]) > self.max_history:
                self.message_history[topic_name] = self.message_history[topic_name][-self.max_history:]
            
            return message_record
            
        except Exception as e:
            logging.error(f"Error processing text message: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'type': 'error',
                'content': f"Error: {str(e)}",
                'topic': topic_name
            }
    
    def get_message_history(self, topic_name: str, limit: int = 10) -> list:
        """获取消息历史
        
        Args:
            topic_name: topic名称
            limit: 最大消息数量
            
        Returns:
            list: 消息历史列表
        """
        if topic_name in self.message_history:
            return self.message_history[topic_name][-limit:]
        return []
    
    def clear_history(self, topic_name: Optional[str] = None):
        """清空历史记录
        
        Args:
            topic_name: topic名称，None表示清空所有
        """
        if topic_name:
            if topic_name in self.message_history:
                self.message_history[topic_name] = []
        else:
            self.message_history.clear()
    
    def format_message_for_display(self, message: Dict) -> str:
        """格式化消息用于显示
        
        Args:
            message: 消息记录
            
        Returns:
            str: 格式化后的消息字符串
        """
        timestamp = message.get('timestamp', '')
        msg_type = message.get('type', 'unknown')
        content = message.get('content', '')
        
        if msg_type == 'json':
            formatted = json.dumps(content, indent=2, ensure_ascii=False)
            return f"[{timestamp}] JSON:\n{formatted}"
        elif msg_type == 'dict':
            formatted = json.dumps(content, indent=2, ensure_ascii=False)
            return f"[{timestamp}] Dict:\n{formatted}"
        else:
            return f"[{timestamp}] {content}"


class TextTopicManager:
    """文字topic管理器类 - 对象式编程实现"""
    
    def __init__(self, ros_manager):
        """初始化文字topic管理器
        
        Args:
            ros_manager: ROS管理器实例
        """
        self.ros_manager = ros_manager
        self.processor = TextMessageProcessor()
        self.text_topics = set()  # 文字topic集合
    
    def add_text_topic(self, topic_name: str, msg_type: str = "std_msgs/String") -> bool:
        """添加文字topic
        
        Args:
            topic_name: topic名称
            msg_type: 消息类型
            
        Returns:
            bool: 添加是否成功
        """
        # 添加到ROS管理器
        success = self.ros_manager.add_topic(topic_name, msg_type)
        if success:
            self.text_topics.add(topic_name)
            
            # 注册回调
            def text_callback(msg):
                processed = self.processor.process_message(topic_name, msg)
                # 这里可以触发UI更新
                
            self.ros_manager.register_ui_callbacks(
                topic_name,
                message_callback=text_callback
            )
            
            logging.info(f"Text topic {topic_name} added")
            return True
        return False
    
    def remove_text_topic(self, topic_name: str) -> bool:
        """移除文字topic
        
        Args:
            topic_name: topic名称
            
        Returns:
            bool: 移除是否成功
        """
        success = self.ros_manager.remove_topic(topic_name)
        if success and topic_name in self.text_topics:
            self.text_topics.remove(topic_name)
            self.processor.clear_history(topic_name)
            logging.info(f"Text topic {topic_name} removed")
            return True
        return False
    
    def subscribe_text_topic(self, topic_name: str) -> bool:
        """订阅文字topic
        
        Args:
            topic_name: topic名称
            
        Returns:
            bool: 订阅是否成功
        """
        return self.ros_manager.subscribe_topic(topic_name)
    
    def unsubscribe_text_topic(self, topic_name: str) -> bool:
        """取消订阅文字topic
        
        Args:
            topic_name: topic名称
            
        Returns:
            bool: 取消订阅是否成功
        """
        return self.ros_manager.unsubscribe_topic(topic_name)
    
    def get_text_topic_list(self) -> list:
        """获取文字topic列表
        
        Returns:
            list: topic名称列表
        """
        return list(self.text_topics)
    
    def get_message_history(self, topic_name: str, limit: int = 10) -> list:
        """获取消息历史
        
        Args:
            topic_name: topic名称
            limit: 最大消息数量
            
        Returns:
            list: 消息历史列表
        """
        return self.processor.get_message_history(topic_name, limit)


# ==================== UI相关函数 - 函数式编程实现 ====================

def create_text_topic_ui(topic_name: str, 
                        message_history: list,
                        on_subscribe: Callable,
                        on_unsubscribe: Callable,
                        on_remove: Callable):
    """创建文字topic的UI
    
    Args:
        topic_name: topic名称
        message_history: 消息历史列表
        on_subscribe: 订阅回调函数
        on_unsubscribe: 取消订阅回调函数
        on_remove: 删除回调函数
    """
    with ui.card().classes("w-full mb-3"):
        # 标题栏
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(f"📝 {topic_name}").classes("font-bold")
            
            with ui.row().classes("gap-1"):
                ui.button("订阅", on_click=lambda: on_subscribe(topic_name))
                ui.button("取消订阅", on_click=lambda: on_unsubscribe(topic_name), color="orange")
                ui.button("删除", on_click=lambda: on_remove(topic_name), color="red")
        
        # 消息显示区域
        with ui.column().classes("w-full mt-2 p-2 bg-gray-100 rounded max-h-64 overflow-y-auto"):
            if message_history:
                for msg in reversed(message_history[-5:]):  # 显示最近5条
                    formatted = TextMessageProcessor().format_message_for_display(msg)
                    ui.label(formatted).classes("text-sm font-mono p-1 border-b")
            else:
                ui.label("暂无消息").classes("text-gray-500 italic")
        
        # 消息统计
        with ui.row().classes("text-xs text-gray-600 mt-1"):
            ui.label(f"消息数: {len(message_history)}")


def create_text_message_display(topic_name: str, message: Dict):
    """创建文字消息显示
    
    Args:
        topic_name: topic名称
        message: 消息记录
    """
    processor = TextMessageProcessor()
    formatted = processor.format_message_for_display(message)
    
    with ui.card().classes("w-full mb-2 p-2"):
        ui.label(f"Topic: {topic_name}").classes("text-sm font-bold")
        ui.label(formatted).classes("text-xs font-mono whitespace-pre-wrap")
