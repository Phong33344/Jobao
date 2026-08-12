#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golike Job Ảo - Single file, chỉ hỗ trợ: Twitter, Threads, LinkedIn, Pinterest, Snapchat
Dùng golike-gauth 0.1.13, bật sig + captcha tự động.
"""

import os
import sys
import time
import json
import threading
import queue
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Any

from golike_gauth import GolikeAuth, auto_solve_captcha
import requests

# ============================================================================
# Colors
# ============================================================================
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    BOLD_CYAN = '\033[1;36m'
    BOLD_WHITE = '\033[1;37m'
    MAGENTA = '\033[35m'
    BOLD_MAGENTA = '\033[1;35m'

print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

# ============================================================================
# Debug API logger — bọc auth.get / auth.post, in request + response đầy đủ
# ============================================================================
def _dump_request(method: str, url: str, params=None, json_body=None, headers=None):
    safe_print(f"\n{Colors.BOLD_MAGENTA}{'─'*60}")
    safe_print(f"  ► {method.upper()}  {url}")
    if params:
        safe_print(f"  PARAMS : {json.dumps(params, ensure_ascii=False)}")
    if json_body is not None:
        safe_print(f"  BODY   : {json.dumps(json_body, separators=(',',':'), ensure_ascii=False)}")
    if headers:
        for k in ("Authorization", "g-auth", "g-device-id", "g-username", "g-version", "g-client", "t"):
            v = headers.get(k)
            if v:
                display = (v[:40] + "...") if len(str(v)) > 43 else v
                safe_print(f"  HDR    {k}: {display}")
    safe_print(f"{Colors.RESET}", end="")

def _dump_response(resp):
    try:
        body = resp.json()
        text = json.dumps(body, indent=2, ensure_ascii=False)
    except Exception:
        text = resp.text[:2000]
    safe_print(f"{Colors.BOLD_YELLOW}  ◄ HTTP {resp.status_code}")
    for line in text.splitlines()[:60]:
        safe_print(f"    {line}")
    if len(text.splitlines()) > 60:
        safe_print(f"    ... (truncated)")
    safe_print(f"{'─'*60}{Colors.RESET}\n")

def debug_get(auth, path: str, params=None):
    """auth.get wrapper với debug dump."""
    resp = auth.get(path, params=params)
    if is_debug_enabled():
        base = getattr(auth, 'base_url', 'https://gateway.golike.net/api')
        url = base.rstrip('/') + path
        hdrs = resp.request.headers if hasattr(resp, 'request') and resp.request else {}
        _dump_request("GET", url, params=params, headers=dict(hdrs))
        _dump_response(resp)
    return resp

def debug_post(auth, path: str, json_body=None):
    """auth.post wrapper với debug dump."""
    resp = auth.post(path, json=json_body)
    if is_debug_enabled():
        base = getattr(auth, 'base_url', 'https://gateway.golike.net/api')
        url = base.rstrip('/') + path
        hdrs = resp.request.headers if hasattr(resp, 'request') and resp.request else {}
        _dump_request("POST", url, json_body=json_body, headers=dict(hdrs))
        _dump_response(resp)
    return resp

def show_banner():
    safe_print(f"{Colors.BOLD_CYAN}Golike Job Ảo - v2 (chỉ Twitter, Threads, LinkedIn, Pinterest, Snapchat){Colors.RESET}")

def countdown(seconds: int, message: str = "Waiting"):
    for remaining in range(seconds, -1, -1):
        with print_lock:
            sys.stdout.write(f"\r{Colors.BOLD_CYAN}[{message}] {Colors.BOLD_YELLOW}{remaining}s... {Colors.RESET}")
            sys.stdout.flush()
        time.sleep(1)
    with print_lock:
        print("\r" + " " * 60 + "\r", end="")

def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"{Colors.BOLD_CYAN}{prompt}{suffix}: {Colors.RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return val or default

def ask_choice(prompt: str, options, allow_back: bool = True) -> int:
    safe_print(f"\n{Colors.BOLD_WHITE}{prompt}{Colors.RESET}")
    for i, label in enumerate(options, start=1):
        safe_print(f"  {Colors.BOLD_CYAN}{i}{Colors.RESET}. {label}")
    if allow_back:
        safe_print(f"  {Colors.BOLD_CYAN}0{Colors.RESET}. {Colors.YELLOW}← Quay lại{Colors.RESET}")
    while True:
        raw = ask("Chọn", "0" if allow_back else "1")
        try:
            n = int(raw)
        except ValueError:
            safe_print(f"{Colors.RED}Vui lòng nhập số.{Colors.RESET}")
            continue
        if allow_back and n == 0:
            return -1
        if 1 <= n <= len(options):
            return n - 1
        safe_print(f"{Colors.RED}Lựa chọn không hợp lệ.{Colors.RESET}")

def mask(s: str, keep: int = 8) -> str:
    if not s:
        return f"{Colors.YELLOW}(rỗng){Colors.RESET}"
    if len(s) <= keep * 2:
        return s[:4] + "..." + s[-4:]
    return s[:keep] + "..." + s[-keep:]

# ============================================================================
# Config
# ============================================================================
FILE_CONFIG = 'config.json'
DEFAULT_CONFIG = {
    "token": "",
    "webhook_url": "",
    "debug": False,
    "so_luong_job": 1000,
    "delay_giay": 5,
    "dung_sau_loi": 5,
}

def init_config_if_missing():
    if not os.path.exists(FILE_CONFIG):
        with open(FILE_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG.copy(), f, indent=4, ensure_ascii=False)

def load_config():
    init_config_if_missing()
    try:
        with open(FILE_CONFIG, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            if k not in data:
                data[k] = v
        # Xóa các key cũ
        for old in ("signing_key", "user_id", "username", "device_id", "g_version"):
            data.pop(old, None)
        save_config(data)
        return data
    except Exception:
        save_config(DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    with open(FILE_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

init_config_if_missing()
CONFIG = load_config()

def set_field(key: str, value):
    CONFIG[key] = value
    save_config(CONFIG)

def get_webhook() -> str:
    return (CONFIG.get("webhook_url") or "").strip()

def is_debug_enabled() -> bool:
    env = os.environ.get("GOLIKE_DEBUG", "").strip().lower()
    if env in ("1", "true", "yes", "on"):
        return True
    return bool(CONFIG.get("debug", False))

# ============================================================================
# GolikeAuth wrapper
# ============================================================================
def create_auth_from_token(token: str) -> GolikeAuth:
    return GolikeAuth.from_token(
        token,
        enable_sig=True,
        captcha_solver=auto_solve_captcha,
        captcha_max_attempts=3,
        fetch_session=True,
    )

def get_auth_from_config() -> Optional[GolikeAuth]:
    token = (CONFIG.get("token") or "").strip()
    if not token:
        return None
    try:
        auth = create_auth_from_token(token)
        CONFIG["username"] = auth.username
        CONFIG["user_id"] = auth.user_id
        save_config(CONFIG)
        return auth
    except Exception as e:
        safe_print(f"{Colors.RED}Lỗi tạo auth từ token: {e}{Colors.RESET}")
        return None

def prompt_auth() -> GolikeAuth:
    safe_print(f"\n{Colors.BOLD_WHITE}{'='*60}{Colors.RESET}")
    safe_print(f"{Colors.BOLD_CYAN}  Nhập JWT token (Bearer){Colors.RESET}")
    safe_print(f"{Colors.BOLD_WHITE}{'='*60}{Colors.RESET}")
    while True:
        token = ask("JWT token", "").strip()
        if not token:
            safe_print(f"{Colors.RED}Token không được rỗng.{Colors.RESET}")
            continue
        try:
            auth = create_auth_from_token(token)
            break
        except Exception as e:
            safe_print(f"{Colors.RED}Lỗi: {e}. Thử lại.{Colors.RESET}")
    CONFIG["token"] = token
    CONFIG["username"] = auth.username
    CONFIG["user_id"] = auth.user_id
    save_config(CONFIG)
    safe_print(f"{Colors.GREEN}✓ Đã tạo auth thành công cho user {auth.username} (ID: {auth.user_id}){Colors.RESET}")
    return auth

# ============================================================================
# Base Provider
# ============================================================================
class BaseProviderBot:
    platform: str = ""

    def __init__(self, auth: GolikeAuth, platform: str = ""):
        if platform:
            self.platform = platform
        if not self.platform:
            raise ValueError("Subclass must set platform")
        self.auth = auth

    def get_accounts(self) -> Optional[Dict]:
        try:
            resp = debug_get(self.auth, f"/{self.platform}-account")
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def complete_job(self, ads_id: int, account_id: int, job_data: Optional[Dict] = None) -> Optional[Dict]:
        raise NotImplementedError

    def skip_job(self, **kwargs):
        raise NotImplementedError

    def account_display_name(self, acc: Dict, idx: int) -> str:
        return acc.get('name') or acc.get('username') or acc.get('screen_name') or f"Account {idx}"

    def account_id(self, acc: Dict) -> str:
        return str(acc.get('id', 'N/A'))

# ============================================================================
# Các lớp provider cụ thể (chỉ 5 platform)
# ============================================================================
class TwitterBot(BaseProviderBot):
    platform = "twitter"

    def get_job(self, account_id: str) -> Optional[Dict]:
        try:
            resp = debug_get(
                self.auth,
                "/advertising/publishers/twitter/jobs",
                params={"account_id": account_id}
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def complete_job(self, ads_id: int, account_id: int, job_data: Optional[Dict] = None) -> Optional[Dict]:
        try:
            job_type = (job_data or {}).get('type', '')
            if job_type == 'comment':
                comment_run = (job_data or {}).get('comment_run') or {}
                comment_id  = comment_run.get('id')       # top-level field
                message     = comment_run.get('message') or ''
                body = {
                    "ads_id":      ads_id,
                    "account_id":  account_id,
                    "async":       True,
                    "comment_id":  comment_id,   # required — id từ comment_run
                    "message":     message,       # required — text comment
                }
            else:
                body = {
                    "ads_id":     ads_id,
                    "account_id": account_id,
                    "async":      True,
                    "data":       None,
                }
            resp = debug_post(
                self.auth,
                "/advertising/publishers/twitter/complete-jobs",
                json_body=body
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def skip_job(self, ads_id: int, object_id: str, account_id: int):
        try:
            debug_post(
                self.auth,
                "/advertising/publishers/twitter/skip-jobs",
                json_body={"ads_id": ads_id, "object_id": object_id, "account_id": account_id}
            )
        except Exception:
            pass

class ThreadsBot(BaseProviderBot):
    platform = "threads"

    def get_job(self, account_id: str) -> Optional[Dict]:
        try:
            resp = debug_get(
                self.auth,
                "/advertising/publishers/threads/jobs",
                params={"account_id": account_id}
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def complete_job(self, ads_id: int, account_id: int, job_data: Optional[Dict] = None) -> Optional[Dict]:
        try:
            job_type = (job_data or {}).get('type', '')
            if job_type == 'comment':
                message = (job_data.get('comment_run') or {}).get('message') or ''
                data_field = {"message": message} if message else None
            else:
                data_field = None
            resp = debug_post(
                self.auth,
                "/advertising/publishers/threads/complete-jobs",
                json_body={"ads_id": ads_id, "account_id": account_id, "async": True, "data": data_field}
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def skip_job(self, ads_id: int, object_id: str, account_id: int):
        try:
            debug_post(
                self.auth,
                "/advertising/publishers/threads/skip-jobs",
                json_body={"ads_id": ads_id, "object_id": object_id, "account_id": account_id}
            )
        except Exception:
            pass

class LinkedInBot(BaseProviderBot):
    platform = "linkedin"

    def get_job(self, account_id: str) -> Optional[Dict]:
        try:
            resp = debug_get(
                self.auth,
                "/advertising/publishers/linkedin/jobs",
                params={"account_id": account_id}
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def complete_job(self, ads_id: int, account_id: int, job_data: Optional[Dict] = None) -> Optional[Dict]:
        try:
            job_type = (job_data or {}).get('type', '')
            if job_type == 'comment':
                message = (job_data.get('comment_run') or {}).get('message') or ''
                data_field = {"message": message} if message else None
            else:
                data_field = None
            resp = debug_post(
                self.auth,
                "/advertising/publishers/linkedin/complete-jobs",
                json_body={"ads_id": ads_id, "account_id": account_id, "async": True, "data": data_field}
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def skip_job(self, ads_id: int, object_id: str, account_id: int):
        try:
            debug_post(
                self.auth,
                "/advertising/publishers/linkedin/skip-jobs",
                json_body={"ads_id": ads_id, "object_id": object_id, "account_id": account_id}
            )
        except Exception:
            pass

class PinterestBot(BaseProviderBot):
    platform = "pinterest"

    def get_job(self, account_id: str) -> Optional[Dict]:
        try:
            resp = debug_get(
                self.auth,
                "/advertising/publishers/pinterest/jobs",
                params={"account_id": account_id}
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def complete_job(self, ads_id: int, account_id: int, job_data: Optional[Dict] = None) -> Optional[Dict]:
        try:
            job_type = (job_data or {}).get('type', '')
            if job_type == 'comment':
                message = (job_data.get('comment_run') or {}).get('message') or ''
                data_field = {"message": message} if message else None
            else:
                data_field = None
            resp = debug_post(
                self.auth,
                "/advertising/publishers/pinterest/complete-jobs",
                json_body={"ads_id": ads_id, "account_id": account_id, "async": True, "data": data_field}
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def skip_job(self, ads_id: int, object_id: str, account_id: int):
        try:
            debug_post(
                self.auth,
                "/advertising/publishers/pinterest/skip-jobs",
                json_body={"ads_id": ads_id, "object_id": object_id, "account_id": account_id}
            )
        except Exception:
            pass

class SnapchatBot(BaseProviderBot):
    platform = "snapchat"

    def get_job(self, account_id: str) -> Optional[Dict]:
        try:
            resp = debug_get(
                self.auth,
                "/advertising/publishers/snapchat/jobs",
                params={"account_id": account_id}
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def complete_job(self, ads_id: int, account_id: int, job_data: Optional[Dict] = None) -> Optional[Dict]:
        try:
            job_type = (job_data or {}).get('type', '')
            if job_type == 'comment':
                message = (job_data.get('comment_run') or {}).get('message') or ''
                data_field = {"message": message} if message else None
            else:
                data_field = None
            resp = debug_post(
                self.auth,
                "/advertising/publishers/snapchat/complete-jobs",
                json_body={"ads_id": ads_id, "account_id": account_id, "async": True, "data": data_field}
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def skip_job(self, ads_id: int, object_id: str, account_id: int):
        try:
            debug_post(
                self.auth,
                "/advertising/publishers/snapchat/skip-jobs",
                json_body={"ads_id": ads_id, "object_id": object_id, "account_id": account_id}
            )
        except Exception:
            pass

# Danh sách platform được hỗ trợ
ALL_PROVIDERS = [
    ("Twitter", TwitterBot),
    ("Threads", ThreadsBot),
    ("LinkedIn", LinkedInBot),
    ("Pinterest", PinterestBot),
    ("Snapchat", SnapchatBot),
]

def get_bot(platform_name: str, auth: GolikeAuth) -> BaseProviderBot:
    for name, cls in ALL_PROVIDERS:
        if name.lower() == platform_name.lower():
            return cls(auth)
    raise ValueError(f"Unknown platform: {platform_name}")

# ============================================================================
# Single Account Runner
# ============================================================================
class SingleAccountRunner:
    def __init__(self, auth: GolikeAuth):
        self.auth = auth
        self.running = True
        self.stats = {
            'username': auth.username,
            'user_id': auth.user_id,
            'coin': 0,
            'total_earned': 0,
            'jobs_done': 0,
        }
        self.max_errors = CONFIG['dung_sau_loi']
        self.delay_sec = CONFIG['delay_giay']
        self.jobs_target = CONFIG['so_luong_job']

    def show_profile(self) -> bool:
        try:
            resp = debug_get(self.auth, "/users/me")
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                self.stats['username'] = data.get('username', self.auth.username)
                self.stats['coin'] = data.get('coin', 0)
                safe_print(f"\n{Colors.BOLD_GREEN}{'='*60}{Colors.RESET}")
                safe_print(f"{Colors.BOLD_CYAN}  Username : {Colors.BOLD_WHITE}{self.stats['username']}{Colors.RESET}")
                safe_print(f"{Colors.BOLD_CYAN}  User ID  : {Colors.BOLD_WHITE}{self.auth.user_id}{Colors.RESET}")
                safe_print(f"{Colors.BOLD_CYAN}  Device   : {Colors.BOLD_WHITE}{self.auth.device_id}{Colors.RESET}")
                safe_print(f"{Colors.BOLD_CYAN}  Coin     : {Colors.BOLD_YELLOW}{self.stats['coin']}{Colors.RESET}")
                safe_print(f"{Colors.BOLD_GREEN}{'='*60}{Colors.RESET}\n")
                return True
            safe_print(f"{Colors.RED}Token không hợp lệ!{Colors.RESET}")
            return False
        except Exception as e:
            safe_print(f"{Colors.RED}Lỗi lấy profile: {e}{Colors.RESET}")
            return False

    def list_accounts(self, platform_name: Optional[str] = None):
        targets = [(platform_name, get_bot(platform_name, self.auth))] if platform_name else [(name, get_bot(name, self.auth)) for name, _ in ALL_PROVIDERS]
        for name, bot in targets:
            safe_print(f"\n{Colors.BOLD_CYAN}── {name} ──{Colors.RESET}")
            accs = bot.get_accounts()
            if not accs or accs.get('status') != 200:
                safe_print(f"{Colors.RED}  Không lấy được: {accs.get('message', 'no response') if accs else 'no response'}{Colors.RESET}")
                continue
            accounts = accs.get('data', [])
            if not accounts:
                safe_print(f"{Colors.YELLOW}  (rỗng){Colors.RESET}")
                continue
            for i, acc in enumerate(accounts):
                safe_print(f"  [{i}] {bot.account_display_name(acc, i)}  {Colors.CYAN}(ID: {bot.account_id(acc)}){Colors.RESET}")

    def run_platform(self, platform_name: str) -> int:
        bot = get_bot(platform_name, self.auth)
        accs = bot.get_accounts()
        if not accs or accs.get('status') != 200:
            safe_print(f"{Colors.RED}Không lấy được danh sách tài khoản {platform_name}!{Colors.RESET}")
            return 0
        accounts = accs.get('data', [])
        if not accounts:
            safe_print(f"{Colors.RED}Không có tài khoản {platform_name} nào!{Colors.RESET}")
            return 0

        safe_print(f"\n{Colors.GREEN}{platform_name}: {len(accounts)} tài khoản{Colors.RESET}")
        for i, acc in enumerate(accounts):
            safe_print(f"  [{i}] {bot.account_display_name(acc, i)} (ID: {bot.account_id(acc)})")

        account_errors = {bot.account_id(acc): 0 for acc in accounts}
        consecutive_errors = 0
        acc_index = 0
        jobs_done = 0
        total_earned = 0

        for i in range(self.jobs_target):
            if not self.running or consecutive_errors >= self.max_errors:
                break

            attempts = 0
            while attempts < len(accounts):
                cur = accounts[acc_index]
                acc_id = bot.account_id(cur)
                if account_errors.get(acc_id, 0) < 3:
                    break
                acc_index = (acc_index + 1) % len(accounts)
                attempts += 1
            else:
                safe_print(f"{Colors.RED}Tất cả tài khoản lỗi >3 lần, dừng.{Colors.RESET}")
                break

            cur_acc = accounts[acc_index]
            acc_id = bot.account_id(cur_acc)
            acc_name = bot.account_display_name(cur_acc, acc_index)

            # Gọi get_job với account_id
            job_json = bot.get_job(account_id=acc_id)
            job_data = job_json.get('data') if job_json and job_json.get('status') == 200 else None

            if not job_data:
                msg = job_json.get('message', 'Unknown') if job_json else 'No response'
                safe_print(f"{Colors.RED}[{i+1}/{self.jobs_target}] [{acc_name}] No job: {msg}. Switching...{Colors.RESET}")
                account_errors[acc_id] = account_errors.get(acc_id, 0) + 1
                consecutive_errors += 1
                acc_index = (acc_index + 1) % len(accounts)
                countdown(2, "Switching")
                continue

            job_type = job_data.get('type', 'unknown')
            link = job_data.get('link', '')
            object_id = job_data.get('object_id', '')
            ads_id = job_data.get('id', '')

            safe_print(f"{Colors.CYAN}[{i+1}/{self.jobs_target}] [{acc_name}] {job_type.upper()} | {link[:35]}...{Colors.RESET}")
            countdown(10, "Processing")

            success = False
            for attempt in range(3):
                try:
                    complete_json = bot.complete_job(ads_id=ads_id, account_id=int(acc_id), job_data=job_data)
                    if complete_json and (complete_json.get('success') or complete_json.get('status') == 200):
                        success = True
                        earned = complete_json.get('data', {}).get('prices', 0)
                        total_earned += earned
                        self.stats['total_earned'] += earned
                        self.stats['jobs_done'] += 1
                        account_errors[acc_id] = 0
                        consecutive_errors = 0
                        safe_print(f"{Colors.BOLD_GREEN}+{earned} VND | Tổng: {self.stats['total_earned']}{Colors.RESET}")
                        break
                except Exception:
                    pass
                if attempt < 2:
                    safe_print(f"{Colors.YELLOW}Thử lại lần {attempt+2}/3...{Colors.RESET}")
                    countdown(3, "Retry")

            if not success:
                safe_print(f"{Colors.RED}Failed sau 3 lần! Switching...{Colors.RESET}")
                account_errors[acc_id] = account_errors.get(acc_id, 0) + 1
                consecutive_errors += 1
                try:
                    bot.skip_job(ads_id=ads_id, object_id=object_id, account_id=int(acc_id))
                except Exception:
                    pass

            acc_index = (acc_index + 1) % len(accounts)
            if self.delay_sec > 10:
                countdown(self.delay_sec - 10, "Delay")
            elif self.delay_sec > 0:
                time.sleep(self.delay_sec)

        safe_print(f"{Colors.BOLD_GREEN}{platform_name} hoàn thành: {jobs_done} jobs | +{total_earned} VND{Colors.RESET}")
        return jobs_done

    def run(self, only_platform: Optional[str] = None):
        if not self.show_profile():
            return
        while self.running:
            for platform_name, _ in ALL_PROVIDERS:
                if not self.running: break
                if only_platform and platform_name.lower() != only_platform.lower(): continue
                safe_print(f"\n{Colors.BOLD_MAGENTA}>>> {platform_name} <<<{Colors.RESET}")
                self.run_platform(platform_name)
                if only_platform:
                    return
                if self.running:
                    time.sleep(5)

# ============================================================================
# Multi-worker (dùng nhiều token từ au.txt)
# ============================================================================
FILE_AUTH = 'au.txt'

class WorkerThread(threading.Thread):
    def __init__(self, auth: GolikeAuth, worker_id: int, stats_queue: queue.Queue):
        super().__init__(daemon=True)
        self.auth = auth
        self.worker_id = worker_id
        self.stats_queue = stats_queue
        self.running = True
        self.stats = {
            'username': auth.username,
            'user_id': auth.user_id,
            'coin': 0,
            'status': 'active',
            'total_earned': 0,
            'jobs_done': 0,
        }
        self.max_errors = CONFIG['dung_sau_loi']
        self.delay_sec = CONFIG['delay_giay']
        self.jobs_target = CONFIG['so_luong_job']

    def update_user_info(self):
        try:
            resp = debug_get(self.auth, "/users/me")
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                self.stats['username'] = data.get('username', self.auth.username)
                self.stats['coin'] = data.get('coin', 0)
                self.stats['status'] = 'active'
                return True
            self.stats['status'] = 'invalid_token'
            return False
        except Exception:
            self.stats['status'] = 'error'
            return False

    def run_platform(self, platform_name: str, bot_class):
        bot = bot_class(self.auth)
        accs = bot.get_accounts()
        if not accs or accs.get('status') != 200:
            return
        accounts = accs.get('data', [])
        if not accounts:
            return
        account_errors = {bot.account_id(acc): 0 for acc in accounts}
        consecutive_errors = 0
        acc_index = 0
        jobs_done = 0
        total_earned = 0

        for i in range(self.jobs_target):
            if not self.running or consecutive_errors >= self.max_errors:
                break
            attempts = 0
            while attempts < len(accounts):
                cur = accounts[acc_index]
                acc_id = bot.account_id(cur)
                if account_errors.get(acc_id, 0) < 3:
                    break
                acc_index = (acc_index + 1) % len(accounts)
                attempts += 1
            else:
                break
            cur_acc = accounts[acc_index]
            acc_id = bot.account_id(cur_acc)
            acc_name = bot.account_display_name(cur_acc, acc_index)

            job_json = bot.get_job(account_id=acc_id)
            job_data = job_json.get('data') if job_json and job_json.get('status') == 200 else None

            if not job_data:
                account_errors[acc_id] = account_errors.get(acc_id, 0) + 1
                consecutive_errors += 1
                acc_index = (acc_index + 1) % len(accounts)
                countdown(2, "Switching")
                continue

            job_type = job_data.get('type', 'unknown')
            link = job_data.get('link', '')
            object_id = job_data.get('object_id', '')
            ads_id = job_data.get('id', '')
            safe_print(f"{Colors.CYAN}[W{self.worker_id}] {job_type.upper()} | {link[:30]}...{Colors.RESET}")
            countdown(10, "Processing")

            success = False
            for attempt in range(3):
                try:
                    complete_json = bot.complete_job(ads_id=ads_id, account_id=int(acc_id), job_data=job_data)
                    if complete_json and (complete_json.get('success') or complete_json.get('status') == 200):
                        success = True
                        earned = complete_json.get('data', {}).get('prices', 0)
                        total_earned += earned
                        self.stats['total_earned'] += earned
                        self.stats['jobs_done'] += 1
                        account_errors[acc_id] = 0
                        consecutive_errors = 0
                        break
                except Exception:
                    pass
                if attempt < 2:
                    countdown(3, "Retry")
            if not success:
                account_errors[acc_id] = account_errors.get(acc_id, 0) + 1
                consecutive_errors += 1
                try:
                    bot.skip_job(ads_id=ads_id, object_id=object_id, account_id=int(acc_id))
                except Exception:
                    pass
            acc_index = (acc_index + 1) % len(accounts)
            if self.delay_sec > 10:
                countdown(self.delay_sec - 10, "Delay")
            elif self.delay_sec > 0:
                time.sleep(self.delay_sec)

        safe_print(f"{Colors.GREEN}[W{self.worker_id}] {platform_name} done: {jobs_done} jobs, +{total_earned} VND{Colors.RESET}")

    def run(self):
        self.update_user_info()
        while self.running:
            for platform_name, bot_class in ALL_PROVIDERS:
                if not self.running:
                    break
                safe_print(f"{Colors.BOLD_MAGENTA}[W{self.worker_id}] >>> {platform_name} <<<{Colors.RESET}")
                self.run_platform(platform_name, bot_class)
                self.update_user_info()
                self.stats_queue.put((self.worker_id, self.stats.copy()))
                if self.running:
                    time.sleep(5)

    def stop(self):
        self.running = False

# ============================================================================
# Controller multi
# ============================================================================
class JobaoController:
    def __init__(self):
        self.workers = []
        self.stats_queue = queue.Queue()
        self.running = True
        self.webhook_url = get_webhook()
        self.message_id = None

    def load_tokens(self) -> List[str]:
        if not os.path.exists(FILE_AUTH):
            return []
        tokens = []
        with open(FILE_AUTH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    tokens.append(line)
        return tokens

    def start_workers(self):
        tokens = self.load_tokens()
        if not tokens:
            safe_print(f"{Colors.RED}File {FILE_AUTH} không có token nào.{Colors.RESET}")
            return
        for idx, token in enumerate(tokens):
            try:
                auth = create_auth_from_token(token)
                w = WorkerThread(auth, idx+1, self.stats_queue)
                w.start()
                self.workers.append(w)
                time.sleep(1)
            except Exception as e:
                safe_print(f"{Colors.RED}Worker {idx+1} lỗi: {e}{Colors.RESET}")

    def send_webhook_report(self, stats_dict):
        if not self.webhook_url or not stats_dict:
            return
        total_earned = sum(s.get('total_earned', 0) for s in stats_dict.values())
        total_coin = sum(s.get('coin', 0) for s in stats_dict.values())
        jobs = sum(s.get('jobs_done', 0) for s in stats_dict.values())
        desc = "\n".join([f"W{wid}: {s['username']} - {s['status']} - Earned: {s['total_earned']}" for wid, s in stats_dict.items()])
        payload = {
            "content": None,
            "embeds": [{
                "title": "📊 Golike Multi Status",
                "description": desc[:4000],
                "color": 5814783,
                "fields": [
                    {"name": "Total Earned", "value": f"{total_earned} VND", "inline": True},
                    {"name": "Total Coin", "value": f"{total_coin}", "inline": True},
                    {"name": "Jobs Done", "value": f"{jobs}", "inline": True},
                ],
                "footer": {"text": datetime.now().strftime("%H:%M:%S")}
            }]
        }
        try:
            if self.message_id:
                url = f"{self.webhook_url}/messages/{self.message_id}"
                resp = requests.patch(url, json=payload)
                if resp.status_code not in (200, 204):
                    resp = requests.post(self.webhook_url, json=payload)
                    if resp.status_code == 200:
                        self.message_id = resp.json().get('id')
            else:
                resp = requests.post(self.webhook_url, json=payload)
                if resp.status_code == 200:
                    self.message_id = resp.json().get('id')
        except Exception as e:
            safe_print(f"{Colors.RED}Webhook error: {e}{Colors.RESET}")

    def monitor_loop(self):
        last_report = 0
        while self.running:
            time.sleep(10)
            stats = {}
            while not self.stats_queue.empty():
                wid, s = self.stats_queue.get_nowait()
                stats[wid] = s
            now = time.time()
            if now - last_report >= 600 and stats:
                self.send_webhook_report(stats)
                last_report = now

    def run(self):
        show_banner()
        self.start_workers()
        if not self.workers:
            return
        monitor = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            safe_print(f"\n{Colors.YELLOW}Shutting down...{Colors.RESET}")
            for w in self.workers:
                w.stop()
            for w in self.workers:
                w.join(timeout=3)
            stats = {}
            while not self.stats_queue.empty():
                wid, s = self.stats_queue.get_nowait()
                stats[wid] = s
            self.send_webhook_report(stats)

# ============================================================================
# Headless run
# ============================================================================
def run_headless(platform_arg: str) -> int:
    show_banner()
    auth = get_auth_from_config()
    if auth is None:
        safe_print(f"{Colors.RED}Chưa có token hợp lệ trong config.json.{Colors.RESET}")
        safe_print(f"{Colors.YELLOW}Chạy `python main.py` để nhập token trước.{Colors.RESET}")
        return 1
    only_platform = None if platform_arg.lower() == "all" else platform_arg
    runner = SingleAccountRunner(auth)
    runner.run(only_platform=only_platform)
    return 0

# ============================================================================
# Menu
# ============================================================================
def configure_debug():
    current = is_debug_enabled()
    safe_print(f"\nDebug hiện tại: {'BẬT' if current else 'TẮT'}")
    if ask("Bật debug? (y/N)", "n").lower() == "y":
        set_field("debug", True)
        safe_print(f"{Colors.GREEN}Đã bật debug.{Colors.RESET}")
    else:
        set_field("debug", False)
        safe_print(f"{Colors.YELLOW}Đã tắt debug.{Colors.RESET}")

def configure_jobs():
    while True:
        safe_print(f"\n{Colors.BOLD_WHITE}Job settings:{Colors.RESET}")
        safe_print(f"  so_luong_job = {CONFIG['so_luong_job']}")
        safe_print(f"  delay_giay   = {CONFIG['delay_giay']}")
        safe_print(f"  dung_sau_loi = {CONFIG['dung_sau_loi']}")
        idx = ask_choice("Chỉnh:", [
            f"Số job (hiện {CONFIG['so_luong_job']})",
            f"Delay (hiện {CONFIG['delay_giay']})",
            f"Max lỗi (hiện {CONFIG['dung_sau_loi']})",
            "Quay lại"
        ])
        if idx in (-1, 3): break
        if idx == 0:
            v = ask("Số job", str(CONFIG['so_luong_job']))
            try: set_field('so_luong_job', max(1, int(v)))
            except: pass
        elif idx == 1:
            v = ask("Delay (s)", str(CONFIG['delay_giay']))
            try: set_field('delay_giay', max(0, int(v)))
            except: pass
        elif idx == 2:
            v = ask("Max lỗi", str(CONFIG['dung_sau_loi']))
            try: set_field('dung_sau_loi', max(1, int(v)))
            except: pass

def configure_webhook():
    current = get_webhook()
    safe_print(f"\nWebhook hiện tại: {mask(current, 16)}")
    idx = ask_choice("Webhook:", ["Đặt URL mới", "Tắt (xóa)", "Test gửi", "Quay lại"])
    if idx in (-1, 3): return
    if idx == 0:
        url = ask("URL", current)
        set_field('webhook_url', url.strip())
    elif idx == 1:
        set_field('webhook_url', '')
    elif idx == 2:
        if not current:
            safe_print(f"{Colors.RED}Chưa có URL.{Colors.RESET}")
        else:
            try:
                r = requests.post(current, json={"content": "Test"})
                safe_print(f"{Colors.GREEN}OK {r.status_code}{Colors.RESET}" if r.status_code in (200,204) else f"{Colors.RED}Lỗi {r.status_code}{Colors.RESET}")
            except Exception as e:
                safe_print(f"{Colors.RED}{e}{Colors.RESET}")

def configure_auth():
    safe_print(f"\nToken hiện tại: {mask(CONFIG.get('token',''))}")
    if ask("Đổi token? (y/N)", "n").lower() == "y":
        auth = prompt_auth()
        CONFIG["token"] = auth.token
        CONFIG["username"] = auth.username
        CONFIG["user_id"] = auth.user_id
        save_config(CONFIG)
        safe_print(f"{Colors.GREEN}Đã cập nhật token.{Colors.RESET}")

def main_menu(auth: GolikeAuth):
    while True:
        idx = ask_choice("Chọn:", [
            "Chạy 1 account (single)",
            "Chạy multi từ au.txt",
            "Xem profile",
            "Liệt kê accounts",
            "Cấu hình"
        ], allow_back=False)
        if idx == 0:
            runner = SingleAccountRunner(auth)
            p = ask_choice("Platform:", [name for name,_ in ALL_PROVIDERS] + ["Tất cả"])
            if p == -1: continue
            if p == len(ALL_PROVIDERS):
                runner.run()
            else:
                runner.run(only_platform=ALL_PROVIDERS[p][0])
        elif idx == 1:
            JobaoController().run()
        elif idx == 2:
            SingleAccountRunner(auth).show_profile()
        elif idx == 3:
            SingleAccountRunner(auth).list_accounts()
        elif idx == 4:
            c = ask_choice("Cấu hình:", ["GolikeAuth (token)", "Webhook", "Debug", "Job settings", "Quay lại"])
            if c == 0: configure_auth()
            elif c == 1: configure_webhook()
            elif c == 2: configure_debug()
            elif c == 3: configure_jobs()

# ============================================================================
# Main
# ============================================================================
def main():
    args = argparse.ArgumentParser()
    args.add_argument("--run", help="all hoặc platform")
    parsed = args.parse_args()
    if parsed.run:
        sys.exit(run_headless(parsed.run))
    show_banner()
    auth = get_auth_from_config()
    if auth is None:
        safe_print(f"{Colors.YELLOW}Chưa có token, nhập ngay.{Colors.RESET}")
        auth = prompt_auth()
    main_menu(auth)

if __name__ == "__main__":
    main()
