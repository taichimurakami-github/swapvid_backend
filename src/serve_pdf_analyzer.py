import asyncio
import os


from websockets.server import serve
from document_pdf import DocumentPDF
from util.config import Config
from util.asset import Asset


# Start message protocol:
# "run=ASSET_ID&i_page_start=I_PAGE_START&i_page_end=I_PAGE_END"
def parse_start_message(message: str):
    # queries = message.split("&")
    # start_query = queries[0] if len(queries) > 0 else queries
    target_asset_id = message.split("=")[1]

    i_page_start: int | None = None
    i_page_end: int | None = None

    # if len(queries) >= 1:
    #     i_page_start = int(queries[1].split("=")[1])

    # if len(queries) >= 2:
    #     i_page_end = int(queries[2].split("=")[1])

    return target_asset_id, i_page_start, i_page_end


def generate_progress_message(progress: float):
    return f"progress={progress}"


def generate_success_message():
    return f"success"


def generate_error_message(message: str):
    return f"error={message}"


async def run_pdf_analyzer(websocket):
    async for message in websocket:
        print("[PDFAnalyzerService] Running pdf analyzer main.")
        print(f"[PDFAnalyzerService] Received message: {message}")

        if "run" in message:
            (asset_id, i_page_start, i_page_end) = parse_start_message(message)

            dindex_cache_exists = os.path.exists(
                Asset.get_path_document_index(asset_id)
            )
            pdf_exists = os.path.exists(Asset.get_path_pdf_src(asset_id))

            # Needs PDF to run
            if not pdf_exists:
                print("[PDFAnalyzerService] PDF file does not exist. Skipping...")
                return await websocket.send("PDF file does not exist. Skipping...")

            # Skip to run if document index cache already exists
            if dindex_cache_exists:
                print(
                    "[PDFAnalyzerService] Document index cache already exists. Skipping..."
                )
                return await websocket.send(
                    "Document index cache already exists. Skipping..."
                )

            # Analyze PDf
            await websocket.send("Now starting PDF analysis.")

            async def progress_handler(progress):
                await websocket.send(f"progress={progress}")

            await DocumentPDF(
                asset_id, Config().path_poppler_exe
            ).generate_document_index_data(
                websocket,
                Asset.get_dirpath_document_index(),
                Config().path_tesseract_ocr_exe,
                page_start=i_page_start,
                page_end=i_page_end,
                progress_callback_async=progress_handler,
            )

            await websocket.send(generate_success_message())

        else:
            await websocket.send(
                generate_error_message(
                    "Invalid message: Needs 'start' command in front of the message."
                )
            )

        return await websocket.close()


async def main():
    HOST = Config().host
    PORT = Config().port_pdf_analyzer

    async with serve(run_pdf_analyzer, HOST, PORT):
        print("\n\n###############################################")
        print(f"\n\nServing PDF analyzer at localhost:8883\n\n")
        print("###############################################\n\n")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
