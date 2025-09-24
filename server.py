from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import sys

app = FastAPI()


@app.post("/index")
def run_index_files():
    try:
        result = subprocess.run(
            [sys.executable, "index_files.py"], capture_output=True, text=True, check=True)
        return JSONResponse(content={"stdout": result.stdout, "stderr": result.stderr})
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail={
                            "stdout": e.stdout, "stderr": e.stderr, "error": str(e)})


@app.get("/query")
def run_query_db(search_text: str):
    try:
        result = subprocess.run(
            [sys.executable, "query_db.py", search_text], capture_output=True, text=True, check=True)
        return JSONResponse(content={"stdout": result.stdout, "stderr": result.stderr})
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail={
                            "stdout": e.stdout, "stderr": e.stderr, "error": str(e)})
