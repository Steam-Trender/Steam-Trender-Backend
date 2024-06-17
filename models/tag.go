package models

import (
	"gorm.io/gorm"
)

type Tag struct {
	gorm.Model
	ID    uint   `json:"id" gorm:"primary_key"`
	Title string `json:"title"`
}
