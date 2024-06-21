package main

import (
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"gorm.io/gorm"
	"os"
	"steamtrender.com/api/controller"
	"steamtrender.com/api/repository"
	"steamtrender.com/api/service"
)

func SetupComponents[R repository.IRepository, S service.IService, C controller.IController](
	db *gorm.DB,
	newRepository func(*gorm.DB) R,
	newService func(R) S,
	newController func(S) C,
) C {
	repo := newRepository(db)
	svc := newService(repo)
	ctrl := newController(svc)
	return ctrl
}

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

	repository.ConnectDatabase("test.db")

	tagController := SetupComponents(repository.DB,
		repository.NewTagRepository,
		service.NewTagService,
		controller.NewTagController)

	gameController := SetupComponents(repository.DB,
		repository.NewGameRepository,
		service.NewGameService,
		controller.NewGameController)

	// models.SeedDatabase("raw_data/test_games.csv")

	r.GET("/analysis/competitors", gameController.GetCompetitors)
	// get for /analysis/tags
	// get for /analysis/trends
	r.GET("/games/year/max", gameController.GetMaxYear)
	r.GET("/games/year/min", gameController.GetMinYear)
	r.GET("/tags", tagController.GetAllTags)

	r.Run(":" + port)
}
