import urllib3
urllib3.disable_warnings()
import pycountry
import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from time import sleep
import random
import telebot
import hashlib
import string
from faker import Faker
from urllib.parse import urljoin, urlparse, urldefrag
from telebot import types
from io import BytesIO
import re
import sys
import pytz
import subprocess
import yt_dlp
import socket
import threading
import aiohttp
import asyncio
import io
import schedule
import json
import html
from telebot import telebot
import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

fake = Faker()

init(autoreset=True)

__AUTHOR__ = 'Nguyễn Văn Phúc'
__CONTACT__ = 'https://www.facebook.com/100037043542788'
__TOOL_NAME__ = 'Bot Tiện Ích'
THỜI_GIAN_CHỜ = timedelta(seconds=300)
GIỚI_HẠN_CHIA_SẺ = 1000
ALLOWED_GROUP_IDS = [-1002420490082]
TEMP_ADMIN_FILE = 'temp_admins.json'
TOKEN = '7424812505:AAFFsKhKVVLDulR7PFFVumOcL27OzIFmWTA'
TDS_token = 'TDSQfiQjclZXZzJiOiIXZ2V2ciwiIhRXZNJXZrNWayRVdllGSiojIyV2c1Jye'
bot = telebot.TeleBot(TOKEN)

user_cooldowns = {}
core_admins = {5076641486}
share_count = {}
bot_active = True
user_keys = {}
admins = set(core_admins)
COOLDOWN_PERIOD = timedelta(minutes=60)
user_last_time = {}
USERNAME = 'HieuTrickerMeta'
PASSWORD = 'Hieu12345'
TEMP_ADMINS_FILE = 'temp_admins.json'
temp_admins = []
last_checked_day = datetime.now().day  # Lưu ngày hiện tại khi khởi động bot

# Định nghĩa hàm kiểm tra admin chính thức
def is_admin(user_id):
    return user_id in core_admins

# Lưu admin tạm thời vào file
def save_temp_admins():
    with open(TEMP_ADMINS_FILE, 'w') as f:
        json.dump(temp_admins, f, indent=4)

# Tải admin tạm thời từ file
def load_temp_admins():
    if os.path.exists(TEMP_ADMINS_FILE):
        with open(TEMP_ADMINS_FILE, 'r') as f:
            global temp_admins
            temp_admins = json.load(f)

# Kiểm tra xem user có phải là admin tạm thời không (kiểm tra cả thư mục user và thêm file ID nếu còn hạn)
def is_temp_admin(user_id):
    current_time = datetime.now()
    today_day = current_time.day  # Lấy ngày hiện tại
    user_file_path = f"./user/{today_day}/{user_id}.txt"  # Đường dẫn tới file user của ngày hiện tại

    # Kiểm tra trong danh sách admin tạm thời
    for admin in temp_admins:
        if admin.get('user_id') == user_id:
            expiry_time = datetime.strptime(admin['expiry_time'], '%Y-%m-%d %H:%M:%S')
            if current_time < expiry_time:
                # Nếu admin còn hạn, tạo file ID trong thư mục user để sử dụng dịch vụ
                create_user_file(user_id, admin['full_name'], expiry_time, today_day)
                return True
            else:
                # Nếu hết hạn, xóa file trong thư mục user
                if os.path.exists(user_file_path):
                    os.remove(user_file_path)
                return False
    # Nếu không còn admin tạm thời, xóa file trong thư mục user nếu còn
    if os.path.exists(user_file_path):
        os.remove(user_file_path)
    return False

# Tạo file ID trong thư mục user
def create_user_file(user_id, full_name, expiry_time, today_day):
    user_folder_path = f"./user/{today_day}"
    if not os.path.exists(user_folder_path):
        os.makedirs(user_folder_path)  # Tạo thư mục nếu chưa tồn tại

    user_file_path = f"{user_folder_path}/{user_id}.txt"
    with open(user_file_path, 'w') as user_file:
        user_file.write(f"User ID: {user_id}\nFull Name: {full_name}\nExpiry: {expiry_time}\n")

# Hàm tự động kiểm tra admin tạm thời xem có hết hạn không mỗi 1 giờ
def check_admins_expiry():
    global last_checked_day
    while True:
        current_time = datetime.now()
        today_day = current_time.day  # Lấy ngày hiện tại

        if today_day != last_checked_day:  # Kiểm tra nếu đã sang ngày mới
            # Cập nhật thư mục user cho ngày mới với các admin tạm thời còn hạn
            for admin in temp_admins:
                expiry_time = datetime.strptime(admin['expiry_time'], '%Y-%m-%d %H:%M:%S')
                if current_time < expiry_time:
                    create_user_file(admin['user_id'], admin['full_name'], expiry_time, today_day)
            last_checked_day = today_day  # Cập nhật ngày kiểm tra cuối cùng

        expired_admins = []  # Danh sách admin hết hạn

        for admin in temp_admins:
            expiry_time = datetime.strptime(admin['expiry_time'], '%Y-%m-%d %H:%M:%S')
            user_id = admin['user_id']
            full_name = admin.get('full_name', 'Unknown')
            
            if current_time >= expiry_time:
                expired_admins.append(admin)
                user_file_path = f"./user/{today_day}/{user_id}.txt"
                if os.path.exists(user_file_path):
                    os.remove(user_file_path)
                    print(f"File {user_file_path} đã được xóa.")

                for group_id in ALLOWED_GROUP_IDS:
                    bot.send_message(
                        group_id, 
                        f"<blockquote>Người dùng {full_name} với ID [{user_id}] đã hết hạn sử dụng VIP.</blockquote>",
                        parse_mode='HTML'
                    )
        
        for admin in expired_admins:
            temp_admins.remove(admin)

        if expired_admins:
            save_temp_admins()

        sleep(900)  # Chờ 1 giờ trước khi kiểm tra lại
# Lệnh /adduser để thêm admin tạm thời và tạo file ID trong thư mục user
@bot.message_handler(commands=['adduser'])
def add_user(message):
    user_id = message.from_user.id
    if is_admin(user_id):  # Chỉ admin chính thức mới được thêm user
        try:
            params = message.text.split()
            user_to_add = int(params[1])  # ID người dùng cần thêm
            duration = params[2]  # Thời gian admin tạm thời, ví dụ: 1day
            full_name = bot.get_chat(user_to_add).first_name  # Lấy tên đầy đủ của người dùng
            
            if "day" in duration:
                days = int(duration.replace("day", ""))
                expiration_time = datetime.now() + timedelta(days=days)
                
                # Tạo thư mục user theo ngày hiện tại
                current_time = datetime.now()
                today_day = current_time.day
                user_folder_path = f"./user/{today_day}"
                if not os.path.exists(user_folder_path):
                    os.makedirs(user_folder_path)  # Tạo thư mục nếu chưa tồn tại

                # Tạo file user với ID trong thư mục
                user_file_path = f"{user_folder_path}/{user_to_add}.txt"
                with open(user_file_path, 'w') as user_file:
                    user_file.write(f"User ID: {user_to_add}\nFull Name: {full_name}\nExpiry: {expiration_time}\n")

                # Thêm admin tạm thời vào danh sách
                temp_admins.append({
                    "user_id": user_to_add,
                    "expiry_time": expiration_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "full_name": full_name
                })
                
                save_temp_admins()  # Lưu danh sách admin tạm thời vào file
                bot.reply_to(message, f"<blockquote>Đã thêm {full_name} (ID: {user_to_add}) vào danh sách VIP đến ngày {expiration_time}.</blockquote>", parse_mode="HTML")
            else:
                bot.reply_to(message, "Vui lòng nhập thời gian đúng định dạng (ví dụ: 1day).")
        except (IndexError, ValueError):
            bot.reply_to(message, "Vui lòng nhập đúng định dạng /adduser <user_id> <số ngày>.")
    else:
        bot.reply_to(message, "Bạn không có quyền sử dụng lệnh này.")
@bot.message_handler(commands=['listvip'])
def list_vip_admins(message):
    user_id = message.from_user.id
    if is_admin(user_id):  # Chỉ admin chính thức mới được sử dụng lệnh này
        if temp_admins:
            vip_list = "<b>Danh sách người dùng VIP:</b>\n<blockquote>"
            current_time = datetime.now()
            for admin in temp_admins:
                expiry_time = datetime.strptime(admin['expiry_time'], '%Y-%m-%d %H:%M:%S')
                remaining_time = expiry_time - current_time
                full_name = admin.get('full_name', 'Unknown')  # Lấy tên người dùng, nếu không có để Unknown
                vip_list += f"- {full_name} (ID: {admin['user_id']}): Hết hạn vào {expiry_time} ({remaining_time.days} ngày còn lại)\n"
            vip_list += "</blockquote>"
        else:
            vip_list = "<b>Không có người dùng nào trong danh sách.</b>"
        
        bot.reply_to(message, vip_list, parse_mode='HTML')
    else:
        bot.reply_to(message, "Bạn không có quyền sử dụng lệnh này.", parse_mode='HTML')

# Tải admin tạm thời từ file khi khởi động bot
load_temp_admins()

# Cập nhật tất cả admin còn hạn ngay khi khởi động bot
for admin in temp_admins:
    expiry_time = datetime.strptime(admin['expiry_time'], '%Y-%m-%d %H:%M:%S')
    if datetime.now() < expiry_time:
        create_user_file(admin['user_id'], admin['full_name'], expiry_time, datetime.now().day)

# Tạo một thread để chạy hàm kiểm tra admin hết hạn định kỳ
admin_check_thread = threading.Thread(target=check_admins_expiry)
admin_check_thread.daemon = True  # Đặt daemon để thread chạy nền
admin_check_thread.start()

def login_tds(username, password):
    login_url = 'https://traodoisub.com/scr/login.php'
    data = {
        'username': username,
        'password': password,
        'submit': 'Đăng nhập'
    }

    session = requests.Session()
    response = session.post(login_url, data=data)

    if 'PHPSESSID' in session.cookies:
        return session.cookies['PHPSESSID']
    else:
        return None

def buy_hearts_tiktok(phpsessid, video_url, amount):
    buy_url = 'https://traodoisub.com/mua/tiktok_like/themid.php'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cookies = {
        'PHPSESSID': phpsessid,
    }

    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://traodoisub.com',
        'referer': 'https://traodoisub.com/mua/tiktok_like/',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'maghinho': '',
        'id': video_url,
        'sl': amount,
        'dateTime': current_time,
    }

    response = requests.post(buy_url, cookies=cookies, headers=headers, data=data)
    return response.status_code, response.text

def TimeStamp():
    now = str(datetime.now().date())
    return now
def is_allowed_group(message):
    return message.chat.id in ALLOWED_GROUP_IDS

@bot.message_handler(commands=['muakey'])
def startkey(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm\nhttps://t.me/botvphc ")
        return

    user_id = message.from_user.id
    current_time = datetime.now()
    today_day = current_time.day
    key = "VPHC-" + str(user_id * today_day - 2007)

    # Thông báo cho người dùng rằng key đang được xử lý
    bot.reply_to(message, "Mua key liên hệ @abcdxyz310107\nSau khi có key dùng lệnh /key {key} để kích hoạt")

    # Gửi key trực tiếp cho admin
    for admin_id in core_admins:
        admin_message = f"User: {message.from_user.username}, ID: {user_id}, Key: {key}"
        bot.send_message(admin_id, admin_message)
@bot.message_handler(commands=['key'])
def key(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm\nhttps://t.me/botvphc")
        return

    if len(message.text.split()) != 2:
        bot.reply_to(message, 'VUI LÒNG NHẬP KEY Ví Dụ /key VPHC-124322973736')
        return

    user_id = message.from_user.id
    key = message.text.split()[1]
    current_time = datetime.now()
    today_day = current_time.day
    expected_key = "VPHC-" + str(user_id * today_day - 2007)

    if key == expected_key:
        text_message = f'<blockquote>KEY ĐÚNG🔓\nThank bạn đã ủng hộ tôi💗</blockquote>'
        bot.reply_to(message, text_message, parse_mode='HTML')
        user_path = f'./user/{today_day}'
        os.makedirs(user_path, exist_ok=True)
        with open(f'{user_path}/{user_id}.txt', "w") as fi:
            fi.write("")
    else:
        bot.reply_to(message, 'KEY KHÔNG HỢP LỆ.')

@bot.message_handler(commands=['tim'])
def handle_tim(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm\nhttps://t.me/botvphc")
        return

    user_id = message.from_user.id
    current_time = datetime.now()

    if is_admin(user_id):
        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            os.makedirs(f"./user/{today_day}", exist_ok=True)
            with open(today_path, "w") as fi:
                fi.write("")

    else:
        last_tim_time = user_last_time.get(user_id)
        if last_tim_time and current_time - last_tim_time < COOLDOWN_PERIOD:
            remaining_time = COOLDOWN_PERIOD - (current_time - last_tim_time)
            bot.reply_to(message, f"Vui lòng đợi {remaining_time.seconds // 60} phút trước khi sử dụng lại lệnh /tim.")
            return
            
        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            bot.reply_to(message, 'hãy /muakey trước khi sử dụng lệnh /tim !')
            return

    try:
        params = message.text.split()
        if len(params) < 2:
            bot.reply_to(message, "Vui lòng nhập URL video TikTok theo định dạng: /tim <video_url>")
            return

        video_url = params[1]
        amount = '50'

        phpsessid = login_tds(USERNAME, PASSWORD)
        
        if not phpsessid:
            bot.reply_to(message, "Đăng nhập thất bại")
            return

        status_code, response_text = buy_hearts_tiktok(phpsessid, video_url, amount)
        
        if status_code == 200:
            username = message.from_user.username
            a = requests.get(f'https://www.tikwm.com/api?url={video_url}').json()
            b = a['data']
            c = b['digg_count']
            d = b['play']
            
            success_message = f"<blockquote>đơn<a href='{d}'>‎</a> đã được gửi đi\n\n👥 id người dùng: {user_id}\n👥 username: @{username}\n🛒 Đơn Mua: {amount} TIM\n❤️ số tim hiện tại: {c}\n❤️ tim tăng: {c + 50}</blockquote>\n\n<blockquote>CRE: @abcdxyz310107</blockquote>"
            bot.reply_to(message, success_message, parse_mode='HTML')
            
            user_last_time[user_id] = current_time
            
        else:
            bot.reply_to(message, f"Mua tim thất bại")

    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")

# Hàm mua like Facebook
def buy_likes_facebook(phpsessid, post_id, amount):
    buy_url = 'https://traodoisub.com/mua/like/themid.php'  # Đường dẫn mua like Facebook
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cookies = {
        'PHPSESSID': phpsessid,
    }

    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://traodoisub.com',
        'referer': 'https://traodoisub.com/mua/like/',  # Referer đúng
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'maghinho': '',
        'id': post_id,
        'sl': amount,
        'dateTime': current_time,
    }

    response = requests.post(buy_url, cookies=cookies, headers=headers, data=data)
    return response.status_code, response.text

@bot.message_handler(commands=['likefb'])
def handle_like(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm\nhttps://t.me/botvphc")
        return

    user_id = message.from_user.id
    current_time = datetime.now()

    # Kiểm tra nếu người dùng là admin thì không cần vượt link
    if is_admin(user_id):
        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            os.makedirs(f"./user/{today_day}", exist_ok=True)
            with open(today_path, "w") as fi:
                fi.write("")
    else:
        # Kiểm tra thời gian cooldown cho user không phải admin
        last_like_time = user_last_time.get(user_id)
        if last_like_time and current_time - last_like_time < COOLDOWN_PERIOD:
            remaining_time = COOLDOWN_PERIOD - (current_time - last_like_time)
            bot.reply_to(message, f"Vui lòng đợi {remaining_time.seconds // 60} phút trước khi sử dụng lại lệnh /likefb.")
            return

        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            bot.reply_to(message, 'Bạn chưa nhập key. Hãy sử dụng lệnh /muakey trước khi dùng lệnh /likefb.')
            return

    params = message.text.split()
    if len(params) < 2:
        bot.reply_to(message, "Vui lòng nhập theo định dạng: /likefb {id bài viết}\nVí dụ /likefb 1146849999893107")
        return

    post_id = params[1]
    amount = 20  # Đặt amount mặc định là 20

    phpsessid = login_tds(USERNAME, PASSWORD)

    if not phpsessid:
        bot.reply_to(message, "Đăng nhập thất bại")
        return

    status_code, response_text = buy_likes_facebook(phpsessid, post_id, amount)

    if status_code == 200:
        # Thông báo thành công với format đẹp mắt
        response_message = (
            f"✨ **Tăng Like Thành Công** ✨\n"
            f"╭━━━━━━━━━━━━━━━╮\n"
            f"┣ 🆔 **Post ID**: {post_id}\n"
            f"┣ 💬 **Số lượng like**: {amount}\n"
            f"┣ 🚀 **Status**: Like đã được tăng!\n"
            f"╰━━━━━━━━━━━━━━━╯\n"
            f"🎉 Cảm ơn bạn đã sử dụng dịch vụ."
        )
        bot.reply_to(message, response_message, parse_mode='Markdown')

        # Cập nhật thời gian sử dụng lệnh /like
        user_last_time[user_id] = current_time
    else:
        bot.reply_to(message, "Mua like thất bại.")

# Hàm gọi API để lấy số xu
def get_sodu():
    url = f'https://traodoisub.com/api/?fields=profile&access_token={TDS_token}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('success') == 200:
            xu = data['data']['xu']
            # Sử dụng thẻ blockquote trong thông báo
            return f"<blockquote>Số dư: {xu}\n\nTim TikTok -30.000 (50tim)\nLike Facebook -7.400 (20like)\nFollow TikTok Tây -50.000(100follow)\nFollow TikTok Việt -140.000(100follow)\nFollow Facebook -69.000(30follow)\nLike Instagram -35.000(50like)\nFollow Instagram -60.000(50follow)\nCảm Xúc Facebook -39.000(30like)</blockquote>"
        else:
            return "<blockquote>Không lấy được số dư</blockquote>"
    else:
        return "<blockquote>Lỗi khi lấy số dư</blockquote>"

# Xử lý lệnh /sodu
@bot.message_handler(commands=['sodu'])
def handle_sodu(message):
    result = get_sodu()
    bot.reply_to(message, result, parse_mode='HTML')  # Sử dụng chế độ HTML 
    
# follow tiktok
def buy_follow_tiktok(phpsessid, tiktok_url, amount):
    buy_url = 'https://traodoisub.com/mua/tiktok_follow3/themid.php'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cookies = {
        'PHPSESSID': phpsessid,
    }

    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://traodoisub.com',
        'referer': 'https://traodoisub.com/mua/tiktok_follow3/',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'maghinho': '',
        'id': tiktok_url,
        'sl': amount,
        'dateTime': current_time,
    }

    response = requests.post(buy_url, cookies=cookies, headers=headers, data=data)
    return response.status_code, response.text  

@bot.message_handler(commands=['fl'])
def handle_fl(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm\nhttps://t.me/botvphc")
        return

    user_id = message.from_user.id
    current_time = datetime.now()

    if is_admin(user_id):
        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            os.makedirs(f"./user/{today_day}", exist_ok=True)
            with open(today_path, "w") as fi:
                fi.write("")
    else:
        last_fl_time = user_last_time.get(user_id)
        if last_fl_time and current_time - last_fl_time < COOLDOWN_PERIOD:
            remaining_time = COOLDOWN_PERIOD - (current_time - last_fl_time)
            bot.reply_to(message, f"Vui lòng đợi {remaining_time.seconds // 60} phút trước khi sử dụng lại lệnh /fl.")
            return

        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            bot.reply_to(message, 'Hãy /muakey trước khi sử dụng lệnh /fl!')
            return

    try:
        params = message.text.split()
        if len(params) < 2:
            bot.reply_to(message, "💬 Vui lòng nhập theo định dạng: /fl https://www.tiktok.com/@{username}\n\n⚠️ Lưu ý phải nhập link theo định dạng này mới buff được nha\nhttps://www.tiktok.com/@")
            return

        tiktok_profile_url = params[1]
        username = tiktok_profile_url.split('@')[-1]  # Chỉ lấy phần username sau dấu '@'

        # Lấy số lượng followers từ API
        follower_count = get_tiktok_followers(username)
        if follower_count is None:
            bot.reply_to(message, "Không thể lấy thông tin số lượng followers.")
            return

        amount = 100  # Số lượng follow mà bạn muốn mua

        # Mua follow TikTok
        phpsessid = login_tds(USERNAME, PASSWORD)
        if not phpsessid:
            bot.reply_to(message, "Đăng nhập thất bại")
            return

        status_code, response_text = buy_follow_tiktok(phpsessid, tiktok_profile_url, str(amount))

        # Thông báo kết quả sau khi thực hiện lệnh
        if status_code == 200:
            bot.reply_to(message, f"""<blockquote>Đang tiến hành tăng follow TikTok
╭───────────────╮
│🎵 TikTok: {tiktok_profile_url}
│📊 Số Follow Ban Đầu: {follower_count}
│📈 Số Follow Đang Tăng: {amount} Tây
│💬 Follow sẽ lên sau 30-60p chứ không phải buff cái là lên luôn
╰───────────────╯
</blockquote>""", parse_mode='HTML')

            user_last_time[user_id] = current_time
        else:
            bot.reply_to(message, "Mua follow TikTok thất bại")

    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")
        
#fl tik việt
def buy_follow_tiktok(phpsessid, tiktok_profile_url, amount):
    buy_url = 'https://traodoisub.com/mua/tiktok_follow/themid.php'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cookies = {
        'PHPSESSID': phpsessid,
    }

    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://traodoisub.com',
        'referer': 'https://traodoisub.com/mua/tiktok_follow/',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'maghinho': '',
        'id': tiktok_profile_url,
        'sl': amount,
        'dateTime': current_time,
    }

    response = requests.post(buy_url, cookies=cookies, headers=headers, data=data)
    return response.status_code, response.text

#Follow Tik Việt
def get_tiktok_followers(username):
    url = f'https://api.insightigapp.com/v1/task/analytics?username={username}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 0 and data['data']:
            return data['data']['followers']
    return None

@bot.message_handler(commands=['fl2'])
def handle_fl2(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm\nhttps://t.me/botvphc")
        return

    user_id = message.from_user.id
    current_time = datetime.now()

    if is_admin(user_id):
        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            os.makedirs(f"./user/{today_day}", exist_ok=True)
            with open(today_path, "w") as fi:
                fi.write("")
    else:
        last_fl2_time = user_last_time.get(user_id)
        if last_fl2_time and current_time - last_fl2_time < COOLDOWN_PERIOD:
            remaining_time = COOLDOWN_PERIOD - (current_time - last_fl2_time)
            bot.reply_to(message, f"Vui lòng đợi {remaining_time.seconds // 60} phút trước khi sử dụng lại lệnh /fl2.")
            return

        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            bot.reply_to(message, 'hãy /muakey trước khi sử dụng lệnh /fl2!')
            return

    try:
        params = message.text.split()
        if len(params) < 2:
            bot.reply_to(message, "💬Vui lòng nhập theo định dạng: /fl2 https://www.tiktok.com/@{username}\n\n⚠️Lưu ý phải nhập link theo định dạng này mới buff được nha\nhttps://www.tiktok.com/@")
            return

        tiktok_profile_url = params[1]
        username = tiktok_profile_url.split('@')[-1]  # Chỉ lấy phần username sau dấu '@'

        # Lấy số lượng followers từ API
        follower_count = get_tiktok_followers(username)
        if follower_count is None:
            bot.reply_to(message, "Không thể lấy thông tin số lượng followers.")
            return

        amount = 100  # Số lượng follow mà bạn muốn mua

        # Mua follow TikTok
        phpsessid = login_tds(USERNAME, PASSWORD)
        if not phpsessid:
            bot.reply_to(message, "Đăng nhập thất bại")
            return

        status_code, response_text = buy_follow_tiktok(phpsessid, tiktok_profile_url, str(amount))

        # Thông báo kết quả sau khi thực hiện lệnh
        if status_code == 200:
            bot.reply_to(message, f"""<blockquote>Đang tiến hành tăng follow TikTok
╭───────────────╮
│🎵 TikTok: {tiktok_profile_url}
│📊 Số Follow Ban Đầu: {follower_count}
│📈 Số Follow Đang Tăng: {amount} Việt
│💬 Follow sẽ lên sau 30-60p chứ không phải buff cái là lên luôn
╰───────────────╯
</blockquote>""", parse_mode='HTML')

            user_last_time[user_id] = current_time
        else:
            bot.reply_to(message, "Mua follow TikTok thất bại")

    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")
#follow fb
def buy_follow_facebook(phpsessid, user_id, amount):
    buy_url = 'https://traodoisub.com/mua/facebook_follow/themid.php'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cookies = {
        'PHPSESSID': phpsessid,
    }

    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://traodoisub.com',
        'referer': 'https://traodoisub.com/mua/facebook_follow/',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'maghinho': '',
        'id': user_id,
        'sl': amount,
        'dateTime': current_time,
    }

    response = requests.post(buy_url, cookies=cookies, headers=headers, data=data)
    return response.status_code

@bot.message_handler(commands=['sub'])
def handle_sub(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm\nhttps://t.me/botvphc")
        return

    user_id = message.from_user.id
    current_time = datetime.now()

    if is_admin(user_id):
        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            os.makedirs(f"./user/{today_day}", exist_ok=True)
            with open(today_path, "w") as fi:
                fi.write("")
    else:
        last_sub_time = user_last_time.get(user_id)
        if last_sub_time and current_time - last_sub_time < COOLDOWN_PERIOD:
            remaining_time = COOLDOWN_PERIOD - (current_time - last_sub_time)
            bot.reply_to(message, f"Vui lòng đợi {remaining_time.seconds // 60} phút trước khi sử dụng lại lệnh /sub.")
            return

        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            bot.reply_to(message, 'Hãy /muakey trước khi sử dụng lệnh /sub!')
            return

    try:
        params = message.text.split()
        if len(params) < 2:
            bot.reply_to(message, "Vui lòng nhập theo định dạng: /sub <id fb>")
            return

        facebook_id = params[1]
        amount = '30'

        # Thông báo duy nhất
        bot.reply_to(message, f"""<blockquote>Đang tiến hành buff follow
╭───────────────╮
│👤 UID: {facebook_id}
│📈 Số lượng: {amount} follow
│⏳ Đang tiến hàng tăng follow, vui lòng chờ đợi...
╰───────────────╯
</blockquote>""", parse_mode='HTML')

        # Mua follow
        phpsessid = login_tds(USERNAME, PASSWORD)
        if not phpsessid:
            bot.reply_to(message, "Đăng nhập thất bại")
            return

        status_code = buy_follow_facebook(phpsessid, facebook_id, amount)
        if status_code == 200:
            user_last_time[user_id] = current_time
        else:
            bot.reply_to(message, "Mua follow thất bại")

    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")
#Like ig
def buy_like_instagram(phpsessid, ig_post_url, amount):
    buy_url = 'https://traodoisub.com/mua/instagram_like/themid.php'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cookies = {
        'PHPSESSID': phpsessid,
    }

    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://traodoisub.com',
        'referer': 'https://traodoisub.com/mua/instagram_like/',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'maghinho': '',
        'id': ig_post_url,
        'sl': amount,
        'dateTime': current_time,
    }

    response = requests.post(buy_url, cookies=cookies, headers=headers, data=data)
    return response.status_code, response.text

@bot.message_handler(commands=['likeig'])
def handle_likeig(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm\nhttps://t.me/botvphc")
        return

    user_id = message.from_user.id
    current_time = datetime.now()

    if is_admin(user_id):
        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            os.makedirs(f"./user/{today_day}", exist_ok=True)
            with open(today_path, "w") as fi:
                fi.write("")
    else:
        last_likeig_time = user_last_time.get(user_id)
        if last_likeig_time and current_time - last_likeig_time < COOLDOWN_PERIOD:
            remaining_time = COOLDOWN_PERIOD - (current_time - last_likeig_time)
            bot.reply_to(message, f"Vui lòng đợi {remaining_time.seconds // 60} phút trước khi sử dụng lại lệnh /likeig.")
            return

        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            bot.reply_to(message, 'hãy /muakey trước khi sử dụng lệnh /likeig!')
            return

    try:
        params = message.text.split()
        if len(params) < 2:
            bot.reply_to(message, "Vui lòng nhập URL bài đăng Instagram theo định dạng /likeig <url>\n\n Mua bằng link có định dạng như này\nhttps://www.instagram.com/p/DCJ5XrZSJ-h/.")
            return

        ig_post_url = params[1]
        amount = '50'

        bot.reply_to(message, f"""<blockquote>Đang tiến hành tăng like Instagram
╭───────────────╮
│📷 Bài đăng: {ig_post_url}
│❤️ Số like đang tăng {amount}
│⏳ Đang tiến hành, vui lòng đợi...
╰───────────────╯
</blockquote>""", parse_mode='HTML')

        # Mua like Instagram
        phpsessid = login_tds(USERNAME, PASSWORD)
        if not phpsessid:
            bot.reply_to(message, "Đăng nhập thất bại")
            return

        status_code, response_text = buy_like_instagram(phpsessid, ig_post_url, amount)

        if status_code != 200:
            bot.reply_to(message, "Mua like Instagram thất bại")

        user_last_time[user_id] = current_time

    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")  
#follow ig
def buy_follow_instagram(phpsessid, instagram_profile_url, amount):
    buy_url = 'https://traodoisub.com/mua/instagram_follow/themid.php'
    current_time = datetime.now().strftime('%Y-%m-%d+%H:%M:%S')

    cookies = {
        'PHPSESSID': phpsessid,
    }

    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://traodoisub.com',
        'referer': 'https://traodoisub.com/mua/instagram_follow/',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'maghinho': '',
        'id': instagram_profile_url,
        'sl': amount,
        'dateTime': current_time,
    }

    response = requests.post(buy_url, cookies=cookies, headers=headers, data=data)
    return response.status_code, response.text

@bot.message_handler(commands=['flig'])
def handle_flig(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm được phép.")
        return

    user_id = message.from_user.id
    current_time = datetime.now()

    if is_admin(user_id):
        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            os.makedirs(f"./user/{today_day}", exist_ok=True)
            with open(today_path, "w") as fi:
                fi.write("")
    else:
        last_flig_time = user_last_time.get(user_id)
        if last_flig_time and current_time - last_flig_time < COOLDOWN_PERIOD:
            remaining_time = COOLDOWN_PERIOD - (current_time - last_flig_time)
            bot.reply_to(message, f"Vui lòng đợi {remaining_time.seconds // 60} phút trước khi sử dụng lại lệnh /flig.")
            return

        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            bot.reply_to(message, 'Hãy sử dụng lệnh /getkey trước khi dùng lệnh /flig!')
            return

    try:
        params = message.text.split()
        if len(params) < 2:
            bot.reply_to(message, "Vui lòng nhập URL Instagram theo định dạng: /flig <link ig>\nVui lòng mua bằng link theo định dạng sau: ví dụ\nhttps://www.instagram.com/nvp310107")
            return

        instagram_profile_url = params[1]
        amount = '50'  # Số lượng follow mặc định là 50

        # Mua follow Instagram
        phpsessid = login_tds(USERNAME, PASSWORD)
        if not phpsessid:
            bot.reply_to(message, "Đăng nhập thất bại.")
            return

        status_code, response_text = buy_follow_instagram(phpsessid, instagram_profile_url, amount)

        # Thông báo duy nhất, đẹp hơn
        if status_code == 200:
            bot.reply_to(message, f"""<b>🎉 Đang tiến hành tăng follow Instagram 🎉</b>

<b>📷 Instagram:</b> <code>{instagram_profile_url}</code>
<b>👥 Số lượng:</b> {amount} follow
<b>⏳ Tình trạng:</b> Đã gửi yêu cầu tăng follow. Quá trình sẽ diễn ra trong vài phút. 
Cảm ơn bạn đã sử dụng dịch vụ!""", parse_mode='HTML')

            user_last_time[user_id] = current_time
        else:
            bot.reply_to(message, "Mua follow Instagram thất bại.")

    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")
#cảm xúc Faceboob
def buy_facebook_reaction(phpsessid, post_id, amount, reaction_type, speed):
    buy_url = 'https://traodoisub.com/mua/facebook_reaction/themid.php'
    current_time = datetime.now().strftime('%Y-%m-%d+%H:%M:%S')

    cookies = {
        'PHPSESSID': phpsessid,
    }

    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://traodoisub.com',
        'referer': 'https://traodoisub.com/mua/facebook_reaction/',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'maghinho': '',
        'id': post_id,
        'sl': amount,
        'dateTime': current_time,
        'loaicx': reaction_type,  
        'speed': speed,
    }

    response = requests.post(buy_url, cookies=cookies, headers=headers, data=data)
    return response.status_code, response.text

@bot.message_handler(commands=['cxfb'])
def handle_cxfb(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm được phép.")
        return

    user_id = message.from_user.id
    current_time = datetime.now()

    if is_admin(user_id):
        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            os.makedirs(f"./user/{today_day}", exist_ok=True)
            with open(today_path, "w") as fi:
                fi.write("")
    else:
        last_cxfb_time = user_last_time.get(user_id)
        if last_cxfb_time and current_time - last_cxfb_time < COOLDOWN_PERIOD:
            remaining_time = COOLDOWN_PERIOD - (current_time - last_cxfb_time)
            bot.reply_to(message, f"Vui lòng đợi {remaining_time.seconds // 60} phút trước khi sử dụng lại lệnh /cxfb.")
            return

        today_day = current_time.day
        today_path = f"./user/{today_day}/{user_id}.txt"

        if not os.path.exists(today_path):
            bot.reply_to(message, 'Hãy sử dụng lệnh /getkey trước khi dùng lệnh /cxfb!')
            return

    try:
        params = message.text.split()
        if len(params) < 3:
            bot.reply_to(
                message,
                "Vui lòng nhập thông tin theo định dạng: /cxfb <id bài viết> <loại cảm xúc>\n"
                "Không biết lấy id sử dụng lệnh /idfb {link} để lấy\n"
                "Danh sách cảm xúc: LIKE, LOVE, CARE, HAHA, WOW, SAD, ANGRY."
            )
            return

        post_id = params[1]
        reaction_type = params[2].strip().upper()  # Giữ nguyên chữ hoa, không chuyển thành chữ thường
        amount = '30'  # Mặc định số lượng cảm xúc là 30

        # Kiểm tra cảm xúc nhập vào có hợp lệ không
        valid_reactions = ["LIKE", "LOVE", "CARE", "HAHA", "WOW", "SAD", "ANGRY"]
        if reaction_type not in valid_reactions:
            bot.reply_to(message, f"Loại cảm xúc không hợp lệ. Hãy chọn một trong các loại: {', '.join(valid_reactions)}.")
            return

        # Tạo thông báo gửi cho người dùng
        reaction_message = (
            f"<blockquote>Đang tiến hành tăng cảm xúc Facebook\n"
            f"╭───────────────╮\n"
            f"│📘 Post ID: {post_id}\n"
            f"│❤️ Loại cảm xúc: {reaction_type}\n"
            f"│👥 Số cảm xúc: {amount}\n"
            f"│⏳ Đang tiến hành, vui lòng đợi...\n"
            f"╰───────────────╯\n"
            f"</blockquote>"
        )

        bot.reply_to(message, reaction_message, parse_mode='HTML')

        # Mua cảm xúc Facebook
        phpsessid = login_tds(USERNAME, PASSWORD)
        if not phpsessid:
            bot.reply_to(message, "Đăng nhập thất bại.")
            return

        status_code, response_text = buy_facebook_reaction(
            phpsessid, post_id, amount, reaction_type, speed=1
        )

        if status_code == 200:
            user_last_time[user_id] = current_time  # Cập nhật thời gian sau khi thành công
            bot.reply_to(message, "Mua cảm xúc Facebook thành công!")
        else:
            bot.reply_to(message, "Mua cảm xúc Facebook thất bại. Vui lòng thử lại sau.")

    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")
# Class từ code 1
class KsxKoji:
    def __Get_ThongTin__(self, cookie):
        id_ck = cookie.split('c_user=')[1].split(';')[0]
        a = requests.get('https://mbasic.facebook.com/profile.php?='+id_ck, headers={'cookie': cookie}).text
        try:
            self.name = a.split('<title>')[1].split('</title>')[0]
            self.fb_dtsg = a.split('<input type="hidden" name="fb_dtsg" value="')[1].split('"')[0]
            self.jazoest = a.split('<input type="hidden" name="jazoest" value="')[1].split('"')[0]
            return True
        except:
            return False

    def __Get_Page__(self, cookie):
        self.dem = 0
        data = {
            'fb_dtsg': self.fb_dtsg,
            'jazoest': self.jazoest,
            'variables': '{"showUpdatedLaunchpointRedesign":true,"useAdminedPagesForActingAccount":false,"useNewPagesYouManage":true}',
            'doc_id': '5300338636681652'
        }
        getidpro5 = requests.post('https://www.facebook.com/api/graphql/', headers={'cookie': cookie}, data=data).json()['data']['viewer']['actor']['profile_switcher_eligible_profiles']['nodes']
        list_page = []
        for uidd in getidpro5:
            self.dem += 1
            uid_page = uidd['profile']['id']
            list_page.append(uid_page)
        return list_page

    def __Follow__(self, cookie, id, taget):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'vi,vi-VN;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'content-encoding': 'br',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': f'{cookie} i_user={id};',
            'origin': 'https://www.facebook.com',
            'referer': 'https://www.facebook.com',
            'sec-ch-prefers-color-scheme': 'light',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        data = {
            'av': id,
            '__user': id,
            'fb_dtsg': self.fb_dtsg,
            'jazoest': self.jazoest,
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'CometUserFollowMutation',
            'variables': '{"input":{"attribution_id_v2":"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,tap_search_bar,1713671419755,394049,190055527696468,,","is_tracking_encrypted":false,"subscribe_location":"PROFILE","subscribee_id":"'+taget+'","tracking":null,"actor_id":"'+id+'","client_mutation_id":"19"},"scale":1}',
            'server_timestamps': 'true',
            'doc_id': '7393793397375006',
        }

        follow = requests.post('https://www.facebook.com/api/graphql/', headers=self.headers, data=data)
        try:
            check = follow.json()['errors']
            for i in check:
                if i['summary'] == 'Tài khoản của bạn hiện bị hạn chế':
                    return 'block'
        except:
            if 'IS_SUBSCRIBED' in follow.text:
                return True
            else:
                return False

# Lệnh /cookie chỉ cho chat riêng với bot
@bot.message_handler(commands=['cookie'])
def process_cookie(message):
    if message.chat.type != 'private':
        bot.reply_to(message, 'Lệnh này chỉ dùng trong chat riêng với bot.')
        return
    
    cookie = ' '.join(message.text.split()[1:])
    if 'c_user=' in cookie:
        f = KsxKoji()
        fb = f.__Get_ThongTin__(cookie)
        if fb:
            list_page = f.__Get_Page__(cookie)
            response = f"Name Profile: {f.name} | Có {f.dem} Page"
            with open('list_cookie.txt', 'a+') as file:
                file.write(cookie + '\n')
        else:
            response = 'Cookie không hợp lệ hoặc đã hết hạn.'
    else:
        response = 'Cookie không đúng định dạng.'
    
    bot.reply_to(message, response)

# Lệnh /follow chỉ cho chat trong group
@bot.message_handler(commands=['follow'])
def follow_profile(message):
    if not bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt')
        return
    
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, 'Xin lỗi, bot này chỉ hoạt động trong nhóm này https://t.me/botvphc')
        return
    
    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Vui lòng nhập ID và số lượng.')
        return
    
    taget = args[0]
    so_luong = int(args[1])
    delay = 10  # Đặt delay 
    
    x = 0
    dem = 0
    dem_ck = 0
    follow_success = 0
    follow_fail = 0
    with open('list_cookie.txt', 'r') as file:
        open_file = file.read().splitlines()
    
    list_page = []
    
    # Gửi thông báo khi bắt đầu lệnh follow
    message_follow = bot.reply_to(
        message,
        "Đang Tiến Hành Buff Sub\n"
        "╭───────────────╮\n"
        f"│» UID: {taget}\n"
        f"│» Follow thành công: {follow_success}\n"
        f"│» Follow thất bại: {follow_fail}\n"
        "╰───────────────╯"
    )

    while True:
        try:
            cookie = open_file[dem_ck]
            f = KsxKoji()
            f.__Get_ThongTin__(cookie)
            list_page = f.__Get_Page__(cookie)
            while True:
                try:
                    dem += 1
                    id = list_page[x]
                    fl = f.__Follow__(cookie, id, taget)
                    if fl == True:
                        follow_success += 1
                    elif fl == 'block':
                        bot.reply_to(message, f"Profile {f.name} đã bị block. Chuyển sang profile tiếp theo.")
                        list_page.clear()
                        time.sleep(2)
                        dem_ck += 1
                        x = 0
                        dem = 0
                        break
                    elif fl == False:
                        follow_fail += 1

                    # Cập nhật thông báo theo thời gian thực
                    new_message_text = (
                        "Đang Tiến Hành Buff Sub\n"
                        "╭───────────────╮\n"
                        f"│» UID: {taget}\n"
                        f"│» Follow thành công: {follow_success}\n"
                        f"│» Follow thất bại: {follow_fail}\n"
                        "╰───────────────╯"
                    )

                    # Chỉ cập nhật nếu nội dung mới khác nội dung hiện tại
                    if new_message_text != message_follow.text:
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=message_follow.message_id,
                            text=new_message_text
                        )
                    
                    x += 1
                    if dem >= so_luong:
                        bot.reply_to(message, f"Thành công {so_luong} sub")
                        return
                    if x >= len(list_page):
                        break
                    time.sleep(delay)
                except IndexError:
                    break
            dem_ck += 1
            if dem_ck >= len(open_file):
                bot.reply_to(message, f"Đã sử dụng hết {dem_ck} cookie, nhưng không đủ để follow {so_luong} lần.")
                break
        except Exception as e:
            bot.reply_to(message, f"Bảo trì 🛡️")
            break
                       
def banner():
    return f'''
{Fore.GREEN}
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║    {Fore.CYAN}{Style.BRIGHT}{__TOOL_NAME__}{Fore.GREEN}                                        ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║    {Fore.YELLOW}Author  : {Fore.WHITE}{__AUTHOR__}{Fore.GREEN}                                         ║
║    {Fore.YELLOW}Contact : {Fore.WHITE}{__CONTACT__}{Fore.GREEN}                          ║
╚════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
    '''

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.first_name or "Người dùng"
    name_bot = bot.get_me().first_name  

    if chat_id in ALLOWED_GROUP_IDS:
        msg = bot.reply_to(
            message,
            f"<b>Xin chào bạn {username}!</b>\n\n"
            f"🔖 <b>Dưới đây là danh sách lệnh của bot mà bạn có thể sử dụng:</b>\n\n"
            f"<blockquote expandable>┌───⭓ {name_bot}\n"
            f"│» Xin chào @{username}\n"
            f"╭───────────────╮\n"
            f"│<b>DỊCH VỤ FACEBOOK VIP</b>\n"
            f"╰───────────────╯\n"
            f"│» /sub : Follow Facebook V2\n"
            f"│» /cxfb : Tăng Cảm Xúc\n"
            f"╭───────────────╮\n"
            f"│<b>DỊCH VỤ FACEBOOK</b>\n"
            f"╰───────────────╯\n"
            f"│» /likefb : Tăng like bài viết Facebook (Bảo Trì🔐)\n"
            f"│» /share : Buff share bài viết Facebook\n"
            f"│» /idfb : Get id Facebook\n"
            f"│» /checkfb : Check info fb\n"
            f"│» /cookie : để góp page để sử dụng follow Facebook V1\n"
            f"│» /regfb : Lỏ lắm\n"
            f"│» /follow : Follow Facebook V1\n"
            f"╭───────────────╮\n"
            f"│<b>DỊCH VỤ TIKTOK</b>\n"
            f"╰───────────────╯\n"
            f"│» /tim : Buff tim TikTok\n"
            f"│» /fl : Buff Follow Tây TikTok (Bảo Trì🔐)\n"
            f"│» /fl2 : Buff Follow Việt TikTok\n"
            f"│» /tiktok : Tải Video Tiktok\n"
            f"│» /tt : Check thông tin tài khoản TikTok\n"
            f"╭───────────────╮\n"
            f"│<b>DỊCH VỤ INSTAGRAM</b>\n"
            f"╰───────────────╯\n"
            f"│» /likeig : Buff Like Instagram\n"
            f"│» /flig : Buff Follow Instagram\n"
            f"╭───────────────╮\n"
            f"│<b>TIỆN ÍCH KHÁC</b>\n"
            f"╰───────────────╯\n"
            f"│» /video : Ramdom video TikTok\n"
            f"│» /like : Tăng like Free Fire\n"
            f"│» /in4 : Info Telegram\n"
            f"│» /thoitiet : Check thời tiết\n"
            f"│» /down : Tải video Facebook, YouTube,...\n"
            f"│» /code : Lấy Code HTML của web\n"
            f"│» /tv : Đổi ngôn ngữ sang Tiếng Việt\n"
            f"╭───────────────╮\n"
            f"│<b>LỆNH CHO ADMIN</b>\n"
            f"╰───────────────╯\n"
            f"│» /adduser : Thêm Vip\n"
            f"│» /listvip : Kiểm tra danh sách Vip\n"
            f"└───────────⧕</blockquote>\n\n"
            f"💭 <b>LƯU Ý:</b> Trước khi dùng, bấm các lệnh để xem hướng dẫn sử dụng.",
            parse_mode='HTML'
        )
    else:
        msg = bot.reply_to(
            message,
            "Xin lỗi, bot này chỉ hoạt động trong nhóm này: https://t.me/botvphc"
        )
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
#share fb
def get_tokens_from_cookies(file_path):
    """Lấy token từ cookies trong file."""
    tokens = []
    try:
        with open(file_path, 'r') as file:
            cookies = file.read().split('\n')
        
        for cookie in cookies:
            if cookie.strip():
                headers = {
                    'authority': 'business.facebook.com',
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9',
                    'cache-control': 'no-cache',
                    'cookie': cookie.strip(),
                    'referer': 'https://www.facebook.com/',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                }
                try:
                    response = requests.get('https://business.facebook.com/content_management', headers=headers)
                    token = response.text.split('EAAG')[1].split('","')[0]
                    tokens.append(f"{cookie}|EAAG{token}")
                except Exception:
                    continue
    except Exception as e:
        print(f"Lỗi khi đọc file cookies: {e}")
    return tokens

def share_post(cookie_token, post_id, share_number):
    """Chia sẻ bài viết bằng token lấy từ cookie."""
    try:
        cookie, token = cookie_token.split('|')
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'connection': 'keep-alive',
            'cookie': cookie,
            'host': 'graph.facebook.com'
        }
        url = f'https://graph.facebook.com/me/feed'
        params = {
            'link': f'https://m.facebook.com/{post_id}',
            'published': '0',
            'access_token': token
        }
        res = requests.post(url, headers=headers, params=params).json()
        print(f"[{share_number}] Chia sẻ bài viết thành công: {res}")
    except Exception as e:
        print(f"Lỗi khi chia sẻ bài viết: {e}")

def get_facebook_post_id(post_url):
    """Lấy post ID từ URL bài viết."""
    try:
        response = requests.get(f'https://chongluadao.x10.bz/api/fb/getidfbvinhq.php?url={post_url}', verify=False)
        response.raise_for_status()
        data = response.json()
        post_id = data.get("id")
        if post_id:
            return post_id
        else:
            raise Exception("Không tìm thấy ID bài viết")
    except Exception as e:
        return f"Lỗi: {e}"

@bot.message_handler(commands=['share'])
def share(message):
    """Xử lý lệnh /share từ người dùng."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_time = time.time()

    # Kiểm tra nhóm cho phép
    if chat_id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, 'Bot này chỉ hoạt động trong nhóm được phép.')
        return

    # Kiểm tra thời gian chờ
    if user_id in user_cooldowns and current_time - user_cooldowns[user_id] < THỜI_GIAN_CHỜ:
        remaining_time = int(THỜI_GIAN_CHỜ - (current_time - user_cooldowns[user_id]))
        bot.reply_to(message, f'Bạn cần đợi {remaining_time} giây trước khi chia sẻ lần tiếp theo.')
        return

    # Kiểm tra key
    today_day = datetime.now().day
    key_path = f'./user/{today_day}/{user_id}.txt'

    if not os.path.exists(key_path):
        bot.reply_to(message, 'Bạn cần /getkey trước khi sử dụng lệnh /share.')
        return

    try:
        args = message.text.split()
        if len(args) != 3:
            bot.reply_to(message, 'Sai cú pháp! Vui lòng nhập: /share {link bài viết} {số lần chia sẻ}')
            return

        post_url, total_shares = args[1], int(args[2])
        post_id = get_facebook_post_id(post_url)

        if isinstance(post_id, str) and post_id.startswith("Lỗi"):
            bot.reply_to(message, post_id)
            return

        if user_id not in admins and total_shares > GIỚI_HẠN_CHIA_SẺ:
            bot.reply_to(message, f'Số lần chia sẻ vượt quá giới hạn {GIỚI_HẠN_CHIA_SẺ} lần.')
            return

        tokens = get_tokens_from_cookies('cookies.txt')
        if not tokens:
            bot.reply_to(message, 'Không tìm thấy token nào từ cookies.')
            return

        def share_with_delay(cookie_token, post_id, count):
            share_post(cookie_token, post_id, count)
            time.sleep(5)

        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(total_shares):
                token = random.choice(tokens)
                share_number = share_count.get(user_id, 0) + 1
                share_count[user_id] = share_number
                futures.append(executor.submit(share_with_delay, token, post_id, share_number))
            for future in futures:
                future.result()

        user_cooldowns[user_id] = current_time
        bot.reply_to(message, 'Đơn của bạn đã hoàn thành.')
    except Exception as e:
        bot.reply_to(message, f'Lỗi: {e}')

@bot.message_handler(commands=['idfb'])
def idfb(message):
    chat_id = message.chat.id
    if chat_id not in ALLOWED_GROUP_IDS:
        msg = bot.reply_to(message, 'Xin lỗi, bot này chỉ hoạt động trong nhóm này https://t.me/botvphc')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id,message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    
    try:
        link = message.text.split()[1]
        wait = bot.reply_to(message, "🔎")
        get_id_post = requests.post('https://id.traodoisub.com/api.php', data={"link": link}).json()
        if 'success' in get_id_post:
            id_post = get_id_post["id"]
            msg = bot.reply_to(message, f"Lấy id facebook thành công\n+ URL: {link}\n+ ID: `{id_post}`", parse_mode='Markdown')
        else:
            msg = bot.reply_to(message, 'Link không hợp lệ không thể lấy ID')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=wait.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
    except Exception as e:
        msg = bot.reply_to(message, f'Lỗi: {e}')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
# Các hàm từ đoạn code 2 bắt đầu từ đây

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def get_mail_domains():
    url = "https://api.mail.tm/domains"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['hydra:member']
        else:
            print(f'[×] E-mail Error : {response.text}')
            return None
    except Exception as e:
        print(f'[×] Error : {e}')
        return None

def create_mail_tm_account():
    mail_domains = get_mail_domains()
    if mail_domains:
        domain = random.choice(mail_domains)['domain']
        username = generate_random_string(10)
        password = fake.password()
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)
        first_name = fake.first_name()
        last_name = fake.last_name()
        url = "https://api.mail.tm/accounts"
        headers = {"Content-Type": "application/json"}
        data = {"address": f"{username}@{domain}", "password": password}       
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                print(f'[√] Email Created')
                return f"{username}@{domain}", password, first_name, last_name, birthday
            else:
                print(f'[×] Email Error : {response.text}')
                return None, None, None, None, None
        except Exception as e:
            print(f'[×] Error : {e}')
            return None, None, None, None, None

def register_facebook_account(email, password, first_name, last_name, birthday):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    gender = random.choice(['M', 'F'])
    req = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday.strftime('%Y-%m-%d'),
        'client_country_code': 'EN',
        'fb_api_caller_class': 'com.facebook.registration.protocol.RegisterAccountMethod',
        'fb_api_req_friendly_name': 'registerAccount',
        'firstname': first_name,
        'format': 'json',
        'gender': gender,
        'lastname': last_name,
        'email': email,
        'locale': 'en_US',
        'method': 'user.register',
        'password': password,
        'reg_instance': generate_random_string(32),
        'return_multiple_errors': True
    }
    sorted_req = sorted(req.items(), key=lambda x: x[0])
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    ensig = hashlib.md5((sig + secret).encode()).hexdigest()
    req['sig'] = ensig
    api_url = 'https://b-api.facebook.com/method/user.register'
    reg = _call(api_url, req)
    id = reg.get('new_user_id', 'N/A')
    token = reg.get('session_info', {}).get('access_token', 'N/A')
    return email, id, token, password, f"{first_name} {last_name}", birthday, gender

def _call(url, params, post=True):
    headers = {'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBCR/;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'}
    if post:
        response = requests.post(url, data=params, headers=headers)
    else:
        response = requests.get(url, params=params, headers=headers)
    return response.json()

@bot.message_handler(commands=['regfb'])
def create_accounts(message):
    try:
        args = message.text.split()
        num_accounts = 1  
        if len(args) > 1:
            try:
                num_accounts = int(args[1])
            except ValueError:
                bot.reply_to(message, "Số lần phải là một số nguyên.")
                return
        
        for _ in range(num_accounts):
            email, password, first_name, last_name, birthday = create_mail_tm_account()
            if email:
                email, id, token, password, name, birthday, gender = register_facebook_account(email, password, first_name, last_name, birthday)
                msg_content = f'''<pre>[+] Email: {email}
[+] ID: {id}
[+] Token: {token}
[+] Password: {password}
[+] Name: {name}
[+] BirthDay: {birthday}
[+] Gender: {gender}
===================================</pre>'''
                bot.reply_to(message, msg_content, parse_mode='HTML')
            else:
                bot.reply_to(message, "Không thể tạo tài khoản email. Vui lòng thử lại sau.")
    except Exception as e:
        bot.reply_to(message, f'Lỗi: {e}')
@bot.message_handler(commands=['in4'])
def get_info(message):
    chat_id = message.chat.id
    message_id = message.message_id
    text = message.text.split()

    def get_user_info(user):
        user_mention = user.first_name
        user_link = f'<a href="tg://user?id={user.id}">{user_mention}</a>'
        user_id = user.id
        username = user.username if user.username else "Không có username"
        full_name = user.full_name if hasattr(user, 'full_name') else "No Name"
        language_code = user.language_code if hasattr(user, 'language_code') else "Không rõ"
        bio = bot.get_chat(user_id).bio or "Không có bio"

        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            status = chat_member.status
        except Exception as e:
            bot.send_message(chat_id, f"Không thể lấy thông tin thành viên: {e}", parse_mode='HTML')
            return None, None

        status_text = "Thành viên"
        if status == 'administrator':
            status_text = "Quản Trị Viên"
        elif status == 'creator':
            status_text = "Chủ sở hữu"
        elif status == 'member':
            status_text = "Thành viên"
        elif status == 'restricted':
            status_text = "Bị hạn chế"
        elif status == 'left':
            status_text = "Đã rời đi"
        elif status == 'kicked':
            status_text = "Đã bị đuổi"

        info = (f"┌─┤📄 Thông tin của bạn├──⭓\n"
                f"├▷<b>ID</b> : <code>{user_id}</code>\n"
                f"├▷<b>Name</b>: {user_link}\n"
                f"├▷<b>UserName</b>: @{username}\n"
                f"├▷<b>Language</b>: {language_code}\n"
                f"├▷<b>Bio</b>: {bio}\n"
                f"├▷<b>Trạng thái</b>: {status_text}\n"
                f"└───────────────⭓")

        return info, user_id

    if len(text) > 1:
        username = text[1].lstrip('@')
        try:
            user_list = bot.get_chat_administrators(chat_id)
            target_user = None

            for user in user_list:
                if user.user.username == username:
                    target_user = user.user
                    break

            if not target_user:
                bot.send_message(chat_id, f"Không thể tìm thấy thông tin người dùng: @{username}", parse_mode='HTML')
                return

            info, user_id = get_user_info(target_user)

            if info:
                photos = bot.get_user_profile_photos(user_id)
                if photos.total_count > 0:
                    photo_file_id = photos.photos[0][-1].file_id  # Lấy file_id của ảnh có độ phân giải cao nhất
                    bot.send_photo(chat_id, photo_file_id, caption=info, parse_mode='HTML')
                else:
                    bot.send_message(chat_id, "Người dùng không có ảnh đại diện.")

        except Exception as e:
            bot.send_message(chat_id, f"Không thể tìm thấy thông tin người dùng: {e}", parse_mode='HTML')
    else:
        user = message.from_user
        info, user_id = get_user_info(user)

        if info:
            photos = bot.get_user_profile_photos(user_id)
            if photos.total_count > 0:
                photo_file_id = photos.photos[0][-1].file_id  # Lấy file_id của ảnh có độ phân giải cao nhất
                bot.send_photo(chat_id, photo_file_id, caption=info, parse_mode='HTML')
            else:
                bot.send_message(chat_id, "Bạn không có ảnh đại diện.")

    # Delete user's command message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        bot.send_message(chat_id, f"Không thể xóa tin nhắn: {e}", parse_mode='HTML')
# Xử lý lệnh /tiktok
@bot.message_handler(commands=['tiktok'])
def get_video(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        video_url = args[1]
        api_url = f'https://www.tikwm.com/api?url={video_url}'
        
        # Gửi request tới API và lấy kết quả trả về
        response = requests.get(api_url)
        
        # Kiểm tra xem API có trả về dữ liệu hay không
        if response.status_code == 200:
            data = response.json().get("data", {})
            
            # Lấy thông tin cần thiết từ dữ liệu API trả về
            title = data.get("title", "Không có tiêu đề")
            author = data.get("author", {}).get("nickname", "Không rõ tác giả")
            region = data.get("region", "Không rõ khu vực")
            duration = data.get("duration", 0)
            create_time = data.get("create_time", "Không rõ thời gian")
            play_count = data.get("play_count", "0")
            digg_count = data.get("digg_count", "0")
            comment_count = data.get("comment_count", "0")
            share_count = data.get("share_count", "0")
            download_count = data.get("download_count", "0")
            collect_count = data.get("collect_count", "0")
            music_url = data.get("music_info", {}).get("play", None)
            
            # Lấy danh sách các URL ảnh và video
            image_urls = data.get("images", [])
            video_url = data.get("play")
            
            # Tạo tin nhắn theo định dạng yêu cầu với HTML
            message_text = f"""
🎥 {title if video_url else 'None'}

<blockquote>👤 Tác giả: {author}
🌍 Khu Vực: {region}
🎮 Độ Dài Video: {duration} Giây
🗓️ Ngày Đăng: {create_time}
---------------------------------------
▶️ Views: {play_count}
❤️ Likes: {digg_count} like
💬 Comments: {comment_count}
🔄 Shares: {share_count}
⬇️ Downloads: {download_count}
📥 Favorites: {collect_count}</blockquote>
"""
            
            # Nếu có video
            if video_url:
                if image_urls:
                    # Gửi tất cả các ảnh trong một tin nhắn
                    media_group = [types.InputMediaPhoto(media=url) for url in image_urls if url]
                    if media_group:
                        bot.send_media_group(message.chat.id, media=media_group)
                
                # Gửi video và tiêu đề trong một tin nhắn văn bản
                bot.send_video(message.chat.id, video=video_url, caption=message_text, parse_mode='HTML')
            else:
                # Nếu chỉ có ảnh (không có video), gửi ảnh
                if image_urls:
                    media_group = [types.InputMediaPhoto(media=url) for url in image_urls if url]
                    if media_group:
                        bot.send_media_group(message.chat.id, media=media_group)
                
                # Gửi thông tin video nếu không có video
                bot.send_message(message.chat.id, message_text, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Không thể lấy thông tin video.")
    else:
        bot.send_message(message.chat.id, "⚠️ Vui lòng nhập url sau lệnh /tiktok.\n💭 Ví dụ: /tiktok https://vt.tiktok.com/abcd/.")
@bot.message_handler(commands=['code'])
def handle_code_command(message):
    # Tách lệnh và URL từ tin nhắn
    command_args = message.text.split(maxsplit=1)

    # Kiểm tra xem URL có được cung cấp không
    if len(command_args) < 2:
        bot.reply_to(message, "Vui lòng cung cấp url sau lệnh /code. Ví dụ: /code https://xnxx.com")
        return

    url = command_args[1]
    domain = urlparse(url).netloc
    file_name = f"{domain}.txt"
    
    try:
        # Lấy nội dung HTML từ URL
        response = requests.get(url)
        response.raise_for_status()  # Xảy ra lỗi nếu có lỗi HTTP

        # Lưu nội dung HTML vào file
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response.text)

        # Gửi file về người dùng
        with open(file_name, 'rb') as file:
            bot.send_document(message.chat.id, file, caption=f"HTML của trang web {url}")

        # Phản hồi tin nhắn gốc
        bot.reply_to(message, "Đã gửi mã nguồn HTML của trang web cho bạn.")

    except requests.RequestException as e:
        bot.reply_to(message, f"Đã xảy ra lỗi khi tải trang web: {e}")

    finally:
        # Đảm bảo xóa file sau khi gửi
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except Exception as e:
                bot.reply_to(message, f"Đã xảy ra lỗi khi xóa file: {e}")
@bot.message_handler(commands=['tv'])
def tieng_viet(message):
    chat_id = message.chat.id
    message_id = message.message_id
    
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton("Tiếng Việt 🇻🇳", url='https://t.me/setlanguage/abcxyz')
    keyboard.add(url_button)
    
    bot.send_message(chat_id, 'Click Vào Nút "<b>Tiếng Việt</b>" để đổi thành tv VN in đờ bét.', reply_markup=keyboard, parse_mode='HTML')
    
    # Delete user's command message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        bot.send_message(chat_id, f"Không thể xóa tin nhắn: {e}", parse_mode='HTML')
# Hàm lấy thông tin TikTok
def get_tiktok_info(username):
    url = f"https://iuhchinh.x10.mx/tt.php?user={html.escape(username)}"
    try:
        # Bỏ qua SSL với verify=False
        response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()
        
        # Truy cập thông tin từ trường "info"
        user_info = data['info']['userInfo']['user']
        stats = data['info']['userInfo']['stats']

        # Lấy thông tin người dùng
        nickname = html.escape(user_info.get('nickname', 'Không có') or 'Không có')
        bio = html.escape(user_info.get('signature', 'Không có') or 'Không có')
        avatar_url = html.escape(user_info.get('avatarLarger', '') or '')
        unique_id = html.escape(user_info.get('uniqueId', 'Không có') or 'Không có')
        create_time = datetime.fromtimestamp(user_info.get('createTime', 0)).strftime('%Y-%m-%d %H:%M:%S') if user_info.get('createTime') else 'Không có'
        language = html.escape(user_info.get('language', 'Không có') or 'Không có')
        nick_name_update = datetime.fromtimestamp(user_info.get('nickNameModifyTime', 0)).strftime('%Y-%m-%d %H:%M:%S') if user_info.get('nickNameModifyTime') else 'Không có'
        unique_id_update = datetime.fromtimestamp(user_info.get('uniqueIdModifyTime', 0)).strftime('%Y-%m-%d %H:%M:%S') if user_info.get('uniqueIdModifyTime') else 'Không có'
        region = html.escape(user_info.get('region', 'Không có') or 'Không có')

        # Trạng thái tài khoản
        is_verified = "Đã xác minh" if user_info.get('verified') else "Chưa xác minh"
        account_status = "Công Khai" if not user_info.get('privateAccount') else "Riêng Tư"
        has_playlist = "Có danh sách phát" if user_info.get('profileTab', {}).get('showPlayListTab') else "Không có danh sách phát"
        following_visibility = "Danh sách following đã bị ẩn" if user_info.get('followingVisibility') == 2 else "Danh sách following hiển thị"

        # Thống kê
        follower_count = stats.get('followerCount', 0) or 0
        following_count = stats.get('followingCount', 0) or 0
        friend_count = stats.get('friendCount', 0) or 0
        heart_count = stats.get('heart', 0) or 0
        video_count = stats.get('videoCount', 0) or 0

        result = f"""
<blockquote>╭─────────────⭓
│ 𝗜𝗗: {html.escape(user_info.get('id', 'Không có') or 'Không có')}
│ ‎𝗡𝗮𝗺𝗲:<a href="{avatar_url}">‎</a>{nickname}
│ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: {unique_id}
│ 𝗟𝗶𝗻𝗸: <a href="https://www.tiktok.com/@{unique_id}">https://www.tiktok.com/@{unique_id}</a>
│ 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱: {is_verified}
│ 𝗦𝘁𝗮𝘁𝘂𝘀:
│ | -> Tài khoản này đang ở chế độ {account_status}
│ | -> Là tài khoản Cá Nhân
│ | -> {has_playlist}
│ | -> {following_visibility}
│ 𝗖𝗿𝗲𝗮𝘁𝗲𝗱 𝗧𝗶𝗺𝗲: {create_time}
│ 𝗕𝗶𝗼: {bio}
│ 𝗙𝗼𝗹𝗹𝗼𝘄𝗲𝗿𝘀: {follower_count:,} Follower
│ 𝗙𝗼𝗹𝗹𝗼𝘄𝗶𝗻𝗴: {following_count} Đang Follow
│ 𝗙𝗿𝗶𝗲𝗻𝗱𝘀: {friend_count} Bạn Bè
│ 𝗟𝗶𝗸𝗲𝘀: {heart_count:,} Thích
│ 𝗩𝗶𝗱𝗲𝗼𝘀: {video_count} Video
├─────────────⭔
| 𝗟𝗮𝗻𝗴𝘂𝗮𝗴𝗲: {language}
| 𝗡𝗮𝗺𝗲 𝗨𝗽𝗱𝗮𝘁𝗲: {nick_name_update}
| 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 𝗨𝗽𝗱𝗮𝘁𝗲: {unique_id_update}
| 𝗥𝗲𝗴𝗶𝗼𝗻: {region}
╰─────────────⭓
</blockquote>
        """
        return result
    except requests.RequestException as e:
        return f"⚠️ Lỗi kết nối tới API: {e}"
    except KeyError as e:
        return f"⚠️ API trả về dữ liệu không hợp lệ: {e}"

# Hàm xử lý lệnh /tt
@bot.message_handler(commands=['tt'])
def handle_tiktok_info(message):
    try:
        # Lấy username từ tin nhắn
        username = message.text.split(' ', 1)[1].strip() if len(message.text.split(' ')) > 1 else None
        
        if username:
            result = get_tiktok_info(username)
            bot.reply_to(message, result, parse_mode='HTML')  
        else:
            bot.reply_to(message, "⚠️ Vui lòng nhập username hoặc link TikTok sau /tt.\n💬 Ví dụ: /tt nvp31012007")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Đã xảy ra lỗi: {e}")

#facebook
def mtt_sendreaction(bot_token, chat_id, message_id, emoji, is_big):
    url = f"https://api.telegram.org/bot{bot_token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [
            {
                "type": "emoji",
                "emoji": emoji
            }
        ],
        "is_big": is_big
    }
    sendreaction = requests.post(url, json=payload)

@bot.message_handler(commands=['checkfb'])
def check_fb(message):
    chat_id = message.chat.id
    message_id = message.message_id
    emoji = "⚡"
    is_big = True
    mtt_sendreaction(TOKEN, chat_id, message_id, emoji, is_big)
    
    args = message.text.split(maxsplit=1)
    
    if len(args) != 2:
        bot.reply_to(message, "🤖 Usage: /checkfb <Facebook ID>")
        return
    
    fb_id = args[1]
    idi = f'https://chongluadao.x10.bz/api/fb/getidfbvinhq.php?url=https://www.facebook.com/{fb_id}'  # Thay API mới
    idid = requests.get(idi)
    date = idid.json()
    datr = date['id']
    api_url = f"https://dichvukey.site/api/apiCheck.php?id={datr}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if data['status'] != 'success':
            bot.reply_to(message, "🤖 Không tìm thấy thông tin tài khoản.")
            return

        profile = data['result']

        response_message = f"<blockquote>╭─────────────⭓\n"

        if 'name' in profile:
            response_message += f"│ 𝗡𝗮𝗺𝗲: <a href=\'{profile['picture']['data']['url']}\'>‎</a><a href='{profile['link']}'>{profile['name']}</a>\n"
        if 'id' in profile:
            response_message += f"│ 𝗨𝗜𝗗: {profile['id']}\n"
        if 'username' in profile:
            response_message += f"│ 𝗨𝘀𝗲𝗿 𝗡𝗮𝗺𝗲: {profile['username']}\n"
        if 'is_verified' in profile:
            verification_status = 'Đã Xác Minh✅' if profile['is_verified'] else 'Chưa Xác Minh❌'
            response_message += f"│ 𝗩𝗲𝗿𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻: {verification_status}\n"
        if 'followers' in profile:
            response_message += f"│ 𝗙𝗼𝗹𝗹𝗼𝘄𝗲𝗿𝘀: {profile['followers']} người theo dõi\n"
        if 'created_time' in profile:
            response_message += f"│ 𝗗𝗮𝘁𝗲 𝗖𝗿𝗲𝗮𝘁𝗲𝗱: {profile['created_time']}\n"

        if 'gender' in profile:
            response_message += f"│ 𝗚𝗲𝗻𝗱𝗲𝗿: {'Nam' if profile['gender'] == 'male' else 'Nữ'}\n"
        if 'relationship_status' in profile:
            response_message += f"│ 𝗥𝗲𝗹𝗮𝘁𝗶𝗼𝗻𝘀𝗵𝗶𝗽: {profile['relationship_status']}\n"
        if 'hometown' in profile:
            response_message += f"│ 𝗛𝗼𝗺𝗲𝘁𝗼𝘄𝗻: {profile['hometown']['name']}\n"
        if 'location' in profile:
            response_message += f"│ 𝗟𝗼𝗰𝗮𝘁𝗶𝗼𝗻: {profile['location']['name']}\n"

        if 'work' in profile:
            response_message += "│ 𝗪𝗼𝗿𝗸:\n"
            for job in profile['work']:
                job_company = job.get('employer', {}).get('name', '')
                job_position = job.get('position', {}).get('name', '')
                if job_company or job_position:
                    response_message += f"│ -> {job_company} - {job_position}\n"

        if 'education' in profile:
            response_message += "│ 𝗘𝗱𝘂𝗰𝗮𝘁𝗶𝗼𝗻:\n"
            for education in profile['education']:
                school_name = education.get('school', {}).get('name', '')
                education_type = education.get('type', '')
                if school_name or education_type:
                    response_message += f"│ -> {school_name} ({education_type})\n"

        if 'birthday' in profile:
            response_message += f"│ 𝗕𝗶𝗿𝘁𝗵𝗱𝗮𝘆: {profile['birthday']}\n"
        if 'quotes' in profile:
            response_message += f"│ 𝗤𝘂𝗼𝘁𝗲𝘀: {profile['quotes']}\n"

        response_message += "├─────────────⭔\n"
        if 'locale' in profile:
            response_message += f"│ 𝗟𝗮𝗻𝗴𝘂𝗮𝗴𝗲: {profile['locale']}\n"
        if 'updated_time' in profile:
            response_message += f"│ 𝗧𝗶𝗺𝗲 𝗨𝗽𝗱𝗮𝘁𝗲: {profile['updated_time']}\n"
        if 'timezone' in profile:
            response_message += f"│ 𝗧𝗶𝗺𝗲 𝗭𝗼𝗻𝗲: GMT {profile['timezone']}\n"
        response_message += "╰─────────────⭓\n</blockquote>"

        bot.reply_to(message, response_message, parse_mode='HTML')
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"🤖 Error: {e}")
# Thời tiết
API_KEY = 'OUEaxPOl'  # API key của bạn

# Hàm lấy dữ liệu thời tiết từ API
def get_weather(city):
    try:
        url = f"https://nguyenmanh.name.vn/api/weather?city={city}&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            weather_info = data['result']
            return weather_info
        else:
            return None
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu từ API: {e}")
        return None

# Lệnh /thoitiet {địa điểm}
@bot.message_handler(commands=['thoitiet'])
def send_weather_info(message):
    try:
        # Lấy địa điểm từ lệnh
        city = message.text.split(' ', 1)[1]
        
        # Gọi API để lấy thông tin thời tiết
        weather = get_weather(city)
        if weather:
            # Format thông báo thời tiết với thẻ blockquote và HTML
            weather_message = f"""<blockquote>╭─────────────⭓
│ 🌍 Địa điểm: {weather['name']}
│ ☁️‎Tình trạng thời tiết: {weather['weather'][0]['description']}
│ 🌡️Nhiệt độ hiện tại: {weather['main']['temp']}°C
│ 🌡️Nhiệt độ cảm nhận: {weather['main']['feels_like']}°C
│ 🌬️Áp suất khí quyển: {weather['main']['pressure']} hPa
│ 💧Độ ẩm: {weather['main']['humidity']}%
│ 🌧️Lượng mưa trong 1 giờ: {weather.get('rain', {}).get('1h', 'Không có')} mm
│ 🍃Tốc độ gió: {weather['wind']['speed']} m/s
│ 💨Hướng gió: {weather['wind']['deg']}°
│ 🌪️Gió giật: {weather['wind'].get('gust', 'Không có')} m/s
│ 🌫️Mức độ che phủ của mây: {weather['clouds']['all']}%
├─────────────⭔
│Time Zone: GMT 7
╰─────────────⭓</blockquote>"""
            # Gửi thông báo đến người dùng với parse_mode HTML
            bot.reply_to(message, weather_message, parse_mode='HTML')
        else:
            bot.reply_to(message, "Không thể lấy thông tin thời tiết")
    except IndexError:
        bot.reply_to(message, "Nhập địa điểm sau lệnh /thoitiet.")
    except Exception as e:
        bot.reply_to(message, f"Có lỗi xảy ra: {e}")     
        
@bot.message_handler(commands=['down'])
def start(message):
    if len(message.text.split()) == 1:
        sai = bot.reply_to(message, "⚠️ Vui lòng nhập link to download sau /down.\n\n💭 Ví dụ: /down https://vt.tiktok.com/abcd/.\n\n🌐 Nền tảng hỗ trợ: 📱 Tiktok, Douyin, Threads, Instagram, Facebook, Pinterest, Reddit, Twitter, Snapchat, Bilibili, Linkedin, Telegram, Soundcloud, Spotify, Zingmp3.\n\n❗️ Lưu ý: Các link có video quá dài thì Bot có khả năng sẽ không gửi được video mà bạn mong muốn")
        bot.delete_message(message.chat.id, sai.message_id)
        return
    wait = bot.reply_to(message, "<blockquote>🔎 𝘛𝘪𝘦‌‌𝘯 𝘏𝘢‌𝘯𝘩 𝘓𝘢‌‌𝘺 𝘛𝘩𝘰‌𝘯𝘨 𝘛𝘪𝘯....</blockquote>",parse_mode='Html') 
    url = message.text.split()[1]
    user_id = message.from_user.id
    output_path = f'{user_id}.mp4'
    ydl_opts = {'format': 'best','outtmpl': output_path,'quiet': True,'postprocessors': [{'key': 'FFmpegVideoConvertor','preferedformat': 'mp4'}]}
    try:
        buffer = io.BytesIO()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            video_url = result['url']
            response = requests.get(video_url, stream=True, timeout=30)
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    buffer.write(chunk)
        buffer.seek(0)
        try:
            bot.send_video(message.chat.id, buffer, caption=f'» Url: {url}\n<blockquote>» Video: <a href="{video_url}">Click để xem</a></blockquote>', parse_mode="HTML")
        except:
            bot.reply_to(message, f'<blockquote>» Url: {url}\n\n» Video: <a href="{video_url}">Click để xem</a></blockquote>', parse_mode="HTML")
    except:
        bot.reply_to(message, "⚠️ Url Video Không Lấy Được, 💬 Vui Lòng Sử Dụng Url Khác.")
    bot.delete_message(message.chat.id, wait.message_id)  
@bot.message_handler(commands=['video'])
def send_random_video(message):
    # Gửi yêu cầu đến API
    api_url = "https://gaitiktok.onrender.com/random?apikey=randomtnt"
    response = requests.get(api_url)
    data = response.json()

    if data["code"] == 0:
        video_url = data["data"]["play"]
        title = data["data"]["title"]
        nickname = data["data"]["author"]["nickname"]
        unique_id = data["data"]["author"]["unique_id"]

        # Tạo caption kèm thẻ blockquote
        caption = (f"<b>RANDOM VIDEO TIKTOK</b>\n"
                   f"<blockquote>╭─────────⭓\n"
                   f"│📝 Tiêu đề: {title if title else 'Không có'}\n"
                   f"│🔠 Tên kênh: {nickname}\n"
                   f"│🆔 ID người dùng: {unique_id}\n"
                   f"╰─────────⭓</blockquote>")

        # Gửi video kèm tin nhắn với chế độ HTML
        bot.send_video(message.chat.id, video=video_url, caption=caption, parse_mode='HTML')
    else:
        bot.reply_to(message, "Không thể lấy video.")     
# Hàm để lấy thông tin từ API
def get_instagram_info(username):
    url = f"https://chongluadao.x10.bz/api/other/instagrapvinh.php?input={username}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and 'result' in data and 'user' in data['result']:
            user_data = data['result']['user']
            return user_data
    return None

# Xử lý lệnh /instagram
@bot.message_handler(commands=['ig'])
def send_instagram_info(message):
    try:
        # Lấy username từ tin nhắn
        username = message.text.split('/ig ')[1]
        info = get_instagram_info(username)
        
        if info:
            full_name = info.get('full_name', 'Không có thông tin')
            biography = info.get('biography', 'Không có tiểu sử')
            follower_count = info.get('follower_count', 'Không rõ')
            following_count = info.get('following_count', 'Không rõ')
            post_count = info.get('media_count', 'Không rõ')
            profile_pic_url = info.get('profile_pic_url', '')
            is_verified = 'Đã xác minh' if info.get('is_verified') else 'Chưa xác minh'
            account_type = 'Đây là tài khoản công khai' if not info.get('is_private') else 'Đây là tài khoản riêng tư'
            is_linked_to_whatsapp = 'Có liên kết với Whatsapp' if info.get('connected_fb_page') else 'Không liên kết với Whatsapp'
            biography_with_link = 'Có liên kết ngoài' if 'external_url' in info and info['external_url'] else 'Không có liên kết ngoài'
            creation_date = info.get('creation_date', 'Không rõ')

            # Tạo nội dung thông báo theo định dạng yêu cầu
            message_text = f"""
<blockquote>╭─────────────⭓
│ ID: {html.escape(info.get('pk', 'Không rõ'))}
│ ‎Tên: <a href="{profile_pic_url}">‎{html.escape(full_name)}</a>
│ Username: {html.escape(username)}
│ Link: <a href="https://www.instagram.com/{html.escape(username)}">https://www.instagram.com/{html.escape(username)}</a>
│ 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱: {is_verified}
│ Ngày Tạo: {creation_date}
│ Trạng Thái:
│ | -> {account_type}
│ | -> {is_linked_to_whatsapp}
│ Tiểu Sử: {biography}
│ Tiểu Sử Link: {biography_with_link}
├─────────────⭔
│ 𝗙𝗼𝗹𝗹𝗼𝘄𝗲𝗿𝘀: {follower_count} người theo dõi
│ Đang Theo Dõi: Đang theo dõi {following_count} người dùng
│ 𝗣𝗼𝘀𝘁𝘀: {post_count} bài viết
╰─────────────⭓
</blockquote>
            """

            # Gửi thông báo
            bot.send_message(message.chat.id, message_text, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Không tìm thấy thông tin cho tài khoản này.")
    except IndexError:
        bot.send_message(message.chat.id, "Vui lòng nhập username. Ví dụ: /ig duongvantuank7")
#freefire
def get_freefire_info(user_id):
    url = f"https://ffwlxd-info.vercel.app/player-info?region={region}&uid={uid}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_country_flag(region_code):
    try:
        country = pycountry.countries.get(alpha_2=region_code)
        if country:
            flag = chr(ord(region_code[0]) + 127397) + chr(ord(region_code[1]) + 127397)
            return f"{country.name} {flag}"
    except:
        return "Không xác định"

def translate_language(language_code):
    try:
        language_code = language_code.replace("Language_", "").upper()
        language = pycountry.languages.get(alpha_2=language_code[:2])
        if language:
            return language.name
    except:
        return "Không xác định"

def format_freefire_info(data):
    def check_and_add(label, value):
        invalid_values = ["None", "Not Found", "Found", "Not Found/Not Found", ""]
        if value and value not in invalid_values:
            return f"├─ {label}: {value}\n"
        return None

    language = translate_language(data['Account Language'])
    region = get_country_flag(data['Account Region'])

    account_info = ""
    account_info += check_and_add("Tên", data.get('Account Name')) or ""
    account_info += check_and_add("UID", data.get('Account UID')) or ""
    account_info += check_and_add("Level", f"{data['Account Level']} (Exp: {data['Account XP']})") or ""
    account_info += check_and_add("Sever", region) or ""
    account_info += check_and_add("Ngôn Ngữ", language) or ""
    account_info += check_and_add("Likes", data.get('Account Likes')) or ""
    account_info += check_and_add("Tiểu Sử", data.get('Account Signature')) or ""
    account_info += check_and_add("Điểm Rank", data.get('BR Rank Points')) or ""
    account_info += check_and_add("Điểm Uy Tín", data.get('Account Honor Score')) or ""
    account_info += check_and_add("Ngày Tạo Acc", data.get('Account Create Time (GMT 0530)')) or ""
    account_info += check_and_add("Đăng Nhập Lần Cuối", data.get('Account Last Login (GMT 0530)')) or ""

    if account_info.strip():
        account_info = f"┌ 👤 THÔNG TIN TÀI KHOẢN\n{account_info}"

    pet_info = ""
    pet_info += check_and_add("Pet Đang Chọn", "Có" if data['Equipped Pet Information']['Selected?'] else "Không") or ""
    pet_info += check_and_add("Tên Pet", data['Equipped Pet Information']['Pet Name']) or ""
    pet_info += check_and_add("Level Pet", f"{data['Equipped Pet Information']['Pet Level']} (Exp: {data['Equipped Pet Information']['Pet XP']})") or ""

    if pet_info.strip():
        pet_info = f"┌ 🐾 THÔNG TIN PET\n{pet_info}"

    guild_info = ""
    guild_info += check_and_add("ID Quân Đoàn", data['Guild Information']['Guild ID']) or ""
    guild_info += check_and_add("Tên Quân Đoàn", data['Guild Information']['Guild Name']) or ""
    guild_info += check_and_add("Level", data['Guild Information']['Guild Level']) or ""
    guild_info += check_and_add("Số Thành Viên", f"{data['Guild Information']['Guild Current Members']}/{data['Guild Information']['Guild Capacity']}") or ""
    guild_info += check_and_add("Tên Chủ Quân Đoàn", data['Guild Leader Information']['Leader Name']) or ""

    if guild_info.strip():
        guild_info = f"┌ 👥 THÔNG TIN QUÂN ĐOÀN\n{guild_info}"

    full_info = "\n\n".join(filter(None, [account_info, pet_info, guild_info]))

    return f"<blockquote>{full_info}</blockquote>" if full_info.strip() else "Không có thông tin hợp lệ."

def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return BytesIO(response.content)
    return None

def create_freefire_sticker(data):
    nickname = data['Account Name']
    level = data['Account Level']
    avatar_id = data['Account Avatar Image'].split('=')[-1]
    banner_id = data['Account Banner Image'].split('=')[-1]
    pin_id = data['Account Pin Image'].split('=')[-1]

    sticker_url = f"https://api.scaninfo.vn/freefire/ffui/?nickname={nickname}&level={level}&avatar_id={avatar_id}&banner_id={banner_id}&pin_id={pin_id}"
    
    return sticker_url

@bot.message_handler(commands=['ff'])
def send_freefire_info(message):
    try:
        user_id = message.text.split()[1]
        data = get_freefire_info(user_id)
        if data:
            info = format_freefire_info(data)
            bot.reply_to(message, info, parse_mode='HTML')

            # Gửi sticker sau khi gửi thông tin tài khoản
            sticker_url = create_freefire_sticker(data)
            image_file = download_image(sticker_url)
            if image_file:
                bot.send_sticker(message.chat.id, image_file)
            else:
                bot.reply_to(message, "Không gửi được ảnh")
        else:
            bot.reply_to(message, "Không tìm thấy ID")
    except IndexError:
        bot.reply_to(message, "⚠️ Vui lòng nhập ID sau /ff.\n💬 Ví dụ: /ff 123456789")
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")                                  
# Khởi động bot
print(banner())
bot.infinity_polling()