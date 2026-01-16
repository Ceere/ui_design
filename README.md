# Qualcomm Robotics SDK Tools - ROS Topic查看器

## 项目简介

基于ROS和NiceGUI的Topic数据查看器。支持ROS Topic订阅、SSH远程命令执行、实时数据可视化等功能。

## Device环境配置

```bash
sudo apt install ros-jazzy-rosbridge-server
sudo apt install ros-jazzy-rosapi
source /opt/ros/jazzy/setup.bash
ros2 run rosapi rosapi_node &
ros2 run rosbridge_server rosbridge_websocket
```

## Host端环境配置

```bash
cd workspace
git clone https://github.com/Ceere/ui_design.git
pip install nicegui roslibpy paramiko opencv-python numpy
cd /workspace/to/ui_design
python src/ui/main.py
```