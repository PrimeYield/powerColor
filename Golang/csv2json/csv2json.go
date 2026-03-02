package csv2json

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
)

type LotteryData struct {
	FirstZone  []int `json:"zone1"`
	SecondZone int   `json:"zone2"`
}

func ProcessCSV(filename string, results map[int]LotteryData) error {
	file, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return err
	}

	for i, row := range records {
		if i == 0 || len(row) < 8 {
			continue
		}

		term, _ := strconv.Atoi(row[0])

		var firstZone []int
		for j := 1; j <= 6; j++ {
			num, _ := strconv.Atoi(row[j])
			firstZone = append(firstZone, num)
		}

		secondZone, _ := strconv.Atoi(row[7])

		results[term] = LotteryData{
			FirstZone:  firstZone,
			SecondZone: secondZone,
		}
	}
	return nil
}

func Csv2json() {
	allResults := make(map[int]LotteryData)

	files, err := filepath.Glob("./history/*.csv")
	if err != nil {
		fmt.Printf("讀取目錄失敗: %v\n", err)
		return
	}

	for _, fileName := range files {
		fmt.Printf("正在處理檔案: %s...\n", fileName)

		err := ProcessCSV(fileName, allResults)
		if err != nil {
			fmt.Printf("處理 %s 時發生錯誤: %v\n", fileName, err)
			continue
		}
	}

	jsonData, err := json.MarshalIndent(allResults, "", "    ")
	if err != nil {
		fmt.Printf("JSON 轉換失敗: %v\n", err)
		return
	}

	outputFile := "from2014to2026.json"
	err = os.WriteFile(outputFile, jsonData, 0644)
	if err != nil {
		fmt.Printf("寫入文件失敗: %v\n", err)
		return
	}

	fmt.Printf("\n所有檔案處理完成！共計 %d 筆資料，已儲存至 %s\n", len(allResults), outputFile)
}
