"""
JOBAO - Golike Automation Tool
Version: Professional v3.1 (Multi-Account Status chính xác như ảnh)
"""
import os
import sys
import time
import json
from datetime import datetime

try:
    from curl_cffi import requests
except ImportError:
    os.system("pip install curl_cffi")
    from curl_cffi import requests

# ==============================================================================
# CONFIG & WEBHOOK & SETTINGS
# ==============================================================================
FILE_CAU_HINH = 'config.json'

CAU_HINH = {
    "authorization": "",
    "webhook_url": "",
    "webhook_enabled": True,
    "so_luong_job": 1000,
    "delay_giay": 5,
    "dung_sau_loi": 5
}

def tai_cau_hinh():
    global CAU_HINH
    if os.path.exists(FILE_CAU_HINH):
        try:
            with open(FILE_CAU_HINH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in CAU_HINH.items():
                    if k in data:
                        CAU_HINH[k] = data[k]
        except:
            pass
    if not CAU_HINH["authorization"] and os.path.exists('user.txt'):
        try:
            with open('user.txt', 'r') as f:
                first_token = f.readline().strip()
                if first_token:
                    CAU_HINH["authorization"] = first_token
        except: pass

def luu_cau_hinh():
    with open(FILE_CAU_HINH, 'w', encoding='utf-8') as f:
        json.dump(CAU_HINH, f, indent=4, ensure_ascii=False)

tai_cau_hinh()

def gui_webhook(noi_dung):
    if not CAU_HINH["webhook_enabled"] or not