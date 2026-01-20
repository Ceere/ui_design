#!/usr/bin/env python3
"""
启动ROS Topic查看器应用
重构后使用清晰的分层架构
这个脚本确保从正确的目录运行应用
"""
import sys
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 切换到项目根目录（src/ui的父目录的父目录）
project_root = os.path.dirname(os.path.dirname(current_dir))
os.chdir(project_root)

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(project_root, 'src'))


from nicegui import ui
from ui.topic_page import topic_page
from ui_function.connect_device_controller import ConnectDeviceController

device_controller = ConnectDeviceController()

@ui.page('/')
def page():

    ui.page_title('Qualcomm Robotics SDK Tools')
    with ui.header(elevated=True).style('background-color: #4f6db9'):
        ui.link('Qualcomm Robotics SDK', '/').classes('text-red-500')
        ui.link('Topic', '/topic_page').classes('text-red-500')
    
    #占位
    ui.label()
    ui.label()
    ui.label()
    ui.label()
    ui.label()

    with ui.column().classes('flex w-full items-center justify-center'):
        ui.label('Welcome to use qualcomm robotics sdk and more').classes('text-blue-500')

    with ui.card().style('background-color: #ffffff; margin-bottom: 5px; margin-left: auto; margin-right: auto;'):
        
        # Connect to device
        with ui.column():

            device_ip_input = ui.input(label='Device IP', placeholder='10.64.39.55', value='10.64.39.55').classes('w-80')
            username = ui.input(label='Username', placeholder='guohmiao', value='guohmiao').classes('w-80')
            password = ui.input(label='Password', placeholder='password', password=True, password_toggle_button=True, value='oelinux123').classes('w-80')
            ssh_port = ui.input(label="SSH Port", placeholder='2345', value='2345').classes('w-80')
            ros_bridge_port = ui.input(label="ros bridge port", placeholder='9090', value='9090').classes('w-80')
            
            def handle_connect_click():
                """处理连接按钮点击"""
                ip = device_ip_input.value
                ssh_port_val = int(ssh_port.value) if ssh_port.value else 22
                ros_port_val = int(ros_bridge_port.value) if ros_bridge_port.value else 9090
                username_val = username.value if username.value else "root"
                password_val = password.value if password.value else None
                
                # 检查是否已经连接到相同的设备
                from ui_function.get_object import get_object_instance
                
                # 使用get_object_instance获取实例
                _, ros_bridge, ssh_manager = get_object_instance()
                
                # 检查ROS是否已经连接到相同的IP和端口
                ros_already_connected = (
                    ros_bridge.ros_is_connected and 
                    ros_bridge.ros_host == ip and 
                    ros_bridge.ros_port == ros_port_val
                )
                
                # 检查SSH是否已经连接到相同的IP和端口
                ssh_already_connected = (
                    ssh_manager.is_connected and
                    ssh_manager.hostname == ip and
                    ssh_manager.port == ssh_port_val and
                    ssh_manager.username == username_val
                )
                
                # 如果已经连接到相同的设备，直接跳转
                if ros_already_connected and ssh_already_connected:
                    ui.navigate.to('/topic_page')
                    return
                
                # 使用控制器处理连接逻辑
                success, message = device_controller.init_bridge_ssh(
                    ip_address=ip,
                    ssh_port=ssh_port_val,
                    ros_port=ros_port_val,
                    username=username_val,
                    password=password_val
                )
                
                # 显示连接结果
                if success:
                    ui.navigate.to('/topic_page')
                else:
                    ui.notify(message, type='negative')
            
            
    # 连接按钮 - 居中显示
    with ui.row().classes('w-full justify-center'):
        ui.button(text='Connect', on_click=handle_connect_click).style('margin: 0 auto;')

ui.run()
