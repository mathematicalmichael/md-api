# server.py
import logging
import os
import tempfile
import tracemalloc

# import uuid
from io import BytesIO

import litserve as ls
from markitdown import MarkItDown
from markitdown._markitdown import UnsupportedFormatException

tracemalloc.start()
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
NUM_API_SERVERS = int(os.environ.get("NUM_API_SERVERS", 4))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DocumentConversionAPI(ls.LitAPI):
    def setup(self, device):
        self.md = MarkItDown()

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
            return self.md.convert(original_filename).text_content
        file_ext = os.path.splitext(original_filename)[1]
        try:
            output = self.extract_text(file_data, file_ext)
        except UnsupportedFormatException:
            output = "Unsupported format"
        return output

    def extract_text(self, file_data, file_ext):
        # md.convert wants a file path. we are receiving
        # a request, so we need to make it look like its on disk
        output = "None"
        with tempfile.NamedTemporaryFile(delete=True, suffix=file_ext) as f:
            f.write(file_data)
            f.flush()  # Ensure all data is written to the file
            filename = f.name
            logger.debug(f"{filename=}, {file_ext=}")
            result = self.md.convert(filename)
            output = result.text_content
        return output

    def encode_response(self, output):
        return {"output": output}


if __name__ == "__main__":
    server = ls.LitServer(
        DocumentConversionAPI(),
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
