package repositories

import (
	"gorm.io/gorm"

	"steamtrender.com/api/models"
)

type GameRepository struct {
	DB *gorm.DB
}

func NewGameRepository(db *gorm.DB) *GameRepository {
	return &GameRepository{DB: db}
}

func (repo *GameRepository) ReadGames(minReviews int) ([]models.Game, error) {
	var games []models.Game
	if err := repo.DB.Where("reviews >= ?", minReviews).Find(&games).Error; err != nil {
		return nil, err
	}
	return games, nil
}
