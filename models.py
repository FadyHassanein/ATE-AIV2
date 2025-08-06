from langchain_openai import ChatOpenAI


chat_model= ChatOpenAI(
    model="gpt-4.1", 
    temperature=0.0, 
    streaming= True,
    api_key="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")
