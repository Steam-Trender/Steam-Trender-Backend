PROJECT = "SteamTrender API"

# make run port=80
run:
	uvicorn app.main:app --host 0.0.0.0 --port $(port) --reload

pretty:
	black .
	isort .


.PHONY: run

