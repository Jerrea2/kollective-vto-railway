from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from PIL import Image
import io
import uvicorn
import nest_asyncio
from pyngrok import ngrok
import threading

# Required to allow re-entry into event loop
nest_asyncio.apply()

app = FastAPI()

# Enable CORS for all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CORS-enabled static file handler
class CORSMiddlewareStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

# ✅ Serve clothing images
app.mount(
    "/api/clothing-images",
    CORSMiddlewareStaticFiles(directory="clothing-images"),
    name="clothing-images"
)

# ✅ Try-On API
@app.post("/api/try-on-2d")
async def try_on(userPhoto: UploadFile = File(...), clothingItem: UploadFile = File(...)):
    user_bytes = await userPhoto.read()
    clothing_bytes = await clothingItem.read()

    user_img = Image.open(io.BytesIO(user_bytes)).convert("RGBA").resize((512, 512))
    clothing_img = Image.open(io.BytesIO(clothing_bytes)).convert("RGBA").resize((512, 512))

    result = Image.alpha_composite(user_img, clothing_img)
    result_path = "virtual_tryon_result.png"
    result.save(result_path)

    return FileResponse(result_path, media_type="image/png")

# ✅ Start ngrok tunnel in a separate thread
def start_ngrok():
    url = ngrok.connect(7860)
    print(f"🌐 Public API endpoint: {url}/api/try-on-2d")

if __name__ == "__main__":
    threading.Thread(target=start_ngrok).start()
    uvicorn.run(app, host="0.0.0.0", port=7860)
