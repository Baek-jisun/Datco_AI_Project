import json
import os
import uuid  
from langchain_ollama import ChatOllama
from langchain.chains.combine_documents import create_stuff_documents_chain
from config import MODEL_NAME, SOURCE_DIR 
from engine import rag_engine
from prompts import get_qa_prompt

async def stream_answer(query: str, history):
    if rag_engine.compression_retriever is None:
        rag_engine.setup_engine()
    
    if not rag_engine.compression_retriever:
        yield f"data: {json.dumps({'type': 'content', 'delta': '업로드된 문서가 없습니다.'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    llm = ChatOllama(model=MODEL_NAME, temperature=0, streaming=True)

    retrieved_docs = rag_engine.compression_retriever.invoke(query)
    filtered_docs = [] 
    
    if retrieved_docs:
        first_doc = retrieved_docs[0]
        filtered_docs.append(first_doc)
        first_file = os.path.basename(first_doc.metadata.get('source', ''))
        for doc in retrieved_docs[1:4]:
            curr_file = os.path.basename(doc.metadata.get('source', ''))
            if curr_file == first_file or len(filtered_docs) < 2:
                filtered_docs.append(doc)

    if not filtered_docs:
        yield f"data: {json.dumps({'type': 'content', 'delta': '문서에서 확인 불가'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    chain = create_stuff_documents_chain(llm, get_qa_prompt())
    full_response = ""
    async for chunk in chain.astream({"input": query, "chat_history": history.messages, "context": filtered_docs}):
        yield f"data: {json.dumps({'type': 'content', 'delta': chunk})}\n\n"
        full_response += chunk

    stop_keywords = ["확인 불가", "정보 없음", "내용 없음", "찾을 수 없습니다"]
    if not any(keyword in full_response for keyword in stop_keywords):
        seen = set()
        sources = []
        
        memo_content = f"질문: {query}\n\n"
        memo_content += f"AI 답변:\n{full_response}\n\n"
        memo_content += "="*50 + "\n[참조 근거 원문]\n"

        for d in filtered_docs:
            p = d.metadata.get('page', 0) + 1
            f = os.path.basename(d.metadata.get('source', ''))
            if f"{f}_{p}" not in seen:
                sources.append({"file": f, "page": p, "snippet": d.page_content[:150] + "..."})
                memo_content += f"\n▶ 출처: {f} (p.{p})\n"
                memo_content += f"내용: {d.page_content.strip()}\n"
                memo_content += "-"*30 + "\n"
                seen.add(f"{f}_{p}")

        file_name = f"memo_{uuid.uuid4().hex[:8]}.txt"
        file_path = os.path.join(SOURCE_DIR, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f_out:
            f_out.write(memo_content)

        yield f"data: {json.dumps({'type': 'sources', 'data': sources, 'download_url': file_name})}\n\n"
    
    yield "data: [DONE]\n\n"