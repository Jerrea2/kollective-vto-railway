import os
import torch
from fastapi import FastAPI
from diffusers import StableDiffusionXLPipeline

print(" IDENTITY GATE HIT  src.inference IMPORTED ")
print("FILE=", __file__)
print("CWD=", os.getcwd())
print("SYS_PATH_HEAD=", __import__("sys").path[:3])

app = FastAPI()

MODEL_PATH = "/workspace/models/sdxl"
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

os.makedirs(MODEL_PATH, exist_ok=True)

def load_pipeline():
    model_index = os.path.join(MODEL_PATH, "model_index.json")

    if not os.path.exists(model_index):
        print(" SDXL not found locally.")
        print("Downloading SDXL into:", MODEL_PATH)

        pipe = StableDiffusionXLPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16,
            variant="fp16"
        )

        pipe.save_pretrained(MODEL_PATH)
        print(" SDXL downloaded and saved.")

    else:
        print(" Loading SDXL from local path:", MODEL_PATH)
        pipe = StableDiffusionXLPipeline.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16
        )

    pipe.to("cuda")
    return pipe


print("Initializing SDXL pipeline...")
pipe = load_pipeline()
print("SDXL READY.")

@app.get("/health")
def health():
    return {"status": "ok"}
