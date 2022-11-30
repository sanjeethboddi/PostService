activate:
	./venv/bin/deactivate
	source ./venv/bin/activate
build:
	docker build -t server .
run:
	docker run -d -p 8080:80 server

	

