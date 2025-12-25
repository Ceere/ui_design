from device.device import get_device
from ros.ros_bridge import get_ros_bridge
import logging

def connect_device(device_ip: str) -> bool:
    """连接到指定IP地址的设备
    
    Args:
        device_ip: 设备IP地址
        
    Returns:
        bool: 连接是否成功
    """
    logging.debug(f"Connecting to device: {device_ip}")
    ros_bridge = get_ros_bridge()
    
    # 调用ROS桥接器的连接方法
    if ros_bridge.connect_ros_bridge(ros_host=device_ip):
        logging.info(f"Successfully connected to device: {device_ip}")
        return True
    else:
        logging.error(f"Failed to connect to device: {device_ip}")
        return False
