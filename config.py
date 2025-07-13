import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Line Bot 設定
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    
    # OpenAI 設定
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # 郵件設定
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_TO = os.getenv('EMAIL_TO')
    
    # 資料庫設定
    DATABASE_PATH = 'never_give_up.db'
    
    # 時間設定
    MORNING_TIME = "08:00"
    EVENING_TIME = "20:00"
    SUMMARY_TIME = "20:30" 