logs:  ## - Псевдоним для команды просмотра всех логов
	sudo docker compose logs -f

check:  ## - Псевдоним для команды просмотра запущенных контейнеров в docker compose
	sudo docker compose ps -a

help:   ## - Выводит список команд
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

start:  ## - Запускает все контейнеры
	sudo docker compose --env-file env.example up -d --build

stop:  ## - Удаляет все контейнеры
	sudo docker compose down -v --remove-orphans

faust_log: ## - Запуск Faust
	sudo docker compose logs -f faust

make ksql: ## - Запуск ksqlDB CLI
	sudo docker compose exec ksqldb-cli ksql http://ksqldb-server:8088