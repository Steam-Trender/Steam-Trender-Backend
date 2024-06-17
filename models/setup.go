package models

import (
	"encoding/csv"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"os"
)

var DB *gorm.DB

func ConnectDatabase(databasePath string) {
	database, err := gorm.Open(sqlite.Open(databasePath), &gorm.Config{})

	if err != nil {
		panic("Failed to connect to database")
	}

	err = database.AutoMigrate(&Game{}, &Tag{})
	if err != nil {
		return
	}

	DB = database
}

func SeedDatabase(filePath string) {
	file, err := os.Open(filePath)

	if err != nil {
		panic("Could not open CSV file")
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		panic("Could not read CSV file")
	}

	for _, record := range records[1:] {
		game := Game{
			Title:   record[0],
			Reviews: 0,
		}
		DB.Create(&game)
	}
}
