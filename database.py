import sqlite3
import datetime
from config import Config

class Database:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """初始化資料庫表格"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用戶表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 每日目標表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                goal1 TEXT,
                goal2 TEXT,
                goal3 TEXT,
                date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 日記表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                content TEXT,
                date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 單字學習記錄表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                words TEXT,
                date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 記帳表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                amount DECIMAL(10,2) NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 記帳分類表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                category_name TEXT NOT NULL,
                color TEXT DEFAULT '#4CAF50',
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, name):
        """新增用戶"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, name)
            VALUES (?, ?)
        ''', (user_id, name))
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        """取得用戶資料"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def save_daily_goals(self, user_id, goal1, goal2, goal3):
        """儲存每日目標"""
        today = datetime.date.today()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO daily_goals (user_id, goal1, goal2, goal3, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, goal1, goal2, goal3, today))
        conn.commit()
        conn.close()
    
    def get_daily_goals(self, user_id, date=None):
        """取得每日目標"""
        if date is None:
            date = datetime.date.today()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM daily_goals 
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))
        goals = cursor.fetchone()
        conn.close()
        return goals
    
    def save_diary(self, user_id, content):
        """儲存日記"""
        today = datetime.date.today()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO diaries (user_id, content, date)
            VALUES (?, ?, ?)
        ''', (user_id, content, today))
        conn.commit()
        conn.close()
    
    def get_diary(self, user_id, date=None):
        """取得日記"""
        if date is None:
            date = datetime.date.today()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM diaries 
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))
        diary = cursor.fetchone()
        conn.close()
        return diary
    
    def save_vocabulary_record(self, user_id, words):
        """儲存單字學習記錄"""
        today = datetime.date.today()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vocabulary_records (user_id, words, date)
            VALUES (?, ?, ?)
        ''', (user_id, words, today))
        conn.commit()
        conn.close()
    
    def get_today_summary(self, user_id):
        """取得今日總結資料"""
        today = datetime.date.today()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 取得用戶資料
        cursor.execute('SELECT name FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        # 取得今日目標
        cursor.execute('''
            SELECT goal1, goal2, goal3 FROM daily_goals 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        goals = cursor.fetchone()
        
        # 取得今日日記
        cursor.execute('''
            SELECT content FROM diaries 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        diary = cursor.fetchone()
        
        # 取得今日單字記錄
        cursor.execute('''
            SELECT words FROM vocabulary_records 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        vocab_records = cursor.fetchall()
        
        conn.close()
        
        # 取得今日記帳記錄
        cursor.execute('''
            SELECT amount, category, description FROM expenses 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        expense_records = cursor.fetchall()
        
        conn.close()
        
        return {
            'user_name': user[0] if user else '用戶',
            'goals': goals,
            'diary': diary[0] if diary else None,
            'vocabulary': [record[0] for record in vocab_records],
            'expenses': [{'amount': record[0], 'category': record[1], 'description': record[2]} for record in expense_records]
        }
    
    def save_expense(self, user_id, amount, category, description, date=None):
        """儲存記帳記錄"""
        if date is None:
            date = datetime.date.today()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (user_id, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, amount, category, description, date))
        conn.commit()
        conn.close()
    
    def get_expenses(self, user_id, start_date=None, end_date=None):
        """取得記帳記錄"""
        if start_date is None:
            start_date = datetime.date.today()
        if end_date is None:
            end_date = start_date
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, amount, category, description, date 
            FROM expenses 
            WHERE user_id = ? AND date BETWEEN ? AND ?
            ORDER BY date DESC, created_at DESC
        ''', (user_id, start_date, end_date))
        expenses = cursor.fetchall()
        conn.close()
        return expenses
    
    def get_expense_summary(self, user_id, start_date=None, end_date=None):
        """取得記帳統計"""
        if start_date is None:
            start_date = datetime.date.today()
        if end_date is None:
            end_date = start_date
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 總支出
        cursor.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE user_id = ? AND date BETWEEN ? AND ?
        ''', (user_id, start_date, end_date))
        total = cursor.fetchone()[0] or 0
        
        # 分類統計
        cursor.execute('''
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses 
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
        ''', (user_id, start_date, end_date))
        categories = cursor.fetchall()
        
        conn.close()
        
        return {
            'total': total,
            'categories': [{'category': cat[0], 'total': cat[1], 'count': cat[2]} for cat in categories]
        }
    
    def get_default_categories(self):
        """取得預設記帳分類"""
        return [
            '飲食', '交通', '購物', '娛樂', '醫療', 
            '教育', '居住', '通訊', '其他'
        ]
    
    def save_category(self, user_id, category_name, color='#4CAF50'):
        """儲存自定義分類"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expense_categories (user_id, category_name, color)
            VALUES (?, ?, ?)
        ''', (user_id, category_name, color))
        conn.commit()
        conn.close()
    
    def get_user_categories(self, user_id):
        """取得用戶的分類"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category_name, color FROM expense_categories 
            WHERE user_id = ?
            ORDER BY created_at
        ''', (user_id,))
        categories = cursor.fetchall()
        conn.close()
        
        # 合併預設分類和自定義分類
        default_categories = self.get_default_categories()
        custom_categories = [cat[0] for cat in categories]
        
        return default_categories + custom_categories 