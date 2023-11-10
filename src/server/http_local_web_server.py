from http.server import HTTPServer
from util.config import Config


class HTTPLocalWebServer:
    def __init__(self, port):
        self.__port = port
        self.__address = (Config().host, self.__port)

    def get_address(self):
        return self.__address

    def listen(self, RequestHandlerClass):
        with HTTPServer(self.__address, RequestHandlerClass) as server:
            print("\n\n###############################################")
            print(f"\n\nNow listening at {self.__address}\n\n")
            print("###############################################\n\n")
            server.serve_forever()
