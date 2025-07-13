from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FollowEvent, UnfollowEvent
)
import re
from config import Config
from database import Database
from scheduler import Scheduler
from openai_service import OpenAIService
from expense_service import ExpenseService

app = Flask(__name__)

# Line Bot 設定
line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

# 初始化服務
db = Database()
scheduler = Scheduler(line_bot_api)
openai_service = OpenAIService()
expense_service = ExpenseService()

# 用戶狀態管理
user_states = {}

@app.route("/callback", methods=['POST'])
def callback():
    """Line Webhook 回調處理"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    """處理用戶加好友事件"""
    user_id = event.source.user_id
    
    try:
        # 取得用戶資料
        profile = line_bot_api.get_profile(user_id)
        user_name = profile.display_name
        
        # 儲存用戶資料
        db.add_user(user_id, user_name)
        
        # 發送歡迎訊息
        welcome_message = f"""
歡迎 {user_name}！👋

我是 Never Give Up 機器人，你的個人成長助理！

我的功能：
🌅 每天早上8點提醒你設定今日目標
📝 每天晚上8點提醒你記錄日記
📚 提醒你背單字
📧 每天晚上8:30發送每日總結到信箱

開始使用：
1. 直接輸入你的名字來設定
2. 輸入「目標」來設定今日目標
3. 輸入「日記」來記錄今天
4. 輸入「單字」來記錄學習的單字
5. 輸入「幫助」查看所有指令

讓我們一起成長吧！💪
        """
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=welcome_message)
        )
        
        print(f"新用戶加入: {user_name} ({user_id})")
        
    except Exception as e:
        print(f"處理加好友事件失敗: {str(e)}")

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    """處理用戶取消好友事件"""
    user_id = event.source.user_id
    print(f"用戶取消好友: {user_id}")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """處理文字訊息"""
    user_id = event.source.user_id
    text = event.message.text.strip()
    
    try:
        # 檢查用戶是否存在
        user = db.get_user(user_id)
        if not user:
            # 如果用戶不存在，先加入用戶
            profile = line_bot_api.get_profile(user_id)
            db.add_user(user_id, profile.display_name)
            user = db.get_user(user_id)
        
        user_name = user[1]
        
        # 處理指令
        if text.lower() in ['幫助', 'help', '指令', '功能']:
            handle_help(event)
        elif text.lower() in ['目標', 'goals', '設定目標']:
            handle_goals(event, user_id, user_name)
        elif text.lower() in ['日記', 'diary', '記錄日記']:
            handle_diary(event, user_id, user_name)
        elif text.lower() in ['單字', 'vocabulary', '背單字']:
            handle_vocabulary(event, user_id, user_name)
        elif text.lower() in ['總結', 'summary', '今日總結']:
            handle_summary(event, user_id, user_name)
        elif text.lower() in ['記帳', 'expense', '支出']:
            handle_expense(event, user_id, user_name)
        elif text.lower() in ['記帳統計', 'expense_summary', '支出統計']:
            handle_expense_summary(event, user_id, user_name)
        elif text.lower() in ['匯出記帳', 'export_expense', '匯出支出']:
            handle_export_expense(event, user_id, user_name)
        elif text.lower() in ['測試', 'test']:
            handle_test(event, user_id, user_name)
        elif user_id in user_states:
            # 處理狀態相關的回應
            handle_state_response(event, user_id, user_name, text)
        else:
            # 預設回應
            handle_default_response(event, user_name, text)
            
    except Exception as e:
        print(f"處理訊息失敗: {str(e)}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，處理您的訊息時發生錯誤，請稍後再試。")
        )

def handle_help(event):
    """處理幫助指令"""
    help_text = """
📋 Never Give Up 機器人指令說明

🎯 目標相關：
• 輸入「目標」- 設定今日3個目標
• 輸入「查看目標」- 查看今日目標

📝 日記相關：
• 輸入「日記」- 記錄今日日記
• 輸入「查看日記」- 查看今日日記

📚 學習相關：
• 輸入「單字」- 記錄學習的單字
• 輸入「查看單字」- 查看今日學習的單字

💰 記帳相關：
• 輸入「記帳」- 記錄支出
• 輸入「記帳統計」- 查看支出統計
• 輸入「匯出記帳」- 匯出記帳記錄

📊 總結相關：
• 輸入「總結」- 查看今日總結
• 輸入「測試」- 測試定時任務

⏰ 自動提醒：
• 早上8:00 - 目標提醒
• 晚上8:00 - 日記提醒  
• 晚上8:30 - 總結郵件

💡 小提示：直接輸入文字，我會智能判斷您的意圖！
    """
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=help_text)
    )

def handle_goals(event, user_id, user_name):
    """處理目標設定"""
    # 檢查是否已有今日目標
    today_goals = db.get_daily_goals(user_id)
    
    if today_goals and any([today_goals[2], today_goals[3], today_goals[4]]):
        # 已有目標，顯示現有目標
        goals_text = f"""
📋 {user_name} 的今日目標：

1. {today_goals[2] or '未設定'}
2. {today_goals[3] or '未設定'}  
3. {today_goals[4] or '未設定'}

要重新設定目標嗎？請輸入「重新設定目標」
        """
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=goals_text)
        )
    else:
        # 設定新目標
        user_states[user_id] = {
            'state': 'setting_goals',
            'step': 0,
            'goals': ['', '', '']
        }
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"好的 {user_name}！讓我們來設定今日的3個目標。\n\n請輸入第1個目標：")
        )

def handle_diary(event, user_id, user_name):
    """處理日記記錄"""
    # 檢查是否已有今日日記
    today_diary = db.get_diary(user_id)
    
    if today_diary and today_diary[2]:
        # 已有日記，顯示現有日記
        diary_text = f"""
📝 {user_name} 的今日日記：

{today_diary[2]}

要重新記錄日記嗎？請輸入「重新記錄日記」
        """
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=diary_text)
        )
    else:
        # 記錄新日記
        user_states[user_id] = {
            'state': 'writing_diary',
            'step': 0
        }
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"好的 {user_name}！請分享今天有什麼值得記錄的事情：")
        )

def handle_vocabulary(event, user_id, user_name):
    """處理單字記錄"""
    user_states[user_id] = {
        'state': 'recording_vocabulary',
        'step': 0
    }
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"好的 {user_name}！請輸入你今天學習的單字（可以一次輸入多個，用逗號分隔）：")
    )

def handle_summary(event, user_id, user_name):
    """處理總結查看"""
    summary_data = db.get_today_summary(user_id)
    
    summary_text = f"""
📊 {user_name} 的今日總結

🎯 今日目標：
1. {summary_data['goals'][0] if summary_data['goals'] and summary_data['goals'][0] else '未設定'}
2. {summary_data['goals'][1] if summary_data['goals'] and summary_data['goals'][1] else '未設定'}
3. {summary_data['goals'][2] if summary_data['goals'] and summary_data['goals'][2] else '未設定'}

📝 今日日記：
{summary_data['diary'] if summary_data['diary'] else '未記錄'}

📚 今日單字：
{', '.join(summary_data['vocabulary']) if summary_data['vocabulary'] else '未記錄'}

💰 今日記帳：
{', '.join([f"{exp['category']}:${exp['amount']:,.0f}" for exp in summary_data.get('expenses', [])]) if summary_data.get('expenses') else '未記錄'}

💪 繼續加油！
    """
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=summary_text)
    )

def handle_test(event, user_id, user_name):
    """處理測試指令"""
    test_text = f"""
🧪 測試功能

{user_name}，你可以測試以下功能：

1. 輸入「測試早晨」- 測試早晨訊息
2. 輸入「測試晚上」- 測試晚上訊息
3. 輸入「測試總結」- 測試總結郵件
4. 輸入「測試單字」- 測試單字提醒
    """
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=test_text)
    )

def handle_state_response(event, user_id, user_name, text):
    """處理狀態相關的回應"""
    state = user_states[user_id]
    
    if state['state'] == 'setting_goals':
        handle_goals_response(event, user_id, user_name, text, state)
    elif state['state'] == 'writing_diary':
        handle_diary_response(event, user_id, user_name, text, state)
    elif state['state'] == 'recording_vocabulary':
        handle_vocabulary_response(event, user_id, user_name, text, state)
    elif state['state'] == 'recording_expense':
        handle_expense_response(event, user_id, user_name, text, state)
    elif state['state'] == 'testing':
        handle_test_response(event, user_id, user_name, text, state)

def handle_goals_response(event, user_id, user_name, text, state):
    """處理目標設定的回應"""
    if text.lower() in ['取消', 'cancel', '退出']:
        del user_states[user_id]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已取消目標設定。")
        )
        return
    
    state['goals'][state['step']] = text
    state['step'] += 1
    
    if state['step'] < 3:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"很好！請輸入第{state['step'] + 1}個目標：")
        )
    else:
        # 儲存目標
        db.save_daily_goals(user_id, state['goals'][0], state['goals'][1], state['goals'][2])
        del user_states[user_id]
        
        goals_text = f"""
✅ 目標設定完成！

{user_name} 的今日目標：
1. {state['goals'][0]}
2. {state['goals'][1]}
3. {state['goals'][2]}

加油！我相信你可以完成這些目標！💪
        """
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=goals_text)
        )

def handle_diary_response(event, user_id, user_name, text, state):
    """處理日記記錄的回應"""
    if text.lower() in ['取消', 'cancel', '退出']:
        del user_states[user_id]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已取消日記記錄。")
        )
        return
    
    # 儲存日記
    db.save_diary(user_id, text)
    del user_states[user_id]
    
    diary_text = f"""
✅ 日記記錄完成！

{user_name} 的今日日記：
{text}

謝謝你分享今天的故事！📝
    """
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=diary_text)
    )

def handle_vocabulary_response(event, user_id, user_name, text, state):
    """處理單字記錄的回應"""
    if text.lower() in ['取消', 'cancel', '退出']:
        del user_states[user_id]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已取消單字記錄。")
        )
        return
    
    # 儲存單字
    db.save_vocabulary_record(user_id, text)
    del user_states[user_id]
    
    vocab_text = f"""
✅ 單字記錄完成！

{user_name} 今天學習的單字：
{text}

繼續保持學習的熱情！📚
    """
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=vocab_text)
    )

def handle_expense_response(event, user_id, user_name, text, state):
    """處理記帳回應"""
    if text.lower() in ['取消', 'cancel', '退出']:
        del user_states[user_id]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已取消記帳。")
        )
        return
    
    # 檢查是否要新增分類
    if text.startswith('新增分類'):
        category_name = text.replace('新增分類', '').strip()
        if category_name:
            success, message = expense_service.add_category(user_id, category_name)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=message)
            )
            return
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入分類名稱，例如：新增分類 寵物用品")
            )
            return
    
    # 解析記帳輸入
    amount, category, description = expense_service.parse_expense_input(text)
    
    if amount is None or category is None:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="格式錯誤！請使用以下格式：\n• 100 飲食 午餐\n• 飲食 100 午餐\n• 50 交通")
        )
        return
    
    # 儲存記帳
    success, message = expense_service.add_expense(user_id, amount, category, description)
    
    if success:
        # 顯示今日記帳
        today_expenses = expense_service.get_today_expenses(user_id)
        summary = expense_service.get_expense_summary(user_id, 1)
        expense_message = expense_service.format_expense_message(today_expenses, summary)
        
        complete_message = f"""
✅ {message}

{expense_message}

要繼續記帳嗎？請輸入下一筆支出，或輸入「完成」結束記帳。
        """
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=complete_message)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"❌ {message}")
        )

def handle_test_response(event, user_id, user_name, text, state):
    """處理測試回應"""
    if text == '測試早晨':
        scheduler.manual_trigger('morning', user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已發送測試早晨訊息！")
        )
    elif text == '測試晚上':
        scheduler.manual_trigger('evening', user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已發送測試晚上訊息！")
        )
    elif text == '測試總結':
        scheduler.manual_trigger('summary', user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已發送測試總結郵件！")
        )
    elif text == '測試單字':
        scheduler.send_vocabulary_reminder(user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已發送測試單字提醒！")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入正確的測試指令。")
        )
    
    del user_states[user_id]

def handle_default_response(event, user_name, text):
    """處理預設回應"""
    # 使用AI生成回應
    try:
        ai_response = openai_service.generate_motivational_message(user_name)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ai_response)
        )
    except:
        # 如果AI失敗，使用預設回應
        default_text = f"""
嗨 {user_name}！

我理解您想說：「{text}」

您可以使用以下指令：
• 「目標」- 設定今日目標
• 「日記」- 記錄今日日記
• 「單字」- 記錄學習單字
• 「記帳」- 記錄支出
• 「總結」- 查看今日總結
• 「幫助」- 查看所有指令

有什麼我可以幫助您的嗎？
        """
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=default_text)
        )

def handle_expense(event, user_id, user_name):
    """處理記帳功能"""
    # 檢查是否已有今日記帳
    today_expenses = expense_service.get_today_expenses(user_id)
    
    if today_expenses:
        # 顯示今日記帳
        summary = expense_service.get_expense_summary(user_id, 1)
        message = expense_service.format_expense_message(today_expenses, summary)
        message += "\n\n要新增記帳嗎？請輸入記帳內容，格式：金額 分類 描述"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )
    else:
        # 開始記帳
        user_states[user_id] = {
            'state': 'recording_expense',
            'step': 0
        }
        
        categories = expense_service.get_categories(user_id)
        categories_text = '\n'.join([f"• {cat}" for cat in categories[:10]])  # 只顯示前10個
        
        message = f"""
💰 記帳功能

{user_name}，請輸入記帳內容：

📝 格式範例：
• 100 飲食 午餐
• 飲食 100 午餐
• 50 交通

🏷️ 可用分類：
{categories_text}

💡 小提示：您也可以直接輸入「新增分類 分類名稱」來新增自定義分類
        """
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )

def handle_expense_summary(event, user_id, user_name):
    """處理記帳統計"""
    summary = expense_service.get_expense_summary(user_id, 7)
    message = expense_service.format_summary_message(summary, 7)
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

def handle_export_expense(event, user_id, user_name):
    """處理匯出記帳"""
    try:
        # 生成CSV內容
        csv_content = expense_service.export_expenses_csv(user_id)
        
        # 建立檔案名稱
        from datetime import datetime
        filename = f"記帳記錄_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # 發送檔案（這裡需要實作檔案發送功能）
        # 由於Line Bot的限制，我們先提供下載連結或直接顯示內容
        message = f"""
📊 記帳記錄匯出

{user_name}，您的記帳記錄已準備好！

📁 檔案名稱：{filename}
📄 記錄筆數：{len(csv_content.split('\n')) - 2} 筆
📅 時間範圍：過去30天

💡 由於Line Bot限制，請複製以下CSV內容到您的電腦：

{csv_content[:1000]}...

（內容過長，已截斷。完整內容請聯繫管理員）
        """
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )
        
    except Exception as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"匯出失敗：{str(e)}")
        )

if __name__ == "__main__":
    # 啟動排程器
    scheduler.start()
    
    print("Never Give Up Line Bot 已啟動！")
    print("定時任務已設定：")
    print(f"  早上 {Config.MORNING_TIME} - 發送目標提醒")
    print(f"  晚上 {Config.EVENING_TIME} - 發送日記提醒")
    print(f"  晚上 {Config.SUMMARY_TIME} - 發送總結郵件")
    
    # 啟動Flask應用
    app.run(host='0.0.0.0', port=5000, debug=True) 