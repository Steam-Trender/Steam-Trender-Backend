package service

import (
	"steamtrender.com/api/repository"
	"steamtrender.com/api/schema"
	"steamtrender.com/api/utils"
)

type IGameService interface {
	IService
	AnalyzeCompetitors(float64, int, int, int, []uint, []uint) (schema.CompetitorsData, error)
	AnalyzeTags(float64, int, int, int, []uint) ([]schema.CompetitorsData, error)
}

type GameService struct {
	Repo repository.IGameRepository
}

func NewGameService(repo *repository.GameRepository) *GameService {
	return &GameService{Repo: repo}
}

func (service *GameService) AnalyzeCompetitors(reviwsCoeff float64, minReviews int, minYear int, maxYear int, whitelistTagIDs, blacklistTagIDs []uint) (schema.CompetitorsData, error) {
	games, err := service.Repo.ReadGames(minReviews, minYear, maxYear, whitelistTagIDs, blacklistTagIDs)
	if err != nil {
		return schema.CompetitorsData{}, err
	}

	data := service.AnalyzeGames(games, reviwsCoeff)

	return data, nil
}

func (service *GameService) AnalyzeTags(reviwsCoeff float64, minYear, maxYear, reviews int, tags []uint) ([]schema.CompetitorsData, error) {
	var results []schema.CompetitorsData
	// fix it ^^^
	for _, tag := range tags {
		fakeTags := []uint{tag}
		games, err := service.Repo.ReadGames(reviews, minYear, maxYear, fakeTags, nil)
		if err != nil {
			return nil, err
		}

		data := service.AnalyzeGames(games, reviwsCoeff)
		results = append(results, data)
	}

	return results, nil
}

func (gs *GameService) AnalyzeGames(games []schema.Game, reviewsCoeff float64) schema.CompetitorsData {
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
			owners = append(owners, reviews[len(reviews)-1]*reviewsCoeff)
			prices = append(prices, float64(game.Price))
			revenues = append(revenues, prices[len(prices)-1]*owners[len(owners)-1]*utils.RevenueCoeff())
		}

		data.MedianReviews = utils.CalculateMedian(reviews)
		data.MedianOwners = utils.CalculateMedian(owners)
		data.MedianPrice = utils.CalculateMedian(prices)
		data.MedianRevenue = utils.CalculateMedian(revenues)
	}

	return data
}

var _ IGameService = &GameService{}
