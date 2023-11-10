import os
import json
from pathlib import Path
from typing import Callable, Any

from pdf import PDFLoader, PDFLoaderResult
from ocr import TesseractOCR, ShapedLineBox
from document_index import DocumentIndex, DocumentMetadata, DocumentType, PageMetadata
from util.asset import DefaultAssets, Asset

# from util import paths
from util.image import binarize_pilimg
from util.config import Config
from util.asset import Asset


class DocumentPDF:
    def __init__(
        self,
        asset_id: str,
        poppler_exe_path: str | Path,
    ):
        pdf_src_path = Asset.get_path_pdf_src(asset_id)

        assert os.path.exists(pdf_src_path)
        assert os.path.exists(poppler_exe_path)

        self.__path_pdf_src = pdf_src_path
        self.__loader = PDFLoader(poppler_exe_path)

        self.__asset_id = DefaultAssets.from_str(asset_id)

        assert self.__asset_id is not None

    def detect_document_type(self, pdf_loader_result: PDFLoaderResult) -> DocumentType:
        """
        Detects PDF document type simply depends on the aspect ratio of the first page.
        If width is larger than height, it is a slide. Else, it is a document.
        """
        page_metadata: PageMetadata = pdf_loader_result.metadata_pages[0]

        return (
            DocumentType.SLIDE
            if page_metadata.width >= page_metadata.height
            else DocumentType.DOCUMENT
        )

    def generate_document_index_data(
        self,
        path_output_dir: str | Path,
        path_tesseract_ocr_bin: str | Path,
        page_start=None,
        page_end=None,
        save_file=True,
        progress_callback: Callable[[float], None] | None = None,
    ):
        pdf_src_basename = self.__asset_id.value

        print("\nConverting pdf into image")
        pdf2img_result = self.__loader.convert_pdf_to_img(
            self.__path_pdf_src,
            i_start=page_start,
            i_end=page_end,
            concat_margin_y_px=0,
        )

        # You shold use .jpg extension for the output file, because .png has a pixel limit.
        pdf2img_result.image_concat.save(
            os.path.join(path_output_dir, f"{pdf_src_basename}.concat.png")
        )

        ocr_result_pages: list[list[ShapedLineBox]] = []
        n_pages = pdf2img_result.n_pages

        ocr_tool = TesseractOCR(path_tesseract_ocr_bin)

        for i in range(n_pages):
            print(f"\nProcessing OCR to image No.{i} / {n_pages - 1}")

            if progress_callback is not None:
                progress_callback(i / n_pages - 1)

            img_page = pdf2img_result.image_pages[i]
            page_metadata: PageMetadata = pdf2img_result.metadata_pages[i]

            img_gray = binarize_pilimg(img_page)

            ocr_linebox_object_result = ocr_tool.extract(
                img_gray,
                "eng",
                default_offset_left=0,
                default_offset_top=page_metadata.offset_top,
            )

            ocr_result_pages.append(ocr_linebox_object_result.data)

        doc_type = self.detect_document_type(pdf2img_result)

        document_index_data = DocumentIndex(
            index_data=ocr_result_pages,
            metadata=DocumentMetadata(
                metadata_pages=pdf2img_result.metadata_pages,
                width=pdf2img_result.width,
                height=pdf2img_result.height,
                n_pages=pdf2img_result.n_pages,
                asset_id=self.__asset_id,
                doc_type=doc_type,
            ),
        )

        if save_file:
            os.makedirs(path_output_dir, exist_ok=True)
            write_file_path = os.path.join(
                path_output_dir, f"{pdf_src_basename}.index.json"
            )
            with open(write_file_path, "w", encoding="utf-8") as fp:
                json.dump(document_index_data.to_json_serializable(), fp)
                print(f"Index data saved as {write_file_path}")

        return document_index_data

    async def ws_generate_document_index_data(
        self,
        websocketInstance: Any,
        path_output_dir: str | Path,
        path_tesseract_ocr_bin: str | Path,
        page_start=None,
        page_end=None,
        save_file=True,
        progress_callback: Callable[[float], None] | None = None,
    ):
        await websocketInstance.send("progress=0%")
        pdf_src_basename = self.__asset_id.value

        print("\nConverting pdf into image")
        pdf2img_result = self.__loader.convert_pdf_to_img(
            self.__path_pdf_src,
            i_start=page_start,
            i_end=page_end,
            concat_margin_y_px=0,
        )

        # You shold use .jpg extension for the output file, because .png has a pixel limit.

        pdf2img_result.image_concat.save(
            os.path.join(path_output_dir, f"{pdf_src_basename}.concat.png")
        )

        ocr_result_pages: list[list[ShapedLineBox]] = []
        n_pages = pdf2img_result.n_pages

        ocr_tool = TesseractOCR(path_tesseract_ocr_bin)

        for i in range(n_pages):
            await websocketInstance.send(f"progress={int(100 * i / (n_pages - 1))}%")
            print(f"\nProcessing OCR to image No.{i} / {n_pages - 1}")

            if progress_callback is not None:
                progress_callback(i / n_pages - 1)

            img_page = pdf2img_result.image_pages[i]
            page_metadata: PageMetadata = pdf2img_result.metadata_pages[i]

            img_gray = binarize_pilimg(img_page)

            ocr_linebox_object_result = ocr_tool.extract(
                img_gray,
                "eng",
                default_offset_left=0,
                default_offset_top=page_metadata.offset_top,
            )

            ocr_result_pages.append(ocr_linebox_object_result.data)

        doc_type = self.detect_document_type(pdf2img_result)

        document_index_data = DocumentIndex(
            index_data=ocr_result_pages,
            metadata=DocumentMetadata(
                metadata_pages=pdf2img_result.metadata_pages,
                width=pdf2img_result.width,
                height=pdf2img_result.height,
                n_pages=pdf2img_result.n_pages,
                asset_id=self.__asset_id,
                doc_type=doc_type,
            ),
        )

        if save_file:
            os.makedirs(path_output_dir, exist_ok=True)
            write_file_path = os.path.join(
                path_output_dir, f"{pdf_src_basename}.index.json"
            )
            with open(write_file_path, "w", encoding="utf-8") as fp:
                json.dump(document_index_data.to_json_serializable(), fp)
                print(f"Index data saved as {write_file_path}")

        return document_index_data


if __name__ == "__main__":
    targets = [asset_id.value for asset_id in DefaultAssets.get_all_values()]

    for asset_id in targets:
        print(f"Current Attempt: {asset_id}")
        DocumentPDF(
            asset_id,
            Config.get_instance().path_poppler_exe,
        ).generate_document_index_data(
            path_output_dir=Asset.get_dirpath_document_index(),
            path_tesseract_ocr_bin=Config.get_instance().path_tesseract_ocr_exe,
        )
