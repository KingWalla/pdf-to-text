from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import subprocess
import tempfile
import os

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, "input.pdf")
        txt_path = os.path.join(tmp, "output.txt")

        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        subprocess.run(
            ["pdftotext", "-layout", pdf_path, txt_path],
            check=True
        )

        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    pages = [p.strip() for p in content.split("\f") if p.strip()]
    return JSONResponse(content=[{"page": i + 1, "text": t} for i, t in enumerate(pages)])
