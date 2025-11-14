import os
import cloudinary
import cloudinary.uploader
import requests
import traceback
import time
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")
REPLICATE_MODEL_VERSION = "a02643ce418c0e12bad371c4adbfaec0dd1cb34b034ef37650ef205f92ad6199"
BACKEND_BASE_URL = "https://kollective-vto-railway-production.up.railway.app"
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Cloudinary
cloudinary.config(cloudinary_url=CLOUDINARY_URL)

@app.get("/")
def root():
    return {"message": "Kollective VTO Backend is live"}

def upload_to_cloudinary(img_bytes: bytes, public_id: str = None) -> str:
    try:
        result = cloudinary.uploader.upload(
            img_bytes,
            public_id=public_id,
            resource_type="image",
            folder="vto_uploads",  # Optional: keeps things organized
            overwrite=True
        )
        return result["secure_url"]
    except Exception as e:
        print("Cloudinary upload error:", e)
        raise Exception("Cloudinary upload failed")

def call_replicate(photo_url: str, clothing_url: str) -> str:
    if not REPLICATE_API_KEY:
        raise Exception("REPLICATE_API_KEY not set")
    api_url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "version": REPLICATE_MODEL_VERSION,
        "input": {
            "image": photo_url,
            "garment": clothing_url,
            "part": "upper_body",
        }
    }
    print("REPLICATE PAYLOAD:", payload)
    response = requests.post(api_url, headers=headers, json=payload)
    print("REPLICATE response:", response.text)
    if response.status_code != 201:
        raise Exception(f"Replicate API error: {response.text}")
    prediction = response.json()
    prediction_url = prediction["urls"]["get"]
    status = prediction["status"]

    while status not in ["succeeded", "failed", "canceled"]:
        time.sleep(2)
        poll_response = requests.get(prediction_url, headers=headers)
        poll = poll_response.json()
        status = poll["status"]
        print("REPLICATE POLLING STATUS:", status)

    if status == "succeeded":
        output_url = poll["output"][0] if isinstance(poll["output"], list) else poll["output"]
        print("REPLICATE SUCCEEDED, OUTPUT URL:", output_url)
        return output_url
    else:
        print("Replicate failed:", poll)
        raise Exception("Replicate try-on failed.")

@app.get("/api/clothing-images")
async def get_clothing_images():
    folder_path = "static/clothing-images"
    try:
        if not os.path.exists(folder_path):
            return JSONResponse(status_code=404, content={"error": "Clothing images folder not found."})
        files = os.listdir(folder_path)
        image_urls = [
            f"{BACKEND_BASE_URL}/static/clothing-images/{file}"
            for file in files
            if file.lower().endswith(".png") or file.lower().endswith(".jpg")
        ]
        return JSONResponse(content=image_urls)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/try-on-2d")
async def try_on_2d(
    image: UploadFile = File(...),
    clothing_filename: str = Form(...)
):
    print("TRY-ON ENDPOINT HIT")
    try:
        photo_bytes = await image.read()
        print("Photo bytes received:", len(photo_bytes))

        # Upload user photo to Cloudinary
        print("Uploading user photo to Cloudinary...")
        photo_url = upload_to_cloudinary(photo_bytes, public_id=None)
        print("User photo uploaded:", photo_url)

        # Construct clothing image public URL (use static/ directly)
        clothing_url = f"{BACKEND_BASE_URL}/static/clothing-images/{clothing_filename}"
        print("Clothing URL:", clothing_url)

        # Call Replicate API with both URLs
        print("Calling Replicate API...")
        output_url = call_replicate(photo_url, clothing_url)
        print("Try-on finished, output URL:", output_url)

        return {"output_url": output_url}

    except Exception as e:
        error_str = traceback.format_exc()
        print("ERROR IN TRY-ON ENDPOINT:", error_str)
        return JSONResponse(status_code=500, content={"error": error_str})
