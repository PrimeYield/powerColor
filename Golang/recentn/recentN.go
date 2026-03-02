package recentn

import (
	"PowerColor/Golang/csv2json"
	"PowerColor/Golang/global"
	"encoding/json"
	"fmt"
	"os"
	"sort"
)

type OrderedStats struct {
	PeriodCount int         `json:"period_count"`
	Zone1       map[int]int `json:"zone1_statistics"`
	Zone2       map[int]int `json:"zone2_statistics"`
}

func RecentN() {
	var input int

inputNum:
	_, err := fmt.Scan(&input)
	if err != nil {
		fmt.Println("輸入錯誤，請輸入數字")
		goto inputNum
	}
	if input <= 0 {
		input = 0
	}

	global.RecentN = input
	fileData, _ := os.ReadFile("from2014to2026.json")
	var allData map[int]csv2json.LotteryData
	json.Unmarshal(fileData, &allData)

	var terms []int
	for term := range allData {
		terms = append(terms, term)
	}
	sort.Sort(sort.Reverse(sort.IntSlice(terms)))

	if global.RecentN > len(terms) {
		global.RecentN = len(terms)
	}
	recentTerms := terms[:global.RecentN]

	zone1Counts := make(map[int]int)
	zone2Counts := make(map[int]int)

	for _, term := range recentTerms {
		data := allData[term]
		for _, num := range data.FirstZone {
			zone1Counts[num]++
		}
		zone2Counts[data.SecondZone]++
	}

	// var zone1List []StatEntry
	// for num, count := range zone1Counts {
	// 	zone1List = append(zone1List, StatEntry{Number: num, Count: count})
	// }
	// sort.Slice(zone1List, func(i, j int) bool {
	// 	return zone1List[i].Number < zone1List[j].Number
	// })

	// var zone2List []StatEntry
	// for num, count := range zone2Counts {
	// 	zone2List = append(zone2List, StatEntry{Number: num, Count: count})
	// }
	// sort.Slice(zone2List, func(i, j int) bool {
	// 	return zone2List[i].Number < zone2List[j].Number
	// })

	result := OrderedStats{
		PeriodCount: global.RecentN,
		Zone1:       zone1Counts,
		Zone2:       zone2Counts,
	}

	outputJson, _ := json.MarshalIndent(result, "", "    ")
	os.WriteFile(fmt.Sprint(global.RecentN)+"_recent_stats.json", outputJson, 0644)

	fmt.Printf("成功統計最近 %d 期的數據，已存至 recent_stats.json\n", global.RecentN)
}
