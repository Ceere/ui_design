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
                return True
            else:
                return False
            
        except Exception as e:
            return False, f'Connection error: {str(e)}'
    