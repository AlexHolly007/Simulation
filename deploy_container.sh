docker-compose down --remove-orphans
docker rmi simulation_main_app_img simulation_microservice_img -f 2>/dev/null
docker-compose up --build