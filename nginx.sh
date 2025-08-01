sudo nano /etc/nginx/sites-available/gynocare.kilush.com 

```
server {
    listen 80;
    listen [::]:80;

    server_name  gynocare.kilush.com www.gynocare.kilush.com;

    root /var/www/html;  # Update the path to your website's root directory
    index index.html index.htm;

    location / {
http://localhost:5173/        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }


    # Additional configurations can be added here, such as SSL/TLS settings or PHP handling
}

```

sudo rm /etc/nginx/sites-enabled/gynocare.kilush.com 

sudo ln -s /etc/nginx/sites-available/gynocare.kilush.com  /etc/nginx/sites-enabled/

sudo certbot --nginx -d gynocare.kilush.com -d www.gynocare.kilush.com

sudo nginx -t

sudo systemctl reload nginx

