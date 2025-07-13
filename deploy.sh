#!/bin/bash

# Never-Give-Up Line Bot VPS 部署腳本
# 適用於 Ubuntu/Debian 系統

echo "🚀 開始部署 Never-Give-Up Line Bot..."

# 檢查是否為root用戶
if [ "$EUID" -eq 0 ]; then
    echo "❌ 請不要使用root用戶執行此腳本"
    exit 1
fi

# 更新系統
echo "📦 更新系統套件..."
sudo apt update && sudo apt upgrade -y

# 安裝必要套件
echo "🔧 安裝必要套件..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl

# 建立專案目錄
PROJECT_DIR="/home/$USER/never-give-up"
echo "📁 建立專案目錄: $PROJECT_DIR"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 建立虛擬環境
echo "🐍 建立Python虛擬環境..."
python3 -m venv venv
source venv/bin/activate

# 升級pip
pip install --upgrade pip

# 安裝Python依賴
echo "📚 安裝Python依賴..."
pip install -r requirements.txt

# 建立環境變數檔案
if [ ! -f .env ]; then
    echo "⚙️ 建立環境變數檔案..."
    cp env_example.txt .env
    echo "請編輯 .env 檔案並填入您的設定"
    echo "檔案位置: $PROJECT_DIR/.env"
fi

# 建立supervisor配置
echo "🔧 建立Supervisor配置..."
sudo tee /etc/supervisor/conf.d/never-give-up.conf > /dev/null <<EOF
[program:never-give-up]
command=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/app.py
directory=$PROJECT_DIR
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/log/never-give-up.err.log
stdout_logfile=/var/log/never-give-up.out.log
environment=HOME="$PROJECT_DIR"
EOF

# 建立Nginx配置
echo "🌐 建立Nginx配置..."
sudo tee /etc/nginx/sites-available/never-give-up > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # 請替換為您的網域

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 啟用Nginx站點
sudo ln -sf /etc/nginx/sites-available/never-give-up /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 重啟supervisor
echo "🔄 重啟Supervisor..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start never-give-up

# 設定防火牆
echo "🔥 設定防火牆..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# 建立日誌目錄
sudo mkdir -p /var/log/never-give-up
sudo chown $USER:$USER /var/log/never-give-up

# 建立systemd服務（可選）
echo "🔧 建立systemd服務..."
sudo tee /etc/systemd/system/never-give-up.service > /dev/null <<EOF
[Unit]
Description=Never Give Up Line Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 建立管理腳本
echo "📝 建立管理腳本..."
tee $PROJECT_DIR/manage.sh > /dev/null <<EOF
#!/bin/bash

# Never-Give-Up Line Bot 管理腳本

PROJECT_DIR="$PROJECT_DIR"

case "\$1" in
    start)
        echo "🚀 啟動機器人..."
        sudo supervisorctl start never-give-up
        ;;
    stop)
        echo "⏹️ 停止機器人..."
        sudo supervisorctl stop never-give-up
        ;;
    restart)
        echo "🔄 重啟機器人..."
        sudo supervisorctl restart never-give-up
        ;;
    status)
        echo "📊 機器人狀態..."
        sudo supervisorctl status never-give-up
        ;;
    logs)
        echo "📋 查看日誌..."
        tail -f /var/log/never-give-up.out.log
        ;;
    update)
        echo "📦 更新程式碼..."
        cd \$PROJECT_DIR
        git pull
        source venv/bin/activate
        pip install -r requirements.txt
        sudo supervisorctl restart never-give-up
        ;;
    backup)
        echo "💾 備份資料庫..."
        cp \$PROJECT_DIR/never_give_up.db \$PROJECT_DIR/backup_\$(date +%Y%m%d_%H%M%S).db
        echo "備份完成"
        ;;
    *)
        echo "使用方法: \$0 {start|stop|restart|status|logs|update|backup}"
        exit 1
        ;;
esac
EOF

chmod +x $PROJECT_DIR/manage.sh

echo ""
echo "✅ 部署完成！"
echo ""
echo "📋 後續步驟："
echo "1. 編輯環境變數: nano $PROJECT_DIR/.env"
echo "2. 設定網域: sudo nano /etc/nginx/sites-available/never-give-up"
echo "3. 重啟服務: sudo supervisorctl restart never-give-up"
echo "4. 檢查狀態: $PROJECT_DIR/manage.sh status"
echo ""
echo "🔧 管理指令："
echo "  啟動: $PROJECT_DIR/manage.sh start"
echo "  停止: $PROJECT_DIR/manage.sh stop"
echo "  重啟: $PROJECT_DIR/manage.sh restart"
echo "  狀態: $PROJECT_DIR/manage.sh status"
echo "  日誌: $PROJECT_DIR/manage.sh logs"
echo "  更新: $PROJECT_DIR/manage.sh update"
echo "  備份: $PROJECT_DIR/manage.sh backup"
echo ""
echo "🌐 Webhook URL: http://your-domain.com/callback"
echo "📧 日誌位置: /var/log/never-give-up.out.log"
echo ""
echo "💪 Never Give Up! 部署成功！" 