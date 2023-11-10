from dataclasses import dataclass, field

from document_index import (
    FoundRelatedPage,
    FoundRelatedLine,
    DocumentMetadata,
)
from ocr import LinePositionWithPageOffset
from video_frame import VideoFrameMetadata


@dataclass
class DocumentScaleViewport:
    """
    Represents a viewport of a document.

    Args:
        document_metadata (DocumentMetadata): The metadata of the document.
        top (int): The top position of the bbox of the viewport (px).
        left (int): The left position of the bbox of the viewport (px).
        right (int): The right position of the bbox of the viewport (px).
        bottom (int): The bottom position of the bbox of the viewport (px).
    """

    document_metadata: DocumentMetadata
    viewport_width: int = field(init=False)
    viewport_height: int = field(init=False)
    top: int
    left: int
    right: int
    bottom: int

    def __post_init__(self):
        self.viewport_width = self.right - self.left
        self.viewport_height = self.bottom - self.top

    def get_relative_dsize_tuple(self):
        """Get the relative size of the viewport to the document."""
        return (
            self.viewport_width / self.document_metadata.width,
            self.viewport_height / self.document_metadata.height,
        )

    def get_absolute_dsize_tuple(self):
        """Get the absolute size of the viewport."""
        return (self.viewport_width, self.viewport_height)

    def get_relative_bbox_tuple(self):
        """Get the relative bbox of the viewport to the document."""
        return (
            (
                self.left / self.document_metadata.width,
                self.top / self.document_metadata.height,
            ),
            (
                self.right / self.document_metadata.width,
                self.bottom / self.document_metadata.height,
            ),
        )

    def get_absolute_bbox_tuple(self):
        """Get the absolute bbox of the viewport."""
        return (self.left, self.top), (self.right, self.bottom)

    def get_size(self):
        """Get the size of the viewport."""
        return self.viewport_width * self.viewport_height


def __estimate_viewport(
    line_position_video_frame: LinePositionWithPageOffset,  # [[left, top], [right, bottom]]
    line_position_document: LinePositionWithPageOffset,  # [[left, top], [right, bottom]]
    video_metadata: VideoFrameMetadata,
    doc_metadata: DocumentMetadata,
):
    # 拡大率を考慮して，viewportのbboxを計算
    # vf_line_dsize = line_position_video_frame.get_box_dsize()
    # doc_line_dsize = line_position_document.get_box_dsize()

    r_vtd = line_position_document.get_height() / line_position_video_frame.get_height()

    lp_vf = line_position_video_frame
    lp_doc = line_position_document

    vf_left_px = lp_doc.get_offset_left() + lp_doc.get_left() - lp_vf.get_left() * r_vtd
    vf_top_px = lp_doc.get_offset_top() + lp_doc.get_top() - lp_vf.get_top() * r_vtd

    vf_right_px = vf_left_px + video_metadata.width * r_vtd
    vf_bottom_px = vf_top_px + video_metadata.height * r_vtd

    return DocumentScaleViewport(
        document_metadata=doc_metadata,
        top=vf_top_px,
        left=vf_left_px,
        right=vf_right_px,
        bottom=vf_bottom_px,
    )


def estimate_viewport_from_line(
    match_result: FoundRelatedLine,
    doc_metadata: DocumentMetadata,
    video_metadata: VideoFrameMetadata,
):
    """Estimate the location of the area in the document from the match result between video and document."""
    return __estimate_viewport(
        line_position_video_frame=match_result.match_src_from_video_frame.position,
        line_position_document=match_result.match_src_from_index.position,
        video_metadata=video_metadata,
        doc_metadata=doc_metadata,
    )


def estimate_viewport_from_page(
    match_result: FoundRelatedPage,
    doc_metadata: DocumentMetadata,
    video_metadata: VideoFrameMetadata,
):
    """
    Estimate the location of the area in the document from the match result between video and document.

    Args:
        viewport (Viewport): The viewport to estimate from.
        camera (Camera): The camera to estimate.

    Returns:
        Camera: The estimated camera.
    """

    slide_height_px = doc_metadata.height / doc_metadata.n_pages
    slide_height = 1 / doc_metadata.n_pages

    result = __estimate_viewport(
        # match_result.ocr_result_video_frame.data[0].position,
        line_position_video_frame=match_result.match_src_from_video_frame.position,
        line_position_document=match_result.match_src_from_index.position,
        video_metadata=video_metadata,
        doc_metadata=doc_metadata,
    )

    # detected_dsize = bbox.get_bbox_dsize(result[2])

    slide_page_area_size = doc_metadata.width * slide_height_px
    detected_area_size = result.get_size()

    is_detected_size_valid = 0.9 <= detected_area_size / slide_page_area_size <= 1.2

    if is_detected_size_valid:
        return result

    # ---
    # If detected_area_size is too large or too small:
    # Re-calculate viewport area as just bbox of matched slide part.
    # ---

    return DocumentScaleViewport(
        document_metadata=doc_metadata,
        top=match_result.i_page * slide_height * doc_metadata.height,
        left=0,
        bottom=(match_result.i_page + 1) * slide_height * doc_metadata.height,
        right=1.0 * doc_metadata.width,
    )
