# Never-Give-Up Line Bot

一個智能的Line機器人，幫助您建立良好的日常習慣和個人成長追蹤。

## 🎯 功能特色

1. **🌅 早上8點自動提醒**：傳送訊息詢問今日要達成的3件事
2. **📝 智能目標管理**：儲存和管理您的每日目標
3. **📚 單字學習提醒**：提醒您背單字，建立學習習慣
4. **🌙 晚上8點日記提醒**：提醒您記錄今天值得記住的事情
5. **📊 智能日記系統**：儲存您的每日反思和記錄
6. **📧 晚上8:30自動總結**：將今日所有內容整理成精美郵件發送
7. **🤖 AI智能對話**：整合OpenAI API，提供個性化回應和建議
8. **💰 智能記帳系統**：記錄支出、分類統計、CSV匯出功能

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

複製 `env_example.txt` 為 `.env` 並填入您的設定：

```bash
cp env_example.txt .env
```

編輯 `.env` 檔案：

```env
# Line Bot 設定 (必需)
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
LINE_CHANNEL_SECRET=your_line_channel_secret_here

# OpenAI 設定 (可選，但建議設定)
OPENAI_API_KEY=your_openai_api_key_here

# 郵件設定 (可選，用於發送每日總結)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_TO=recipient_email@example.com
```

### 3. 取得Line Bot憑證

1. 前往 [Line Developers Console](https://developers.line.biz/)
2. 建立新的Provider和Channel
3. 選擇 "Messaging API" 頻道類型
4. 取得 Channel Access Token 和 Channel Secret
5. 設定 Webhook URL：`https://your-domain.com/callback`
   **注意：Line Bot要求使用HTTPS，請確保您的網域已安裝SSL憑證**

### 4. 啟動機器人

```bash
python app.py
```

機器人將在 `http://localhost:5000` 啟動，並開始監聽Line Webhook。

## 📱 使用方式

### 基本指令

- **「目標」** - 設定今日3個目標
- **「日記」** - 記錄今日日記
- **「單字」** - 記錄學習的單字
- **「記帳」** - 記錄支出
- **「記帳統計」** - 查看支出統計
- **「匯出記帳」** - 匯出記帳記錄
- **「總結」** - 查看今日總結
- **「幫助」** - 查看所有指令


### 智能對話

機器人支援自然語言對話，您可以：
- 直接輸入文字進行對話
- 機器人會智能判斷您的意圖
- 整合AI提供個性化回應

### 記帳功能

強大的記帳系統，支援：
- 快速記帳：支援多種輸入格式
- 分類管理：預設分類 + 自定義分類
- 統計分析：日/週/月支出統計
- CSV匯出：完整記帳記錄匯出

## ⏰ 自動提醒時間

- **08:00** - 早上目標提醒
- **20:00** - 晚上日記提醒
- **20:30** - 發送每日總結郵件

## 🏗️ 專案結構

```
Never-Give-Up/
├── app.py                 # 主要應用程式
├── config.py             # 配置管理
├── database.py           # 資料庫操作
├── email_service.py      # 郵件服務
├── openai_service.py     # OpenAI AI服務
├── expense_service.py    # 記帳服務
├── scheduler.py          # 定時任務排程器
├── requirements.txt      # Python依賴
├── env_example.txt       # 環境變數範例
├── deploy.sh            # VPS部署腳本
├── ssl_manager.sh       # SSL憑證管理腳本
├── VPS_DEPLOYMENT.md    # VPS部署指南
├── EXPENSE_GUIDE.md     # 記帳功能指南
└── README.md            # 專案說明
```

## 🔧 技術架構

- **後端框架**：Flask
- **Line Bot SDK**：line-bot-sdk
- **資料庫**：SQLite
- **定時任務**：schedule
- **AI服務**：OpenAI GPT-3.5
- **郵件服務**：SMTP

## 📊 資料庫結構

- **users** - 用戶資料
- **daily_goals** - 每日目標
- **diaries** - 日記記錄
- **vocabulary_records** - 單字學習記錄
- **expenses** - 記帳記錄
- **expense_categories** - 記帳分類

## 🚀 部署建議

### 本地開發
```bash
python app.py
```

### VPS部署（推薦）
詳細的VPS部署指南請參考 [VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md)

```bash
# 快速部署（包含SSL憑證自動安裝）
chmod +x deploy.sh
./deploy.sh
```

**部署腳本會自動：**
- 安裝所有必要套件
- 設定Nginx反向代理
- 安裝Let's Encrypt SSL憑證
- 配置防火牆
- 建立管理腳本
- 提供SSL憑證管理工具

### 雲端部署
推薦使用以下平台：
- **Heroku** - 簡單易用
- **Google Cloud Platform** - 穩定可靠
- **AWS** - 功能強大
- **Vercel** - 快速部署

### 本地開發
```bash
# 使用ngrok進行本地測試
ngrok http 5000
```

## 🔒 安全性

- 所有敏感資訊都透過環境變數管理
- Line Webhook簽名驗證
- 資料庫使用參數化查詢防止SQL注入
- 錯誤處理和日誌記錄

## 🤝 貢獻

歡迎提交Issue和Pull Request！

## 📄 授權

MIT License

## 🆘 常見問題

### Q: 如何取得Line Bot憑證？
A: 請參考 [Line Developers 官方文件](https://developers.line.biz/docs/)

### Q: 如何設定Gmail應用程式密碼？
A: 請參考 [Google 安全性設定](https://support.google.com/accounts/answer/185833)

### Q: 機器人沒有回應怎麼辦？
A: 檢查Webhook URL設定和伺服器是否正常運行

### Q: SSL憑證如何安裝？
A: 部署腳本會自動安裝Let's Encrypt憑證，或使用SSL管理工具：
```bash
# 互動式SSL管理
./ssl_manager.sh

# 手動安裝
sudo certbot --nginx -d your-domain.com
```

### Q: 如何修改定時提醒時間？
A: 編輯 `config.py` 中的時間設定

---

💪 **Never Give Up! 讓我們一起成長！**