import io
import base64

from PIL import Image, ImageOps


def binarize_pilimg(pilimg: Image, bin_thresh=100, maxval=255) -> Image:
    """Binarizes PIL image.""" ""
    pilimg = pilimg.convert("L")
    return pilimg.point(lambda p: maxval if p > bin_thresh else 0)


def cvt_dataurl_to_decoded_base64url(dataurl: str):
    """Converts dataurl to decoded base64url."""
    encoded_base64url = dataurl.split(",")[1]
    return base64.b64decode(encoded_base64url)


def cvt_dataurl_to_pil_grayscale(dataurl: str):
    """Converts dataurl to PIL grayscale image."""
    return ImageOps.grayscale(
        Image.open(io.BytesIO(cvt_dataurl_to_decoded_base64url(dataurl)))
    )


def cvt_dataurl_to_pil_rgb(dataurl: str):
    """Converts dataurl to PIL RGB image."""
    return Image.open(io.BytesIO(cvt_dataurl_to_decoded_base64url(dataurl)))
