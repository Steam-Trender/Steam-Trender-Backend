package controller

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"steamtrender.com/api/service"
	"steamtrender.com/api/utils"
)

type IGameController interface {
	IController
	GetCompetitors(c *gin.Context)
	GetMaxYear(c *gin.Context)
	GetMinYear(c *gin.Context)
}

type GameController struct {
	Service service.IGameService
}

func NewGameController(service *service.GameService) *GameController {
	return &GameController{Service: service}
}

var _ IController = &GameController{}

// GET /analysis/competitors
func (controller *GameController) GetCompetitors(c *gin.Context) {
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
	data, err := controller.Service.GetGamesData(reviewsCoeff, minReviews, whitelist, blacklist)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, data)
}

// GET /games/years/max
func (controller *GameController) GetMaxYear(c *gin.Context) {
	// date, err := bc.Repo.ReadReleaseDate(repositories.MaxDate)
	// if err != nil {
	//	c.JSON(500, gin.H{"error": err.Error()})
	//	return
	//}
	//year := date.Year()
	//c.JSON(200, year)
	c.JSON(200, 300)
}

// GET /games/years/min
func (bc *GameController) GetMinYear(c *gin.Context) {
	c.JSON(200, 300)
}

var _ IGameController = &GameController{}
