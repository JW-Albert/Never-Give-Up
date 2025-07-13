import csv
import io
import datetime
from database import Database

class ExpenseService:
    def __init__(self):
        self.db = Database()
    
    def add_expense(self, user_id, amount, category, description):
        """新增記帳記錄"""
        try:
            # 驗證金額
            amount = float(amount)
            if amount <= 0:
                return False, "金額必須大於0"
            
            # 驗證分類
            if not category or len(category.strip()) == 0:
                return False, "請選擇或輸入分類"
            
            # 儲存記錄
            self.db.save_expense(user_id, amount, category.strip(), description.strip())
            return True, "記帳成功！"
            
        except ValueError:
            return False, "金額格式錯誤，請輸入數字"
        except Exception as e:
            return False, f"記帳失敗：{str(e)}"
    
    def get_today_expenses(self, user_id):
        """取得今日記帳記錄"""
        today = datetime.date.today()
        expenses = self.db.get_expenses(user_id, today, today)
        
        result = []
        for expense in expenses:
            result.append({
                'id': expense[0],
                'amount': expense[1],
                'category': expense[2],
                'description': expense[3],
                'date': expense[4]
            })
        
        return result
    
    def get_expense_summary(self, user_id, days=7):
        """取得記帳統計"""
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        summary = self.db.get_expense_summary(user_id, start_date, end_date)
        return summary
    
    def export_expenses_csv(self, user_id, start_date=None, end_date=None):
        """匯出記帳記錄為CSV"""
        if start_date is None:
            start_date = datetime.date.today() - datetime.timedelta(days=30)
        if end_date is None:
            end_date = datetime.date.today()
        
        expenses = self.db.get_expenses(user_id, start_date, end_date)
        
        # 建立CSV內容
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 寫入標題
        writer.writerow(['日期', '分類', '金額', '描述'])
        
        # 寫入資料
        for expense in expenses:
            writer.writerow([
                expense[4],  # 日期
                expense[2],  # 分類
                expense[1],  # 金額
                expense[3]   # 描述
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    def get_categories(self, user_id):
        """取得用戶可用的分類"""
        return self.db.get_user_categories(user_id)
    
    def add_category(self, user_id, category_name):
        """新增自定義分類"""
        try:
            if not category_name or len(category_name.strip()) == 0:
                return False, "分類名稱不能為空"
            
            # 檢查是否已存在
            existing_categories = self.get_categories(user_id)
            if category_name.strip() in existing_categories:
                return False, "分類已存在"
            
            self.db.save_category(user_id, category_name.strip())
            return True, "分類新增成功！"
            
        except Exception as e:
            return False, f"新增分類失敗：{str(e)}"
    
    def format_expense_message(self, expenses, summary=None):
        """格式化記帳訊息"""
        if not expenses:
            return "今天還沒有記帳記錄。"
        
        message = "📊 記帳記錄：\n\n"
        
        total = 0
        for expense in expenses:
            amount = expense['amount']
            total += amount
            message += f"💰 {expense['category']}: ${amount:,.0f}\n"
            if expense['description']:
                message += f"   📝 {expense['description']}\n"
            message += "\n"
        
        message += f"💵 今日總支出: ${total:,.0f}"
        
        if summary and summary['categories']:
            message += "\n\n📈 分類統計：\n"
            for cat in summary['categories'][:5]:  # 只顯示前5個分類
                percentage = (cat['total'] / total * 100) if total > 0 else 0
                message += f"• {cat['category']}: ${cat['total']:,.0f} ({percentage:.1f}%)\n"
        
        return message
    
    def format_summary_message(self, summary, days=7):
        """格式化統計訊息"""
        if not summary or summary['total'] == 0:
            return f"過去{days}天沒有記帳記錄。"
        
        message = f"📊 過去{days}天記帳統計：\n\n"
        message += f"💵 總支出: ${summary['total']:,.0f}\n"
        message += f"📅 平均每日: ${summary['total']/days:,.0f}\n\n"
        
        if summary['categories']:
            message += "🏷️ 分類統計：\n"
            for i, cat in enumerate(summary['categories'][:5], 1):
                percentage = (cat['total'] / summary['total'] * 100) if summary['total'] > 0 else 0
                message += f"{i}. {cat['category']}: ${cat['total']:,.0f} ({percentage:.1f}%)\n"
        
        return message
    
    def parse_expense_input(self, text):
        """解析記帳輸入文字"""
        """支援格式：
        1. 金額 分類 描述 (例如: 100 飲食 午餐)
        2. 分類 金額 描述 (例如: 飲食 100 午餐)
        3. 金額 分類 (例如: 100 飲食)
        """
        parts = text.strip().split()
        
        if len(parts) < 2:
            return None, None, None
        
        # 嘗試解析金額
        amount = None
        category = None
        description = None
        
        # 檢查第一個部分是否為數字
        try:
            amount = float(parts[0])
            if len(parts) >= 2:
                category = parts[1]
            if len(parts) >= 3:
                description = ' '.join(parts[2:])
        except ValueError:
            # 第一個不是數字，可能是分類
            if len(parts) >= 2:
                try:
                    amount = float(parts[1])
                    category = parts[0]
                    if len(parts) >= 3:
                        description = ' '.join(parts[2:])
                except ValueError:
                    return None, None, None
        
        return amount, category, description 