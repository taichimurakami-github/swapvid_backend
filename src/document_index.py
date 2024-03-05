import json
from enum import Enum
from collections.abc import Iterable
from dataclasses import dataclass, field

from ocr import ShapedLineBox, OCRResult, LinePositionWithPageOffset
from util import text
from util.base_class import JSONSerializableData


class DocumentType(Enum):
    SLIDE = "slide"
    DOCUMENT = "document"

    @staticmethod
    def from_str(document_type: str):
        try:
            return DocumentType[document_type.upper()]

        except (AttributeError, KeyError, ValueError):
            None


@dataclass
class PageMetadata(JSONSerializableData):
    width: int
    height: int
    offset_top: int
    page_id: int

    def get_as_tuple(self) -> tuple[int, int, int]:
        return self.width, self.height, self.offset_top

    def to_json_serializable(self):
        return self.get_as_tuple()


@dataclass
class DocumentMetadata(JSONSerializableData):
    asset_id: str
    width: int
    height: int
    n_pages: int
    doc_type: DocumentType
    metadata_pages: list[PageMetadata]

    def to_json_serializable(self):
        dict_fmt = self.__dict__.copy()

        # Convert json unserializable data to serializable data
        dict_fmt["asset_id"] = self.asset_id
        dict_fmt["doc_type"] = self.doc_type.value
        dict_fmt["metadata_pages"] = [
            page_metadata.to_json_serializable()
            for page_metadata in self.metadata_pages
        ]

        return dict_fmt


@dataclass
class FoundRelatedPage:
    i_page: int
    match_src_from_index: ShapedLineBox
    match_src_from_video_frame: ShapedLineBox
    ngram_score: float
    sq_match_score: float


@dataclass
class FoundRelatedLine:
    i_line_video_frame: int
    i_line_index_data: int
    match_src_from_index: ShapedLineBox
    match_src_from_video_frame: ShapedLineBox
    ngram_score: float
    sq_match_score: float


@dataclass
class ShapedLineBoxOutput:
    content: str
    position: Iterable[Iterable[int, int], Iterable[int, int], Iterable[int, int]]


@dataclass
class DocumentIndexOutput:
    index_data: list[list[ShapedLineBoxOutput]]
    document_metadata: DocumentMetadata


@dataclass
class DocumentIndex(JSONSerializableData):
    metadata: DocumentMetadata

    index_data: list[
        list[ShapedLineBox]
    ]  # A list consists of list of all OCRResult.data in each page.

    concat_index_data: list[ShapedLineBox] = field(
        init=False
    )  # A list consists of all OCRResult.data in index_data, without separating by pages.

    def __post_init__(self):
        self.concat_index_data = self.__get_concat_linebox_data()

    def get_the_page_index_data(self, i_page):
        return self.index_data[i_page]

    def to_json_serializable(self):
        json_serializable_index_data = []

        for index_data in self.index_data:
            json_serializable_index_data.append([])
            for shaped_linebox in index_data:
                json_serializable_index_data[-1].append(
                    shaped_linebox.to_json_serializable()
                )

        return {
            "index_data": json_serializable_index_data,
            "metadata": self.metadata.to_json_serializable(),
        }

    @staticmethod
    def from_output_file(path_index_output: str):
        """Loads the index data from output json file."""

        with open(path_index_output, "r") as fp:
            index_output_raw: DocumentIndexOutput = json.load(fp)

            index_data_output = index_output_raw["index_data"]
            metadata_output = index_output_raw["metadata"]

            # Type check for index_data
            # Check the data structure of the first content in the first page.
            assert (
                isinstance(index_data_output, Iterable)
                and isinstance(index_data_output[0], Iterable)
                and len(index_data_output[0]) > 0
                and isinstance(index_data_output[0][0], dict)
                and isinstance(index_data_output[0][0]["content"], str)
                and len(index_data_output[0][0]["position"]) == 3
            )  # If index_data is empty, then it's invalid data.

            index_data_converted: list[list[ShapedLineBox]] = []

            for index_list_of_page in index_data_output:
                index_data_converted.append([])
                for linebox in index_list_of_page:
                    index_data_converted[-1].append(
                        ShapedLineBox(
                            content=linebox["content"],
                            position=LinePositionWithPageOffset(linebox["position"]),
                        )
                    )

            # Type check for metadata
            # assert (
            #     isinstance(metadata_output, dict)
            #     and isinstance(metadata_output["asset_id"], str)
            #     and isinstance(metadata_output["width"], int)
            #     and isinstance(metadata_output["height"], int)
            #     and isinstance(metadata_output["n_pages"], int)
            #     and DocumentType.from_str(metadata_output["doc_type"]) in DocumentType
            #     and len(metadata_output["metadata_pages"]) > 0
            #     and len(metadata_output["metadata_pages"][0]) == 3
            #     and isinstance(metadata_output["metadata_pages"][0][0], int)
            # )

            metadata_converted = DocumentMetadata(
                asset_id=metadata_output["asset_id"],
                width=metadata_output["width"],
                height=metadata_output["height"],
                n_pages=metadata_output["n_pages"],
                doc_type=DocumentType.from_str(metadata_output["doc_type"]),
                metadata_pages=metadata_output["metadata_pages"],
            )

            return DocumentIndex(
                index_data=index_data_converted, metadata=metadata_converted
            )

    # Concats ocr result of each page
    def __get_concat_linebox_data(self) -> OCRResult:
        data_concat: list[ShapedLineBox] = []

        for shaped_lineboxes_of_all_pages in self.index_data:
            for shaped_lineboxes_of_page in shaped_lineboxes_of_all_pages:
                data_concat.append(shaped_lineboxes_of_page)

        return data_concat

    def search_most_matching_line(
        self,
        ocr_result_video_frame: OCRResult,
        max_n_series=3,
        th_valid_similarity_ngram=0.75,
        th_valid_similarity_sqmatch=0.7,
        th_valid_str_length=10,
        th_valid_strlen_rate_min=0.8,
    ):
        """Searches for the most matching line between document index data and OCRResult.data from video frame."""
        n_series = min(len(ocr_result_video_frame.data), max_n_series)

        # If a number of DocumentIndex OCRResult.data is less than n_series,
        # the attempt is considered to be failured.
        if len(self.concat_index_data) < n_series or len(self.concat_index_data) < len(
            ocr_result_video_frame.data
        ):
            raise ValueError(
                "Invalid LBBFMT index data: contents are too short. Please check pdf data and analyze it again."
            )

        if len(ocr_result_video_frame.data) < 1:
            print("WARNING: No LBBFMT target detected.")
            return None

        for n in reversed(range(1, n_series + 1)):  # Attempt order : [n, n-1, ..., 1]
            for i_line_video_frame in range(len(ocr_result_video_frame.data) - n):
                curr_lines_from_video_frame = [
                    ocr_result_video_frame.data[a]
                    for a in range(i_line_video_frame, i_line_video_frame + n)
                ]  # [i, i+1, i+2, ..., i+(n_series - 1)]

                for i_line_index_data in range(len(self.concat_index_data) - n):
                    curr_lines_from_index_data = [
                        self.concat_index_data[b]
                        for b in range(i_line_index_data, i_line_index_data + n)
                    ]

                    all_lines_matched = True

                    for j, _ in enumerate(curr_lines_from_index_data):
                        curr_video_frame_line = curr_lines_from_video_frame[j]
                        curr_index_line = curr_lines_from_index_data[j]

                        if len(curr_index_line.content) < th_valid_str_length:
                            all_lines_matched = False
                            break

                        r_len_1, r_len_2 = text.calc_text_length_rate(
                            curr_index_line.content,
                            curr_video_frame_line.content,
                        )

                        if (
                            r_len_1 < th_valid_strlen_rate_min
                            or r_len_2 < th_valid_strlen_rate_min
                        ):
                            all_lines_matched = False
                            break

                        sm_ngram, sm_sqmatch = text.calc_text_similarity(
                            curr_index_line.content,
                            curr_video_frame_line.content,
                        )

                        if (
                            sm_ngram < th_valid_similarity_ngram
                            or sm_sqmatch < th_valid_similarity_sqmatch
                        ):
                            all_lines_matched = False
                            break

                        # print(
                        #     f"\ncontent '{curr_video_frame_line.content}' \n\nfrom video matched (ngram={sm_ngram}, sqmatch={sm_sqmatch})"
                        # )

                    if all_lines_matched:
                        return FoundRelatedLine(
                            i_line_video_frame=i_line_video_frame,
                            i_line_index_data=i_line_index_data,
                            match_src_from_index=curr_index_line,
                            match_src_from_video_frame=curr_video_frame_line,
                            ngram_score=sm_ngram,
                            sq_match_score=sm_sqmatch,
                        )

        return None

    def search_most_matching_page(
        self,
        ocr_result_video_frame: OCRResult,
        th_valid_similarity_ngram=0.75,
        th_valid_similarity_sqmatch=0.7,
        th_valid_str_length=10,
        th_valid_strlen_rate_min=0.8,
    ):
        """Searches for the most matching page between document index data and OCRResult.data from video frame."""
        prev_found_related_page_list: list[FoundRelatedPage] = []

        for curr_linebox_from_vf in ocr_result_video_frame.data:
            # targetで検出されたOCR検出結果を上から順に操作
            # スライド差分は上から下に展開されるため，必ずタイトルは残る場合が多い
            # or 早い段階でタイトルに該当する部分は出現するはず
            if len(curr_linebox_from_vf.content) < th_valid_str_length:
                continue

            # List of id of pages for next attempt
            # Repeat the attempt for each page in document until it finds one specific related page.
            active_page_id_list_for_next_attempt = (
                [
                    v.i_page for v in prev_found_related_page_list
                ]  # Attempt prev found pages if number of them is more than one page (num of pages > 1)
                if len(prev_found_related_page_list) > 0
                else list(
                    range(self.metadata.n_pages)
                )  # Attempt all pages in document if no related pages are found in previous attempt
            )

            # Find related pages of current linebox from ocr result
            curr_found_related_page_list = self.__get_ocr_result_related_pages(
                curr_linebox_from_video_frame=curr_linebox_from_vf,
                active_page_id_list=active_page_id_list_for_next_attempt,
                th_valid_similarity_ngram=th_valid_similarity_ngram,
                th_valid_similarity_sqmatch=th_valid_similarity_sqmatch,
                th_valid_str_length=th_valid_str_length,
                th_valid_strlen_rate_min=th_valid_strlen_rate_min,
            )

            # CASE 1:
            # If one related page found, then return it
            if len(curr_found_related_page_list) == 1:
                return curr_found_related_page_list[0]

            # CASE 2:
            # If no related page found, then try again with the result of PREVIOUS attempt
            # to attempt again with content from different line of ocr result
            if (
                len(curr_found_related_page_list) == 0
                and len(prev_found_related_page_list) > 0
            ):
                curr_found_related_page_list = prev_found_related_page_list

            # CASE 3:
            # If multiple related pages found, then try again with the result of CURRENT attempt
            # to specify the most matching page
            # print(
            #     f"\nprev_found_related_page_list={prev_found_related_page_list},\ncurr_result={curr_found_related_page_list}"
            # )
            prev_found_related_page_list = curr_found_related_page_list

        # If there are still multiple related pages found
        # after attempts for all lines from ocr result finished,
        # then return the most matching page by calculating the total score of each matching algorithm.
        # The page with highest score will be considered as "most matching".
        if len(prev_found_related_page_list) > 0:
            most_matching_page = prev_found_related_page_list[0]

            for found_page in prev_found_related_page_list:
                score_of_most_matching_page = (
                    most_matching_page.ngram_score + most_matching_page.sq_match_score
                )  # sm_ngram + sm_sqmatch
                score_of_found_page = (
                    found_page.ngram_score + found_page.sq_match_score
                )  # sm_ngram + sm_sqmatch

                if score_of_found_page > score_of_most_matching_page:
                    most_matching_page = found_page

            return most_matching_page

        # Failed to match. Return an empty tuple.
        return None

    def __get_ocr_result_related_pages(
        self,
        curr_linebox_from_video_frame: ShapedLineBox,
        active_page_id_list: list[int],
        th_valid_similarity_ngram: float,
        th_valid_similarity_sqmatch: float,
        th_valid_str_length: float,
        th_valid_strlen_rate_min: float,
    ):
        result: list[FoundRelatedPage] = []
        for i_page, ocr_result_page in enumerate(self.index_data):
            if i_page not in active_page_id_list:
                continue

            for curr_linebox_from_index in ocr_result_page:
                if len(curr_linebox_from_index.content) < th_valid_str_length:
                    continue

                r_len_1, r_len_2 = text.calc_text_length_rate(
                    curr_linebox_from_index.content,
                    curr_linebox_from_video_frame.content,
                )

                if (
                    r_len_1 < th_valid_strlen_rate_min
                    or r_len_2 < th_valid_strlen_rate_min
                ):
                    continue

                sm_ngram, sm_sqmatch = text.calc_text_similarity(
                    curr_linebox_from_index.content,
                    curr_linebox_from_video_frame.content,
                )

                if (
                    sm_ngram < th_valid_similarity_ngram
                    or sm_sqmatch < th_valid_similarity_sqmatch
                ):
                    continue

                # print(
                #     f"\nContent {curr_linebox_from_video_frame.content} found in page {i_page}."
                # )

                # Add this page id for next attempt targets
                # And trying next page

                result.append(
                    FoundRelatedPage(
                        i_page=i_page,
                        match_src_from_index=curr_linebox_from_index,
                        match_src_from_video_frame=curr_linebox_from_video_frame,
                        ngram_score=sm_ngram,
                        sq_match_score=sm_sqmatch,
                    )
                )

        return result
