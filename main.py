import os
import threading
import time
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["https://artc-editor.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("videos", exist_ok=True)
os.makedirs("tmp", exist_ok=True)

class RenderRequest(BaseModel):
    script: str
    duration: int

@app.post("/render/")
async def render_script(req: RenderRequest):
    script_id = str(uuid.uuid4())
    duration = req.duration
    lua_path = f"tmp/{script_id}.lua"
    with open(lua_path, "w") as f:
        f.write(req.script)

    output_path = f"videos/{script_id}.mp4"

    try:
        result = subprocess.run(
            ["./bin/artc", lua_path, "-x", "-o", output_path, "-d", str(duration)],
            check=True,
            capture_output=True,
            timeout=60
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"artc failed: {e.stderr.decode()}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="artc command timed out")

    threading.Timer(120, delete_file, args=(output_path,)).start()

    return {"video_url": f"/videos/{script_id}.mp4"}

def delete_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted file: {path}")
    except Exception as e:
        print(f"Failed to delete {path}: {e}")

app.mount("/videos", StaticFiles(directory="videos"), name="videos")

