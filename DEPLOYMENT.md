# Never-Give-Up Line Bot 部署指南

## 🚀 部署選項

### 1. 本地開發環境

#### 前置需求
- Python 3.8+
- pip
- ngrok (用於本地測試)

#### 步驟
```bash
# 1. 克隆專案
git clone <your-repo-url>
cd Never-Give-Up

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 設定環境變數
cp env_example.txt .env
# 編輯 .env 檔案

# 5. 測試功能
python test_bot.py

# 6. 啟動機器人
python app.py
```

#### 使用ngrok進行本地測試
```bash
# 安裝ngrok
# 啟動隧道
ngrok http 5000

# 複製HTTPS URL，設定到Line Developers Console
# Webhook URL: https://your-ngrok-url.ngrok.io/callback
```

### 2. Heroku 部署

#### 前置需求
- Heroku帳號
- Heroku CLI

#### 步驟
```bash
# 1. 登入Heroku
heroku login

# 2. 建立Heroku應用
heroku create your-app-name

# 3. 設定環境變數
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_token
heroku config:set LINE_CHANNEL_SECRET=your_secret
heroku config:set OPENAI_API_KEY=your_openai_key
heroku config:set EMAIL_USER=your_email
heroku config:set EMAIL_PASSWORD=your_password
heroku config:set EMAIL_TO=recipient_email

# 4. 部署
git add .
git commit -m "Initial deployment"
git push heroku main

# 5. 設定Webhook URL
# 在Line Developers Console設定：
# https://your-app-name.herokuapp.com/callback
```

#### 建立Procfile
```procfile
web: python app.py
```

### 3. Google Cloud Platform 部署

#### 前置需求
- Google Cloud帳號
- Google Cloud CLI

#### 步驟
```bash
# 1. 初始化專案
gcloud init

# 2. 啟用App Engine
gcloud app create

# 3. 部署
gcloud app deploy

# 4. 設定環境變數
gcloud app deploy --set-env-vars LINE_CHANNEL_ACCESS_TOKEN=your_token
```

#### 建立app.yaml
```yaml
runtime: python39
entrypoint: python app.py

env_variables:
  LINE_CHANNEL_ACCESS_TOKEN: "your_token"
  LINE_CHANNEL_SECRET: "your_secret"
  OPENAI_API_KEY: "your_openai_key"
```

### 4. AWS 部署

#### 使用AWS Lambda + API Gateway

#### 步驟
1. 建立Lambda函數
2. 設定API Gateway
3. 上傳程式碼
4. 設定環境變數
5. 設定Webhook URL

### 5. Vercel 部署

#### 步驟
```bash
# 1. 安裝Vercel CLI
npm i -g vercel

# 2. 部署
vercel

# 3. 設定環境變數
vercel env add LINE_CHANNEL_ACCESS_TOKEN
vercel env add LINE_CHANNEL_SECRET
```

## 🔧 環境變數設定

### 必需變數
```env
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
```

### 可選變數
```env
# OpenAI API (建議設定)
OPENAI_API_KEY=your_openai_api_key

# 郵件設定
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient_email@example.com
```

## 📱 Line Bot 設定

### 1. 建立Line Bot
1. 前往 [Line Developers Console](https://developers.line.biz/)
2. 建立新的Provider
3. 建立Messaging API頻道
4. 取得Channel Access Token和Channel Secret

### 2. 設定Webhook
- Webhook URL: `https://your-domain.com/callback`
- 啟用Webhook
- 設定簽名驗證

### 3. 取得QR Code
- 在Line Developers Console取得QR Code
- 掃描加入機器人好友

## 🔒 安全性設定

### 1. 環境變數
- 永遠不要將敏感資訊提交到Git
- 使用環境變數管理所有敏感資訊
- 定期更換API金鑰

### 2. 資料庫安全
- 使用參數化查詢防止SQL注入
- 定期備份資料庫
- 限制資料庫存取權限

### 3. HTTPS
- 確保所有外部存取都使用HTTPS
- 設定適當的SSL憑證

## 📊 監控和日誌

### 1. 應用程式日誌
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. 錯誤監控
- 設定錯誤通知
- 監控API使用量
- 追蹤用戶活動

### 3. 效能監控
- 監控回應時間
- 追蹤資料庫查詢效能
- 監控記憶體使用量

## 🚨 故障排除

### 常見問題

#### 1. Webhook驗證失敗
- 檢查Channel Secret設定
- 確認Webhook URL正確
- 檢查伺服器時間同步

#### 2. 機器人沒有回應
- 檢查伺服器是否運行
- 確認Line Bot設定正確
- 檢查日誌檔案

#### 3. 定時任務不執行
- 確認伺服器時間正確
- 檢查排程器是否啟動
- 確認資料庫連接正常

#### 4. 郵件發送失敗
- 檢查SMTP設定
- 確認應用程式密碼正確
- 檢查防火牆設定

### 除錯技巧
```bash
# 查看日誌
tail -f app.log

# 測試資料庫連接
python -c "from database import Database; db = Database(); print('DB OK')"

# 測試Line Bot API
python -c "from linebot import LineBotApi; api = LineBotApi('your_token'); print('API OK')"
```

## 📈 擴展建議

### 1. 資料庫升級
- 考慮使用PostgreSQL或MySQL
- 實作資料庫連接池
- 加入資料庫遷移功能

### 2. 快取系統
- 使用Redis快取常用資料
- 實作會話管理
- 加入API回應快取

### 3. 微服務架構
- 分離不同功能模組
- 使用訊息佇列
- 實作服務發現

### 4. 容器化
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## 📞 支援

如果遇到問題，請：
1. 檢查本文件的故障排除部分
2. 查看GitHub Issues
3. 提交新的Issue並提供詳細資訊

---

💪 **祝您部署順利！** 