# import sys
import pprint
from dataclasses import dataclass

from server.http_local_web_server import HTTPLocalWebServer
from server.http_post_handler_base import HttpPostHandlerBase, ResponseBodyContent
from sequence_analyzer import (
    SequenceAnalyzer,
    SequenceAnalyzerResult,
)
from video_frame import VideoFrameImage
from util.asset import DefaultAssets
from util.config import Config


@dataclass
class SwapVidSQAnalyzerResponse(ResponseBodyContent):
    """Represents data for response body content."""

    document_available: bool
    estimated_viewport: tuple[tuple[int, int], tuple[int, int]] | None
    matched_content_vf: str | None
    matched_content_doc: str | None
    score_ngram: int | None
    score_sqmatch: int | None

    @staticmethod
    def from_sequence_analyzer_result(result: SequenceAnalyzerResult):
        """A factory method to create from a SequenceAnalyzerResult object."""

        if result.content_matching_result is None:
            return SwapVidSQAnalyzerResponse(
                document_available=result.document_available,
                estimated_viewport=None,
                matched_content_vf=None,
                matched_content_doc=None,
                score_ngram=None,
                score_sqmatch=None,
            )

        return SwapVidSQAnalyzerResponse(
            document_available=result.document_available,
            estimated_viewport=result.viewport_estimation_result.get_relative_bbox_tuple(),
            matched_content_vf=result.content_matching_result.match_src_from_video_frame.content,
            matched_content_doc=result.content_matching_result.match_src_from_index.content,
            score_ngram=result.content_matching_result.ngram_score,
            score_sqmatch=result.content_matching_result.sq_match_score,
        )

    def to_json_serializable(self):
        return self.__dict__


class HttpPostHandler(HttpPostHandlerBase):
    def __init__(self, *args, **kwargs):
        self.__config = Config.get_instance()

        self.__sqa = SequenceAnalyzer(
            self.__config.path_tesseract_ocr_exe,
        )

        super().__init__(*args, **kwargs)

    def do_POST(self):
        # try:

        origin_url = self.headers["Origin"]

        print(f"\n\n\nNew request received at {self.path}:")
        print(
            f"\nCurrent request: Protocol Version={self.protocol_version}, Client Address={self.client_address}, Request Origin={origin_url}"
        )

        asset_id = DefaultAssets.from_str(self.path.split("/")[-1])

        body_content_dataurl_str = self.get_body_content_str()
        video_frame = VideoFrameImage.from_dataurl(body_content_dataurl_str).resize(
            1280, 720
        )

        result = self.__sqa.match_content_sequence(
            asset_id=asset_id,
            video_frame=video_frame,
        )

        res_data = SwapVidSQAnalyzerResponse.from_sequence_analyzer_result(result)
        res_data_dict = res_data.to_json_serializable()

        if result.content_matching_result:
            # print("\nmatch_result_vf")
            # pprint.pprint(result.content_matching_result)
            # print("\nmatch_result_index")
            # pprint.pprint(result.content_matching_result)
            print("\nSequence Analyzer Response:")
            pprint.pprint(res_data)
            print("\n")

        self.send_ok_res(res_data_dict, origin_url)

    # except (TypeError, NameError, ValueError) as err:
    #     print("\nRequest-dependent error occurred:")
    #     print(err)
    #     self.send_error_res(
    #         status_code=500, error_type=err.name, error_content=str(err)
    #     )

    # except (AssertionError, SystemError, SyntaxError, RuntimeError) as err:
    #     print("\nInternal system error occurred:")
    #     print(err)
    #     self.send_error_res(
    #         status_code=500,
    #         error_type="internal_system_error",
    #         error_content=str(err.msg),
    #     )


server = None


def main():
    server = HTTPLocalWebServer(8881)
    server.listen(HttpPostHandler)


if __name__ == "__main__":
    main()
