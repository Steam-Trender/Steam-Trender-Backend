package models

import (
	"gorm.io/gorm"
)

type Game struct {
	gorm.Model
	ID      uint   `json:"id" gorm:"primary_key"`
	Title   string `json:"title"`
	Reviews int    `json:"reviews"`
}
