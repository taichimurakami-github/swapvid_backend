import os
import yaml
from pprint import pprint
from pathlib import Path
from dataclasses import dataclass, field

from util.base_class import Singleton


@dataclass
class Config(Singleton):
    """
    Singleton class for the interface of SwapVid backend configuration.
    """

    dirpath_config: str = field(init=False)
    path_config: str = field(init=False)
    path_tesseract_ocr_exe: str = field(init=False)
    path_poppler_exe: str = field(init=False)
    dirpath_data_root: str = field(init=False)

    host: str = field(init=False)
    port_sequence_analyzer: int = field(init=False)
    port_pdf_receiver: int = field(init=False)
    port_pdf_analyzer: int = field(init=False)

    frontend_url: str = field(init=False)

    __initialized: bool = field(init=False, default=False)

    def __init__(self):
        if self.__initialized:
            return

        print("\nInitializing config class...")
        self.dirpath_config = Path(__file__).parent.parent
        self.path_config = os.path.join(self.dirpath_config, "config.yml")

        with open(self.path_config, encoding="utf-8") as fp:
            self.__data = yaml.safe_load(fp)

            print(f"\nConfig file loaded from {self.path_config}")
            pprint(self.__data)

            self.path_tesseract_ocr_exe = self.__data["paths"]["3rd_party"][
                "tesseract_ocr"
            ]

            self.path_poppler_exe = self.__data["paths"]["3rd_party"]["poppler"]

            self.dirpath_data_root = self.__data["paths"]["data_dir_root"]

            self.host = self.__data["host"]

            self.port_sequence_analyzer = self.__data["ports"]["sequence_analyzer"]

            self.port_pdf_receiver = self.__data["ports"]["pdf_receiver"]

            self.port_pdf_analyzer = self.__data["ports"]["pdf_analyzer"]

            self.port_file_explorer = self.__data["ports"]["file_explorer"]

            self.frontend_url = self.__data["frontend"]["url"]

            self.__initialized = True
