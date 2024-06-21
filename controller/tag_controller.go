package controller

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"steamtrender.com/api/service"
)

type ITagController interface {
	IController
	GetAllTags(c *gin.Context)
}

type TagController struct {
	Service service.ITagService
}

func NewTagController(service *service.TagService) *TagController {
	return &TagController{Service: service}
}

var _ IController = &TagController{}

func (controller *TagController) GetAllTags(c *gin.Context) {
	tags, err := controller.Service.GetAllTags()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, tags)
}
