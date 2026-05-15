# README.md 입니다.

python -3.12 -m venv finetune_env
.\finetune_env\Scripts\activate
python -m pip install -U pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -U transformers datasets accelerate peft bitsandbytes trl
pip install bitsandbytes-windows

python -3.12 -m venv rag_env
.\rag_env\Scripts\activate
python -m pip install -U pip
pip install fastapi uvicorn python-multipart python-dotenv jinja2
pip install langchain langchain-community langchain-core langchain-ollama langchain-text-splitters
pip install "chromadb>=1.3.5,<2.0.0" langchain-chroma
pip install rank-bm25 FlashRank onnxruntime pypdf pdfplumber requests tqdm

