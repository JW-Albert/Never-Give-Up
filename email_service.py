import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import datetime

class EmailService:
    def __init__(self):
        self.host = Config.EMAIL_HOST
        self.port = Config.EMAIL_PORT
        self.user = Config.EMAIL_USER
        self.password = Config.EMAIL_PASSWORD
        self.to_email = Config.EMAIL_TO
    
    def send_daily_summary(self, user_name, summary_data):
        """發送每日總結郵件"""
        if not all([self.user, self.password, self.to_email]):
            print("郵件設定不完整，跳過發送郵件")
            return False
        
        try:
            # 建立郵件內容
            subject = f"Never Give Up - {user_name} 的每日總結 ({datetime.date.today()})"
            
            # 建立HTML內容
            html_content = self._create_summary_html(user_name, summary_data)
            
            # 建立郵件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.user
            msg['To'] = self.to_email
            
            # 附加HTML內容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 發送郵件
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            
            print(f"成功發送每日總結郵件給 {user_name}")
            return True
            
        except Exception as e:
            print(f"發送郵件失敗: {str(e)}")
            return False
    
    def _create_summary_html(self, user_name, summary_data):
        """建立總結HTML內容"""
        today = datetime.date.today()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #4CAF50; background-color: #f9f9f9; }}
                .goal-item {{ margin: 10px 0; padding: 10px; background-color: white; border-radius: 5px; }}
                .vocab-item {{ margin: 5px 0; padding: 5px; background-color: #e8f5e8; border-radius: 3px; }}
                .diary-content {{ background-color: white; padding: 15px; border-radius: 5px; font-style: italic; }}
                .expense-item {{ margin: 8px 0; padding: 8px; background-color: #fff3e0; border-radius: 3px; }}
                .expense-desc {{ margin: 2px 0 8px 15px; padding: 5px; background-color: #f5f5f5; border-radius: 3px; font-size: 0.9em; color: #666; }}
                .expense-total {{ margin: 10px 0; padding: 10px; background-color: #ffebee; border-radius: 5px; font-weight: bold; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Never Give Up - 每日總結</h1>
                <p>{user_name} 的 {today} 總結報告</p>
            </div>
        """
        
        # 今日目標
        if summary_data['goals']:
            html += """
            <div class="section">
                <h2>📋 今日目標</h2>
            """
            goals = summary_data['goals']
            for i, goal in enumerate([goals[0], goals[1], goals[2]], 1):
                if goal:
                    html += f'<div class="goal-item">🎯 目標 {i}: {goal}</div>'
            html += "</div>"
        
        # 今日日記
        if summary_data['diary']:
            html += f"""
            <div class="section">
                <h2>📝 今日日記</h2>
                <div class="diary-content">{summary_data['diary']}</div>
            </div>
            """
        
        # 今日單字學習
        if summary_data['vocabulary']:
            html += """
            <div class="section">
                <h2>📚 今日單字學習</h2>
            """
            for vocab in summary_data['vocabulary']:
                html += f'<div class="vocab-item">📖 {vocab}</div>'
            html += "</div>"
        
        # 今日記帳
        if summary_data.get('expenses'):
            html += """
            <div class="section">
                <h2>💰 今日記帳</h2>
            """
            total_expense = 0
            for expense in summary_data['expenses']:
                amount = expense['amount']
                total_expense += amount
                html += f'<div class="expense-item">💵 {expense["category"]}: ${amount:,.0f}</div>'
                if expense['description']:
                    html += f'<div class="expense-desc">📝 {expense["description"]}</div>'
            
            html += f'<div class="expense-total">💸 今日總支出: ${total_expense:,.0f}</div>'
            html += "</div>"
        
        # 如果沒有任何內容
        if not any([summary_data['goals'], summary_data['diary'], summary_data['vocabulary'], summary_data.get('expenses')]):
            html += """
            <div class="section">
                <h2>📊 今日總結</h2>
                <p>今天還沒有記錄任何內容，明天繼續加油！💪</p>
            </div>
            """
        
        html += """
            <div class="section">
                <p style="text-align: center; color: #666;">
                    --- Never Give Up 機器人自動發送 ---
                </p>
            </div>
        </body>
        </html>
        """
        
        return html 