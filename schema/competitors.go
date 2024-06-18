package schema

import (
	"steamtrender.com/api/models"
)

type CompetitorsData struct {
	Games         []models.Game
	MedianReviews float64
	MedianOwners  float64
	MedianPrice   float64
	TotalGames    int64
	MedianRevenue float64
}
