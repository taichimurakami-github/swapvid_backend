
ASSET_SLIDE_01 = CHI2021Fujita
ASSET_SLIDE_02 = IEEEVR2022Ogawa
ASSET_SLIDE_03 = IEEEVR2022Hoshikawa
ASSET_SLIDE_04 = SampleLectureLLM01

ASSET_DOCUMENT_01 = EdanMeyerVpt
ASSET_DOCUMENT_02 = EdanMeyerAlphaCode

TARGET = ASSET_SLIDE_01

generate-index:
	python3 ./document_pdf.py

init:
	docker compose up --build

run:
	docker compose up

run-sqa:
	python3 serve_sequence_analyzer.py

run-pdf-receiver:
	python3 serve_pdf_receiver.py

run-pdf-analyzer:
	python3 serve_pdf_analyzer.py

run-pdf-services:
	python3 serve_pdf_receiver.py & python3 serve_pdf_analyzer.py

freeze-pypackages:
	pip freeze > requirements.txt