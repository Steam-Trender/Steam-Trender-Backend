package main

import (
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"os"
	"steamtrender.com/api/controllers"
	"steamtrender.com/api/models"
	"steamtrender.com/api/repositories"
	"steamtrender.com/api/services"
)

func main() {
	if err := godotenv.Load(); err != nil {
		panic("Error loading .env file")
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	r := gin.Default()

	trustedProxies := []string{"192.168.0.1"}
	if err := r.SetTrustedProxies(trustedProxies); err != nil {
		panic("Could not set trusted proxies")
	}

	models.ConnectDatabase("test.db")

	// models.SeedDatabase("raw_data/test_games.csv")

	gameRepo := repositories.NewGameRepository(models.DB)
	gameService := services.NewGameService(gameRepo)
	gameController := controllers.NewGameController(gameService)

	r.GET("/analysis/competitors", gameController.GetCompetitors)
	// get for /analysis/tags
	// get for /analysis/trends
	r.GET("/games/year/max", gameController.GetMaxYear)
	r.GET("/games/year/min", gameController.GetMinYear)

	r.Run(":" + port)
}
