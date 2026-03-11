import json
import requests

# 1. 取得資料 (假設你已經拿到了原始的 JSON 內容)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.taiwanlottery.com.tw/"
}

all_results = {}

for i in range(2008,2027):
    for j in range(1,13):
        month_str = f"{i}-{j:02d}" 
        # url = f"https://api.taiwanlottery.com/TLCAPIWeB/Lottery/SuperLotto638Result?month={month_str}&endMonth={month_str}&pageNum=1&pageSize=10"
        url = f"https://api.taiwanlottery.com/TLCAPIWeB/Lottery/SuperLotto638Result?period&month={month_str}&endMonth={month_str}&pageNum=1&pageSize=200"
        response = requests.get(url)
        raw_data = response.json()

        # 2. 定位原始資料列表
        lotto_list = raw_data.get("content", {}).get("superLotto638Res", [])

        # 3. 轉換成你指定的格式
        formatted_data = {}

        for item in lotto_list:
            period = str(item.get("period")) # 將期別轉為字串作為 Key
            numbers = item.get("drawNumberAppear", [])
            
            if len(numbers) >= 7:
                formatted_data[period] = {
                    "zone1": numbers[:6],  # 取前 6 碼
                    "zone2": numbers[6]    # 取第 7 碼 (特別號)
                }

        # 4. 輸出成 .json 文件
        with open(f"{month_str}_lotto_results.json", "w", encoding="utf-8") as f:
            # ensure_ascii=False 可以讓中文(如果有)正常顯示，indent=4 讓排版漂亮
            json.dump(formatted_data, f, ensure_ascii=False, indent=4)

        print(f"成功轉換 {len(formatted_data)} 筆資料並儲存為 {month_str}_lotto_results.json")