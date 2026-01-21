from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import subprocess
import tempfile
import os

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/extract")
async def extract_text(
    file: UploadFile = File(...),
    start_index: int = Form(1),  # ✅ 시작 index를 variable로
):
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

    # ✅ 빈 페이지도 유지 (strip은 하되, 제거하지 않음)
    raw_pages = content.split("\f")

    result = []
    for i, page_text in enumerate(raw_pages):
        result.append({
            "index": start_index + i,
            "text": page_text.strip()  # 빈 페이지면 ""
        })

    return JSONResponse(content=result)
