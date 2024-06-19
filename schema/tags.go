package schema

type TagData struct {
	Tag           string
	MedianReviews float64
	TotalGames    int64
	ReveneMin     float64
	RevenueQ1     float64
	RevenueMedian float64
	RevenueQ3     float64
	RevenueMax    float64
}

type TagsData struct {
	Tags []TagData
}
