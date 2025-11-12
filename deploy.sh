#!/bin/bash

# Deploy script for Telegram bot

# Ishlash papkasiga o'tish
cd /opt/tgbot/contactus || exit 1

# Git remote URL ni tekshirish (SSH bo'lishi kerak)
git remote -v

# Yangilanishlarni olish
echo "Pulling latest code from GitHub..."
git fetch origin main
git reset --hard origin/main

# Virtual environment (agar ishlatilsa) faollashtirish
# source venv/bin/activate

# Python dependencies yangilash
pip install -r requirements.txt

# PM2 bilan botni restart qilish
if pm2 list | grep -q "contactus-bot"; then
    echo "Restarting existing bot..."
    pm2 restart contactus-bot
else
    echo "Starting bot for the first time..."
    pm2 start "python3 app.py" --name contactus-bot
fi

# PM2 holatini saqlash
pm2 save

echo "Deployment completed."
