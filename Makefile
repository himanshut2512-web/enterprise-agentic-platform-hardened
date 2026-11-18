.PHONY: install api ui test
install:
	pip install -e .[dev]
api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
ui:
	streamlit run ui/app.py --server.port 8501
test:
	pytest -q
