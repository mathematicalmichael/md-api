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
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SimpleLitAPI(ls.LitAPI):
    def setup(self, device):
        self.md = MarkItDown()

    def decode_request(self, request):
        file_obj = request["content"].file
        try:
            file_bytes = file_obj.read()
            filename = request["content"].filename  # Extract filename from the request
            return file_bytes, filename
        finally:
            file_obj.close()  # Explicitly close the file object

    def predict(self, file_data_and_name):
        file_data, original_filename = file_data_and_name
        file_ext = os.path.splitext(original_filename)[1]
        # md.convert wants a file path. we are receiving
        # a request, so we need to make it look like its on disk
        # use tempfile to create a file-like object
        # `NamedTemporaryFile` will handle cleanup after the `with` block
        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix=file_ext) as f:
                f.write(file_data)
                f.flush()  # Ensure all data is written to the file
                filename = f.name
                logger.debug(f"{filename=}, {file_ext=}")
                result = self.md.convert(filename)
                output = result.text_content
        except UnsupportedFormatException:
            output = "Unsupported format"
        return output

    def encode_response(self, output):
        return {"output": output}


if __name__ == "__main__":
    server = ls.LitServer(
        SimpleLitAPI(),
        accelerator="auto",
        max_batch_size=1,
        track_requests=True,
        api_path="/convert",
    )
    server.run(port=8000, host="0.0.0.0", log_level=LOG_LEVEL.lower())
