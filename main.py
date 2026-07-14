import os
import sys
import time
import json
import uuid
import queue
import base64
import hashlib
import secrets
import threading
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

try:
    from curl_cffi import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "curl_cffi"])
    from curl_cffi import requests

salt = "glk-gauth-v3-2026q3"
info = "aes-gcm-key"
client = "109096667105508"
version = "26.07.10.2"
url = "https://gateway.golike.net/api"
agent = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"
regex = hashlib.re.compile(r"^[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+$") if hasattr(hashlib, "re") else __import__("re").compile(r"^[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+$")
lock = threading.Lock()
path = "config.json"
txt = "au.txt"

class color:
    reset = '\033[0m'
    bold = '\033[1m'
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    blue = '\033[34m'
    cyan = '\033[36m'
    white = '\033[37m'
    magenta = '\033[35m'

default = {
    "token": "",
    "signing_key": "",
    "user_id": 0,
    "username": "",
    "password": "",
    "device_id": "",
    "webhook_url": "",
    "so_luong_job": 1000,
    "delay_giay": 5,
    "dung_sau_loi": 5,
}

def say(*args, **kwargs):
    with lock:
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass
        print(*args, **kwargs)


def banner():
    os.system("cls" if os.name == "nt" else "clear")
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    data = f"""
{color.cyan}╔════════════════════════════════════════════════════════════════════════╗
{color.cyan}║{color.white}                       ⛃  BÉ TẬP CODE TOOL  ⛃                        {color.cyan}║
{color.cyan}╠════════════════════════════════════════════════════════════════════════╣
{color.cyan}║ {color.yellow}⛃  TOOL BY       {color.white}: ThanhBinh Tool                                     {color.cyan}║
{color.cyan}║ {color.yellow}⛃  VERSION       {color.white}: Professional v1.0                    {color.cyan}║
{color.cyan}║ {color.yellow}⛃  DATE          {color.white}: {now}                             {color.cyan}║
{color.cyan}╚════════════════════════════════════════════════════════════════════════╝{color.reset}
"""
    say(data)

def wait(seconds: int, msg: str = "Waiting"):
    for remaining in range(seconds, -1, -1):
        with lock:
            sys.stdout.write(f"\r{color.cyan}[{msg}] {color.yellow}{remaining}s... {color.reset}")
            sys.stdout.flush()
        time.sleep(1)
    with lock:
        print("\r" + " " * 60 + "\r", end="")

def ask(prompt: str, defaultval: str = "") -> str:
    suffix = f" [{defaultval}]" if defaultval else ""
    try:
        val = input(f"{color.cyan}{prompt}{suffix}: {color.reset}").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return val or defaultval

def choice(prompt: str, options, allow: bool = True) -> int:
    say(f"\n{color.white}{prompt}{color.reset}")
    for i, label in enumerate(options, start=1):
        say(f"  {color.cyan}{i}{color.reset}. {label}")
    if allow:
        say(f"  {color.cyan}0{color.reset}. {color.yellow}← Quay lại{color.reset}")
    while True:
        raw = ask("Chọn", "0" if allow else "1")
        try:
            n = int(raw)
        except ValueError:
            say(f"{color.red}Vui lòng nhập số.{color.reset}")
            continue
        if allow and n == 0:
            return -1
        if 1 <= n <= len(options):
            return n - 1
        say(f"{color.red}Lựa chọn không hợp lệ.{color.reset}")

def mask(s: str, keep: int = 8) -> str:
    if not s:
        return f"{color.yellow}(rỗng){color.reset}"
    if len(s) <= keep * 2:
        return s[:4] + "..." + s[-4:]
    return s[:keep] + "..." + s[-keep:]

def init():
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default.copy(), f, indent=4, ensure_ascii=False)

def load():
    init()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        legacy = {"auth_token", "t_token"}
        if legacy & set(data.keys()):
            data = default.copy()
            save(data)
            return data
        updated = False
        for k, v in default.items():
            if k not in data:
                data[k] = v
                updated = True
        if updated:
            save(data)
        return data
    except Exception:
        save(default.copy())
        return default.copy()

def save(data: dict):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

config = load()

def put(key: str, val, data: dict = None):
    cfg = data if data is not None else config
    cfg[key] = val
    save(cfg)
    return cfg

def check(data: dict = None) -> bool:
    cfg = data if data is not None else config
    token = (cfg.get("token") or "").strip()
    sk = (cfg.get("signing_key") or "").strip()
    try:
        uid = int(cfg.get("user_id") or 0)
    except (TypeError, ValueError):
        uid = 0
    return bool(token) and bool(sk) and uid > 0

def webhook(data: dict = None) -> str:
    cfg = data if data is not None else config
    return (cfg.get("webhook_url") or "").strip()

def encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.replace("-", "+").replace("_", "/") + pad)

def btoa(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")

def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def device() -> str:
    return str(uuid.uuid4())

def nonce() -> str:
    return encode(secrets.token_bytes(16))

def parse(raw: str) -> bytes:
    if not raw:
        raise ValueError("signing_key rỗng")
    raw = raw.strip()
    s = raw
    hexs = (
        len(s) == 64
        and all(c in "0123456789abcdefABCDEF" for c in s)
    )
    if hexs:
        try:
            res = bytes.fromhex(s)
            if len(res) == 32:
                return res
        except ValueError:
            pass
    try:
        res = base64.b64decode(s, validate=False)
        if len(res) == 32:
            return res
    except Exception:
        pass
    try:
        pad = "=" * (-len(s) % 4)
        res = base64.urlsafe_b64decode(s + pad)
        if len(res) == 32:
            return res
    except Exception:
        pass
    raise ValueError("signing_key không decode ra được 32 bytes.")

def derive(raw: str) -> bytes:
    ikm = parse(raw)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode("utf-8"),
        info=info.encode("utf-8"),
    ).derive(ikm)

def route(p: str, prefix: str = "/api") -> str:
    p = p.split("?", 1)[0].split("#", 1)[0]
    val = p.lstrip("/")
    if prefix and not val.startswith(prefix.strip("/") + "/") and val != prefix.strip("/"):
        val = f"{prefix.strip('/')}/{val}" if val else prefix
    return "/" + val

def body(b) -> str:
    if b is None:
        return ""
    if isinstance(b, str):
        return b
    if isinstance(b, (bytes, bytearray)):
        try:
            return bytes(b).decode("utf-8")
        except UnicodeDecodeError:
            return bytes(b).decode("utf-8", errors="replace")
    return json.dumps(b, separators=(",", ":"), ensure_ascii=False)

def payload(method: str, p: str, b: str, dev: str, uid: int, ts: Optional[int] = None, val: Optional[str] = None) -> dict:
    t = ts if ts is not None else int(time.time() * 1000)
    x = val if val is not None else nonce()
    n = method.upper()
    k = route(p)
    q = sha(b)
    r = sha(f"{t}:{dev}:{q}:{salt}")[:16]
    return {"t": t, "x": x, "d": dev, "u": uid, "n": n, "k": k, "q": q, "r": r}

def encrypt(method: str, p: str, b, raw: str, dev: str, uid: int) -> str:
    key = derive(raw)
    data = body(b)
    pay = payload(method, p, data, dev, uid)
    pt = json.dumps(pay, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    iv = secrets.token_bytes(12)
    ct = AESGCM(key).encrypt(iv, pt, None)
    return encode(iv + ct)

def decrypt(token: str, raw: str) -> dict:
    key = derive(raw)
    data = decode(token)
    iv, ct = data[:12], data[12:]
    pt = AESGCM(key).decrypt(iv, ct, None)
    return json.loads(pt.decode("utf-8"))

def header(ts: Optional[int] = None) -> str:
    val = ts if ts is not None else int(time.time())
    once = btoa(str(val).encode("ascii"))
    twice = btoa(once.encode("ascii"))
    thrice = btoa(twice.encode("ascii"))
    return thrice

def login(user: str, pwd: str) -> dict:
    try:
        body = {"username": user, "password": pwd}
        hd = {
            "content-type": "application/json;charset=utf-8",
            "accept": "application/json",
            "user-agent": agent
        }
        resp = requests.post(f"{url}/auto/login", json=body, headers=hd, impersonate="chrome")
        res = resp.json()
        if res and res.get("success") is True:
            sec = res.get("security", {})
            info = res.get("data", {})
            return {
                "ok": True,
                "token": res.get("token"),
                "key": sec.get("signing_key"),
                "device": sec.get("device_id"),
                "id": int(info.get("id") or 0),
                "name": info.get("username"),
            }
        return {"ok": False, "msg": res.get("message") or "Sai tài khoản hoặc mật khẩu"}
    except Exception as e:
        return {"ok": False, "msg": str(e)}

class Auth:
    def __init__(self, token: str, key: str, uid: int, user: str, dev: str):
        self.token = token
        self.key = key
        self.uid = uid
        self.user = user
        self.dev = dev
        if not self.token:
            raise ValueError("Token rỗng")
        if not regex.match(self.token.strip()):
            raise ValueError("Token không hợp lệ")
        if not self.key:
            raise ValueError("Key rỗng")
        parse(self.key)
        if not isinstance(self.uid, int) or self.uid <= 0:
            raise ValueError("Uid không hợp lệ")
        if not self.user:
            raise ValueError("User rỗng")
        if not self.dev:
            self.dev = device()

    def headers(self, method: str, p: str, b=None) -> dict:
        data = body(b) if b is not None else ""
        gauth = encrypt(method, p, data, self.key, self.dev, self.uid)
        return {
            "accept": "application/json, text/plain, */*",
            "accept-language": "vi,en-US;q=0.9,en;q=0.8",
            "authorization": f"Bearer {self.token}",
            "t": header(),
            "g-auth": gauth,
            "g-device-id": self.dev,
            "g-username": self.user,
            "g-version": version,
            "g-client": client,
            "content-type": "application/json;charset=utf-8",
            "origin": "https://app.golike.net",
            "referer": "https://app.golike.net/",
            "user-agent": agent,
            "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }

    def refresh(self) -> bool:
        user = config.get("username") or ""
        pwd = config.get("password") or ""
        if not user or not pwd:
            return False
        res = login(user, pwd)
        if res.get("ok"):
            self.token = res.get("token")
            self.key = res.get("key")
            self.uid = res.get("id")
            self.user = res.get("name")
            self.dev = res.get("device")
            self.store()
            return True
        return False

    def request(self, method: str, p: str, params=None, body=None) -> dict:
        try:
            uri = p
            if params:
                uri = f"{p}?{urlencode(params)}"
            target = f"{url}{uri}"
            method = method.upper()
            hd = self.headers(method, p, body)
            if body is not None:
                data = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
                resp = requests.request(method, target, headers=hd, data=data.encode("utf-8"), impersonate="chrome")
            else:
                resp = requests.request(method, target, headers=hd, impersonate="chrome")
            res = resp.json()
            code = res.get("status") or res.get("code")
            msg = str(res.get("message") or res.get("error") or "")
            expired = (
                resp.status_code in (401, 403) or
                code in (401, 403) or
                "phien ban" in msg.lower() or
                "phiên bản" in msg.lower() or
                "chữ ký" in msg.lower() or
                "signing" in msg.lower()
            )
            if expired:
                say(f"{color.yellow}  Phát hiện token/key hết hạn hoặc lỗi chữ ký! Đang tự động đăng nhập lại...{color.reset}")
                if self.refresh():
                    say(f"{color.green}  Đăng nhập lại thành công! Thử lại tác vụ...{color.reset}")
                    hd = self.headers(method, p, body)
                    if body is not None:
                        resp = requests.request(method, target, headers=hd, data=data.encode("utf-8"), impersonate="chrome")
                    else:
                        resp = requests.request(method, target, headers=hd, impersonate="chrome")
                    res = resp.json()
                else:
                    say(f"{color.red}  Đăng nhập lại thất bại!{color.reset}")
            return res
        except Exception as e:
            say(f"{method.upper()} {p} error: {e}")
            return None

    def get(self, p: str, params=None) -> dict:
        return self.request("GET", p, params=params)

    def post(self, p: str, body: dict = None) -> dict:
        return self.request("POST", p, body=body or {})

    def verify(self) -> dict:
        try:
            data = json.dumps({"ping": 1}, separators=(",", ":"))
            hd = self.headers("POST", "/security/echo", data)
            last = None
            res = None
            for imp in ("chrome120", "chrome110", "chrome"):
                try:
                    resp = requests.post(f"{url}/security/echo", headers=hd, data=data.encode("utf-8"), impersonate=imp, timeout=30)
                    res = resp.json()
                    break
                except Exception as e:
                    last = e
            if res is None:
                return {"ok": False, "errors": [str(last)]}
            code = res.get("code") or res.get("status")
            msg = str(res.get("message") or res.get("error") or "")
            if code == 429 or "429" in msg or "qua nhanh" in msg.lower():
                return {"ok": False, "errors": ["rate_limit_429"], "message": "Rate limit"}
            g = (res.get("data") or {}).get("gauth") if isinstance(res.get("data"), dict) else {}
            g = g or {}
            errs = list(g.get("errors") or [])
            decoded = g.get("decoded")
            fail = any("decrypt" in str(e).lower() for e in errs)
            if decoded is not None and not fail:
                return {"ok": True, "errors": errs, "decoded": decoded}
            if fail or (g.get("header_present") and decoded is None and errs):
                return {"ok": False, "errors": errs or ["decrypt_fail"]}
            return {"ok": False, "errors": errs or ["no_gauth_in_response"]}
        except Exception as e:
            return {"ok": False, "errors": [str(e)]}

    def put(self, p: str, body: dict = None) -> dict:
        return self.request("PUT", p, body=body or {})

    def patch(self, p: str, body: dict = None) -> dict:
        return self.request("PATCH", p, body=body or {})

    def delete(self, p: str) -> dict:
        return self.request("DELETE", p)

    def dump(self) -> dict:
        return {"token": self.token, "signing_key": self.key, "user_id": self.uid, "username": self.user, "device_id": self.dev}

    def store(self) -> None:
        for k, v in self.dump().items():
            put(k, v)

class Bot:
    def __init__(self, auth: Auth, platform: str):
        self.auth = auth
        self.platform = platform

    def accounts(self) -> Optional[Dict[str, Any]]:
        return self.auth.get(f"/{self.platform}-account")

    def job(self, acc: str) -> Optional[Dict[str, Any]]:
        return self.auth.get(f"/advertising/publishers/{self.platform}/jobs", params={"account_id": acc, "data": "null"})

    def done(self, ads: str, acc: str) -> Optional[Dict[str, Any]]:
        pay = {"ads_id": ads, "account_id": acc, "async": True, "data": None}
        return self.auth.post(f"/advertising/publishers/{self.platform}/complete-jobs", body=pay)

    def skip(self, ads: str, acc: str, obj: str):
        pay = {"ads_id": ads, "account_id": acc, "object_id": obj}
        try:
            self.auth.post(f"/advertising/publishers/{self.platform}/skip-jobs", body=pay)
        except Exception:
            pass

    def name(self, acc: Dict[str, Any], idx: int) -> str:
        return acc.get('name') or acc.get('username') or acc.get('screen_name') or f"Account {idx}"

    def id(self, acc: Dict[str, Any]) -> str:
        return str(acc.get('id', 'N/A'))

platforms = ["twitter", "linkedin", "threads", "pinterest", "snapchat"]

class Runner:
    def __init__(self, auth: Auth):
        self.auth = auth
        self.active = True
        self.stats = {
            'username': auth.user,
            'user_id': auth.uid,
            'coin': 0,
            'total_earned': 0,
            'jobs_done': 0,
        }
        self.max = config['dung_sau_loi']
        self.delay = config['delay_giay']
        self.target = config['so_luong_job']

    def profile(self) -> bool:
        try:
            resp = self.auth.get("/users/me")
            if resp and resp.get('status') == 200:
                data = resp['data']
                self.stats['username'] = data.get('username', data.get('name', self.auth.user))
                self.stats['coin'] = data.get('coin', 0)
                say(f"\n{color.green}{'='*60}{color.reset}")
                say(f"  Username : {color.white}{self.stats['username']}{color.reset}")
                say(f"  User ID  : {color.white}{self.auth.uid}{color.reset}")
                say(f"  Device   : {color.white}{self.auth.dev}{color.reset}")
                say(f"  Coin     : {color.yellow}{self.stats['coin']}{color.reset}")
                say(f"{color.green}{'='*60}{color.reset}\n")
                say(f"{color.cyan}  Dang kiem tra signing_key (g-auth)...{color.reset}")
                v = self.auth.verify()
                if not v.get("ok"):
                    say(f"{color.red}  signing_key SAI / het han (server decrypt_fail){color.reset}")
                    return False
                say(f"{color.green}  signing_key OK (server decrypt duoc g-auth){color.reset}\n")
                return True
            say(f"{color.red}Token không hợp lệ!{color.reset}")
            return False
        except Exception as e:
            say(f"{color.red}Lỗi khi lấy profile: {e}{color.reset}")
            return False

    def coin(self):
        try:
            resp = self.auth.get("/users/me")
            if resp and resp.get('status') == 200:
                self.stats['coin'] = resp['data'].get('coin', 0)
        except Exception:
            pass

    def list(self, plat: Optional[str] = None):
        targets = [plat] if plat else platforms
        for name in targets:
            bot = Bot(self.auth, name)
            resp = bot.accounts()
            say(f"\n{color.cyan}── {name.upper()} ──{color.reset}")
            if not resp or resp.get('status') != 200:
                continue
            accounts = resp.get('data', []) or []
            if not accounts:
                say(f"{color.yellow}  (rỗng){color.reset}")
                continue
            for i, acc in enumerate(accounts):
                accname = bot.name(acc, i)
                accid = bot.id(acc)
                say(f"  [{i}] {accname}  {color.cyan}(ID: {accid}){color.reset}")

    def run(self, name: str) -> int:
        bot = Bot(self.auth, name)
        resp = bot.accounts()
        if not resp or resp.get('status') != 200:
            say(f"{color.red}Không thể lấy danh sách tài khoản {name}!{color.reset}")
            return 0
        accounts = resp.get('data', []) or []
        if not accounts:
            say(f"{color.red}Không có tài khoản {name} nào!{color.reset}")
            return 0
        say(f"\n{color.green}{name.upper()}: Tìm thấy {len(accounts)} tài khoản{color.reset}")
        for i, acc in enumerate(accounts):
            say(f"  [{i}] {bot.name(acc, i)} (ID: {bot.id(acc)})")
        say(f"\n{color.green}Bắt đầu chạy {self.target} jobs trên {name}...{color.reset}")
        say(f"{color.cyan}{'='*60}{color.reset}")

        errors = {bot.id(acc): 0 for acc in accounts}
        fails = 0
        idx = 0
        done = 0
        earned = 0

        for i in range(self.target):
            if not self.active:
                break
            if fails >= self.max:
                break
            attempts = 0
            while attempts < len(accounts):
                current = accounts[idx]
                accid = bot.id(current)
                if errors.get(accid, 0) < 3:
                    break
                idx = (idx + 1) % len(accounts)
                attempts += 1
            else:
                break
            current = accounts[idx]
            accid = bot.id(current)
            accname = bot.name(current, idx)
            jobresp = bot.job(accid)
            if not jobresp or jobresp.get('status') != 200:
                errors[accid] = errors.get(accid, 0) + 1
                fails += 1
                idx = (idx + 1) % len(accounts)
                wait(2, "Switching")
                continue
            jobdata = jobresp['data']
            jobtype = jobdata.get('type', 'unknown')
            link = jobdata.get('link', '')
            obj = jobdata.get('object_id', '')
            ads = jobdata.get('id', '')
            say(f"{color.cyan}[{i+1}/{self.target}] [{accname}] {jobtype.upper()} | {link[:35]}...{color.reset}")
            wait(10, "Processing")
            success = False
            for attempt in range(3):
                complete = bot.done(ads, accid)
                if complete and (complete.get('success') or complete.get('status') == 200):
                    success = True
                    done += 1
                    price = complete.get('data', {}).get('prices', 0)
                    earned += price
                    self.stats['total_earned'] += price
                    self.stats['jobs_done'] += 1
                    errors[accid] = 0
                    fails = 0
                    now = datetime.now().strftime("%H:%M:%S")
                    say(
                        f"{color.red}| {color.cyan}{self.stats['jobs_done']}{color.red} | "
                        f"{color.yellow}{now}{color.red} | "
                        f"{color.green}SUCCESS{color.red} | "
                        f"{color.blue}{name.upper()}:{jobtype}{color.red} | "
                        f"{color.green}+{price}{color.red} | "
                        f"{color.yellow}{self.stats['total_earned']} VND{color.reset}"
                    )
                    break
                else:
                    if attempt < 2:
                        wait(3, "Retry")
            if not success:
                errors[accid] = errors.get(accid, 0) + 1
                fails += 1
                bot.skip(ads, accid, obj)
            idx = (idx + 1) % len(accounts)
            if self.delay > 10:
                wait(self.delay - 10, "Delay")
            elif self.delay > 0:
                time.sleep(self.delay)
        return done

    def scan(self) -> List[str]:
        active = []
        for name in platforms:
            bot = Bot(self.auth, name)
            resp = bot.accounts()
            if resp and resp.get('status') == 200:
                accounts = resp.get('data', []) or []
                if accounts:
                    active.append(name)
        return active

    def start(self, plat: Optional[str] = None):
        if not self.profile():
            return
        say(f"{color.cyan}  Đang kiểm tra liên kết các mạng xã hội...{color.reset}")
        active = [plat] if plat else self.scan()
        if not active:
            say(f"{color.red}Không tìm thấy tài khoản mạng xã hội nào được liên kết!{color.reset}")
            return
        say(f"{color.green}Tìm thấy các platform hoạt động: {', '.join([p.upper() for p in active])}{color.reset}")
        try:
            while self.active:
                for name in active:
                    if not self.active:
                        break
                    say(f"\n{color.magenta}>>> Chuyển sang {name.upper()} <<<{color.reset}")
                    self.run(name)
                    self.coin()
                    say(f"{color.cyan}  ↳ Coin hiện tại: {self.stats['coin']} | Tổng kiếm: {self.stats['total_earned']} VND{color.reset}")
                    if self.active:
                        time.sleep(5)
        except KeyboardInterrupt:
            pass
        finally:
            say(f"{color.green}Tổng kết: {self.stats['jobs_done']} jobs | {self.stats['total_earned']} VND{color.reset}")

    def stop(self):
        self.active = False

class Worker(threading.Thread):
    def __init__(self, auth: Auth, wid: int, stats: queue.Queue):
        super().__init__(daemon=True)
        self.auth = auth
        self.wid = wid
        self.stats = stats
        self.active = True
        self.info = {
            'auth': auth.user or auth.token[:15] + '...',
            'username': auth.user or 'Unknown',
            'user_id': auth.uid,
            'coin': 0,
            'status': 'initializing',
            'total_earned': 0,
            'jobs_done': 0,
            'last_update': datetime.now(),
        }
        self.max = config['dung_sau_loi']
        self.delay = config['delay_giay']
        self.target = config['so_luong_job']

    def update(self) -> bool:
        try:
            resp = self.auth.get("/users/me")
            if resp and resp.get('status') == 200:
                data = resp['data']
                self.info['username'] = data.get('username', data.get('name', self.auth.user))
                self.info['coin'] = data.get('coin', 0)
                self.info['status'] = 'active'
                return True
            self.info['status'] = 'invalid_token'
            return False
        except Exception as e:
            self.info['status'] = f'error: {str(e)[:20]}'
            return False

    def run_platform(self, name: str):
        bot = Bot(self.auth, name)
        resp = bot.accounts()
        if not resp or resp.get('status') != 200:
            return
        accounts = resp.get('data', []) or []
        if not accounts:
            return
        errors = {bot.id(acc): 0 for acc in accounts}
        fails = 0
        idx = 0
        for i in range(self.target):
            if not self.active:
                break
            if fails >= self.max:
                break
            attempts = 0
            while attempts < len(accounts):
                current = accounts[idx]
                accid = bot.id(current)
                if errors.get(accid, 0) < 3:
                    break
                idx = (idx + 1) % len(accounts)
                attempts += 1
            else:
                break
            current = accounts[idx]
            accid = bot.id(current)
            accname = bot.name(current, idx)
            jobresp = bot.job(accid)
            if not jobresp or jobresp.get('status') != 200:
                errors[accid] = errors.get(accid, 0) + 1
                fails += 1
                idx = (idx + 1) % len(accounts)
                wait(2, "Switching")
                continue
            jobdata = jobresp['data']
            jobtype = jobdata.get('type', 'unknown')
            link = jobdata.get('link', '')
            obj = jobdata.get('object_id', '')
            ads = jobdata.get('id', '')
            say(f"[Worker {self.wid}] [{i+1}/{self.target}] [{accname}] {jobtype.upper()} | {link[:35]}...{color.reset}")
            wait(10, "Processing")
            success = False
            for attempt in range(3):
                complete = bot.done(ads, accid)
                if complete and (complete.get('success') or complete.get('status') == 200):
                    success = True
                    price = complete.get('data', {}).get('prices', 0)
                    self.info['total_earned'] += price
                    self.info['jobs_done'] += 1
                    errors[accid] = 0
                    fails = 0
                    now = datetime.now().strftime("%H:%M:%S")
                    say(
                        f"{color.red}| {color.cyan}{self.info['jobs_done']}{color.red} | "
                        f"{color.yellow}{now}{color.red} | "
                        f"{color.green}SUCCESS{color.red} | "
                        f"{color.blue}{name.upper()}:{jobtype}{color.red} | "
                        f"{color.green}+{price}{color.red} | "
                        f"{color.yellow}{self.info['total_earned']} VND{color.reset}"
                    )
                    break
                else:
                    if attempt < 2:
                        wait(3, "Retry")
            if not success:
                errors[accid] = errors.get(accid, 0) + 1
                fails += 1
                bot.skip(ads, accid, obj)
            idx = (idx + 1) % len(accounts)
            if self.delay > 10:
                wait(self.delay - 10, "Delay")
            elif self.delay > 0:
                time.sleep(self.delay)

    def run(self):
        if not self.update():
            self.info['status'] = 'invalid_token'
            self.push()
            return
        self.push()
        while self.active:
            for name in platforms:
                if not self.active:
                    break
                self.run_platform(name)
                self.update()
                self.push()
                if self.active:
                    time.sleep(5)

    def push(self):
        self.info['last_update'] = datetime.now()
        self.stats.put((self.wid, self.info.copy()))

    def stop(self):
        self.active = False

class Controller:
    def __init__(self):
        self.workers: List[Worker] = []
        self.stats = queue.Queue()
        self.active = True
        self.msgid = None
        self.webhook = webhook()

    def tokens(self) -> List[str]:
        res: List[str] = []
        if not os.path.exists(txt):
            return res
        with open(txt, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    res.append(line)
        return res

    def build(self, token: str) -> Auth:
        return Auth(
            token=token,
            key=config['signing_key'],
            uid=int(config['user_id']),
            user=config['username'],
            dev=config['device_id'],
        )

    def spawn(self):
        toks = self.tokens()
        if not toks:
            return
        for idx, token in enumerate(toks):
            try:
                auth = self.build(token)
            except ValueError:
                continue
            worker = Worker(auth, idx + 1, self.stats)
            worker.start()
            self.workers.append(worker)
            time.sleep(1)

    def data(self) -> Dict[int, Dict]:
        res: Dict[int, Dict] = {}
        while not self.stats.empty():
            try:
                wid, info = self.stats.get_nowait()
                res[wid] = info
            except queue.Empty:
                break
        return res

    def embed(self, stats: Dict[int, Dict]) -> dict:
        total = len(self.workers)
        active = sum(1 for s in stats.values() if s['status'] == 'active')
        dead = total - active
        earned = sum(s['total_earned'] for s in stats.values())
        coin = sum(s['coin'] for s in stats.values())
        done = sum(s['jobs_done'] for s in stats.values())
        lines = []
        for wid, s in stats.items():
            emoji = "🟢" if s['status'] == 'active' else "🔴"
            lines.append(
                f"{emoji} **Worker {wid}** - `{s['username']}`\n"
                f"   Coin: {s['coin']} | Earned: {s['total_earned']} | Jobs: {s['jobs_done']}\n"
                f"   Status: {s['status']}"
            )
        return {
            "title": "📊 Golike Multi-Account Status",
            "description": "\n".join(lines) if lines else "No data",
            "color": 5814783,
            "fields": [
                {"name": "Active Workers", "value": f"{active}/{total}", "inline": True},
                {"name": "Total Coin", "value": f"{coin}", "inline": True},
                {"name": "Total Earned", "value": f"{earned}", "inline": True},
                {"name": "Jobs Completed", "value": f"{done}", "inline": True},
                {"name": "Dead Workers", "value": f"{dead}", "inline": True},
            ],
            "footer": {"text": f"Last update: {datetime.now().strftime('%H:%M:%S')}"},
        }

    def report(self, stats: Dict[int, Dict]):
        if not stats or not self.webhook:
            return
        payload_data = {
            "content": None,
            "embeds": [self.embed(stats)],
            "username": "Job Ảo Monitor",
        }
        try:
            if self.msgid:
                resp = requests.patch(f"{self.webhook}/messages/{self.msgid}", json=payload_data, impersonate="chrome")
                if resp.status_code != 200:
                    resp = requests.post(self.webhook, json=payload_data, impersonate="chrome")
                    if resp.status_code == 200:
                        self.msgid = resp.json().get('id')
            else:
                resp = requests.post(self.webhook, json=payload_data, impersonate="chrome")
                if resp.status_code == 200:
                    self.msgid = resp.json().get('id')
        except Exception:
            pass

    def monitor(self):
        last = 0
        while self.active:
            time.sleep(10)
            stats = self.data()
            now = time.time()
            if now - last >= 600:
                self.report(stats)
                last = now

    def stop(self):
        self.active = False
        for w in self.workers:
            w.stop()
        for w in self.workers:
            w.join(timeout=5)

    def run(self):
        banner()
        self.spawn()
        if not self.workers:
            return
        thread = threading.Thread(target=self.monitor, daemon=True)
        thread.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
            stats = self.data()
            self.report(stats)

def configure():
    while True:
        say(f"\n{color.white}── Job settings ──{color.reset}")
        say(f"  so_luong_job = {color.yellow}{config['so_luong_job']}{color.reset}")
        say(f"  delay_giay   = {color.yellow}{config['delay_giay']}{color.reset}")
        say(f"  dung_sau_loi = {color.yellow}{config['dung_sau_loi']}{color.reset}")
        idx = choice(
            "Chỉnh cấu hình job:",
            [
                f"Số job / platform  (hiện: {config['so_luong_job']})",
                f"Delay giây         (hiện: {config['delay_giay']})",
                f"Dừng sau N lỗi    (hiện: {config['dung_sau_loi']})",
            ],
        )
        if idx == -1:
            return
        if idx == 0:
            v = ask("Số job / platform", str(config['so_luong_job']))
            try:
                put('so_luong_job', max(1, int(v)))
            except ValueError:
                pass
        elif idx == 1:
            v = ask("Delay (giây)", str(config['delay_giay']))
            try:
                put('delay_giay', max(0, int(v)))
            except ValueError:
                pass
        elif idx == 2:
            v = ask("Dừng sau N lỗi", str(config['dung_sau_loi']))
            try:
                put('dung_sau_loi', max(1, int(v)))
            except ValueError:
                pass

def keys():
    say(f"\n{color.white}── Cấu hình tài khoản Golike ──{color.reset}")
    say(f"  username    = {color.yellow}{config.get('username', '')}")
    say(f"  user_id     = {color.yellow}{config.get('user_id', 0)}")
    idx = choice(
        "Chỉnh tài khoản:",
        [
            "Đổi tài khoản đăng nhập (nhập user/pass mới)",
            "Xoá thông tin đăng nhập",
        ],
    )
    if idx == -1:
        return
    if idx == 0:
        user = ask("Nhập tài khoản Golike", "")
        pwd = ask("Nhập mật khẩu Golike", "")
        put("username", user)
        put("password", pwd)
        say(f"\n{color.cyan}  Đang kiểm tra thông tin đăng nhập mới...{color.reset}")
        res = login(user, pwd)
        if res.get("ok"):
            put("token", res.get("token"))
            put("signing_key", res.get("key"))
            put("device_id", res.get("device"))
            put("user_id", res.get("id"))
            say(f"{color.green}✓ Cập nhật tài khoản thành công!{color.reset}")
        else:
            say(f"{color.red}Đăng nhập thất bại: {res.get('msg')}{color.reset}")
    elif idx == 1:
        for k in ('token', 'signing_key', 'user_id', 'username', 'device_id', 'password'):
            put(k, "" if k != 'user_id' else 0)
        say(f"{color.yellow}Đã xoá thông tin tài khoản.{color.reset}")

def hooks():
    current = config.get('webhook_url', '')
    say(f"\n{color.white}── Discord Webhook ──{color.reset}")
    say(f"  Hiện tại: {color.cyan}{mask(current, keep=16)}{color.reset}")
    idx = choice(
        "Chỉnh Webhook:",
        [
            "Đổi / đặt webhook URL",
            "Tắt webhook (set rỗng)",
            "Test gửi 1 message",
        ],
    )
    if idx == -1:
        return
    if idx == 0:
        val = ask("Webhook URL mới", current)
        put('webhook_url', val.strip())
    elif idx == 1:
        put('webhook_url', '')
    elif idx == 2:
        val = current.strip()
        if not val:
            return
        try:
            resp = requests.post(val, json={"content": "✅ Test webhook từ Golike Tool", "username": "Job Ảo Monitor"}, impersonate="chrome")
        except Exception:
            pass

def show():
    say(f"\n{color.white}── config.json ──{color.reset}")
    say(f"  token        = {mask(config.get('token', ''))}")
    say(f"  signing_key  = {mask(config.get('signing_key', ''), 6)}")
    say(f"  user_id      = {color.yellow}{config.get('user_id', 0)}")
    say(f"  username     = {color.yellow}{config.get('username', '')}")
    say(f"  device_id    = {color.yellow}{config.get('device_id', '')}")
    say(f"  webhook_url  = {mask(config.get('webhook_url', ''), keep=20)}")
    say(f"  so_luong_job = {color.yellow}{config['so_luong_job']}")
    say(f"  delay_giay   = {color.yellow}{config['delay_giay']}")
    say(f"  dung_sau_loi = {color.yellow}{config['dung_sau_loi']}")

def menu():
    while True:
        idx = choice(
            "Cấu hình:",
            [
                "GolikeAuth (5 trường)",
                "Discord Webhook",
                "Job settings (số job / delay / max errors)",
                "Xem toàn bộ config hiện tại",
            ],
        )
        if idx == -1:
            return
        if idx == 0:
            keys()
        elif idx == 1:
            hooks()
        elif idx == 2:
            configure()
        elif idx == 3:
            show()

def ensure(ask_anyway: bool = False):
    if ask_anyway or not webhook():
        if ask_anyway:
            say(f"\n{color.white}── Discord Webhook ──{color.reset}")
        url = ask("Discord Webhook URL (Enter = bỏ qua / tắt)", config.get('webhook_url', ''))
        put('webhook_url', url.strip())
    return config['webhook_url']

def setup() -> Auth:
    init()
    user = config.get("username") or ""
    pwd = config.get("password") or ""
    if not user or not pwd:
        say(f"\n{color.cyan}── Đăng nhập Golike tự động 100% ──{color.reset}")
        user = ask("Nhập tài khoản Golike", "")
        pwd = ask("Nhập mật khẩu Golike", "")
        put("username", user)
        put("password", pwd)
    say(f"\n{color.cyan}  Đang tự động đăng nhập Golike...{color.reset}")
    res = login(user, pwd)
    if not res.get("ok"):
        say(f"{color.red}  Đăng nhập thất bại: {res.get('msg')}{color.reset}")
        put("username", "")
        put("password", "")
        return setup()
    auth = Auth(
        token=res.get("token"),
        key=res.get("key"),
        uid=res.get("id"),
        user=res.get("name"),
        dev=res.get("device"),
    )
    auth.store()
    say(f"{color.green}  Đăng nhập thành công! Chào sếp {auth.user}{color.reset}")
    if not webhook():
        if ask("Bạn có muốn cấu hình Discord Webhook? (y/N)", "n").lower() == "y":
            ensure()
    return auth

def single(auth: Auth):
    runner = Runner(auth)
    idx = choice(
        "Chạy 1 account:",
        [
            "Chạy tất cả platforms (vòng lặp vô hạn)",
            "Chọn 1 platform cụ thể",
            "Chỉ liệt kê accounts (không chạy job)",
            "Xem profile",
        ],
    )
    if idx == -1:
        return
    if idx == 3:
        runner.profile()
    elif idx == 2:
        runner.list()
    elif idx == 1:
        options = [name.upper() for name in platforms]
        platform_idx = choice("Chọn platform:", options)
        if platform_idx != -1:
            runner.start(plat=platforms[platform_idx])
    else:
        runner.start()

def multi():
    if not os.path.exists(txt):
        return
    if not webhook():
        if ask("Vào cấu hình webhook ngay? (y/N)", "n").lower() == "y":
            hooks()
    Controller().run()

def profile(auth: Auth):
    Runner(auth).profile()

def accs(auth: Auth):
    runner = Runner(auth)
    if runner.profile():
        runner.list()

def main():
    banner()
    try:
        auth = setup()
        while True:
            idx = choice(
                "Chọn tính năng:",
                [
                    "Chạy 1 account (single mode)",
                    "Chạy multi-account từ au.txt (multi-thread)",
                    "Xem profile",
                    "Liệt kê accounts của từng platform",
                    "Cấu hình (GolikeAuth / Webhook / Jobs)",
                ],
                allow=False,
            )
            if idx == 0:
                single(auth)
            elif idx == 1:
                multi()
            elif idx == 2:
                profile(auth)
            elif idx == 3:
                accs(auth)
            elif idx == 4:
                menu()
    except KeyboardInterrupt:
        say(f"\n{color.yellow}Thoát.{color.reset}")

if __name__ == "__main__":
    main()
