package coldHot

import (
	"encoding/json"
	"fmt"
	"os"

	. "PowerColor/Golang/csv2json"
)

func CountResult() {
	fileData, err := os.ReadFile("from2014to2026.json")
	if err != nil {
		fmt.Println("讀取合併文件失敗:", err)
		return
	}

	var allData map[string]LotteryData
	if err := json.Unmarshal(fileData, &allData); err != nil {
		fmt.Println("解析 JSON 失敗:", err)
		return
	}

	firstZoneStats := make(map[int]int)
	secondZoneStats := make(map[int]int)

	for _, data := range allData {
		for _, num := range data.FirstZone {
			firstZoneStats[num]++
		}
		secondZoneStats[data.SecondZone]++
	}

	summary := StatsSummary{
		FirstZoneStats:  firstZoneStats,
		SecondZoneStats: secondZoneStats,
	}

	statJson, err := json.MarshalIndent(summary, "", "    ")
	if err != nil {
		fmt.Println("轉換統計 JSON 失敗:", err)
		return
	}

	outputFile := "coldHot.json"
	err = os.WriteFile(outputFile, statJson, 0644)
	if err != nil {
		fmt.Println("寫入 coldHot.json 失敗:", err)
		return
	}

	fmt.Printf("統計完成！冷熱號碼分析已儲存至: %s\n", outputFile)
}
