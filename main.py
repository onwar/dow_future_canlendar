from ics import Calendar, Event
from datetime import date, timedelta
import holidays

def get_third_friday(year, month):
    """
    计算指定年份和月份的第三个星期五。
    逻辑：每个月的15日到21日之间必定包含第三个星期五。
    """
    d = date(year, month, 15)
    # weekday(): 0=Monday, 4=Friday
    days_ahead = (4 - d.weekday() + 7) % 7
    return d + timedelta(days=days_ahead)

def get_last_trading_day(contract_year, contract_month):
    """
    根据CME规则确定最后交易日：
    通常是合约月份的第三个星期五。
    如果这天是假日（NYSE休市），则提前至前一个交易日。
    """
    base_date = get_third_friday(contract_year, contract_month)
    
    # 修正点：直接使用 holidays.NYSE 类来获取纽交所假期
    nyse_holidays = holidays.NYSE(years=contract_year)
    
    # 如果第三个星期五是假期，向前寻找最近的工作日
    # 同时排除周末 (weekday > 4) 和 假期
    while base_date in nyse_holidays or base_date.weekday() > 4: 
        base_date -= timedelta(days=1)
        
    return base_date

def generate_contract_code(year, month):
    """
    生成 CME 风格的代码，例如: YMH26
    月份代码: H(3), M(6), U(9), Z(12)
    """
    month_codes = {3: 'H', 6: 'M', 9: 'U', 12: 'Z'}
    year_short = str(year)[-2:]
    return f"YM{month_codes[month]}{year_short}"

def main():
    c = Calendar()
    
    current_year = date.today().year
    # 生成今年和明年的日历
    target_years = [current_year, current_year + 1]
    contract_months = [3, 6, 9, 12] 
    
    print(f"Generating calendar for years: {target_years}")

    for year in target_years:
        for month in contract_months:
            last_trade = get_last_trading_day(year, month)
            code = generate_contract_code(year, month)
            
            e = Event()
            e.name = f"🔔 Last Trade: {code} (E-mini Dow)"
            e.begin = last_trade
            e.make_all_day()
            e.description = (
                f"Product: E-mini Dow ($5)\n"
                f"Contract: {code}\n"
                f"Rule: 3rd Friday of {last_trade.strftime('%B')}\n"
                f"Status: Calculated (Holiday Adjusted)"
            )
            
            c.events.add(e)
            print(f"Generated: {code} -> {last_trade}")

    output_file = "emini_dow_calendar.ics"
    with open(output_file, "w") as f:
        f.writelines(c.serialize())
    print(f"\nSuccessfully created {output_file}")

if __name__ == "__main__":
    main()
