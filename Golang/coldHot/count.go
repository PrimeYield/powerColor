package coldHot

type StatsSummary struct {
	FirstZoneStats  map[int]int `json:"zone1_statistics"`
	SecondZoneStats map[int]int `json:"zone2_statistics"`
}

type StatEntry struct {
	Number int `json:"number"`
	Count  int `json:"count"`
	// map[int]int `json:"NumWithCount`
}
