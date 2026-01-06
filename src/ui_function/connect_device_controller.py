"""
用于主页面，负责device对象，ssh对象，ros bridge对象的创建以及初始化
"""
from ros.ros_bridge import get_ros_bridge
from device.device import get_device
from ssh.ssh import get_ssh_manager
import datetime
import logging


class ConnectDeviceController:
    """连接设备控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.ros_bridge = get_ros_bridge()
        self.ssh_manager = get_ssh_manager()
        self.device = get_device()
    
    def init_bridge_ssh(self, ip_address: str, ssh_port: int = 22, ros_port: int = 9090, 
                         username: str = "root", password: str = None) -> tuple[bool, str]:
        """连接到设备 - 同时连接ROS和SSH
        
        Args:
            ip_address: 设备IP地址
            ssh_port: SSH端口号
            ros_port: ROS桥接端口号
            username: SSH用户名
            password: SSH密码
            
        Returns:
            tuple[bool, str]: (是否成功, 消息)
        """
        if not ip_address:
            return False, 'Please enter a device IP address'
        
        try:
            # 更新device的IP
            self.device.device_ip = ip_address
            
            # 连接ROS桥接器（使用指定的端口）
            ros_success = False
            try:
                # 调用ROS桥接器的连接方法，指定端口
                if self.ros_bridge.connect_ros_bridge(ros_host=ip_address, ros_port=ros_port):
                    ros_success = True
                else:
                    ros_success = False
            except Exception as ros_e:
                logging.error(f"ROS连接失败: {ros_e}")
                ros_success = False
            
            # 尝试连接SSH
            ssh_success = False
            try:
                ssh_success = self.ssh_manager.connect(
                    hostname=ip_address,
                    username=username,
                    password=password,
                    port=ssh_port
                )
            except Exception as ssh_e:
                logging.warning(f"SSH连接尝试失败: {ssh_e}")
            
            if ros_success:
                message = f"成功连接到设备 {ip_address}"
                if ssh_success:
                    message += f" (ROS:{ros_port}和SSH:{ssh_port}连接成功)"
                else:
                    message += f" (ROS:{ros_port}连接成功，SSH连接失败)"
                return True, message
            else:
                return False, f"无法连接到设备 {ip_address} (ROS端口: {ros_port}) (SSH端口: {ssh_port})"
            
        except Exception as e:
            return False, f'Connection error: {str(e)}'