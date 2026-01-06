"""
SSH连接管理器 - 简化的SSH连接和执行命令功能
单例模式，可以更新参数
"""
import paramiko
import logging
from typing import Tuple


class SSHManager:
    """简化的SSH连接管理器类 - 单例模式"""
    
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, hostname: str = "localhost", username: str = "root", port: int = 22):
        """初始化SSH管理器
        
        Args:
            hostname: SSH主机地址
            username: 用户名
            port: 端口号
        """
        # 确保只初始化一次
        if not SSHManager._initialized:
            self.hostname = hostname
            self.username = username
            self.port = port
            self.ssh_client = None
            self.is_connected = False
            SSHManager._initialized = True
    
    def update_parameters(self, hostname: str = None, username: str = None, port: int = None) -> bool:
        """更新连接参数，如果需要则重新连接
        
        Args:
            hostname: 新的主机名
            username: 新的用户名
            port: 新的端口号
            
        Returns:
            bool: 是否需要重新连接
        """
        need_reconnect = False
        
        if hostname is not None and hostname != self.hostname:
            self.hostname = hostname
            need_reconnect = True
        
        if username is not None and username != self.username:
            self.username = username
            need_reconnect = True
        
        if port is not None and port != self.port:
            self.port = port
            need_reconnect = True
        
        return need_reconnect
    
    def connect(self, hostname: str = None, username: str = None, 
                password: str = None, port: int = None) -> bool:
        """连接到SSH服务器
        
        Args:
            hostname: 主机名或IP地址（如果为None则使用当前设置）
            username: 用户名（如果为None则使用当前设置）
            password: 密码（可选）
            port: 端口号（如果为None则使用当前设置）
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 更新参数并检查是否需要重新连接
            need_reconnect = self.update_parameters(hostname, username, port)
            
            # 如果客户端不存在或者需要重新连接，创建新的连接
            if self.ssh_client is None or need_reconnect:
                if self.ssh_client is not None:
                    self.disconnect()
                
                # 创建SSH客户端
                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # 连接参数
                connect_kwargs = {
                    'hostname': self.hostname,
                    'username': self.username,
                    'port': self.port,
                    'timeout': 10
                }
                
                if password:
                    connect_kwargs['password'] = password
                
                # 建立连接
                self.ssh_client.connect(**connect_kwargs)
                self.is_connected = True
                
                logging.info(f"成功连接到SSH服务器: {self.username}@{self.hostname}:{self.port}")
                return True
            else:
                # 已经连接
                logging.info(f"SSH已经连接到: {self.username}@{self.hostname}:{self.port}")
                return True
            
        except Exception as e:
            logging.error(f"SSH连接失败: {e}")
            self.disconnect()
            return False
    
    def disconnect(self):
        """断开SSH连接"""
        try:
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
            
            self.is_connected = False
            logging.info("SSH连接已断开")
            
        except Exception as e:
            logging.error(f"断开SSH连接时出错: {e}")
    
    def execute_command(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """执行SSH命令并获取结果
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            
        Returns:
            Tuple[bool, str, str]: (是否成功, 标准输出, 标准错误)
        """
        if not self.is_connected or not self.ssh_client:
            return False, "", "未连接到SSH服务器"
        
        try:
            # 执行命令
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            
            # 读取输出
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            return True, output, error
            
        except Exception as e:
            error_msg = f"执行命令失败: {e}"
            logging.error(error_msg)
            return False, "", error_msg
    
    def __del__(self):
        """析构函数，确保断开连接"""
        self.disconnect()


def get_ssh_manager():
    """获取SSH管理器单例实例
    
    Returns:
        SSHManager: SSH管理器实例
    """
    ssh_manager = SSHManager()
    return ssh_manager
