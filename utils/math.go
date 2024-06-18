package utils

import (
	"github.com/montanaflynn/stats"
)

func CalculatePercentile(data []float64, p float64) float64 {
	percentile, _ := stats.Percentile(data, p)
	return percentile
}

func CalculateMedian(data []float64) float64 {
	median, _ := stats.Median(data)
	return median
}
