package schema

type TrendData struct {
	Year          int64
	TotalGames    int64
	MedianReviews float64
	MedianOwners  float64
	MedianPrice   float64
	ReveneMin     float64
	RevenueQ1     float64
	RevenueMedian float64
	RevenueQ3     float64
	RevenueMax    float64
}

type TrendsData struct {
	Trends []TrendData
}
