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
