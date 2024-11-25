export $(grep -v '^#' .env | xargs)
docker container run -p 3307:3306 --name Consumption -e  MYSQL_ROOT_PASSWORD=$SQL_PASSWORD -d mysql:latest