import cv2
import base64
import numpy as np
from typing import Optional

def process_image_message(msg) -> Optional[np.ndarray]:
    """将 ROS 消息转换为 numpy 图像数组"""
    try:
        image_bytes = base64.b64decode(msg['data'])
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        
        if msg['encoding'] == 'bgr8':
            return img_array.reshape((msg['height'], msg['width'], 3))
        elif msg['encoding'] == 'rgb8':
            return img_array.reshape((msg['height'], msg['width'], 3))
        else:
            raise ValueError(f"不支持的编码格式: {msg['encoding']}")
    except Exception as e:
        return None

def handle_image_message(msg):

    if 'data' in msg and 'encoding' in msg:  
        img = process_image_message(msg)
        if img is not None:
            _, buffer = cv2.imencode('.png', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            return img_base64
 