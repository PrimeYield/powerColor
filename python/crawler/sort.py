import json
import glob

# 準備兩個空字典來存放不同的排序邏輯
appear_data = {}
size_data = {}

# 1. 獲取所有你抓下來的原始資料檔 (假設檔名包含 _lotto_results.json)
file_list = glob.glob("*_results.json")

print(f"正在讀取 {len(file_list)} 個原始檔案...")

for file_path in file_list:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 這裡假設你的原始檔案內容是 API 直接轉存的格式
            # 包含 content -> superLotto638Res 列表
            raw = json.load(f)
            
            # 取得該月的所有期別資料
            lotto_list = raw.get("content", {}).get("superLotto638Res", [])
            
            for item in lotto_list:
                period = str(item.get("period"))
                
                # 提取「大小排序」欄位 (Size)
                num_size = item.get("drawNumberSize", [])
                if len(num_size) >= 7:
                    size_data[period] = {
                        "zone1": num_size[:6],
                        "zone2": num_size[6]
                    }
                
                # 提取「開獎順序」欄位 (Appear)
                num_appear = item.get("drawNumberAppear", [])
                if len(num_appear) >= 7:
                    appear_data[period] = {
                        "zone1": num_appear[:6],
                        "zone2": num_appear[6]
                    }
                    
    except Exception as e:
        print(f"處理檔案 {file_path} 時發生錯誤: {e}")

# 2. 核心邏輯：依照「期號整數化」進行排序
def sort_by_period(data_dict):
    # 將 Key 轉為 int 進行排序，確保 103 排在 99 之後
    sorted_keys = sorted(data_dict.keys(), key=int)
    return {k: data_dict[k] for k in sorted_keys}

final_appear = sort_by_period(appear_data)
final_size = sort_by_period(size_data)

# 3. 分別輸出成兩個檔案
files_to_save = {
    "from2008to2026_appear_sort_results.json": final_appear,
    "from2008to2026_size_sort_results.json": final_size
}

for filename, content in files_to_save.items():
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)
    print(f"已儲存：{filename} (共 {len(content)} 筆)")

print("--- 任務完成 ---")