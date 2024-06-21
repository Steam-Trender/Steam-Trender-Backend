package schema

type Tag struct {
	ID    uint   `json:"id" gorm:"primary_key"`
	Title string `json:"title"`
}

type Tags struct {
	Tags []Tag `json:"tags"`
}

type TagAnalysisData struct {
	Tag           string
	MedianReviews float64
	TotalGames    int64
	ReveneMin     float64
	RevenueQ1     float64
	RevenueMedian float64
	RevenueQ3     float64
	RevenueMax    float64
}

type TagsAnalysis struct {
	Tags []TagAnalysisData
}
