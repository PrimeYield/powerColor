import json
import glob

# 準備兩個空字典來存放不同的排序邏輯
appear_data = {}
size_data = {}

# 1. 獲取所有你抓下來的原始資料檔 (假設檔名包含 _lotto_results.json)
file_list = glob.glob("*_results.json")

# print(f"正在讀取 {len(file_list)} 個原始檔案...")
i=0
for file_path in file_list:
    i += 1
    print(f"get {i} / {len(file_list)} files {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
            
            lotto_list = [
               {k: v}
               for k, v in sorted(raw.items(),key=lambda x: int(x[0]))
            ]
            
            # print(lotto_list[0])
            # print(lotto_list[100])
        save_path = f"./data/sort/sort_{file_path}"
        with open(save_path,"w",encoding="utf-8") as f:
            json.dump(lotto_list, f, ensure_ascii=False,indent=4)

                    
    except Exception as e:
        print(f"處理檔案 {file_path} 時發生錯誤: {e}")



# 3. 分別輸出成兩個檔案
# files_to_save = {
#     "./data/sort/from2008to2026_appear_sort_results.json": final_appear,
#     "./data/sort/from2008to2026_size_sort_results.json": final_size
# }

# for filename, content in files_to_save.items():
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(content, f, ensure_ascii=False, indent=4)
#     print(f"已儲存：{filename} (共 {len(content)} 筆)")

print("--- 任務完成 ---")