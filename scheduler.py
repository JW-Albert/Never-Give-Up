import schedule
import time
import threading
import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
from config import Config
from database import Database
from email_service import EmailService
from openai_service import OpenAIService

class Scheduler:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.db = Database()
        self.email_service = EmailService()
        self.openai_service = OpenAIService()
        self.running = False
    
    def start(self):
        """啟動排程器"""
        if self.running:
            return
        
        self.running = True
        
        # 設定定時任務
        schedule.every().day.at(Config.MORNING_TIME).do(self.morning_task)
        schedule.every().day.at(Config.EVENING_TIME).do(self.evening_task)
        schedule.every().day.at(Config.SUMMARY_TIME).do(self.summary_task)
        
        # 在背景執行排程器
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        print(f"排程器已啟動，定時任務設定：")
        print(f"  早上 {Config.MORNING_TIME} - 發送目標提醒")
        print(f"  晚上 {Config.EVENING_TIME} - 發送日記提醒")
        print(f"  晚上 {Config.SUMMARY_TIME} - 發送總結郵件")
    
    def stop(self):
        """停止排程器"""
        self.running = False
        schedule.clear()
        print("排程器已停止")
    
    def _run_scheduler(self):
        """執行排程器主迴圈"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
    
    def morning_task(self):
        """早上任務：發送目標提醒"""
        print(f"執行早上任務 - {datetime.datetime.now()}")
        
        try:
            # 取得所有用戶
            users = self._get_all_users()
            
            for user_id in users:
                try:
                    user = self.db.get_user(user_id)
                    user_name = user[1] if user else "用戶"
                    
                    # 取得昨日目標作為參考
                    yesterday = datetime.date.today() - datetime.timedelta(days=1)
                    yesterday_goals = self.db.get_daily_goals(user_id, yesterday)
                    
                    # 生成激勵訊息
                    message = self.openai_service.generate_motivational_message(
                        user_name, 
                        yesterday_goals[1:4] if yesterday_goals else None
                    )
                    
                    # 發送訊息
                    self.line_bot_api.push_message(
                        user_id,
                        TextSendMessage(text=message)
                    )
                    
                    print(f"已發送早晨訊息給 {user_name}")
                    
                except Exception as e:
                    print(f"發送早晨訊息給用戶 {user_id} 失敗: {str(e)}")
            
        except Exception as e:
            print(f"早上任務執行失敗: {str(e)}")
    
    def evening_task(self):
        """晚上任務：發送日記提醒"""
        print(f"執行晚上任務 - {datetime.datetime.now()}")
        
        try:
            # 取得所有用戶
            users = self._get_all_users()
            
            for user_id in users:
                try:
                    user = self.db.get_user(user_id)
                    user_name = user[1] if user else "用戶"
                    
                    # 生成晚上反思提示
                    message = self.openai_service.generate_evening_reflection(user_name)
                    
                    # 發送訊息
                    self.line_bot_api.push_message(
                        user_id,
                        TextSendMessage(text=message)
                    )
                    
                    print(f"已發送晚上訊息給 {user_name}")
                    
                except Exception as e:
                    print(f"發送晚上訊息給用戶 {user_id} 失敗: {str(e)}")
            
        except Exception as e:
            print(f"晚上任務執行失敗: {str(e)}")
    
    def summary_task(self):
        """總結任務：發送每日總結郵件"""
        print(f"執行總結任務 - {datetime.datetime.now()}")
        
        try:
            # 取得所有用戶
            users = self._get_all_users()
            
            for user_id in users:
                try:
                    # 取得今日總結資料
                    summary_data = self.db.get_today_summary(user_id)
                    
                    # 使用AI增強總結
                    ai_enhancement = self.openai_service.enhance_summary(summary_data)
                    if ai_enhancement:
                        summary_data['ai_enhancement'] = ai_enhancement
                    
                    # 發送郵件
                    self.email_service.send_daily_summary(
                        summary_data['user_name'], 
                        summary_data
                    )
                    
                    print(f"已發送總結郵件給 {summary_data['user_name']}")
                    
                except Exception as e:
                    print(f"發送總結郵件給用戶 {user_id} 失敗: {str(e)}")
            
        except Exception as e:
            print(f"總結任務執行失敗: {str(e)}")
    
    def _get_all_users(self):
        """取得所有用戶ID"""
        conn = self.db.db_path
        import sqlite3
        conn = sqlite3.connect(conn)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users
    
    def send_vocabulary_reminder(self, user_id):
        """發送單字學習提醒"""
        try:
            user = self.db.get_user(user_id)
            user_name = user[1] if user else "用戶"
            
            message = self.openai_service.generate_vocabulary_suggestions(user_name)
            
            self.line_bot_api.push_message(
                user_id,
                TextSendMessage(text=message)
            )
            
            print(f"已發送單字提醒給 {user_name}")
            
        except Exception as e:
            print(f"發送單字提醒失敗: {str(e)}")
    
    def manual_trigger(self, task_type, user_id=None):
        """手動觸發任務（用於測試）"""
        if task_type == "morning":
            if user_id:
                # 為特定用戶執行
                users = [user_id]
            else:
                users = self._get_all_users()
            
            for uid in users:
                try:
                    user = self.db.get_user(uid)
                    user_name = user[1] if user else "用戶"
                    message = self.openai_service.generate_motivational_message(user_name)
                    self.line_bot_api.push_message(uid, TextSendMessage(text=message))
                    print(f"手動觸發早晨任務 - 已發送給 {user_name}")
                except Exception as e:
                    print(f"手動觸發早晨任務失敗: {str(e)}")
        
        elif task_type == "evening":
            if user_id:
                users = [user_id]
            else:
                users = self._get_all_users()
            
            for uid in users:
                try:
                    user = self.db.get_user(uid)
                    user_name = user[1] if user else "用戶"
                    message = self.openai_service.generate_evening_reflection(user_name)
                    self.line_bot_api.push_message(uid, TextSendMessage(text=message))
                    print(f"手動觸發晚上任務 - 已發送給 {user_name}")
                except Exception as e:
                    print(f"手動觸發晚上任務失敗: {str(e)}")
        
        elif task_type == "summary":
            if user_id:
                users = [user_id]
            else:
                users = self._get_all_users()
            
            for uid in users:
                try:
                    summary_data = self.db.get_today_summary(uid)
                    ai_enhancement = self.openai_service.enhance_summary(summary_data)
                    if ai_enhancement:
                        summary_data['ai_enhancement'] = ai_enhancement
                    self.email_service.send_daily_summary(summary_data['user_name'], summary_data)
                    print(f"手動觸發總結任務 - 已發送給 {summary_data['user_name']}")
                except Exception as e:
                    print(f"手動觸發總結任務失敗: {str(e)}") 