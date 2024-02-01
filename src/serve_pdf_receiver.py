# import sys
import os
import pprint

from server.http_local_web_server import HTTPLocalWebServer
from server.http_post_handler_base import HttpPostHandlerBase
from util.asset import Asset
from util.config import Config


class HttpPostHandler(HttpPostHandlerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_POST(self):
        print(f"\n\n[PdfReceiverService] New request received at {self.path}:")

        filename = self.path.split("/")[-1]
        filedata_bin = self.get_body_content_raw()

        output_path = os.path.join(Asset.get_dirpath_pdf_src(), f"{filename}.pdf")

        with open(output_path, "wb") as fp:
            print(f"\n[PdfReceiverService] Writting received PDF to {output_path}")
            fp.write(filedata_bin)

        self.send_ok_res(None, self.headers["Origin"])

    # Handle preflight request caused by the cors problem
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    PORT = Config().port_pdf_receiver
    server = HTTPLocalWebServer(PORT)
    server.listen(HttpPostHandler)


if __name__ == "__main__":
    main()
