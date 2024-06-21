package repository

import (
	"gorm.io/gorm"
	"steamtrender.com/api/schema"
)

type ITagRepository interface {
	IRepository
	GetAllTags() ([]schema.Tag, error)
}

type TagRepository struct {
	*BaseRepository
}

func NewTagRepository(db *gorm.DB) *TagRepository {
	return &TagRepository{BaseRepository: NewBaseRepository(db)}
}

func (repo *TagRepository) GetAllTags() ([]schema.Tag, error) {
	var tags []schema.Tag
	err := repo.DB.Find(&tags).Error
	if err != nil {
		return nil, err
	}
	return tags, nil
}

var _ ITagRepository = &TagRepository{}
