
ASSET_SLIDE_01 = CHI2021Fujita
ASSET_SLIDE_02 = IEEEVR2022Ogawa
ASSET_SLIDE_03 = IEEEVR2022Hoshikawa
ASSET_SLIDE_04 = SampleLectureLLM01

ASSET_DOCUMENT_01 = EdanMeyerVpt
ASSET_DOCUMENT_02 = EdanMeyerAlphaCode

TARGET = ASSET_SLIDE_01

create-document-index:
	python3 ./src/document_pdf.py

init:
	docker compose up --build

run:
	docker compose up

stop:
	docker compose down