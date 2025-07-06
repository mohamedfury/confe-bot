#!/bin/bash

echo "1. تحديث الحزم الأساسية..."
sudo apt update && sudo apt upgrade -y

echo "2. تثبيت بايثون 3 و venv و pip إذا مش موجودين..."
sudo apt install -y python3 python3-venv python3-pip build-essential libssl-dev libffi-dev python3-dev

echo "3. إنشاء البيئة الافتراضية (لو موجودة تحذفها أول)..."
rm -rf venv
python3 -m venv venv

echo "4. تفعيل البيئة الافتراضية وتحديث pip..."
./venv/bin/pip install --upgrade pip

echo "5. تثبيت الحزم المطلوبة..."
./venv/bin/pip install aiogram==2.25.1

echo "6. تشغيل البوت..."
./venv/bin/python main.py