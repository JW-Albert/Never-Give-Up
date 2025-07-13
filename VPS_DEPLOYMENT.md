# 🚀 VPS 部署指南

本指南將幫助您在VPS上部署Never-Give-Up Line Bot。

## 📋 前置需求

- Ubuntu 18.04+ 或 Debian 9+ VPS
- 至少 1GB RAM
- 至少 10GB 硬碟空間
- 網域（可選，但建議）

## 🔧 快速部署

### 1. 連接到VPS

```bash
ssh username@your-vps-ip
```

### 2. 下載專案

```bash
# 克隆專案
git clone https://github.com/your-username/Never-Give-Up.git
cd Never-Give-Up

# 或上傳檔案
# 使用 scp 或 SFTP 上傳專案檔案
```

### 3. 執行部署腳本

```bash
# 給予執行權限
chmod +x deploy.sh

# 執行部署腳本
./deploy.sh
```

## 📝 手動部署步驟

如果您想手動部署，請按照以下步驟：

### 1. 更新系統

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 安裝必要套件

```bash
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl
```

### 3. 建立專案目錄

```bash
mkdir -p ~/never-give-up
cd ~/never-give-up
```

### 4. 上傳專案檔案

將所有專案檔案上傳到此目錄。

### 5. 建立虛擬環境

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. 設定環境變數

```bash
cp env_example.txt .env
nano .env
```

填入您的設定：
```env
LINE_CHANNEL_ACCESS_TOKEN=your_token
LINE_CHANNEL_SECRET=your_secret
OPENAI_API_KEY=your_openai_key
EMAIL_USER=your_email
EMAIL_PASSWORD=your_password
EMAIL_TO=recipient_email
```

### 7. 設定Supervisor

```bash
sudo nano /etc/supervisor/conf.d/never-give-up.conf
```

內容：
```ini
[program:never-give-up]
command=/home/username/never-give-up/venv/bin/python /home/username/never-give-up/app.py
directory=/home/username/never-give-up
user=username
autostart=true
autorestart=true
stderr_logfile=/var/log/never-give-up.err.log
stdout_logfile=/var/log/never-give-up.out.log
environment=HOME="/home/username/never-give-up"
```

### 8. 設定Nginx

```bash
sudo nano /etc/nginx/sites-available/never-give-up
```

內容：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替換為您的網域

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 9. 啟用Nginx站點

```bash
sudo ln -sf /etc/nginx/sites-available/never-give-up /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 10. 啟動服務

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start never-give-up
```

## 🔧 管理指令

部署完成後，您可以使用以下指令管理機器人：

```bash
# 進入專案目錄
cd ~/never-give-up

# 查看狀態
./manage.sh status

# 啟動機器人
./manage.sh start

# 停止機器人
./manage.sh stop

# 重啟機器人
./manage.sh restart

# 查看日誌
./manage.sh logs

# 更新程式碼
./manage.sh update

# 備份資料庫
./manage.sh backup

# SSL憑證管理
./manage.sh ssl

# 更新SSL憑證
./manage.sh ssl-renew

# 完整SSL管理工具
./ssl_manager.sh
```

## 🌐 網域設定

### 1. DNS設定

在您的DNS提供商處設定A記錄：
```
A    your-domain.com    your-vps-ip
```

### 2. SSL憑證管理

部署腳本會自動安裝SSL管理工具：

```bash
# 使用互動式SSL管理工具
./ssl_manager.sh
```

SSL管理工具功能：
- 安裝新SSL憑證
- 更新現有憑證
- 查看憑證狀態
- 刪除憑證
- 設定自動更新
- 測試憑證
- 查看Nginx SSL配置

### 3. SSL憑證（必需）

Line Bot要求使用HTTPS，請安裝Let's Encrypt免費SSL：

```bash
# 安裝Certbot
sudo apt install certbot python3-certbot-nginx

# 安裝SSL憑證
sudo certbot --nginx -d your-domain.com

# 設定自動更新
sudo crontab -e
# 加入以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. 更新Nginx配置

```bash
sudo nano /etc/nginx/sites-available/never-give-up
```

加入SSL配置：
```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔒 安全性設定

### 1. 防火牆設定

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
```

### 2. 定期更新

```bash
# 建立自動更新腳本
sudo crontab -e
```

加入：
```
0 2 * * 0 /usr/bin/apt update && /usr/bin/apt upgrade -y
```

### 3. 備份設定

```bash
# 建立備份腳本
nano ~/backup.sh
```

內容：
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp ~/never-give-up/never_give_up.db ~/backup_$DATE.db
# 可以加入上傳到雲端儲存的指令
```

## 📊 監控和維護

### 1. 查看日誌

```bash
# 應用程式日誌
tail -f /var/log/never-give-up.out.log

# 錯誤日誌
tail -f /var/log/never-give-up.err.log

# Nginx日誌
sudo tail -f /var/log/nginx/access.log
```

### 2. 系統監控

```bash
# 查看系統資源
htop

# 查看磁碟使用
df -h

# 查看記憶體使用
free -h
```

### 3. 效能優化

```bash
# 調整Nginx設定
sudo nano /etc/nginx/nginx.conf

# 調整Supervisor設定
sudo nano /etc/supervisor/conf.d/never-give-up.conf
```

## 🚨 故障排除

### 常見問題

1. **機器人沒有回應**
   ```bash
   # 檢查服務狀態
   ./manage.sh status
   
   # 查看日誌
   ./manage.sh logs
   ```

2. **Nginx錯誤**
   ```bash
   # 檢查Nginx配置
   sudo nginx -t
   
   # 重啟Nginx
   sudo systemctl restart nginx
   ```

3. **資料庫錯誤**
   ```bash
   # 檢查資料庫檔案
   ls -la ~/never-give-up/never_give_up.db
   
   # 備份並重新建立
   ./manage.sh backup
   ```

4. **SSL憑證問題**
   ```bash
   # 檢查憑證狀態
   sudo certbot certificates
   
   # 重新安裝憑證
   ./manage.sh ssl
   
   # 手動更新憑證
   sudo certbot renew
   ```

5. **記憶體不足**
   ```bash
   # 查看記憶體使用
   free -h
   
   # 重啟服務
   ./manage.sh restart
   ```

### 日誌分析

```bash
# 查看最近的錯誤
grep ERROR /var/log/never-give-up.err.log

# 查看訪問記錄
tail -100 /var/log/nginx/access.log
```

## 📈 擴展建議

### 1. 資料庫升級

考慮使用PostgreSQL或MySQL：
```bash
sudo apt install postgresql postgresql-contrib
```

### 2. 快取系統

安裝Redis：
```bash
sudo apt install redis-server
```

### 3. 監控工具

安裝監控工具：
```bash
sudo apt install htop iotop nethogs
```

## 📞 支援

如果遇到問題：

1. 檢查日誌檔案
2. 確認網路連接
3. 驗證環境變數設定
4. 檢查防火牆設定
5. 聯繫技術支援

---

💪 **祝您部署順利！Never Give Up!** 