import os
from typing import List, Optional
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class MyConfig:
    Real_File: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_NAME: Optional[str] = None
    UNSPLASH_ENABLE: str = None
    UNSPLASH_API_KEYS: Optional[List[str]] = None
    REDIS_ENABLE: str = None
    REDIS_URL: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None

    def __init__(self):
        # 从环境变量读取配置
        self.Real_File = os.getenv('REAL_FILE', 'config.ini')
        
        if self.Real_File == "config.ini":
            self.OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
            self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            self.OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-32B')
            self.UNSPLASH_ENABLE = os.getenv('UNSPLASH_ENABLE', 'false')
            
            # 处理UNSPLASH_API_KEY，如果有多个key用逗号分割
            unsplash_keys = os.getenv('UNSPLASH_API_KEY', '')
            self.UNSPLASH_API_KEYS = [key.strip() for key in unsplash_keys.split(',') if key.strip()]
            
            self.REDIS_ENABLE = os.getenv('REDIS_ENABLE', 'false')
            self.REDIS_URL = os.getenv('REDIS_URL')
            self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
        else:
            # 如果指定了其他配置文件，加载该文件
            load_dotenv(self.Real_File)
            self.OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
            self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            self.OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-32B')
            self.UNSPLASH_ENABLE = os.getenv('UNSPLASH_ENABLE', 'false')
            
            unsplash_keys = os.getenv('UNSPLASH_API_KEY', '')
            self.UNSPLASH_API_KEYS = [key.strip() for key in unsplash_keys.split(',') if key.strip()]
            
            self.REDIS_ENABLE = os.getenv('REDIS_ENABLE', 'false')
            self.REDIS_URL = os.getenv('REDIS_URL')
            self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
            
        print(self.OPENAI_API_KEY)
    
    def get_redis_enabled(self) -> bool:
        """返回Redis是否启用的布尔值"""
        return self.REDIS_ENABLE.lower() in ('true', '1', 'yes', 'on')
    
    def get_unsplash_enabled(self) -> bool:
        """返回Unsplash是否启用的布尔值"""
        return self.UNSPLASH_ENABLE.lower() in ('true', '1', 'yes', 'on')


if __name__ == '__main__':
    my_config = MyConfig()
    print(f"OpenAI模型名称: {my_config.OPENAI_MODEL_NAME}")
    print(f"Redis启用状态: {my_config.REDIS_ENABLE}")
    print(f"Redis启用状态(布尔值): {my_config.get_redis_enabled()}")
    print(f"Unsplash API Keys: {my_config.UNSPLASH_API_KEYS}")
