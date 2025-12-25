"""
Connect Device Controller
处理连接设备的业务逻辑，与UI分离
"""
from ros.ros_bridge import get_ros_bridge
from device.device import get_device
from ros_function.connect_ros_bridge import connect_device
import datetime


class ConnectDeviceController:
    """连接设备控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.ros_bridge = get_ros_bridge()
        self.device = get_device()
        
    def get_connection_status(self) -> dict:
        """获取连接状态
        
        Returns:
            dict: 包含连接状态信息的字典
        """
        status = {
            'is_connected': self.ros_bridge.ros_is_connected,
            'device_ip': getattr(self.device, 'device_ip', None),
            'ros_host': getattr(self.ros_bridge, 'ros_host', None),
            'ros_port': getattr(self.ros_bridge, 'ros_port', None),
            'update_time': datetime.datetime.now().strftime('%H:%M:%S')
        }
        return status
    
    def format_status_text(self, status: dict) -> dict:
        """格式化状态文本
        
        Args:
            status: 状态字典
            
        Returns:
            dict: 格式化后的状态文本字典
        """
        # 连接状态文本
        if status['is_connected']:
            status_text = '状态: 已连接'
        else:
            status_text = '状态: 未连接'
        
        # 设备IP文本
        device_ip = status['device_ip']
        device_ip_text = f'设备IP: {device_ip}' if device_ip else '设备IP: -'
        
        # ROS主机文本
        ros_host = status['ros_host']
        ros_port = status['ros_port']
        if ros_host and ros_port:
            ros_host_text = f'ROS主机: {ros_host}:{ros_port}'
        else:
            ros_host_text = 'ROS主机: -'
        
        # 更新时间文本
        update_time_text = f'更新时间: {status["update_time"]}'
        
        return {
            'status_text': status_text,
            'device_ip_text': device_ip_text,
            'ros_host_text': ros_host_text,
            'update_time_text': update_time_text
        }
    
    def connect_to_device(self, ip_address: str) -> tuple[bool, str]:
        """连接到设备
        
        Args:
            ip_address: 设备IP地址
            
        Returns:
            tuple[bool, str]: (是否成功, 消息)
        """
        if not ip_address:
            return False, 'Please enter a device IP address'
        
        try:
            # 尝试连接
            success = connect_device(ip_address)
            
            if success:
                return True, f'Successfully connected to {ip_address}!'
            else:
                return False, f'Failed to connect to {ip_address}. Please check the IP address and try again.'
        except Exception as e:
            return False, f'Connection error: {str(e)}'
    
    def update_device_info(self, ip_address: str):
        """更新设备信息（如果需要可以扩展）
        
        Args:
            ip_address: 设备IP地址
        """
        # 这里可以添加更新设备信息的逻辑
        # 例如：更新device对象的device_ip属性
        pass
