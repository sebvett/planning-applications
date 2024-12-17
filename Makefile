reset_db:
	docker-compose down
	docker volume rm planning_applications_data
	docker-compose build
	docker-compose up

run:
	docker-compose run scraper $(lpa)
