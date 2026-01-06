from device.device import get_device
from ros.ros_bridge import get_ros_bridge
from ssh.ssh import get_ssh_manager

def get_object_instance():
    device_instance = get_device()
    ros_bridge_instance = get_ros_bridge()
    ssh_instance = get_ssh_manager()
    return device_instance,ros_bridge_instance,ssh_instance