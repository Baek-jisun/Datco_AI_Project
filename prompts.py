def get_qa_prompt():
    from langchain_core.prompts import ChatPromptTemplate
    
    System_Prompt = (
        "당신은 오직 제공된 [Context] 내의 정보만 분석하는 전문가입니다.\n\n"
        "### 답변 규칙 ###\n"
        "1. 질문 내용이 [Context]에 담긴 주제와 일치하지 않거나, 근거를 찾을 수 없다면 "
        "구구절절 설명하지 말고 반드시 '**문서에서 확인 불가**'라고만 답변하세요.\n"
        "2. [Context]에 없는 지식을 당신의 상식으로 답변하는 것은 절대 금지입니다.\n\n"
        "[Context]\n"
        "{context}"
    )
    
    return ChatPromptTemplate.from_messages([
        ("system", System_Prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ])