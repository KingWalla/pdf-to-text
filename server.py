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

    # 페이지 경계: form feed \f
    raw_pages = content.split("\f")

    # ✅ 핵심: strip() 하지 않는다 (공백/개행만 있는 페이지도 "있는 그대로" 유지)
    # ✅ 필요하면 trailing \n 하나 정도만 정리하는 정도는 가능하지만, 일단 원문 보존이 안전
    pages = [p for p in raw_pages]  # 그대로

    return JSONResponse(content=pages)
