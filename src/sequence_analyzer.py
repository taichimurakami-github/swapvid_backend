import os
from dataclasses import dataclass

from document_index import (
    DocumentIndex,
    DocumentType,
    FoundRelatedLine,
    FoundRelatedPage,
)
from ocr import TesseractOCR
from viewport import (
    estimate_viewport_from_line,
    estimate_viewport_from_page,
    DocumentScaleViewport,
)
from video_frame import VideoFrameImage
from util.asset import Asset

# from util import paths


@dataclass
class SequenceAnalyzerResult:
    """
    Result of SequenceAnalyzer.match_content_sequence()
    """

    content_sequence_matched: bool
    document_available: bool
    content_matching_result: FoundRelatedPage | FoundRelatedLine | None
    viewport_estimation_result: DocumentScaleViewport | None


class SequenceAnalyzer:
    """
    Match content sequence (video and document) and generate data used by frontend UI
    """

    __ocr: TesseractOCR
    __document_index_data: dict[str, DocumentIndex]

    def __init__(self, path_tesseract_ocr_bin: str):
        self.__ocr = TesseractOCR(path_tesseract_ocr_bin)
        self.__document_index_data = {}

    def __get_document_index_data(self, asset_id: str) -> DocumentIndex | None:
        if self.__document_index_data.get(asset_id) is None:
            # Load document index data from cached file

            asset_path = Asset.get_path_document_index(asset_id)

            # Check if cached file exists
            if not os.path.exists(asset_path):
                print("[SequenceAnalyzer] Document index cache does not exist.")
                return None

            self.__document_index_data[asset_id] = DocumentIndex.from_output_file(
                asset_path
            )

        return self.__document_index_data[asset_id]

    def match_content_sequence(self, asset_id: str, video_frame: VideoFrameImage):
        """
        Main function of SequenceAnalyzer class.

        :returns: SequenceAnalyzerResult
        """
        document_index: DocumentIndex | None = self.__get_document_index_data(asset_id)

        if document_index is None:
            print(
                "\n[SequenceAnalyzer] Found no document index data. Returning empty result. \n"
            )
            return SequenceAnalyzerResult(
                content_sequence_matched=False,
                content_matching_result=None,
                document_available=False,
                viewport_estimation_result=None,
            )

        video_frame_bin = video_frame.get_binary()

        # Perform OCR on binarized video frame image
        ocr_result_from_video_frame = self.__ocr.extract(video_frame_bin, "eng")
        # print("\n OCR Result from video frame:")
        # pprint.pprint(ocr_result_from_video_frame.data)

        # Perform content matching on OCR result
        match document_index.metadata.doc_type:
            case DocumentType.SLIDE:
                most_matching_page = document_index.search_most_matching_page(
                    ocr_result_from_video_frame
                )

                estimated_viewport = None
                content_matched = most_matching_page is not None

                if content_matched:
                    estimated_viewport = estimate_viewport_from_page(
                        match_result=most_matching_page,
                        doc_metadata=document_index.metadata,
                        video_metadata=video_frame.metadata,
                    )

                return SequenceAnalyzerResult(
                    content_sequence_matched=content_matched,
                    viewport_estimation_result=estimated_viewport,
                    content_matching_result=most_matching_page,
                    document_available=True,
                )

            case DocumentType.DOCUMENT:
                most_matching_line = document_index.search_most_matching_line(
                    ocr_result_from_video_frame
                )

                estimated_viewport = None
                content_matched = most_matching_line is not None

                if content_matched:
                    estimated_viewport = estimate_viewport_from_line(
                        match_result=most_matching_line,
                        doc_metadata=document_index.metadata,
                        video_metadata=video_frame.metadata,
                    )

                return SequenceAnalyzerResult(
                    content_sequence_matched=content_matched,
                    viewport_estimation_result=estimated_viewport,
                    content_matching_result=most_matching_line,
                    document_available=True,
                )

        raise ValueError(
            f"[SequenceAnalyzer] Doctype must be either 'SLIDE' or 'DOCUMENT' of DocumentType class, but got {document_index.metadata.doc_type}"
        )
