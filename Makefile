reset:
	docker-compose down
	docker volume rm planning-applications_planning_applications_data
	docker-compose build
	docker-compose up

reset_db:
# reset_db should reset only the database - don't assume the scraper or db is running
# just make sure we're going to have the db in the right setup when we've run this 
	@CONTAINER_ID=$$(docker ps -a -q -f name=database); \
	if [ "$$CONTAINER_ID" ]; then \
		docker stop $$CONTAINER_ID; \
		docker rm $$CONTAINER_ID; \
	else \
		echo "Container 'database' does not exist."; \
	fi
	@if [ "$(docker volume ls -q -f name=planning-applications_planning_applications_data)" ]; then \
		docker volume rm planning-applications_planning_applications_data; \
	else \
		echo "Volume 'planning-applications_planning_applications_data' does not exist."; \
	fi
	docker-compose up -d db

run:
	docker-compose run scraper $(lpa)
