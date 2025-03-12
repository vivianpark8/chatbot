import os
import requests
import random
from dotenv import load_dotenv
from typing import Union
from fastapi import FastAPI, Request

from utils import kospi, openai, langchain

app = FastAPI()

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
URL = f'http://api.telegram.org/bot{TOKEN}'

@app.post("/") # get 요청이 아니라 post 요청임
# FastAPI 애플리케이션에서 루트 엔드포인트를 의미
# 예를 들어, 서버가 http://localhost:8000/로 실행되고 있으면, / 경로는 이 주소에서 접속할 수 있는 기본 엔드포인트

async def read_root(request: Request):

    body = await request.json()
        
    user_id = body['message']['chat']['id']
    text = body['message']['text']

    if text[0] == '/':
        if text == '/lotto':
            numbers = random.sample(range(1, 46), 6)
            output = str(sorted(numbers))
        elif text == '/kospi':
            output = kospi()
        else:
            output = 'x'
    else:
        #output = openai(OPEN_API_KEY, text)
        output = langchain(text)

    requests.get(f'{URL}/sendMessage?chat_id={user_id}&text={output}') # sendMessage 매소드

    return body

# 텔레그램이 fastapi 통해서 json 구조를 딕셔너리로 바꿔서 출력
# 텔레그램으로 메시지 보내면 텔레그램 서버가 fastapi 통해서 웹 훅 처리