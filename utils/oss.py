import base64
import uuid
from configs.Config import Config
from typing import Optional
from .logger import logging


def upload_image(image: str) -> Optional[str]:
    try:
        # Check if string is base64 image
        if image.startswith("data:image"):
            image_type = image.split("data:image/")[1].split(";")[0]
            image = base64.b64decode(image.split("base64,")[1])
            # Fake upload the image
            file_name = str(uuid.uuid4()) + "." + image_type
            with open(Config.get_oss_config()['PATH'] + '/' + file_name,
                      "wb") as f:
                f.write(image)
            # Return local URL
            return f"http://{Config.get_oss_config()['ADDR']}/{file_name}"
        return None
    except Exception as e:
        logging.error(f"Error uploading image: {e}")
        return None
