package repository

import (
	"gorm.io/gorm"
	"steamtrender.com/api/schema"
	"time"
)

type IGameRepository interface {
	IRepository
	ReadGames(int, []uint, []uint) ([]schema.Game, error)
	ReadReleaseDate(DateType) (time.Time, error)
}

type GameRepository struct {
	*BaseRepository
}

func NewGameRepository(db *gorm.DB) *GameRepository {
	return &GameRepository{BaseRepository: NewBaseRepository(db)}
}

func (repo *GameRepository) ReadGames(minReviews int, whitelistTagIDs []uint, blacklistTagsIds []uint) ([]schema.Game, error) {
	var games []schema.Game
	query := repo.DB.Model(&schema.Game{}).Preload("Tags")

	// filter by reviews
	query = query.Where("reviews >= ?", minReviews)

	// subquery for whitelist: select games that have all tags in the whitelist.
	if len(whitelistTagIDs) > 0 {
		whitelistSubquery := repo.DB.Table("game_tags").Select("game_id").Where("tag_id IN ?", whitelistTagIDs).Group("game_id").Having("COUNT(DISTINCT tag_id) = ?", len(whitelistTagIDs))
		query = query.Where("id IN (?)", whitelistSubquery)
	}

	// subquery for blacklist: remove games that have any tag in the blacklist.
	if len(blacklistTagsIds) > 0 {
		blacklistSubquery := repo.DB.Table("game_tags").Select("game_id").Where("tag_id IN ?", blacklistTagsIds)
		query = query.Not("id IN (?)", blacklistSubquery)
	}

	err := query.Find(&games).Error
	if err != nil {
		return nil, err
	}
	return games, nil
}

type DateType int

const (
	MinDate DateType = iota
	MaxDate
)

func (repo *GameRepository) ReadReleaseDate(dateType DateType) (time.Time, error) {
	var dateQuery string
	if dateType == MinDate {
		dateQuery = "min(ReleaseDate)"
	} else {
		dateQuery = "max(ReleaseDate)"
	}

	var date time.Time
	err := repo.DB.Model(&schema.Game{}).Select(dateQuery).Row().Scan(&date)
	if err != nil {
		return time.Time{}, err
	}
	return date, nil
}

var _ IGameRepository = &GameRepository{}