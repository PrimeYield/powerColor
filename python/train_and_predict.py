import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import random

# --- 1. 資料解析與預處理 ---
def load_json_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # 提取 zone1 的號碼，並確保按期號排序（若 JSON key 是期號）
    sorted_keys = sorted(data.keys())
    sequences = [data[k]['zone1'] for k in sorted_keys]
    return sequences # 返回 List[List[int]]

class PowerColorDataset(Dataset):
    def __init__(self, sequences, seq_len=50, skip_step=2):
        self.seq_len = seq_len
        self.skip_step = skip_step
        self.X_ordered = []
        self.X_shuffled = []
        self.Y = []

        # 滑動窗口處理
        limit = len(sequences) - seq_len - skip_step + 1
        for i in range(limit):
            # 歷史視窗 (seq_len, 6)
            window = sequences[i : i + seq_len]
            
            # 構建有序與亂序的 Multi-hot 矩陣
            m_hot_ord = np.zeros((seq_len, 38))
            m_hot_shuf = np.zeros((seq_len, 38))
            
            for j in range(seq_len):
                nums = np.array(window[j])
                m_hot_ord[j, nums - 1] = 1 # 有序標記
                
                # 亂序標記：隨機打亂（模擬不同輸入組合）
                shuf_nums = random.sample(list(nums), len(nums))
                m_hot_shuf[j, np.array(shuf_nums) - 1] = 1
            
            # 目標值 (跳期預測)
            target_nums = sequences[i + seq_len + skip_step - 1]
            target_m_hot = np.zeros(38)
            target_m_hot[np.array(target_nums) - 1] = 1
            
            self.X_ordered.append(m_hot_ord)
            self.X_shuffled.append(m_hot_shuf)
            self.Y.append(target_m_hot)

    def __len__(self): return len(self.Y)

    def __getitem__(self, idx):
        return (torch.FloatTensor(self.X_ordered[idx]), 
                torch.FloatTensor(self.X_shuffled[idx]), 
                torch.FloatTensor(self.Y[idx]))

# --- 2. 雙軌 iTransformer 模型定義 ---
class iTransformerLayer(nn.Module):
    def __init__(self, d_model, nhead, dropout):
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model * 4, d_model)
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, x):
        res, _ = self.attn(x, x, x)
        x = self.norm1(x + res)
        x = self.norm2(x + self.ff(x))
        return x

class LotteryModel(nn.Module):
    def __init__(self, seq_len=50, d_model=128, n_layers=3, dropout=0.4):
        super().__init__()
        # 轉置投影：將時間維度 (seq_len) 投射到特徵維度 (d_model)
        self.enc_embedding = nn.Linear(seq_len, d_model)
        
        self.layers = nn.ModuleList([iTransformerLayer(d_model, 8, dropout) for _ in range(n_layers)])
        
        # 雙軌特徵融合 (Ordered + Shuffled)
        self.projection = nn.Linear(d_model * 2, 38)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x_ord, x_shuf):
        # iTransformer 核心：交換 Batch, Vars, Seq -> [B, 38, Seq]
        def process_stream(x):
            x = x.permute(0, 2, 1) 
            x = self.enc_embedding(x)
            for layer in self.layers:
                x = layer(x)
            return x.mean(dim=1) # 聚合號碼維度特徵

        feat_ord = process_stream(x_ord)
        feat_shuf = process_stream(x_shuf)
        
        combined = torch.cat([feat_ord, feat_shuf], dim=-1)
        return self.projection(self.dropout(combined))

# --- 3. 執行訓練與預測 ---
def train_and_predict(json_path):
    # 參數設定
    SEQ_LEN = 50
    SKIP_STEP = 2 # 預測 T+2 (跳過一期)
    BATCH_SIZE = 32
    EPOCHS = 100

    # 讀取與加載數據
    sequences = load_json_data(json_path)
    dataset = PowerColorDataset(sequences, seq_len=SEQ_LEN, skip_step=SKIP_STEP)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    model = LotteryModel(seq_len=SEQ_LEN)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    criterion = nn.BCEWithLogitsLoss() # 適合多標籤分類 (Multi-hot)

    # 模擬訓練循環
    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0
        for x_ord, x_shuf, y in loader:
            optimizer.zero_grad()
            output = model(x_ord, x_shuf)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if (epoch+1) % 20 == 0:
            print(f"Epoch {epoch+1}, Loss: {total_loss/len(loader):.4f}")

    # 預測第 1232 期 (基於最後 SEQ_LEN 期)
    model.eval()
    with torch.no_grad():
        last_window = sequences[-SEQ_LEN:]
        # 轉換為 Tensor 格式
        test_ord = np.zeros((1, SEQ_LEN, 38))
        for j in range(SEQ_LEN):
            test_ord[0, j, np.array(last_window[j])-1] = 1
        test_ord = torch.FloatTensor(test_ord)
        
        logits = model(test_ord, test_ord) # 推理時雙軌輸入相同即可
        probs = torch.sigmoid(logits)
        top6 = torch.topk(probs, 6).indices.numpy()[0] + 1
        
    print(f"\n根據跳期規律 (Skip={SKIP_STEP})，預測結果為: {sorted(top6)}")

# 使用方式:
train_and_predict('from2014to2026.json')