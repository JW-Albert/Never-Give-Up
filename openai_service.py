import openai
from config import Config

class OpenAIService:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key
    
    def generate_motivational_message(self, user_name, goals=None):
        """生成激勵訊息"""
        if not self.api_key:
            return f"嗨 {user_name}，今天要達成的3件事是甚麼？"
        
        try:
            prompt = f"""
            請為用戶 {user_name} 生成一個溫暖的早晨問候和激勵訊息。
            如果用戶有設定目標，請根據目標內容給予鼓勵。
            
            要求：
            1. 使用繁體中文
            2. 語氣溫暖友善
            3. 包含問候和目標提醒
            4. 字數控制在100字以內
            """
            
            if goals:
                prompt += f"\n用戶今日目標：\n1. {goals[0] or '未設定'}\n2. {goals[1] or '未設定'}\n3. {goals[2] or '未設定'}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一個溫暖的個人助理，專門提供激勵和鼓勵。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API 錯誤: {str(e)}")
            return f"嗨 {user_name}，今天要達成的3件事是甚麼？"
    
    def generate_evening_reflection(self, user_name):
        """生成晚上反思提示"""
        if not self.api_key:
            return f"嗨 {user_name}，今天有什麼值得記錄下來的事情？"
        
        try:
            prompt = f"""
            請為用戶 {user_name} 生成一個溫暖的晚上反思提示。
            
            要求：
            1. 使用繁體中文
            2. 語氣溫暖友善
            3. 鼓勵用戶記錄今天的美好時刻
            4. 字數控制在80字以內
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一個溫暖的個人助理，專門幫助用戶進行日常反思。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API 錯誤: {str(e)}")
            return f"嗨 {user_name}，今天有什麼值得記錄下來的事情？"
    
    def generate_vocabulary_suggestions(self, user_name):
        """生成單字學習建議"""
        if not self.api_key:
            return f"提醒：{user_name}，記得背單字喔！"
        
        try:
            prompt = f"""
            請為用戶 {user_name} 生成一個單字學習提醒和建議。
            
            要求：
            1. 使用繁體中文
            2. 語氣鼓勵友善
            3. 可以包含一些學習建議
            4. 字數控制在60字以內
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一個溫暖的學習助理，專門鼓勵用戶進行語言學習。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API 錯誤: {str(e)}")
            return f"提醒：{user_name}，記得背單字喔！"
    
    def enhance_summary(self, summary_data):
        """使用AI增強總結內容"""
        if not self.api_key:
            return None
        
        try:
            # 建立總結內容
            summary_text = f"""
            用戶今日總結：
            
            目標：
            {summary_data.get('goals', ['未設定', '未設定', '未設定'])}
            
            日記：
            {summary_data.get('diary', '未記錄')}
            
            單字學習：
            {summary_data.get('vocabulary', [])}
            """
            
            prompt = f"""
            請根據以下用戶的今日總結，生成一個簡短的AI分析或建議：
            
            {summary_text}
            
            要求：
            1. 使用繁體中文
            2. 給予正面鼓勵
            3. 可以包含一些改進建議
            4. 字數控制在100字以內
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一個溫暖的個人成長助理，專門提供正面鼓勵和建設性建議。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=120,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API 錯誤: {str(e)}")
            return None 