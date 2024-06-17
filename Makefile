PROJECT = "Steam Trender API"

run:
	go run main.go

pretty:
	gofmt -w .

.PHONY: run