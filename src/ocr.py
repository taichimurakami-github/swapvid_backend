from typing import Literal
from dataclasses import dataclass
from collections.abc import Iterable

import pyocr
import pyocr.builders

from util.text import remove_non_ascii, remove_cp932
from util.base_class import JSONSerializableData


@dataclass(frozen=True)
class LinePositionWithPageOffset:
    """Represents LinePosition object with page offset."""

    bbox: Iterable[Iterable[int, int], Iterable[int, int], Iterable[int, int]]

    @staticmethod
    def from_positions(
        top: int,
        left: int,
        right: int,
        bottom: int,
        page_offset_left: int,
        page_offset_top: int,
    ):
        """A factory method to create from positions."""
        return LinePositionWithPageOffset(
            ((left, top), (right, bottom), (page_offset_left, page_offset_top))
        )

    def get_left(self):
        """Get left position of bounding box."""
        return self.bbox[0][0]

    def get_top(self):
        """Get top position of bounding box."""
        return self.bbox[0][1]

    def get_right(self):
        """Get right position of bounding box."""
        return self.bbox[1][0]

    def get_bottom(self):
        """Get bottom position of bounding box."""
        return self.bbox[1][1]

    def get_offset_left(self):
        """Get left offset of bounding box."""
        return self.bbox[2][0]

    def get_offset_top(self):
        """Get top offset of bounding box."""
        return self.bbox[2][1]

    def get_width(self):
        """Get width of bounding box."""
        return self.get_right() - self.get_left()

    def get_height(self):
        """Get height of bounding box."""
        return self.get_bottom() - self.get_top()


@dataclass
class ShapedLineBox(JSONSerializableData):
    """Represents Linebox object with LinePositionWithPageOffset and its content."""

    content: str

    # bounding-box object with page offset : [[left, top], [right, bottom], [offset_left, offset_top]] <- (x,y)[]
    # "offset": [default_offset_left, default_offset_top],  # (x, y)
    position: LinePositionWithPageOffset

    def to_json_serializable(self):
        return {
            "content": self.content,
            "position": self.position.bbox,
        }


# Reference:
# https://gitlab.gnome.org/World/OpenPaperwork/pyocr
class OCRResult:
    """Represents OCR result."""

    # data =
    # [
    #   // list of OCRResult for each page
    #
    #   [
    #     // OCRResult for each page
    #
    #     ShapedLineBox, // LineBox object for each line
    #     ShapedLineBox, // LineBox object for each line
    #     ...
    #   ]
    # ]
    data: list[ShapedLineBox]

    def __init__(
        self,
        linebox_object_list: list[pyocr.builders.LineBox],
        default_offset_top=0,
        default_offset_left=0,
    ):
        self.data = self.__parse_pyocr_linebox_object(
            linebox_object_list, default_offset_top, default_offset_left
        )

    def __parse_pyocr_linebox_object(
        self,
        linebox_object_list: Iterable[pyocr.builders.LineBox],
        default_offset_top=0,
        default_offset_left=0,
        valid_str_length_min=10,
    ):
        result: list[ShapedLineBox] = []

        for linebox_object in linebox_object_list:
            # Remove unicode characters not included in cp932 for windows env.
            # Special characters is not necessary for this matching system.
            content = remove_non_ascii(
                " ".join(
                    # Cautions about ocr_result:--------------------------------------
                    #
                    # ocr_result[i]["content"] contains utf-8 chars which cannot be converted to "cp932" (ex: \u2014).
                    # And, if python want to print something, interpreter will automatically try to convert them into "cp932"
                    # Since that, trying to print 'ocr_result' causes UnicodeEncodeError.
                    # Please be careful to filter unconvertable utf-8 chars before use print functions.
                    #
                    # ----------------------------------------------------------------
                    map(
                        lambda wordbox: remove_cp932(wordbox.content),
                        linebox_object.word_boxes,
                    )
                )
            )

            # Filter and remove if content length is too short
            if len(content) < valid_str_length_min:
                continue

            position = LinePositionWithPageOffset.from_positions(
                left=linebox_object.position[0][0],
                top=linebox_object.position[0][1],
                right=linebox_object.position[1][0],
                bottom=linebox_object.position[1][1],
                page_offset_left=default_offset_left,
                page_offset_top=default_offset_top,
            )

            result.append(
                ShapedLineBox(
                    content,
                    position,
                )
            )

        return result


# https://blog.machine-powers.net/2018/08/04/pyocr-and-tips/
class TesseractOCR:
    """Utility class for OCR using Tesseract OCR engine."""

    def __init__(
        self,
        tesseract_path: str,
    ):
        pyocr.pyocr.tesseract.TESSERACT_CMD = tesseract_path
        tools = pyocr.get_available_tools()

        if len(tools) == 0:
            raise SystemError(
                "No OCR tool found. Please check if you've installed any OCR tool, or the path is correct."
            )

        self.__tool = tools[0]
        self.__builder = pyocr.builders.LineBoxBuilder()

    # def write_extracted_result_as_hOCR_fmt(self, filepath, result):
    #     with open(filepath, "w", encoding="utf-8") as f:
    #         self.builder.write_file(f, result)

    # Pyocr uses Pillow.Image object. NOT OpenCV.
    # https://note.com/djangonotes/n/ne993a087f678
    def extract(
        self,
        pil_image,
        language: Literal["jpn", "eng"],
        default_offset_top=0,
        default_offset_left=0,
    ) -> OCRResult:
        """Perform OCR on given image."""
        # -------------------------------
        # objects from pyocr builders:
        #
        # WordBox = {
        #   content: str
        #   position: [[pt1_x, pt1_y], [pt2_x, pt2_y]] (pt1: left-top, pt2: right-bottom)
        # }
        #
        # LineBox =
        # {
        #   word_boxes: WordBox[],
        #   content: str
        #   position: [[pt1_x, pt1_y], [pt2_x, pt2_y]] (pt1: left-top, pt2: right-bottom)
        # }[]
        # -------------------------------
        linebox_object_list: list[pyocr.builders.LineBox] = self.__tool.image_to_string(
            pil_image,
            lang=language,
            builder=self.__builder,
        )

        return OCRResult(linebox_object_list, default_offset_top, default_offset_left)
