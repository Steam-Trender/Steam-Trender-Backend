package service

import (
	"steamtrender.com/api/repository"
	"steamtrender.com/api/schema"
)

type ITagService interface {
	IService
	GetAllTags() (schema.Tags, error)
}

type TagService struct {
	Repo repository.ITagRepository
}

func NewTagService(repo *repository.TagRepository) *TagService {
	return &TagService{Repo: repo}
}

func (service *TagService) GetAllTags() (schema.Tags, error) {
	tags, err := service.Repo.GetAllTags()
	if err != nil {
		return schema.Tags{}, err
	}
	return schema.Tags{Tags: tags}, nil
}

var _ ITagService = &TagService{}
