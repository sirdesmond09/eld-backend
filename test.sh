docker compose run --rm app sh -c "python manage.py wait_for_db && python manage.py makemigrations core && python manage.py migrate && pytest -s"



# docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME}