package service

import (
	"steamtrender.com/api/repository"
	"steamtrender.com/api/schema"
	"steamtrender.com/api/utils"
)

type IGameService interface {
	IService
	GetGamesData(int, int, []uint, []uint) (schema.CompetitorsData, error)
}

type GameService struct {
	Repo repository.IGameRepository
}

func NewGameService(repo *repository.GameRepository) *GameService {
	return &GameService{Repo: repo}
}

func (service *GameService) GetGamesData(reviwsCoeff int, minReviews int, whitelistTagIDs, blacklistTagIDs []uint) (schema.CompetitorsData, error) {
	games, err := service.Repo.ReadGames(minReviews, whitelistTagIDs, blacklistTagIDs)
	if err != nil {
		return schema.CompetitorsData{}, err
	}

	data := schema.CompetitorsData{
		Games:      games,
		TotalGames: int64(len(games)),
	}

	if len(games) > 0 {
		var reviews []float64
		var owners []float64
		var prices []float64
		var revenues []float64

		for _, game := range games {
			reviews = append(reviews, float64(game.Reviews))
			owners = append(owners, reviews[len(reviews)-1]*float64(reviwsCoeff))
			prices = append(prices, float64(game.Price))
			revenues = append(revenues, prices[len(prices)-1]*owners[len(owners)-1]*utils.RevenueCoeff())
		}

		data.MedianReviews = utils.CalculateMedian(reviews)
		data.MedianOwners = utils.CalculateMedian(owners)
		data.MedianPrice = utils.CalculateMedian(prices)
		data.MedianRevenue = utils.CalculateMedian(revenues)
	}

	return data, nil
}

var _ IGameService = &GameService{}