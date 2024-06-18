package controllers

import (
	"net/http"
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

	// Get query parameter 'tags': black & white lists
	whitelistParam := c.QueryArray("w")
	whitelist, err := parseUintArray(whitelistParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid whitelist IDs"})
		return
	}

	blacklistParam := c.QueryArray("b")
	blacklist, err := parseUintArray(blacklistParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid blacklist IDs"})
		return
	}

	games, err := bc.Repo.ReadGames(minReviews, whitelist, blacklist)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}

	c.JSON(200, games)
}

// Get /games/years/max
func (bc *GameController) GetMaxYear(c *gin.Context) {
	date, err := bc.Repo.ReadReleaseDate(repositories.MaxDate)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	year := date.Year()
	c.JSON(200, year)
}

// Get /games/years/min
func (bc *GameController) GetMinYear(c *gin.Context) {
	date, err := bc.Repo.ReadReleaseDate(repositories.MinDate)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	year := date.Year()
	c.JSON(200, year)
}

func parseUintArray(input []string) ([]uint, error) {
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
