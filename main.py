
"""
JOBAO - Golike Automation Tool
All-in-one automation for Twitter, LinkedIn, Threads, Pinterest, Snapchat
Version: Professional v2.0
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

# Giá trị mặc định
CAU_HINH = {
    "authorization": "",
    "webhook_url": "https://discord.com/api/webhooks/1497565399670194186/4JNbWpffK7udWXwGLz5Swxkjpz4vfsFZH1P9add1Q2iEQwwGr04L3PdC18iIA45UzjnY",
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
                # Cập nhật key thiếu nếu file cũ
                for k, v in CAU_HINH.items():
                    if k in data:
                        CAU_HINH[k] = data[k]
        except:
            pass
    # Nếu có file user.txt cũ mà auth trong config rỗng thì lấy auth từ đó
    if not CAU_HINH["authorization"] and os.path.exists('user.txt'):
        try:
            with open('user.txt', 'r') as f:
                CAU_HINH["authorization"] = f.read().strip()
        except: pass

def luu_cau_hinh():
    with open(FILE_CAU_HINH, 'w', encoding='utf-8') as f:
        json.dump(CAU_HINH, f, indent=4, ensure_ascii=False)

tai_cau_hinh()

def gui_webhook(noi_dung):
    if not CAU_HINH["webhook_enabled"] or not CAU_HINH["webhook_url"]:
        return
    try:
        du_lieu = {
            "content": None,
            "embeds": [
                {
                    "title": "JOB ẢO ",
                    "description": noi_dung,
                    "color": 5814783,
                    "footer": {
                        "text": f"Time: {datetime.now().strftime('%H:%M:%S')}"
                    }
                }
            ],
            "username": "Job ảo"
        }
        requests.post(CAU_HINH["webhook_url"], json=du_lieu, impersonate="chrome")
    except:
        pass


# ==============================================================================
# DEBUG MODE
# ==============================================================================
CHE_DO_DEBUG = False

def dat_debug(kich_hoat):
    global CHE_DO_DEBUG
    CHE_DO_DEBUG = kich_hoat

def ghi_log_debug(nhan, du_lieu):
    global CHE_DO_DEBUG
    if CHE_DO_DEBUG:
        print(f"\n{MauSac.DAM_TIM}[DEBUG] {nhan}:{MauSac.MAC_DINH}")
        if isinstance(du_lieu, dict):
            try:
                print(f"{MauSac.VANG}{json.dumps(du_lieu, indent=2, ensure_ascii=False)}{MauSac.MAC_DINH}")
            except:
                print(f"{MauSac.VANG}{du_lieu}{MauSac.MAC_DINH}")
        else:
            chuoi_du_lieu = str(du_lieu)
            if len(chuoi_du_lieu) > 2000:
                print(f"{MauSac.VANG}{chuoi_du_lieu[:2000]}...{MauSac.MAC_DINH}")
            else:
                print(f"{MauSac.VANG}{chuoi_du_lieu}{MauSac.MAC_DINH}")
        print()

# ==============================================================================
# COLORS & UTILS
# ==============================================================================
class MauSac:
    MAC_DINH = '\033[0m'
    DAM = '\033[1m'
    DO = '\033[31m'
    XANH_LA = '\033[32m'
    VANG = '\033[33m'
    XANH_DUONG = '\033[34m'
    XANH_LO = '\033[36m'
    TRANG = '\033[37m'
    DAM_DO = '\033[1;31m'
    DAM_XANH_LA = '\033[1;32m'
    DAM_VANG = '\033[1;33m'
    DAM_XANH_DUONG = '\033[1;34m'
    DAM_XANH_LO = '\033[1;36m'
    DAM_TRANG = '\033[1;37m'
    TIM = '\033[35m'
    DAM_TIM = '\033[1;35m'

def hien_thi_banner():
    os.system("cls" if os.name == "nt" else "clear")
    try:
        thong_tin_ip = requests.get('https://api.ipify.org?format=json', timeout=5).json()
        dia_chi_ip = thong_tin_ip.get('ip', 'Unknown')
    except:
        try:
            thong_tin_ip = requests.get('http://ip-api.com/json', timeout=5).json()
            dia_chi_ip = thong_tin_ip.get('query', 'Lỗi kết nối')
        except:
            dia_chi_ip = "Lỗi kết nối"
    
    thoi_gian_hien_tai = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    text_banner = f"""
{MauSac.DAM_XANH_LO}╔════════════════════════════════════════════════════════════════════════╗
{MauSac.DAM_XANH_LO}║{MauSac.DAM_TRANG}                       ⛃  BÉ TẬP CODE TOOL  ⛃                        {MauSac.DAM_XANH_LO}║
{MauSac.DAM_XANH_LO}╠════════════════════════════════════════════════════════════════════════╣
{MauSac.DAM_XANH_LO}║ {MauSac.DAM_VANG}⛃  TOOL BY       {MauSac.DAM_TRANG}: Bé Tập Code                                     {MauSac.DAM_XANH_LO}║
{MauSac.DAM_XANH_LO}║ {MauSac.DAM_VANG}⛃  YOUTUBER      {MauSac.DAM_TRANG}: HVHTOOL                                         {MauSac.DAM_XANH_LO}║
{MauSac.DAM_XANH_LO}║ {MauSac.DAM_VANG}⛃  YOUTUBE LINK  {MauSac.DAM_TRANG}: https://www.youtube.com/@HVHTOOL                {MauSac.DAM_XANH_LO}║
{MauSac.DAM_XANH_LO}║ {MauSac.DAM_VANG}⛃  VERSION       {MauSac.DAM_TRANG}: Professional v2.0                               {MauSac.DAM_XANH_LO}║
{MauSac.DAM_XANH_LO}║ {MauSac.DAM_VANG}⛃  DATE          {MauSac.DAM_TRANG}: {thoi_gian_hien_tai}                             {MauSac.DAM_XANH_LO}║
{MauSac.DAM_XANH_LO}╚════════════════════════════════════════════════════════════════════════╝{MauSac.MAC_DINH}

{MauSac.DAM_XANH_LO}╔════════════════════════════════════════════════════════════════════════╗
{MauSac.DAM_XANH_LO}║{MauSac.DAM_TRANG}                           ⛃⛃ THÔNG TIN IP                          {MauSac.DAM_XANH_LO}║
{MauSac.DAM_XANH_LO}╠════════════════════════════════════════════════════════════════════════╣
{MauSac.DAM_XANH_LO}║{MauSac.DAM_TRANG} ⛃  Địa chỉ IP: {MauSac.DAM_XANH_LA}{dia_chi_ip}                                          {MauSac.DAM_XANH_LO}║
{MauSac.DAM_XANH_LO}╚════════════════════════════════════════════════════════════════════════╝{MauSac.MAC_DINH}
"""
    for ki_tu in text_banner:
        sys.stdout.write(ki_tu)
        sys.stdout.flush()
        time.sleep(0.0001)
    print()

def dem_nguoc(thoi_gian_giay, thong_diep="Đang chờ"):
    for con_lai in range(thoi_gian_giay, -1, -1):
        sys.stdout.write(f"\r{MauSac.DAM_XANH_LO}[{thong_diep}] {MauSac.DAM_VANG}{con_lai}s... {MauSac.MAC_DINH}")
        sys.stdout.flush()
        time.sleep(1)
    print("\r" + " " * 60 + "\r", end="")

def kiem_tra_trang_thai_server():
    try:
        key_bao_tri = requests.get(
            'https://raw.githubusercontent.com/HOANGHUY785/sever/refs/heads/main/sever.txt',
            impersonate="chrome"
        ).text.strip()
        if key_bao_tri != 'HVHONSEVER1':
            print(f'{MauSac.DAM_DO}SERVER ĐANG BẢO TRÌ HOẶC DỪNG HOẠT ĐỘNG.')
            sys.exit()
    except:
        pass

def ghi_nhat_ky_job(stt, loai_job, nen_tang, gia_tien, tong_tien, thong_tin_them=""):
    gio_hien_tai = datetime.now().strftime("%H:%M:%S")
    
    print(f"{MauSac.DAM_DO}| {MauSac.DAM_XANH_LO}{stt}{MauSac.DAM_DO} | "
          f"{MauSac.DAM_VANG}{gio_hien_tai}{MauSac.DAM_DO} | "
          f"{MauSac.DAM_XANH_LA}SUCCESS{MauSac.DAM_DO} | "
          f"{MauSac.DAM_XANH_DUONG}{nen_tang.upper()}:{loai_job}{MauSac.DAM_DO} | "
          f"{MauSac.DAM_XANH_LA}+{gia_tien}{MauSac.DAM_DO} | "
          f"{MauSac.DAM_VANG}{tong_tien} VND{MauSac.MAC_DINH} {thong_tin_them}")
    
    if CAU_HINH["webhook_enabled"]:
        tin_nhan_webhook = f"**SUCCESS**\nPlatform: `{nen_tang.upper()}`\nType: `{loai_job}`\nPrice: `{gia_tien}`\nTotal: `{tong_tien} VND`"
        gui_webhook(tin_nhan_webhook)

# ==============================================================================
# BASE BOT CLASS
# ==============================================================================
class BotCoBan:
    def __init__(self, golike_auth, golike_t, nen_tang):
        self.golike_auth = golike_auth
        self.golike_t = golike_t
        self.nen_tang = nen_tang
        self.golike_headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': self.golike_auth,
            't': self.golike_t,
            'content-type': 'application/json;charset=utf-8',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
        }

    def lay_danh_sach_tai_khoan(self):
        try:
            phan_hoi = requests.get(
                f'https://gateway.golike.net/api/{self.nen_tang}-account',
                headers=self.golike_headers,
                impersonate="chrome"
            ).json()
            ghi_log_debug(f"{self.nen_tang.upper()} lay_danh_sach_tai_khoan", phan_hoi)
            return phan_hoi
        except Exception as e:
            print(f"{MauSac.DO}Lỗi lấy danh sách tài khoản: {e}{MauSac.MAC_DINH}")
            return None

    def lay_job(self, account_id):
        try:
            phan_hoi = requests.get(
                f'https://gateway.golike.net/api/advertising/publishers/{self.nen_tang}/jobs?account_id={account_id}&data=null',
                headers=self.golike_headers,
                impersonate="chrome"
            ).json()
            ghi_log_debug(f"{self.nen_tang.upper()} lay_job", phan_hoi)
            return phan_hoi
        except Exception as e:
            print(f"{MauSac.DO}Lỗi lấy job: {e}{MauSac.MAC_DINH}")
            return None

    def hoan_thanh_job(self, ads_id, account_id):
        try:
            du_lieu_json = {
                'ads_id': ads_id,
                'account_id': account_id,
                'async': True,
                'data': None
            }
            phan_hoi = requests.post(
                f'https://gateway.golike.net/api/advertising/publishers/{self.nen_tang}/complete-jobs',
                headers=self.golike_headers,
                json=du_lieu_json,
                impersonate="chrome"
            ).json()
            ghi_log_debug(f"{self.nen_tang.upper()} hoan_thanh_job", phan_hoi)
            return phan_hoi
        except Exception as e:
            print(f"{MauSac.DO}Lỗi hoàn thành job: {e}{MauSac.MAC_DINH}")
            return None

    def bo_qua_job(self, ads_id, account_id, object_id):
        try:
            du_lieu_json = {
                'ads_id': ads_id,
                'account_id': account_id,
                'object_id': object_id
            }
            requests.post(
                f'https://gateway.golike.net/api/advertising/publishers/{self.nen_tang}/skip-jobs',
                headers=self.golike_headers,
                json=du_lieu_json,
                impersonate="chrome"
            )
        except:
            pass

# ==============================================================================
# PLATFORM BOTS
# ==============================================================================
class BotTwitter(BotCoBan):
    def __init__(self, golike_auth, golike_t):
        super().__init__(golike_auth, golike_t, "twitter")

class BotLinkedin(BotCoBan):
    def __init__(self, golike_auth, golike_t):
        super().__init__(golike_auth, golike_t, "linkedin")

class BotThreads(BotCoBan):
    def __init__(self, golike_auth, golike_t):
        super().__init__(golike_auth, golike_t, "threads")

class BotPinterest(BotCoBan):
    def __init__(self, golike_auth, golike_t):
        super().__init__(golike_auth, golike_t, "pinterest")

class BotSnapchat(BotCoBan):
    def __init__(self, golike_auth, golike_t):
        super().__init__(golike_auth, golike_t, "snapchat")

# ==============================================================================
# CLI FUNCTIONS
# ==============================================================================
def tai_token_auth():
    auth_hien_tai = CAU_HINH["authorization"]
    if not auth_hien_tai:
        auth_nhap = input(f"{MauSac.XANH_LA}Nhập Authorization Golike: {MauSac.MAC_DINH}").strip()
        if auth_nhap:
            CAU_HINH["authorization"] = auth_nhap
            luu_cau_hinh()
            return auth_nhap
    return auth_hien_tai

def hien_thi_menu(debug_duoc_bat=False):
    trang_thai_debug = f"{MauSac.DAM_XANH_LA}ON" if debug_duoc_bat else f"{MauSac.DAM_DO}OFF"
    
    print(f"\n{MauSac.DAM_XANH_LO}═══════════════════════════════════════════════════════════════{MauSac.MAC_DINH}")
    print(f"{MauSac.DAM_TRANG}                     CHỌN NỀN TẢNG                              {MauSac.MAC_DINH}")
    print(f"{MauSac.DAM_XANH_LO}═══════════════════════════════════════════════════════════════{MauSac.MAC_DINH}")
    print(f"{MauSac.DAM_TRANG}[1] {MauSac.DAM_XANH_LO}🐦 Auto X (Twitter)")
    print(f"{MauSac.DAM_TRANG}[2] {MauSac.DAM_XANH_DUONG}💼 Auto LinkedIn")
    print(f"{MauSac.DAM_TRANG}[3] {MauSac.DAM_TIM}🧵 Auto Threads")
    print(f"{MauSac.DAM_TRANG}[4] {MauSac.DAM_DO}📌 Auto Pinterest")
    print(f"{MauSac.DAM_TRANG}[5] {MauSac.DAM_VANG}👻 Auto Snapchat")
    print(f"{MauSac.DAM_TRANG}[6] {MauSac.DAM_XANH_LA}🔄 Auto ALL (X -> In -> Thread -> Pin -> Snap)")
    print(f"{MauSac.DAM_XANH_LO}═══════════════════════════════════════════════════════════════{MauSac.MAC_DINH}")
    
    trang_thai_wh = f"{MauSac.DAM_XANH_LA}ON" if CAU_HINH["webhook_enabled"] else f"{MauSac.DAM_DO}OFF"
    print(f"{MauSac.DAM_TRANG}[w] {MauSac.DAM_XANH_DUONG}📢 Webhook Mode: {trang_thai_wh}")
    print(f"{MauSac.DAM_TRANG}[s] {MauSac.DAM_VANG}⚙️ Cài đặt (Job, Delay, Lỗi dừng)")
    print(f"{MauSac.DAM_TRANG}[d] {MauSac.DAM_TIM}🔧 Debug Mode: {trang_thai_debug}{MauSac.MAC_DINH}")
    print(f"{MauSac.DAM_TRANG}[0] {MauSac.DAM_DO}❌ Thoát")
    print(f"{MauSac.DAM_XANH_LO}═══════════════════════════════════════════════════════════════{MauSac.MAC_DINH}")
    print(f"{MauSac.XANH_LA}Cấu hình hiện tại: {CAU_HINH['so_luong_job']} jobs | {CAU_HINH['delay_giay']}s delay | Stop {CAU_HINH['dung_sau_loi']} errs{MauSac.MAC_DINH}")

def cai_dat_tham_so():
    print(f"\n{MauSac.DAM_VANG}--- CÀI ĐẶT THAM SỐ CHẠY ---{MauSac.MAC_DINH}")
    try:
        sl = input(f"Số lượng Jobs [{CAU_HINH['so_luong_job']}]: ").strip()
        if sl: CAU_HINH['so_luong_job'] = int(sl)
        
        dl = input(f"Delay (giây) [{CAU_HINH['delay_giay']}]: ").strip()
        if dl: CAU_HINH['delay_giay'] = int(dl)
        
        err = input(f"Dừng sau lỗi liên tiếp [{CAU_HINH['dung_sau_loi']}]: ").strip()
        if err: CAU_HINH['dung_sau_loi'] = int(err)
        
        luu_cau_hinh()
        print(f"{MauSac.XANH_LA}Đã lưu cấu hình mới!{MauSac.MAC_DINH}")
    except ValueError:
        print(f"{MauSac.DO}Giá trị nhập không hợp lệ!{MauSac.MAC_DINH}")

def chay_nhieu_acc(bot, ten_nen_tang):
    so_luong = CAU_HINH['so_luong_job']
    thoi_gian_cho = CAU_HINH['delay_giay']
    loi_toi_da = CAU_HINH['dung_sau_loi']
    
    phan_hoi_acc = bot.lay_danh_sach_tai_khoan()
    if not phan_hoi_acc or phan_hoi_acc.get('status') != 200:
        print(f"{MauSac.DO}Không thể lấy danh sách tài khoản!{MauSac.MAC_DINH}")
        return
    
    danh_sach_acc = phan_hoi_acc.get('data', [])
    if not danh_sach_acc:
        print(f"{MauSac.DO}Không có tài khoản nào!{MauSac.MAC_DINH}")
        return
    
    print(f"\n{MauSac.XANH_LA}Tìm thấy {len(danh_sach_acc)} tài khoản:{MauSac.MAC_DINH}")
    for i, acc in enumerate(danh_sach_acc):
        ten = acc.get('name', acc.get('username', acc.get('screen_name', f'Account {i}')))
        acc_id = acc.get('id', 'N/A')
        print(f"  [{i}] {ten} (ID: {acc_id})")
    
    print(f"\n{MauSac.DAM_XANH_LA}Bắt đầu chạy tự động với {len(danh_sach_acc)} tài khoản...{MauSac.MAC_DINH}")
    print(f"{MauSac.XANH_LO}{'='*60}{MauSac.MAC_DINH}")
    
    if CAU_HINH["webhook_enabled"]:
        msg_khoi_dong = f"**🚀 STARTING...**\nPlatform: `{ten_nen_tang.upper()}`\nAccounts: `{len(danh_sach_acc)}`\nTarget: `{so_luong} jobs`\nMax Fails: `{loi_toi_da}`"
        gui_webhook(msg_khoi_dong)
    
    dem_loi_acc = {acc.get('id'): 0 for acc in danh_sach_acc}
    loi_lien_tiep = 0  
    loi_acc_toi_da = 3
    dem_job_thanh_cong = 0
    tong_tien = 0
    chi_so_acc_hien_tai = 0
    
    for i in range(so_luong):
        if loi_lien_tiep >= loi_toi_da:
            print(f"\n{MauSac.DAM_DO}⛔ ĐÃ ĐẠT GIỚI HẠN {loi_toi_da} LỖI LIÊN TIẾP. DỪNG LẠI!{MauSac.MAC_DINH}")
            if CAU_HINH["webhook_enabled"]:
                gui_webhook(f"**⛔ STOPPED**\nReason: Reached `{loi_toi_da}` consecutive errors.")
            break

        if chi_so_acc_hien_tai >= len(danh_sach_acc):
            chi_so_acc_hien_tai = 0
        
        acc_hien_tai = danh_sach_acc[chi_so_acc_hien_tai]
        acc_id = acc_hien_tai.get('id')
        ten_acc = acc_hien_tai.get('name', acc_hien_tai.get('username', acc_hien_tai.get('screen_name', 'Unknown')))
        
        if dem_loi_acc.get(acc_id, 0) >= loi_acc_toi_da:
            tim_thay_acc_song = False
            for _ in range(len(danh_sach_acc)):
                chi_so_acc_hien_tai = (chi_so_acc_hien_tai + 1) % len(danh_sach_acc)
                acc_tiep = danh_sach_acc[chi_so_acc_hien_tai]
                id_tiep = acc_tiep.get('id')
                if dem_loi_acc.get(id_tiep, 0) < loi_acc_toi_da:
                    tim_thay_acc_song = True
                    break
            if not tim_thay_acc_song:
                print(f"{MauSac.DO}Tất cả tài khoản đều lỗi! Dừng lại.{MauSac.MAC_DINH}")
                break
            continue
        
        job = bot.lay_job(acc_id)
        
        if not job or job.get('status') != 200:
            msg = job.get('message', 'Unknown error') if job else 'No response'
            print(f"{MauSac.DO}[{i+1}/{so_luong}] [{ten_acc}] No job: {msg}. Switching...{MauSac.MAC_DINH}")
            dem_loi_acc[acc_id] = dem_loi_acc.get(acc_id, 0) + 1
            loi_lien_tiep += 1 
            chi_so_acc_hien_tai = (chi_so_acc_hien_tai + 1) % len(danh_sach_acc)
            dem_nguoc(2, "Switching")
            continue
        
        du_lieu = job['data']
        loai_job = du_lieu.get('type', 'unknown')
        link_job = du_lieu.get('link', '')
        object_id = du_lieu.get('object_id', '')
        ads_id = du_lieu.get('id', '')
        
        print(f"{MauSac.XANH_LO}[{i+1}/{so_luong}] [{ten_acc}] {loai_job.upper()} | {link_job[:35]}...{MauSac.MAC_DINH}")
        
        dem_nguoc(10, "Processing")
        
        thanh_cong = False
        for lan_thu in range(3):
            phan_hoi = bot.hoan_thanh_job(ads_id, acc_id)
            if phan_hoi and (phan_hoi.get('success') == True or phan_hoi.get('status') == 200):
                thanh_cong = True
                dem_job_thanh_cong += 1
                tien = phan_hoi.get('data', {}).get('prices', 0)
                tong_tien += tien
                ghi_nhat_ky_job(dem_job_thanh_cong, loai_job, ten_nen_tang.upper(), tien, tong_tien)
                dem_loi_acc[acc_id] = 0
                loi_lien_tiep = 0 
                break
            else:
                if lan_thu < 2:
                    print(f"{MauSac.VANG}Thử lại lần {lan_thu + 2}/3...{MauSac.MAC_DINH}")
                    dem_nguoc(3, "Retry")
        
        if not thanh_cong:
            print(f"{MauSac.DO}Failed sau 3 lần! Switching...{MauSac.MAC_DINH}")
            dem_loi_acc[acc_id] = dem_loi_acc.get(acc_id, 0) + 1
            loi_lien_tiep += 1
            bot.bo_qua_job(ads_id, acc_id, object_id)
            chi_so_acc_hien_tai = (chi_so_acc_hien_tai + 1) % len(danh_sach_acc)
        
        if thoi_gian_cho > 10:
            dem_nguoc(thoi_gian_cho - 10, "Delay")
    
    print(f"{MauSac.DAM_XANH_LA}{'='*60}")
    print(f"{MauSac.DAM_XANH_LA}Hoàn thành! Tổng: {dem_job_thanh_cong} jobs | Kiếm được: {tong_tien} VND{MauSac.MAC_DINH}")

def chay_nen_tang(golike_auth, golike_t, ten_nen_tang, lop_bot):
    print(f"\n{MauSac.DAM_XANH_LO}=== AUTO {ten_nen_tang.upper()} ==={MauSac.MAC_DINH}")
    bot = lop_bot(golike_auth, golike_t)
    chay_nhieu_acc(bot, ten_nen_tang)

def chay_tu_dong_vong_lap(golike_auth, golike_t):
    print(f"\n{MauSac.DAM_XANH_LA}=== KÍCH HOẠT CHẾ ĐỘ AUTO ALL (SMART CYCLE) ==={MauSac.MAC_DINH}")
    print(f"{MauSac.VANG}Cơ chế: Chạy xoay vòng từng nền tảng. Nếu nền tảng nào lỗi/hết job -> Tự động chuyển cái tiếp theo.{MauSac.MAC_DINH}")
    
    danh_sach_nen_tang = [
        ("Twitter", BotTwitter),
        ("LinkedIn", BotLinkedin),
        ("Threads", BotThreads),
        ("Pinterest", BotPinterest),
        ("Snapchat", BotSnapchat)
    ]
    
    so_vong_lap = 0
    while True:
        so_vong_lap += 1
        print(f"\n{MauSac.DAM_TIM}╔═══════════════════════════════════════════════════════════════╗")
        print(f"║                   BẮT ĐẦU VÒNG LẶP THỨ {so_vong_lap}                      ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝{MauSac.MAC_DINH}")
        
        for ten, LopBot in danh_sach_nen_tang:
            print(f"\n{MauSac.DAM_XANH_LO}>>> ĐANG CHUYỂN SANG: {ten.upper()} <<<{MauSac.MAC_DINH}")
            try:
                bot = LopBot(golike_auth, golike_t)
                chay_nhieu_acc(bot, ten)
            except Exception as e:
                print(f"{MauSac.DO}Lỗi khi chạy {ten}: {e}. Bỏ qua...{MauSac.MAC_DINH}")
            
            print(f"{MauSac.VANG}Nghỉ 5s trước khi sang nền tảng tiếp theo...{MauSac.MAC_DINH}")
            time.sleep(5)

def main():
    kiem_tra_trang_thai_server()
    hien_thi_banner()
    
    golike_auth = tai_token_auth()
    golike_t = "VFZSamQwOUVSVEpQVkVFd1RrRTlQUT09"
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'authorization': golike_auth,
        't': golike_t,
        'content-type': 'application/json;charset=utf-8',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
    }
    
    try:
        thong_tin_user = requests.get(
            'https://gateway.golike.net/api/users/me',
            headers=headers,
            impersonate="chrome"
        ).json()
    except Exception as e:
        print(f"{MauSac.DO}Lỗi kết nối: {e}{MauSac.MAC_DINH}")
        sys.exit(1)

    if not thong_tin_user or thong_tin_user.get('status') != 200:
        print(f"{MauSac.DO}Authorization không hợp lệ!{MauSac.MAC_DINH}")
        # Reset auth nếu lỗi
        CAU_HINH["authorization"] = ""
        luu_cau_hinh()
        sys.exit(1)

    du_lieu = thong_tin_user['data']
    print(f"{MauSac.DAM_XANH_LA}✅ Đăng nhập thành công!")
    print(f"{MauSac.DAM_TRANG}   User: {MauSac.VANG}{du_lieu.get('username', du_lieu.get('name', 'N/A'))}")
    print(f"{MauSac.DAM_TRANG}   Coin: {MauSac.VANG}{du_lieu.get('coin', 0)}{MauSac.MAC_DINH}")
    
    debug_duoc_bat = False
    
    while True:
        hien_thi_menu(debug_duoc_bat)
        lua_chon = input(f"\n{MauSac.DAM_VANG}Nhập lựa chọn: {MauSac.MAC_DINH}").strip().lower()

        if lua_chon == '1':
            chay_nen_tang(golike_auth, golike_t, "Twitter", BotTwitter)
        elif lua_chon == '2':
            chay_nen_tang(golike_auth, golike_t, "LinkedIn", BotLinkedin)
        elif lua_chon == '3':
            chay_nen_tang(golike_auth, golike_t, "Threads", BotThreads)
        elif lua_chon == '4':
            chay_nen_tang(golike_auth, golike_t, "Pinterest", BotPinterest)
        elif lua_chon == '5':
            chay_nen_tang(golike_auth, golike_t, "Snapchat", BotSnapchat)
        elif lua_chon == '6':
            chay_tu_dong_vong_lap(golike_auth, golike_t)
        elif lua_chon == 's':
            cai_dat_tham_so()
        elif lua_chon == 'd':
            debug_duoc_bat = not debug_duoc_bat
            dat_debug(debug_duoc_bat)
            trang_thai = "BẬT" if debug_duoc_bat else "TẮT"
            print(f"{MauSac.DAM_TIM}Debug Mode đã {trang_thai}!{MauSac.MAC_DINH}")
            continue
        elif lua_chon == 'w':
            if not CAU_HINH["webhook_url"]:
                print(f"\n{MauSac.VANG}Chưa có Webhook URL!{MauSac.MAC_DINH}")
                url_moi = input(f"Nhập Webhook URL (Discord/...): ").strip()
                if url_moi:
                    CAU_HINH["webhook_url"] = url_moi
                    CAU_HINH["webhook_enabled"] = True
                    luu_cau_hinh()
                    print(f"{MauSac.XANH_LA}Đã lưu và BẬT Webhook!{MauSac.MAC_DINH}")
                else:
                    print(f"{MauSac.DO}URL trống! Hủy.{MauSac.MAC_DINH}")
            else:
                CAU_HINH["webhook_enabled"] = not CAU_HINH["webhook_enabled"]
                luu_cau_hinh()
                trang_thai = "BẬT" if CAU_HINH["webhook_enabled"] else "TẮT"
                print(f"{MauSac.DAM_XANH_DUONG}Webhook Mode đã {trang_thai}!{MauSac.MAC_DINH}")
            continue
        elif lua_chon == '0':
            print(f"\n{MauSac.DAM_XANH_LA}Tạm biệt! 👋{MauSac.MAC_DINH}")
            break
        else:
            print(f"{MauSac.DO}Lựa chọn không hợp lệ!{MauSac.MAC_DINH}")
        
        input(f"\n{MauSac.XANH_LO}Nhấn Enter để tiếp tục...{MauSac.MAC_DINH}")

def run():
    main()

if __name__ == "__main__":
    main()
