package models

import (
	"time"
)

type Game struct {
	ID          uint      `json:"id" gorm:"primary_key"`
	Title       string    `json:"title"`
	Reviews     int       `json:"reviews"`
	Tags        []*Tag    `json:"tags" gorm:"many2many:game_tags;"`
	ReleaseDate time.Time `json:"release"`
	Price       float64   `json:"price"`
}
