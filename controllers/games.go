package controllers

import (
	"strconv"

	"github.com/gin-gonic/gin"
	"steamtrender.com/api/repositories"
)

type GameController struct {
	Repo *repositories.GameRepository
}

func NewGameController(repo *repositories.GameRepository) *GameController {
	return &GameController{Repo: repo}
}

// GET /games
func (bc *GameController) GetGames(c *gin.Context) {
	// Get query parameter 'reviews'
	reviewsParam := c.Query("reviews")
	minReviews := 0

	if reviewsParam != "" {
		var err error
		minReviews, err = strconv.Atoi(reviewsParam)
		if err != nil {
			c.JSON(400, gin.H{"error": "Invalid reviews parameter"})
			return
		}
	}

	games, err := bc.Repo.ReadGames(minReviews)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}

	c.JSON(200, games)
}
