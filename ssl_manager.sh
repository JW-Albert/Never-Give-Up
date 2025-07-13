#!/bin/bash

# Never-Give-Up Line Bot SSL憑證管理腳本

echo "🔒 Never-Give-Up Line Bot SSL憑證管理工具"
echo "=========================================="

# 檢查是否為root用戶
if [ "$EUID" -eq 0 ]; then
    echo "❌ 請不要使用root用戶執行此腳本"
    exit 1
fi

# 檢查certbot是否已安裝
if ! command -v certbot &> /dev/null; then
    echo "📦 安裝Certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# 主選單
show_menu() {
    echo ""
    echo "請選擇操作："
    echo "1) 安裝新SSL憑證"
    echo "2) 更新現有憑證"
    echo "3) 查看憑證狀態"
    echo "4) 刪除憑證"
    echo "5) 設定自動更新"
    echo "6) 測試憑證"
    echo "7) 查看Nginx SSL配置"
    echo "8) 退出"
    echo ""
    read -p "請輸入選項 (1-8): " choice
}

# 安裝新憑證
install_certificate() {
    echo ""
    echo "🔐 安裝新SSL憑證"
    echo "=================="
    
    read -p "請輸入網域名稱 (例如: bot.yourdomain.com): " domain
    
    if [ -z "$domain" ]; then
        echo "❌ 網域不能為空"
        return
    fi
    
    echo "正在安裝SSL憑證..."
    sudo certbot --nginx -d $domain --non-interactive --agree-tos --email admin@$domain
    
    if [ $? -eq 0 ]; then
        echo "✅ SSL憑證安裝成功！"
        echo "🌐 HTTPS URL: https://$domain/callback"
        echo "📝 請在Line Developers Console中更新Webhook URL"
    else
        echo "❌ SSL憑證安裝失敗"
        echo "請檢查："
        echo "1. 網域DNS設定是否正確"
        echo "2. 網域是否指向此伺服器"
        echo "3. 防火牆是否開放80和443端口"
    fi
}

# 更新憑證
renew_certificates() {
    echo ""
    echo "🔄 更新SSL憑證"
    echo "=============="
    
    echo "正在更新所有憑證..."
    sudo certbot renew
    
    if [ $? -eq 0 ]; then
        echo "✅ 憑證更新成功！"
        sudo systemctl reload nginx
    else
        echo "❌ 憑證更新失敗"
    fi
}

# 查看憑證狀態
check_certificates() {
    echo ""
    echo "📊 SSL憑證狀態"
    echo "=============="
    
    sudo certbot certificates
    
    echo ""
    echo "📋 Nginx SSL配置："
    sudo nginx -t
}

# 刪除憑證
delete_certificate() {
    echo ""
    echo "🗑️ 刪除SSL憑證"
    echo "============="
    
    read -p "請輸入要刪除的網域名稱: " domain
    
    if [ -z "$domain" ]; then
        echo "❌ 網域不能為空"
        return
    fi
    
    echo "⚠️ 確定要刪除 $domain 的SSL憑證嗎？(y/N)"
    read -p "確認: " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        sudo certbot delete --cert-name $domain
        echo "✅ 憑證已刪除"
    else
        echo "❌ 操作已取消"
    fi
}

# 設定自動更新
setup_auto_renew() {
    echo ""
    echo "⏰ 設定自動更新"
    echo "=============="
    
    # 檢查是否已設定
    if crontab -l 2>/dev/null | grep -q "certbot renew"; then
        echo "✅ 自動更新已設定"
        crontab -l | grep "certbot renew"
    else
        echo "正在設定自動更新..."
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
        echo "✅ 自動更新已設定（每天中午12點檢查更新）"
    fi
}

# 測試憑證
test_certificate() {
    echo ""
    echo "🧪 測試SSL憑證"
    echo "============="
    
    read -p "請輸入要測試的網域名稱: " domain
    
    if [ -z "$domain" ]; then
        echo "❌ 網域不能為空"
        return
    fi
    
    echo "正在測試SSL憑證..."
    
    # 測試HTTPS連接
    if curl -s -I "https://$domain" | grep -q "HTTP/2 200\|HTTP/1.1 200"; then
        echo "✅ HTTPS連接正常"
    else
        echo "❌ HTTPS連接失敗"
    fi
    
    # 測試憑證有效性
    if openssl s_client -connect $domain:443 -servername $domain < /dev/null 2>/dev/null | openssl x509 -noout -dates; then
        echo "✅ SSL憑證有效"
    else
        echo "❌ SSL憑證無效"
    fi
}

# 查看Nginx SSL配置
view_nginx_config() {
    echo ""
    echo "📋 Nginx SSL配置"
    echo "==============="
    
    echo "檢查Nginx配置..."
    sudo nginx -t
    
    echo ""
    echo "SSL站點配置："
    sudo grep -r "ssl_certificate" /etc/nginx/sites-enabled/ 2>/dev/null || echo "未找到SSL配置"
    
    echo ""
    echo "監聽端口："
    sudo netstat -tlnp | grep :443
}

# 主程式
main() {
    while true; do
        show_menu
        
        case $choice in
            1)
                install_certificate
                ;;
            2)
                renew_certificates
                ;;
            3)
                check_certificates
                ;;
            4)
                delete_certificate
                ;;
            5)
                setup_auto_renew
                ;;
            6)
                test_certificate
                ;;
            7)
                view_nginx_config
                ;;
            8)
                echo "👋 再見！"
                exit 0
                ;;
            *)
                echo "❌ 無效選項，請重新選擇"
                ;;
        esac
        
        echo ""
        read -p "按Enter鍵繼續..."
    done
}

# 執行主程式
main 