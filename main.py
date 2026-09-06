from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from schemas import PromptSchema  

from llm_model import get_gpt_answer
from db import session, Base, engine, get_users_requests, add_users_requests

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print('Все таблицы созданы')
    yield

app = FastAPI(
    title='Использование ИИ с GPT',
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/requests')
def get_my_requests(request: Request):
    print(request.client)
    user_ip_address = request.client.host
    from_db = get_users_requests(user_ip_address)
    return {
        'ip_address': user_ip_address, 
        'from_db': from_db
    }


@app.post('/requests', status_code=201)
def send_prompt(request: Request, prompt: PromptSchema = Body(embed=True)):
    answer = get_gpt_answer(prompt)
    if answer is not None:
        user_ip_address = request.client.host
        add_users_requests(ip_address=user_ip_address, prompt=prompt.prompt, response=answer)
        return {
            'answer': answer
        }
    raise HTTPException(status_code=404, detail='No answer')

@app.get('/', response_class=FileResponse)
def get_frontend():
    return FileResponse("index.html")
