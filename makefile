lint:
	uv run black .
	uv run isort --profile black .

requirements.txt: pyproject.toml
	uv pip compile pyproject.toml -o requirements.txt

build: requirements.txt
	docker build -t md-api .

run: build
	docker run --rm -p 8000:8000 md-api

# files pulled from microsoft/markdownit repo
test-img:
	curl -X POST -F "content=@logo.png;filename=logo.png" http://127.0.0.1:8000/convert

tests/:
	git clone https://github.com/microsoft/markitdown.git
	cp -r markitdown/tests/test_files/ tests/
	rm -rf markitdown

test: tests/
	uv run client.py --path tests/test_files.zip
	uv run client.py --path https://wikipedia.org
	./test.sh
	curl -X POST -F "content=@tests/test_rss.xml;filename=test_rss.xml" http://127.0.0.1:8000/convert

docker-test: build tests/
	mkdir -p output/
	docker run --rm --network=host \
		-v ./output:/app/output:rw \
		-v ./tests:/tests:ro \
		-v ./client.py:/app/client.py:ro \
		-u $$(id -u):$$(id -g) \
		md-api \
		python client.py --path /tests/test_files.zip

debug:
	docker run --rm -ti --network=host \
		-v ./output:/app/output:rw \
		-v ./tests:/tests:ro \
		-v ./client.py:/app/client.py:ro \
		-u $$(id -u):$$(id -g) \
		md-api \
		bash

tag: build
	docker tag md-api:latest mindthemath/md-api:$$(date +%Y%m%d)
	docker tag md-api:latest mindthemath/md-api:latest
	docker images

push: tag
	docker push mindthemath/md-api:$$(date +%Y%m%d)
	docker push mindthemath/md-api:latest

clean:
	rm -rf output/ tests/
	rm -rf ~/.docker/config.json

env:
	rm -rf .venv/
	uv sync
