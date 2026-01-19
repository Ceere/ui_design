import cv2
import base64
import numpy as np
from typing import Optional

def nv12_to_bgr(nv12_image, width, height):
        """
        Convert NV12 image to BGR format.
        """
        yuv = nv12_image.reshape((height * 3 // 2, width))
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
        return bgr

def process_image_message(msg) -> Optional[np.ndarray]:
    """将 ROS 消息转换为 numpy 图像数组"""
    try:
        image_bytes = base64.b64decode(msg['data'])
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        
        if msg['encoding'] == 'bgr8':
            return img_array.reshape((msg['height'], msg['width'], 3))
        elif msg['encoding'] == 'rgb8':
            return img_array.reshape((msg['height'], msg['width'], 3))
        elif msg['encoding'] == 'nv12':
            return nv12_to_bgr(img_array, msg['width'], msg['height'])
    except Exception as e:
        return None

def handle_image_message(msg):

    if 'data' in msg and 'encoding' in msg:  
        img = process_image_message(msg)
        if img is not None:
            _, buffer = cv2.imencode('.png', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            return img_base64
 