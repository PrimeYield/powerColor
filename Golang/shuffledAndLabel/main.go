package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"time"
)

// DataPoint 代表單期獎號結構
type DataPoint struct {
	Zone1 []int `json:"zone1"`
	Zone2 int   `json:"zone2"`
}

// TrainingSample 代表一組訓練樣本
type TrainingSample struct {
	Input []DataPoint `json:"input"`
	Label DataPoint   `json:"label"`
}

func main() {
	// 1. 處理命令列參數
	// 期望格式: go run data_aligner.go [batchSize] [gap]
	if len(os.Args) < 3 {
		fmt.Println("錯誤: 請提供參數 [batchSize] 和 [gap]")
		fmt.Println("範例: go run data_aligner.go 50 1")
		return
	}

	batchSize, err := strconv.Atoi(os.Args[1])
	if err != nil {
		fmt.Printf("無效的 batchSize: %v\n", err)
		return
	}

	gap, err := strconv.Atoi(os.Args[2])
	if err != nil {
		fmt.Printf("無效的 gap: %v\n", err)
		return
	}

	// 2. 讀取第一手資料
	file, err := os.ReadFile("../../data/from2008to2026.json")
	if err != nil {
		fmt.Printf("讀取檔案失敗: %v\n", err)
		return
	}

	var rawData map[string]DataPoint
	if err := json.Unmarshal(file, &rawData); err != nil {
		fmt.Printf("解析 JSON 失敗: %v\n", err)
		return
	}

	// 3. 排序期號
	keys := make([]string, 0, len(rawData))
	for k := range rawData {
		keys = append(keys, k)
	}
	sort.Slice(keys, func(i, j int) bool {
		ki, _ := strconv.Atoi(keys[i])
		kj, _ := strconv.Atoi(keys[j])
		return ki < kj
	})

	// 4. 生成對齊後的樣本集 (Sliding Window)
	var allSamples []TrainingSample
	// 邏輯: 索引 i 到 i+batchSize-1 是 Input
	// 目標 Label 索引是 i + batchSize + gap - 2
	// (例如 i=0, batch=50, gap=1, label 就是索引 49+1-0 = 50，即第 51 筆)
	for i := 0; i <= len(keys)-batchSize-gap+1; i++ {
		input := make([]DataPoint, batchSize)
		for j := 0; j < batchSize; j++ {
			input[j] = rawData[keys[i+j]]
		}

		label := rawData[keys[i+batchSize+gap-2]]

		allSamples = append(allSamples, TrainingSample{
			Input: input,
			Label: label,
		})
	}

	fmt.Printf("參數設定: BatchSize=%d, Gap=%d | 總計生成樣本數: %d\n", batchSize, gap, len(allSamples))

	// 5. 動態產生檔名與路徑
	orderDir := "../../data/order/"
	shuffledDir := "../../data/shuffled/"

	// 自動建立目錄 (如果不存在)
	os.MkdirAll(orderDir, os.ModePerm)
	os.MkdirAll(shuffledDir, os.ModePerm)

	orderFileName := filepath.Join(orderDir, fmt.Sprintf("%d_%d_order_train.json", batchSize, gap))
	shuffledFileName := filepath.Join(shuffledDir, fmt.Sprintf("%d_%d_shuffled_train.json", batchSize, gap))

	// 6. 輸出順序版本
	saveJSON(orderFileName, allSamples)

	// 7. 輸出亂序版本
	shuffledSamples := make([]TrainingSample, len(allSamples))
	copy(shuffledSamples, allSamples)

	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	r.Shuffle(len(shuffledSamples), func(i, j int) {
		shuffledSamples[i], shuffledSamples[j] = shuffledSamples[j], shuffledSamples[i]
	})

	saveJSON(shuffledFileName, shuffledSamples)

	fmt.Printf("資料對齊完成！檔案已儲存至:\n1. %s\n2. %s\n", orderFileName, shuffledFileName)
}

func saveJSON(filename string, data interface{}) {
	file, err := os.Create(filename)
	if err != nil {
		fmt.Printf("建立檔案 %s 失敗: %v\n", filename, err)
		return
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "    ")
	if err := encoder.Encode(data); err != nil {
		fmt.Printf("寫入 JSON %s 失敗: %v\n", filename, err)
	}
}
