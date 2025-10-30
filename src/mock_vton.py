from fastapi import FastAPI, File, UploadFile, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw
import io, datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status":"ok","mock":True,"time":datetime.datetime.utcnow().isoformat()+"Z"}

@app.post("/try-on")
async def try_on(
    user_image: UploadFile = File(...),
    cloth_image: UploadFile = File(...),
    part: str = Form("full_body"),
    output_size: int = Form(1024),
):
    size = min(max(256, int(output_size)), 1536)
    img = Image.new("RGBA", (size, size), (30, 144, 255, 255))
    d = ImageDraw.Draw(img)
    text = f"MOCK VTON\npart={part}\nuser={user_image.filename}\ncloth={cloth_image.filename}"
    d.rectangle([20, 20, size-20, size-20], outline=(255,255,255,200), width=6)
    d.text((40, 40), text, fill=(255,255,255,255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")
