[![Build and Push Docker Image](https://github.com/mathematicalmichael/md-api/actions/workflows/docker.yml/badge.svg)](https://github.com/mathematicalmichael/md-api/actions/workflows/docker.yml)
[![Docker Image](https://img.shields.io/docker/v/mindthemath/md-api/latest)](https://hub.docker.com/r/mindthemath/md-api/tags)

# litserve Implementation of Microsoft markitdown

This exposes `markitdown` via API on port 8000 at `/convert`.
The docker image is published at `mathematicalmichael/md-api:latest` [docker-hub](https://hub.docker.com/r/mathematicalmichael/md-api)

## Usage
Make sure you have installed `uv`: `pip install uv` first, or modify the `makefile` appropriately for your environment.
`uv` is used to resolve and install dependencies. It creates the `requirements.txt` file required by docker.

`make run` will build and run the docker image, but the command is

```bash
docker build -t doc-api .
```

```bash
docker run --rm -p 8000:8000 doc-api
```

Alternatively, you can start the server locally (without docker):
```
uv run server.py
```

### Example `client.py` file:
Note: once the server is up, you can run `make docker-test` to run the following script against a local endpoint using the same image. Alternatively,  `make test` will use `uv` to run a local test.

```python
import argparse
import json
from datetime import datetime
from pathlib import Path

import requests

API_URL = "http://127.0.0.1:8000/convert"


def send_request(path):
    try:
        with open(path, "rb") as inputFile:
            # Use a tuple (filename, file object) for 'files'
            response = requests.post(
                API_URL, files={"content": (Path(path).name, inputFile)}
            )
    except FileNotFoundError:
        # passing a URL for markdownit to scrape
        response = requests.post(API_URL, json={"content": path})
    if response.status_code == 200:
        output = json.loads(response.content)["output"]
        save_output(output)
    else:
        print(
            f"Error: Response with status code {response.status_code} - {response.text}"
        )


def save_output(output):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S").lower()
    Path("output").mkdir(exist_ok=True)
    filename = f"output/{timestamp}.md"

    with open(filename, "wb") as output_file:
        output = output.encode("utf-8")
        output_file.write(output)

    print(f"File saved to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send file to markdownit server and receive generated markdown content."
    )
    parser.add_argument("--path", required=True, help="Path for the document file.")
    args = parser.parse_args()

    send_request(args.path)

```

For local data:
```
curl -X POST -F "content=@tests/test_rss.xml;filename=test_rss.xml" http://127.0.0.1:8000/convert
```

For remote data:
```
curl --request POST \
    --url http://0.0.0.0:8000/convert \
    --header 'Content-Type: application/json' \
    --data '{
        "content": "https://wikipedia.org"
    }'
```

## Contributing

Contributions are welcome!

`pip install uv` and the rest should be straightforward - consult the `makefile` for more details.
