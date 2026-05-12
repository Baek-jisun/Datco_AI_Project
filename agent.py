import json
import os
from langchain_ollama import ChatOllama
from langchain.chains.combine_documents import create_stuff_documents_chain
from config import MODEL_NAME
from engine import rag_engine
from prompts import get_qa_prompt

async def stream_answer(query: str, history):
    if rag_engine.compression_retriever is None:
        rag_engine.setup_engine()
    
    llm = ChatOllama(model=MODEL_NAME, temperature=0.02, streaming=True)

    retrieved_docs = rag_engine.compression_retriever.invoke(query)
    
    filtered_docs = retrieved_docs[:12] if retrieved_docs else []

    print(f"\n{'='*85}\n[STEP 1] 엔진 검색 후보군 (TOP {len(filtered_docs)})")
    for i, doc in enumerate(filtered_docs, 1):
        fname = os.path.basename(doc.metadata.get('source', 'unknown'))
        page = doc.metadata.get('page', 0) + 1
        print(f"  {i:>2}순위: {fname:<40} (p.{page})")
    print(f"{'='*85}")

    chain = create_stuff_documents_chain(llm, get_qa_prompt())
    full_response = ""
    
    async for chunk in chain.astream({
        "input": query, 
        "chat_history": history.messages, 
        "context": filtered_docs
    }):
        yield f"data: {json.dumps({'type': 'content', 'delta': chunk})}\n\n"
        full_response += chunk

    temp_sources = []
    seen = set()
    THRESHOLD = 0.12 
    response_words = set([w for w in full_response.split() if len(w) >= 2])

    print(f"\n[STEP 2] 하이브리드 가중치 정렬 분석 (Threshold: {THRESHOLD})")
    print(f"{'-'*85}")
    
    for i, d in enumerate(filtered_docs, 1):
        p = d.metadata.get('page', 0) + 1
        f = os.path.basename(d.metadata.get('source', ''))
        content_words = [w for w in d.page_content.split() if len(w) >= 2]
        if not content_words: continue
        
        match_count = sum(1 for w in content_words if w in response_words)
        match_density = match_count / len(content_words)
        
        search_rank_score = (len(filtered_docs) - i + 1) / len(filtered_docs)
        
        final_score = (search_rank_score * 0.4) + (match_density * 0.6)

        status = "✅ PASS" if match_density >= THRESHOLD else "❌ DROP"
        print(f"{status:^8} | {f[:30]:<35} (p.{p}) | 밀도:{match_density:.4f} | 보정점수:{final_score:.4f}")

        if match_density >= THRESHOLD and f"{f}_{p}" not in seen:
            temp_sources.append({
                "file": f, 
                "page": p, 
                "score": final_score,
                "snippet": d.page_content[:150].replace('\n', ' ') + "..."
            })
            seen.add(f"{f}_{p}")
    
    temp_sources.sort(key=lambda x: x['score'], reverse=True)

    sources = [
        {"file": s['file'], "page": s['page'], "snippet": s['snippet']} 
        for s in temp_sources
    ]
    
    print(f"{'-'*85}")
    print(f"최종 하이브리드 정렬 완료: {len(sources)}건 리스트업")
    print(f"{'-'*85}\n")

    history.add_user_message(query)
    history.add_ai_message(full_response)
    
    yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"
    yield "data: [DONE]\n\n"