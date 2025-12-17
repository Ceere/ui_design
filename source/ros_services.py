"""
ROS服务调用模块 - 对象式编程实现
提供简化的ROS服务调用功能
"""
import roslibpy
import logging
from typing import Optional, Dict, Any, Callable
from nicegui import ui


class ROSServiceClient:
    """ROS服务客户端类 - 管理单个ROS服务"""
    
    def __init__(self, service_name: str, service_type: str, ros_client):
        """初始化ROS服务客户端
        
        Args:
            service_name: 服务名称
            service_type: 服务类型
            ros_client: ROS客户端
        """
        self.service_name = service_name
        self.service_type = service_type
        self.ros_client = ros_client
        self.service = None
    
    def connect(self) -> bool:
        """连接服务
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.service = roslibpy.Service(
                self.ros_client,
                self.service_name,
                self.service_type
            )
            logging.info(f"Service client created for {self.service_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to create service client for {self.service_name}: {e}")
            return False
    
    def call(self, request_data: Dict) -> Optional[Dict]:
        """调用服务
        
        Args:
            request_data: 请求数据字典
            
        Returns:
            Optional[Dict]: 服务响应，失败返回None
        """
        if not self.service:
            logging.warning(f"Service {self.service_name} not connected")
            return None
        
        try:
            request = roslibpy.ServiceRequest(request_data)
            result = self.service.call(request)
            logging.info(f"Service {self.service_name} called successfully")
            return result
        except Exception as e:
            logging.error(f"Failed to call service {self.service_name}: {e}")
            return None
    
    def close(self):
        """关闭服务连接"""
        if self.service:
            self.service = None


class ServiceManager:
    """服务管理器类 - 管理多个ROS服务"""
    
    def __init__(self, ros_client):
        """初始化服务管理器
        
        Args:
            ros_client: ROS客户端
        """
        self.ros_client = ros_client
        self.services: Dict[str, ROSServiceClient] = {}
    
    def add_service(self, service_name: str, service_type: str) -> bool:
        """添加服务配置
        
        Args:
            service_name: 服务名称
            service_type: 服务类型
            
        Returns:
            bool: 添加是否成功
        """
        if service_name in self.services:
            logging.warning(f"Service {service_name} already exists")
            return False
        
        service_client = ROSServiceClient(service_name, service_type, self.ros_client)
        if service_client.connect():
            self.services[service_name] = service_client
            logging.info(f"Service {service_name} added successfully")
            return True
        else:
            logging.error(f"Failed to add service {service_name}")
            return False
    
    def remove_service(self, service_name: str) -> bool:
        """移除服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 移除是否成功
        """
        if service_name in self.services:
            self.services[service_name].close()
            del self.services[service_name]
            logging.info(f"Service {service_name} removed")
            return True
        return False
    
    def call_service(self, service_name: str, request_data: Dict) -> Optional[Dict]:
        """调用服务
        
        Args:
            service_name: 服务名称
            request_data: 请求数据
            
        Returns:
            Optional[Dict]: 服务响应，失败返回None
        """
        if service_name in self.services:
            return self.services[service_name].call(request_data)
        else:
            logging.warning(f"Service {service_name} not found")
            return None
    
    def get_service_list(self) -> list:
        """获取服务列表
        
        Returns:
            list: 服务名称列表
        """
        return list(self.services.keys())


# 常用服务类型
COMMON_SERVICE_TYPES = {
    "std_srvs/Empty": "空服务",
    "std_srvs/SetBool": "布尔设置服务",
    "std_srvs/Trigger": "触发服务",
    "example_interfaces/srv/AddTwoInts": "两数相加服务"
}


def create_service_request_ui(service_name: str, service_type: str, 
                             on_call: Callable[[Dict], None]) -> Dict:
    """
    创建服务请求UI - 函数式编程实现
    
    Args:
        service_name: 服务名称
        service_type: 服务类型
        on_call: 调用服务的回调函数
        
    Returns:
        Dict: 包含UI元素的字典
    """
    ui_elements = {}
    
    with ui.card().classes("w-full mb-3"):
        ui.label(f"服务: {service_name}").classes("font-bold")
        ui.label(f"类型: {service_type}").classes("text-sm text-gray-600")
        
        # 根据服务类型创建不同的输入字段
        if service_type == "std_srvs/SetBool":
            with ui.column().classes("gap-2 mt-2"):
                ui_elements['data'] = ui.switch("启用", value=True)
                ui.button("调用服务", 
                         on_click=lambda: on_call({'data': ui_elements['data'].value}))
        
        elif service_type == "example_interfaces/srv/AddTwoInts":
            with ui.column().classes("gap-2 mt-2"):
                ui_elements['a'] = ui.number("数字 A", value=0).classes("w-32")
                ui_elements['b'] = ui.number("数字 B", value=0).classes("w-32")
                ui.button("调用服务", 
                         on_click=lambda: on_call({
                             'a': int(ui_elements['a'].value),
                             'b': int(ui_elements['b'].value)
                         }))
        
        elif service_type == "std_srvs/Trigger":
            with ui.column().classes("gap-2 mt-2"):
                ui.button("触发服务", 
                         on_click=lambda: on_call({}))
        
        else:
            # 通用JSON输入
            with ui.column().classes("gap-2 mt-2"):
                ui_elements['json_input'] = ui.textarea("请求数据 (JSON)").classes("w-full")
                ui_elements['json_input'].value = "{}"
                ui.button("调用服务", 
                         on_click=lambda: on_call(
                             eval(ui_elements['json_input'].value)
                         ))
    
    return ui_elements
