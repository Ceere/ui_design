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
from ui.connect_device import connect_device_page
from device.device import device
from ros.ros_bridge import RosBridge

@ui.page('/')
def page():

    ui.page_title('Qualcomm Robotics SDK Tools')
    with ui.header(elevated=True).style('background-color: #4f6db9'):
        ui.link('Qualcomm Robotics SDK', '/').classes('text-red-500')
        ui.link('Connect device', '/connect_device_page').classes('text-red-500')
    
    with ui.column().classes('flex w-full items-center justify-center'):
        ui.label('Welcome to use qualcomm robotics sdk and more').classes('text-blue-500')
        ui.button("Continue").on_click(lambda: ui.navigate.to('/connect_device_page')).classes('mt-4')

ui.run()
