\# AI 챗봇 시스템 설계 문서 (Design Document)



\## 1. 과제 목표 : 복수 개의 PDF 문서를 업로드하여 사용자의 질문에 대한 답변을 생성하고, 해당 답변의 근거가 되는 출처를 함께 제시하는 시스템을 구현



\## 2.  핵심 기능 

* PDF 문서 기반 답변 생성 및 근거 출처 제공 
* 문서에 근거가 없는 경우 "문서에서 확인 불가" 명시
* PDF 텍스트 추출 



\## 3. 사용 아키텍처

* UI : HTML, JS, CSS 
* Server : FastAPI 
* Framework : LangChain 
* Vector DB :ChromaDB
* Methodology/Architecture : RAG
* Embedding : mxbai-embed-large
* LLM : Llama-3-Bllossom



\## 4. 데이터 흐름

* Ingestion: 사용자가 PDF 업로드 → PyMuPDF를 통해 텍스트 추출 → RecursiveCharacterTextSplitter로 청크 분할.
* Indexing: mxbai-embed-large 모델을 통해 벡터화 → ChromaDB에 저장.
* Retrieval: 사용자 질문 수신 → 벡터 유사도 검색을 통해 관련 문서 청크 추출.
* Generation: 질문 + 추출된 문서 + 프롬프트 조합 → Llama-3-Bllossom 모델이 답변 생성 및 출처 표기.



\## 5. 설계 핵심 포인트

* LangChain의 RetrievalQAWithSourcesChain을 활용하여 문서의 페이지 번호를 함께 출력
* 문서에 없는 내용에 대해 허위 답변을 하지 않도록 프롬프트 엔지니어링을 통해 '문서에서 확인 불가' 규칙 강화

