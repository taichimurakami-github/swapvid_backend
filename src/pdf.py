import os
from dataclasses import dataclass
from collections.abc import Iterable

import pdf2image
from PIL.Image import Image, new as new_pil_image

from document_index import PageMetadata


@dataclass
class PDFLoaderResult:
    """Represents PDFLoader result."""

    image_concat: Image
    image_pages: Iterable[Image]
    metadata_pages: Iterable[PageMetadata]
    width: int
    height: int
    n_pages: int


# https://gammasoft.jp/blog/convert-pdf-to-image-by-python/
# https://blog.alivate.com.au/poppler-windows/
# This demo script runs on popper 0.68.0(latest at 2023/5/26)
class PDFLoader:
    """Loads PDF file to parse its content and metadata."""

    def __init__(self, poppler_exe_path: str):
        os.environ["PATH"] = poppler_exe_path

    def __concat_vertically(
        self, images_list: list[Image], concat_margin_y_px: int
    ) -> Image:
        result = images_list[0]

        for i in range(1, len(images_list)):
            img_to_concat = images_list[i]
            dst = new_pil_image(
                "RGB",
                (
                    result.width,
                    result.height + img_to_concat.height + concat_margin_y_px,
                ),
            )
            dst.paste(result, (0, 0))
            dst.paste(img_to_concat, (0, result.height + concat_margin_y_px))
            result = dst

        return result

    def convert_pdf_to_img(
        self, pdf_abs_path: str, i_start=None, i_end=None, concat_margin_y_px=0
    ):
        """Converts PDF file to image."""
        img_pages = pdf2image.convert_from_path(
            pdf_abs_path, first_page=i_start, last_page=i_end
        )
        img_concat = self.__concat_vertically(img_pages, concat_margin_y_px)

        n_pages = len(img_pages)
        offset_top = 0
        metadata: list[PageMetadata] = []
        for i, img_page in enumerate(img_pages):
            w, h = img_page.size  #  w, h = PIL.Image.size
            metadata.append(
                PageMetadata(width=w, height=h, offset_top=offset_top, page_id=i)
            )
            offset_top = offset_top + h + concat_margin_y_px

        pdf_width = metadata[0].width
        pdf_height = offset_top

        return PDFLoaderResult(
            image_concat=img_concat,
            image_pages=img_pages,
            metadata_pages=metadata,
            width=pdf_width,
            height=pdf_height,
            n_pages=n_pages,
        )
