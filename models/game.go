package models

type Game struct {
	ID      uint   `json:"id" gorm:"primary_key"`
	Title   string `json:"title"`
	Reviews int    `json:"reviews"`
	Tag     []Tag  `json:"tags" gorm:"many2many:user_languages;"`
}
