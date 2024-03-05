# import sys
import os
from server.http_local_web_server import HTTPLocalWebServer
from server.http_post_handler_base import HttpPostHandlerBase

from util.config import Config
from util.paths import path_dir_data_base
from util.base_class import JSONSerializableData


class SwapVidBackendFileExplorerResponse(JSONSerializableData):
    pdf_files: list[str]
    index_files: list[str]

    def __init__(self, pdf_files: list[str], index_files: list[str]):
        self.pdf_files = pdf_files
        self.index_files = index_files

    def to_json_serializable(self):
        return {"pdf_files": self.pdf_files, "index_files": self.index_files}


class HttpPostHandler(HttpPostHandlerBase):
    def __init__(self, *args, **kwargs):
        self.SYSTEM_FILES = [".DS_Store"]

        super().__init__(*args, **kwargs)

    def __filter_system_files(self, files: list[str]) -> list[str]:
        return list(filter(lambda f: f not in self.SYSTEM_FILES, files))

    def __get_files_in_pdf_dir(self):
        try:
            return os.listdir(os.path.join(path_dir_data_base, "pdf"))
        except:
            print("[FileExplorerService] Folder '.data/pdf' not found.")
            return []

    def __get_files_in_document_index_dir(self):
        try:
            return os.listdir(os.path.join(path_dir_data_base, "document_index"))
        except:
            print("[FileExplorerService] Folder '.data/document_index' not found.")
            return []

    def do_GET(self):
        print(f"\n\n[FileExplorerService] New request received at {self.path}:")

        pdf_files = self.__get_files_in_pdf_dir()
        index_files = self.__get_files_in_document_index_dir()

        response_data = SwapVidBackendFileExplorerResponse(
            pdf_files=self.__filter_system_files(pdf_files),
            index_files=self.__filter_system_files(index_files),
        )

        body_content = response_data.to_json_serializable()
        self.send_ok_res(body_content, self.headers["Origin"])

    # Handle preflight request caused by the cors problem
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    PORT = Config().port_file_explorer
    server = HTTPLocalWebServer(PORT)
    server.listen(HttpPostHandler)


if __name__ == "__main__":
    main()
