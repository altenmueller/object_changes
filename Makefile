install: create-db
	pip install -r requirements.txt

create-db:
	python model.py

clean:
	rm test.db
	python model.py

web: test
	FLASK_APP=web.py flask run

test:
	flake8 .
