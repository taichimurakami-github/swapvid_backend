import os
from pathlib import Path
from typing import Callable

from util.asset import DefaultAssets

################################
# Path of a directory
################################
path_dir_data_base = Path(os.path.join(Path(__file__).parent.parent, ".data"))

path_dir_document_pdf_src = Path(os.path.join(str(path_dir_data_base), "pdf"))

path_dir_document_index = Path(os.path.join(str(path_dir_data_base), "document_index"))

path_dir_data_activities_analyzed = Path(
    os.path.join(str(path_dir_data_base), "document_activities_analyzed")
)

################################
# Path of a file
################################
path_file_document_concat_img: Callable[[str], Path] = lambda asset_id: Path(
    os.path.join(str(path_dir_document_index), f"{asset_id}.concat.png")
)

path_file_document_index: Callable[[str], Path] = lambda asset_id: Path(
    os.path.join(str(path_dir_document_index), f"{asset_id}.index.json")
)

path_file_document_pdf: Callable[[str], Path] = lambda asset_id: Path(
    os.path.join(str(path_dir_document_pdf_src), f"{asset_id}.pdf")
)

################################
# Path of tools
################################

path_file_tessearct_bin = Path("/opt/homebrew/bin/tesseract")
# path_file_tessearct_bin = "C:/Users/tchi0/AppData/Local/Tesseract-OCR/tesseract.exe"
