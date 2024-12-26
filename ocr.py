# server.py
import logging
import os
import tempfile
import tracemalloc
from io import BytesIO

import easyocr
import litserve as ls

tracemalloc.start()
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
NUM_API_SERVERS = int(os.environ.get("NUM_API_SERVERS", 4))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class OCRAPI(ls.LitAPI):
    def setup(self, device):
        self.ocr = easyocr.Reader(["en"])

    def decode_request(self, request):
        file_obj = request["content"]
        try:
            logger.info("Processing file")
            file_bytes = file_obj.file.read()
            filename = request["content"].filename  # Extract filename from the request
            return file_bytes, filename
        except AttributeError:
            if "http" in file_obj:
                logger.info("Processing URL")
                return None, file_obj
        finally:
            if not isinstance(file_obj, str):
                file_obj.file.close()  # Explicitly close the file object

    def predict(self, file_data_and_name):
        file_data, original_filename = file_data_and_name
        if file_data is None:  # URL support
            logger.debug(f"Using {original_filename}")
            return self.ocr.readtext(original_filename, detail=0)
        try:
            output = self.ocr.readtext(file_data, detail=0)
        except Exception as e:
            output = "Unsupported format"
        return output

    def encode_response(self, output):
        return {"output": " ".join(output)}


if __name__ == "__main__":
    server = ls.LitServer(
        OCRAPI(),
        accelerator="auto",
        max_batch_size=1,
        track_requests=True,
        api_path="/convert",
    )
    server.run(
        port=8000,
        host="0.0.0.0",
        num_api_servers=NUM_API_SERVERS,
        log_level=LOG_LEVEL.lower(),
    )
