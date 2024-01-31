import os
from enum import Enum
from util.config import Config


# class DefaultAssets(Enum):
#     """Represents id of default assets."""

#     IEEEVR2022Ogawa = "IEEEVR2022Ogawa"
#     IEEEVR2022Hoshikawa = "IEEEVR2022Hoshikawa"
#     CHI2021Fujita = "CHI2021Fujita"
#     EdanMeyerVpt = "EdanMeyerVpt"
#     EdanMeyerAlphaCode = "EdanMeyerAlphaCode"
#     SampleLectureLLM01 = "SampleLectureLLM01"

#     @staticmethod
#     def get_all_values():
#         return DefaultAssets.__members__.values()

#     @staticmethod
#     def from_str(asset_id_str):
#         try:
#             return DefaultAssets[asset_id_str]

#         except (AttributeError, KeyError, ValueError):
#             return None


class Asset:
    @staticmethod
    def get_dirpath_pdf_src():
        """Returns a directory path where PDF files are stored."""
        print("\npdf dirpath:")
        print(Config.get_instance().dirpath_data_root)
        return os.path.join(Config.get_instance().dirpath_data_root, "pdf")

    @staticmethod
    def get_dirpath_pdf_concat_img():
        """Returns a directory path where concat images of PDF files are stored."""
        return os.path.join(Config.get_instance().dirpath_data_root, "pdf_concat_img")

    @staticmethod
    def get_dirpath_document_index():
        """Returns a directory path where document index output files are stored."""
        return os.path.join(Config.get_instance().dirpath_data_root, "document_index")

    @staticmethod
    def get_path_pdf_src(asset_id: str):
        """Returns a path of a PDF file."""
        return os.path.join(Asset.get_dirpath_pdf_src(), f"{asset_id}.pdf")

    @staticmethod
    def get_path_pdf_concat_img(asset_id: str):
        """Returns a path of a concat image of a PDF file."""
        return os.path.join(
            Asset.get_dirpath_pdf_concat_img(),
            f"{asset_id}.concat.png",
        )

    @staticmethod
    def get_path_document_index(asset_id: str):
        """Returns a path of a document index output file."""
        return os.path.join(
            Asset.get_dirpath_document_index(),
            f"{asset_id}.index.json",
        )
