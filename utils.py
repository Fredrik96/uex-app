from PIL import Image
from io import BytesIO
import base64


def img_to_base64(img):
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue())


def base64_to_img(base64_img):
    return Image.open(BytesIO(base64.b64decode(base64_img)))