package main

import (
	"PowerColor/Golang/coldHot"
	"PowerColor/Golang/csv2json"
	"PowerColor/Golang/recentn"
)

func main() {
	csv2json.Csv2json()
	coldHot.CountResult()
	for i := 0; i < 10; i++ {
		recentn.RecentN()
	}
}
