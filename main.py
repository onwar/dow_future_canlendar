import requests
import re
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import os

# 目标URL
URL = "https://www.cmegroup.com/markets/equities/dow-jones/e-mini-dow.calendar.html"

def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

def parse_and_generate_ics(html_content):
    if not html_content:
        return

    c = Calendar()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 策略：CME页面的结构通常是每个合约一个块。
    # 我们直接在文本中搜索模式，因为CSS类名可能会变，但文本标签相对稳定。
    # 寻找包含 "Product Code" 的部分
    
    # 提取所有文本以简化搜索（应对复杂的DOM结构）
    text = soup.get_text(" ", strip=True)
    
    # 正则逻辑：
    # 1. 找到 Product Code 后的代码 (例如 YMH26)
    # 2. 找到该代码附近的 Last Trade 日期
    # 这里的正则假设 Product Code 出现后，后面紧跟的日期数据属于它
    
    # 查找所有类似 "Product Code YMH26" 的片段
    # 这里的模式匹配 Product Code 后面跟着的字串
    # 然后尝试在附近找 Last Trade 日期
    
    # 更稳健的方法是遍历页面上可能的容器，但这里用正则进行全局扫描演示
    # 假设数据格式为: "Product Code [CODE] ... Last Trade [Date1] [Date2]" 
    # 注意：通常显示为 First Trade [Date] Last Trade [Date]
    
    # 切分文本块，尝试按合约月份切分
    # CME 页面通常有 "Mar 2026", "Jun 2026" 这样的标题
    
    # 简单正则提取所有可能的合约对
    # 匹配模式： Product Code (CODE) ... Last Trade (DATE)
    # 注意：CME日期格式通常是 20 Mar 2026
    
    pattern = re.compile(r"Product Code\s+([A-Z0-9]+).*?Last Trade\s+(?:\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\s+)?(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})", re.DOTALL)
    
    matches = pattern.findall(text)
    
    # 如果通过正则直接提取有误，可能需要根据实际页面DOM调整，
    # 但根据browse工具看到的内容，文本是连续的。
    
    unique_events = set()

    for code, date_str in matches:
        # 去重
        if code in unique_events:
            continue
        unique_events.add(code)
        
        try:
            # 解析日期，例如 "20 Mar 2026"
            last_trade_date = datetime.strptime(date_str, "%d %b %Y")
            
            # 创建全天事件
            e = Event()
            e.name = f"📅 Last Trade: {code} (E-mini Dow)"
            e.begin = last_trade_date
            e.make_all_day()
            e.description = f"Contract: {code}\nLast Trading Day for E-mini Dow Jones.\nSource: {URL}"
            
            c.events.add(e)
            print(f"Added event: {code} on {date_str}")
            
        except ValueError as e:
            print(f"Date parse error for {code}: {e}")

    # 保存文件
    with open("emini_dow_calendar.ics", "w") as f:
        f.writelines(c.serialize())
        print("Calendar file generated successfully.")

if __name__ == "__main__":
    html = fetch_data()
    parse_and_generate_ics(html)
