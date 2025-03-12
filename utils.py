import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def kospi():
    KOSPI_URL = 'https://finance.naver.com/sise/'
    res = requests.get(KOSPI_URL)

    selector = '#KOSPI_now'

    soup = BeautifulSoup(res.text, 'html.parser')
    kospi = soup.select_one(selector)
    
    return kospi.text


def openai(api_key, user_input):
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': '너는 사용자와 대화하는 챗봇이야 항상 예의있게 대답해줘'}, # 사용자가 보는 영역 아님
            {'role': 'user', 'content': user_input},
        ]

    )
    return completion.choices[0].message.content

def langchain(user_input):
    llm = init_chat_model("gpt-4o-mini", model_provider="openai")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = InMemoryVectorStore(embeddings)

    # 1. load document - 데이터 불러오기
    loader = WebBaseLoader(
        web_paths=(
            'https://n.news.naver.com/mnews/article/032/0003356061',
        )
    )
    docs = loader.load()

    # 2. data split - 데이터 나누기

    # 텍스트를 교집합이 생기게 자르는 방법
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    all_splits = text_splitter.split_documents(docs)

    # 3. Vector Store - 저장
    _ = vector_store.add_documents(documents=all_splits)

    # 4. retrieve - 유사도 검색
    prompt = hub.pull('rlm/rag-prompt')
    retrieved_docs = vector_store.similarity_search(user_input)
    docs_content = '\n\n'.join(doc.page_content for doc in retrieved_docs)
    prompt = prompt.invoke({'question': user_input, 'context': docs_content})
    answer = llm.invoke(prompt).content

    return answer