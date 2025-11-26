import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import shutil
from inference import run_inference

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/tryon")
async def tryon(person: UploadFile = File(...), cloth: UploadFile = File(...)):
    try:
        person_path = "/app/person_input.jpg"
        cloth_path = "/app/cloth_input.png"
        output_path = "/app/output.jpg"

        with open(person_path, "wb") as f:
            shutil.copyfileobj(person.file, f)

        with open(cloth_path, "wb") as f:
            shutil.copyfileobj(cloth.file, f)

        result_path = run_inference(
            person_img_path=person_path,
            cloth_img_path=cloth_path,
            output_path=output_path
        )

        return FileResponse(result_path, media_type="image/jpeg")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
