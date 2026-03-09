from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os
import re
import json
from datetime import datetime, timezone, timedelta
import argparse

os.environ['WDM_LOG'] = '0'
os.environ['WDM_LOCAL'] = '1'
os.environ['CHROMEDRIVER_CDNURL'] = 'https://registry.npmmirror.com/-/binary/chromedriver/'

# IMPORTANT YOU NEED TO CONFIGURE THE PROFILE_PATH AND CHROME_PROFILE ACCORDING TO YOUR DEVICE

profile_path = r"C:\Users\O_O\AppData\Local\Google\Chrome\User Data" #For example C:\Users\<USER>\AppData\Local\Google\Chrome\User Data
chrome_profile = "<YOUR_OWN_PROFILE>" #For example Profile 1 


# Headed browser incase the user isn't login to Xiaomi Cloud yet
def needToAuthenticate():

    chrome_service = Service(ChromeDriverManager().install())
    options = Options()

    options.add_argument("--log-level=3") 
    options.add_argument("--silent")  
    options.add_argument("--disable-logging")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument(f"profile-directory={chrome_profile}")
    return webdriver.Chrome(service=chrome_service, options=options)


# Using Headless browser to check if the user has existing token in Xiaomi CLoud
def alreadyAuthenticated():

    # 手动指定ChromeDriver路径
    chrome_service = Service(executable_path='./chromedriver.exe')
    options = Options()

    options.add_argument("--log-level=3")
    options.add_argument("--silent") 
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-features=EnableMLModel")
    options.add_argument("--headless")
    options.add_argument("--disable-logging")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument(f"profile-directory={chrome_profile}")
    options.add_argument('--no-sandbox') # 解决权限问题
    options.add_argument('--disable-dev-shm-usage') # 解决资源占用问题
    options.add_argument('--remote-debugging-port=9222') # 指定端口
    return webdriver.Chrome(service=chrome_service, options=options)


# Gets the needed cookies to extract all of the user notes
def getCookies():

    driver = alreadyAuthenticated()
    driver.get("https://account.xiaomi.com/pass/serviceLogin?")
    time.sleep(3)
    #print(driver.current_url)

    if "/service/account" in driver.current_url:
        print("[+]Authenticated already...")
        
        cookies = driver.get_cookies()
        with open("cookie.txt", "w") as cookie_file:
            for cookie in cookies:
                if cookie["name"] == "userId":
                    userId = f"userId={cookie['value']}"
                    cookie_file.write(userId + "\n")

        print("[+]userId saved to cookie.txt")

        driver.get("https://us.i.mi.com/note/h5")
        time.sleep(3)
        cookies = driver.get_cookies()


        with open("cookie.txt", "a") as cookie_file:
            for cookie in cookies:
                if cookie["name"] == "serviceToken":
                    serviceToken = f"serviceToken={cookie['value']}"
                    cookie_file.write(serviceToken + "\n")

        print("[+]serviceToken saved to cookie.txt")

    elif "/login/password" in driver.current_url:

        print("[/]Please Authenticate First.")
        driver.quit()
        driver = needToAuthenticate()
        driver.get("https://account.xiaomi.com/pass/serviceLogin?")

        while "service/login" in driver.current_url:
            print(driver.current_url)
            time.sleep(1)
        
        time.sleep(3)
        cookies = driver.get_cookies()
        with open("cookie.txt", "w") as cookie_file:
            for cookie in cookies:
                if cookie["name"] == "userId":
                    userId = f"userId={cookie['value']}"
                    cookie_file.write(userId + "\n")

        print("[+]userId saved to cookie.txt")

        driver.get("https://us.i.mi.com/note/h5")
        time.sleep(3)
        current_url = driver.current_url

        if "verifyPhone" in current_url:
            print("OTP verification page detected.")

            while "verifyPhone" in driver.current_url:
                print("Enter your OTP...")
                time.sleep(1) 

            print("OTP completed")

            cookies = driver.get_cookies()
            with open("cookie.txt", "a") as cookie_file:
                for cookie in cookies:
                    if cookie["name"] == "serviceToken":
                        serviceToken = f"serviceToken={cookie['value']}"
                        cookie_file.write(serviceToken + "\n")

            print("[+]serviceToken saved to cookie.txt")

        else:
            cookies = driver.get_cookies()
            with open("cookie.txt", "a") as cookie_file:
                for cookie in cookies:
                    if cookie["name"] == "serviceToken":
                        serviceToken = f"serviceToken={cookie['value']}"
                        cookie_file.write(serviceToken + "\n")

            print("[+]serviceToken saved to cookie.txt")

    print("ADFSGJKNDFJGHKLJNGHLKERTMNGHLERMHLRTKGNSLDKDFNDKLFNGHLKGN")
    #time.sleep(5)
    driver.quit()


# Export all of Xiaomi Notes
def getNotes():
    # --- 1. 这里填入你获取的所有 Cookie 信息 ---
    cookieHeader = {
        "i.mi.com_istrudev": "---",
        "i.mi.com_isvalid_servicetoken": "---",
        "i.mi.com_ph": "---",
        "i.mi.com_slh": "---",
        "serviceToken": "---",
        "uLocale": "---",
        "userId": "---" 
    }

    print("[/]正在尝试获取笔记列表...")
    
    # --- 2. 确保使用国内 API 地址 ---
    url = "https://i.mi.com/note/full?"
    
    # 模拟真实浏览器，防止 401
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://i.mi.com/",
        "Origin": "https://i.mi.com"
    }

    allNotes = requests.get(url, cookies=cookieHeader, headers=headers)
    
    # 打印状态码用于调试
    print(f"服务器返回状态码: {allNotes.status_code}")

    if allNotes.status_code != 200:
        print(f"[-] 失败原因: {allNotes.text}")
        return None, []

    json_response = allNotes.json()
    entries = json_response.get("data", {}).get("entries", [])
    
    # 如果列表为空，可能是 API 结构变了，打印出来看看
    if not entries:
        print(f"[-] 没找到笔记，完整返回内容: {json_response}")

    return cookieHeader, [entry["id"] for entry in entries if "id" in entry]

    

def exportNotes(cookieHeader, note_ids):
    base_url = "https://i.mi.com/note/note/" # 确保是国内地址

    for id_value in note_ids:
        note_url = f"{base_url}{id_value}" 
        response = requests.get(note_url, cookies=cookieHeader)
        data = response.json()

        try:
            # --- 核心修复：更安全地获取标题 ---
            entry = data.get("data", {}).get("entry", {})
            extra_info_str = entry.get("extraInfo", "{}")
            extra_info = json.loads(extra_info_str)
            
            # 如果没有 title，就用 id 代替，或者取正文的前10个字
            title = extra_info.get("title")
            if not title:
                content_preview = entry.get("content", "")[:10]
                title = content_preview.strip() or f"未命名笔记_{id_value}"
            
            title = title.strip()

            # --- 获取时间 ---
            create_date = datetime.fromtimestamp(int(entry.get("createDate", 0)) / 1000, tz=utc_offset).strftime('%Y-%m-%d %H:%M:%S')
            modify_date = datetime.fromtimestamp(int(entry.get("modifyDate", 0)) / 1000, tz=utc_offset).strftime('%Y-%m-%d %H:%M:%S')

            # --- 获取正文 ---
            content_raw = entry.get("content", "")
            content = re.findall(r'<text[^>]*>(.*?)<\/text>', content_raw)
            if not content:
                content = [content_raw.strip()]

            note_text = f"**Title:** {title}\n\n" \
                        f"**Created Time:** {create_date}\n\n" \
                        f"**Modified Time:** {modify_date}\n\n" \
                        + "\n\n".join(content)
            
            # 文件名合法化
            filename = re.sub(r'[\/:*?"<>|]', '_', title) + ".md"
            
            with open(filename, "w", encoding="utf-8") as file:
                file.write(note_text)
            print(f"[+]成功导出: {filename}")

        except Exception as e:
            print(f"[-]处理笔记 {id_value} 时出错: {e}")
            continue # 出错了就跳过这一条，继续下一条

    print("[+]全部笔记导出完成！")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Extract and save Xiaomi Cloud Notes :D")
    parser.add_argument("-d", "--date", action="store_true", help="Includes created and modified date")
    parser.add_argument("-tz", "--tzone", type=int, default=8, metavar="TZ",help="Set timezone offset (Default is UTC+8.)")
    args = parser.parse_args()

    # --- 核心修改：跳过 getCookies，直接按顺序执行下载函数 ---
    try:
        # 1. 获取 Cookie 和所有笔记 ID
        cookieHeader, note_ids = getNotes()
        
        # 2. 执行导出逻辑
        if note_ids:
            exportNotes(cookieHeader, note_ids)
        else:
            print("[-]未发现笔记，请检查 cookie.txt 中的 userId 和 serviceToken 是否正确。")
            
    except FileNotFoundError:
        print("[-]错误：未找到 cookie.txt 文件，请确保它与脚本在同一目录下。")
    except Exception as e:
        print(f"[-]运行出错: {e}")
