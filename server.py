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

    # ✅ 빈 페이지 포함 + index는 0부터
    result = [
        {
            "index": i,
            "text": page
        }
        for i, page in enumerate(raw_pages)
    ]

    return JSONResponse(content=result)
