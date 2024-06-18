package utils

import (
	"strconv"
)

func ParseUintArray(input []string) ([]uint, error) {
	var result []uint
	for _, str := range input {
		num, err := strconv.ParseUint(str, 10, 32)
		if err != nil {
			return nil, err
		}
		result = append(result, uint(num))
	}
	return result, nil
}
