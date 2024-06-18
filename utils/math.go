package utils

import (
	"sort"
)

func CalculateMedian(numbers []float64) float64 {
	n := len(numbers)
	if n == 0 {
		return 0
	}

	sort.Float64s(numbers)
	mid := n / 2
	if n%2 == 0 {
		return (numbers[mid-1] + numbers[mid]) / 2
	}
	return numbers[mid]
}
