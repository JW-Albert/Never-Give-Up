# 安裝SSL憑證
echo "🔒 安裝SSL憑證..."
echo "請輸入您的網域名稱 (例如: bot.yourdomain.com):"
read -p "網域: " DOMAIN_NAME

if [ ! -z "$DOMAIN_NAME" ]; then
    # 更新Nginx配置中的網域
    sudo sed -i "s/your-domain.com/$DOMAIN_NAME/g" /etc/nginx/sites-available/never-give-up
    sudo nginx -t && sudo systemctl reload nginx
    
    # 使用Certbot安裝SSL憑證
    echo "🔐 正在安裝Let's Encrypt SSL憑證..."
    sudo certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME
    
    if [ $? -eq 0 ]; then
        echo "✅ SSL憑證安裝成功！"
        echo "🌐 HTTPS URL: https://$DOMAIN_NAME/callback"
    else
        echo "⚠️ SSL憑證安裝失敗，請檢查網域設定"
        echo "您可以稍後手動執行: sudo certbot --nginx -d $DOMAIN_NAME"
    fi
else
    echo "⚠️ 未輸入網域，跳過SSL憑證安裝"
    echo "您可以稍後手動安裝SSL憑證"
fi