package utils

const (
	VAT                  = 0.93
	Returns              = 0.92
	AverageRegionalPrice = 0.8
	Discount             = 0.8
	SteamCut             = 0.7
)

func RevenueCoeff() float64 {
	return VAT * Returns * AverageRegionalPrice * Discount * SteamCut
}
