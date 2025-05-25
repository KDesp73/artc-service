import os
import threading
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi import Request
from pydantic import BaseModel
import subprocess
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv
import datetime

load_dotenv()

cloudinary.config( 
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key=os.getenv("CLOUDINARY_PUBLIC"), 
    api_secret=os.getenv("CLOUDINARY_SECRET"),
    secure=True
)

allowed_origins = [
    "https://artc-editor.vercel.app",
    "http://192.168.1.8:3000" # Development
]

app = FastAPI()
app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )

os.makedirs("videos", exist_ok=True)
os.makedirs("tmp", exist_ok=True)

class RenderRequest(BaseModel):
    script: str
    duration: int

@app.post("/render")
async def render_script(req: RenderRequest):
    script_id = str(uuid.uuid4())
    duration = req.duration
    lua_path = f"tmp/{script_id}.lua"
    output_path = f"videos/{script_id}.mp4"

    with open(lua_path, "w") as f:
        f.write(req.script)

    try:
        result = subprocess.run(
                ["./bin/artc", lua_path, "-x", "-o", output_path, "-d", str(duration)],
                check=True,
                capture_output=True,
                timeout=60
                )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"{e.stderr}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="artc command timed out")

    try:
        response = cloudinary.uploader.upload(output_path, resource_type="video")

        url = response["secure_url"]
        print(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

    threading.Timer(120, delete_file, args=(lua_path,)).start()
    threading.Timer(120, delete_file, args=(output_path,)).start()

    return {"video_url": url}

def delete_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted file: {path}")
    except Exception as e:
        print(f"Failed to delete {path}: {e}")

app.mount(
    "/videos",
    StaticFiles(directory="videos", html=False),
    name="videos"
)
