package controllers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"steamtrender.com/api/services"
	"steamtrender.com/api/utils"
)

type GameController struct {
	Service *services.GameService
}

func NewGameController(service *services.GameService) *GameController {
	return &GameController{Service: service}
}

// GET /analysis/competitors
func (gc *GameController) GetCompetitors(c *gin.Context) {
	// Get query parameter 'reviewsCoeff'
	reviewsCoeffParam := c.Query("reviewsCoeff")
	reviewsCoeff := 30

	if reviewsCoeffParam != "" {
		var err error
		reviewsCoeff, err = strconv.Atoi(reviewsCoeffParam)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid reviews coeff parameter"})
			return
		}
	}

	// Get query parameter 'reviews'
	reviewsParam := c.Query("reviews")
	minReviews := 0

	if reviewsParam != "" {
		var err error
		minReviews, err = strconv.Atoi(reviewsParam)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid reviews parameter"})
			return
		}
	}

	// Get query parameter 'tags': black & white lists
	whitelistParam := c.QueryArray("w")
	whitelist, err := utils.ParseUintArray(whitelistParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid whitelist IDs"})
		return
	}

	blacklistParam := c.QueryArray("b")
	blacklist, err := utils.ParseUintArray(blacklistParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid blacklist IDs"})
		return
	}

	// run service
	data, err := gc.Service.GetGamesData(reviewsCoeff, minReviews, whitelist, blacklist)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, data)
}

// Get /games/years/max
func (bc *GameController) GetMaxYear(c *gin.Context) {
	// date, err := bc.Repo.ReadReleaseDate(repositories.MaxDate)
	// if err != nil {
	//	c.JSON(500, gin.H{"error": err.Error()})
	//	return
	//}
	//year := date.Year()
	//c.JSON(200, year)
	c.JSON(200, 300)
}

// Get /games/years/min
func (bc *GameController) GetMinYear(c *gin.Context) {
	c.JSON(200, 300)
}
