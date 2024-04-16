from typing import Union
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import whisper
import os 

from pytube import YouTube
from urllib.parse import unquote

# torch.multiprocessing.set_start_method('spawn')
    
model_path = "medium.pt"
loaded_model = whisper.load_model(model_path)

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/transcribe")
async def model_transcribe(data: dict):
    
    def make_dirs(path):
        # 현재 디렉토리 경로 가져오기
        current_dir = os.getcwd()

        # 'video' 폴더 경로 생성
        path_dir = os.path.join(current_dir, path)

        # 'video' 폴더가 없으면 생성
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
            print(f"'{path_dir}' 폴더가 생성되었습니다.")
        else:
            print(f"'{path_dir}' 폴더가 이미 존재합니다.")
    
    link = unquote(data["link"])
    save_path = unquote(data["save_path"])
    save_path = os.getcwd() + '/' + '/'.join(save_path.split('/')[1:])
    make_dirs(save_path)
    
    yt = YouTube(link)
    path = yt.streams.filter(only_audio=True)[0].download(filename=save_path+"audio.mp3")
    options = dict(task="transcribe", best_of=5)

    results = await asyncio.to_thread(loaded_model.transcribe, path, **options)
    return results

    
if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8200)