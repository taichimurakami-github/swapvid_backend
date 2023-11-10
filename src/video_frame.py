from dataclasses import dataclass, field
from PIL.Image import Image

from util.image import cvt_dataurl_to_pil_grayscale


@dataclass
class VideoFrameMetadata:
    """
    Dataclass for VideoFrameImage.metadata

    @property
    width: width of video frame image (px)
    height: height of video frame image (px)
    channel: number of channels of video frame image
    """

    width: int
    height: int
    channel: int


@dataclass
class VideoFrameImage:
    """Represents a video frame image."""

    data: Image
    metadata: VideoFrameMetadata = field(init=False)

    def __post_init__(self):
        self.data = self.data.copy()
        self.metadata = VideoFrameMetadata(
            width=self.data.size[0],
            height=self.data.size[1],
            channel=self.data.getbands(),
        )

    @staticmethod
    def from_dataurl(dataurl: str):
        """A factory method to create from dataurl.""" ""
        pil_video_frame = cvt_dataurl_to_pil_grayscale(dataurl)
        return VideoFrameImage(data=pil_video_frame)

    def get_grayscale(self):
        """Get grayscale image."""
        return self.data.convert("L")

    def get_binary(self, bin_thresh=100, maxval=255):
        """Get binary image."""
        return self.get_grayscale().point(lambda p: maxval if p > bin_thresh else 0)

    def resize(self, width_px: int, height_px: int):
        """Get the VideoFrameImage instance of resized one."""
        resized_pil = self.data.resize((width_px, height_px))
        return VideoFrameImage(resized_pil)
