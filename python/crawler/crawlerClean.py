import json
import os
import glob

# 1. 建立一個空字典來存放所有期別資料
final_data = {}

# 2. 取得目前資料夾下所有符合 *_lotto_results.json 規則的文件
# 如果你的檔案在特定資料夾，請修改路徑，例如：'data/*.json'
file_list = glob.glob("*_lotto_results.json")

print(f"找到 {len(file_list)} 個檔案，準備開始合併...")

for file_path in file_list:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 讀取單個月份的資料
            monthly_data = json.load(f)
            
            # 使用 update() 方法將內容合併進 final_data
            # 這會自動處理重複的 Key（以後來的為準）
            final_data.update(monthly_data)
            
    except Exception as e:
        print(f"讀取 {file_path} 時發生錯誤: {e}")

# 3. 將合併後的結果排序（按期別從小到大）
# 字典本身無序，但我們可以依據 Key (期別) 排序後存入新字典
sorted_keys = sorted(final_data.keys())
sorted_final_data = {k: final_data[k] for k in sorted_keys}

# 4. 輸出成最終的單一檔案
output_filename = "from2008to2023_lotto_appear_results_merged.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(sorted_final_data, f, ensure_ascii=False, indent=4)

print(f"---")
print(f"合併完成！")
print(f"總筆數：{len(sorted_final_data)} 筆")
print(f"儲存檔名：{output_filename}")