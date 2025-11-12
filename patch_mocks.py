from pathlib import Path
p = Path("inference.py")
s = p.read_text(encoding="utf-8")

# Skip if already present
if "/mock/top-file" in s:
    print("OK: mocks already present"); raise SystemExit(0)

# Ensure imports: add Form & ImageFilter if missing
if "from fastapi import FastAPI, File, UploadFile, Form" not in s and "from fastapi import Form" not in s:
    s = s.replace("from fastapi import FastAPI, File, UploadFile", "from fastapi import FastAPI, File, UploadFile, Form")
    if "from fastapi import FastAPI, File, UploadFile, Form" not in s:
        s = "from fastapi import Form\n" + s

if "from PIL import ImageFilter" not in s:
    if "from PIL import Image" in s:
        s = s.replace("from PIL import Image", "from PIL import Image, ImageFilter")
    else:
        s = "from PIL import ImageFilter\n" + s

# Build the mock endpoints block
block_lines = [
"# ======== Mock endpoints for local CPU testing ========",
"@app.post(\\"/mock/top-file\\")",
"async def mock_top_file(",
"    person_image: UploadFile = File(...),",
"    clothing_image: UploadFile = File(...),",
"    out_size: int = Form(384),",
"    scale: float = Form(0.9),",
"    x_offset: int = Form(0),",
"    y_offset: int = Form(0),",
"    rotation: float = Form(0),",
"    feather: int = Form(4),",
"):",
"    import io",
"    from PIL import Image as _I",
"    try:",
"        person = _I.open(io.BytesIO(await person_image.read())).convert(\\"RGB\\")",
"        clothing = _I.open(io.BytesIO(await clothing_image.read())).convert(\\"RGBA\\")",
"        w, h = person.size",
"        clothing = clothing.resize((int(w*scale), int(h*scale)), _I.LANCZOS)",
"        if abs(rotation) > 0.01:",
"            clothing = clothing.rotate(rotation, expand=True, resample=_I.BICUBIC)",
"        mask = clothing.split()[-1].filter(ImageFilter.GaussianBlur(feather))",
"        px = (w - clothing.width)//2 + x_offset",
"        py = (h//4) + y_offset",
"        combined = person.copy()",
"        combined.paste(clothing, (px, py), mask)",
"        buf = io.BytesIO(); combined.save(buf, format=\\"PNG\\"); buf.seek(0)",
"        return StreamingResponse(buf, media_type=\\"image/png\\")",
"    except Exception as e:",
"        return JSONResponse({\\"error\\": str(e)}, status_code=500)",
"",
"@app.post(\\"/mock/bottom-file\\")",
"async def mock_bottom_file(",
"    person_image: UploadFile = File(...),",
"    clothing_image: UploadFile = File(...),",
"    out_size: int = Form(384),",
"    scale: float = Form(0.9),",
"    x_offset: int = Form(0),",
"    y_offset: int = Form(0),",
"    rotation: float = Form(0),",
"    feather: int = Form(4),",
"):",
"    import io",
"    from PIL import Image as _I",
"    try:",
"        person = _I.open(io.BytesIO(await person_image.read())).convert(\\"RGB\\")",
"        clothing = _I.open(io.BytesIO(await clothing_image.read())).convert(\\"RGBA\\")",
"        w, h = person.size",
"        clothing = clothing.resize((int(w*scale), int(h*scale)), _I.LANCZOS)",
"        if abs(rotation) > 0.01:",
"            clothing = clothing.rotate(rotation, expand=True, resample=_I.BICUBIC)",
"        mask = clothing.split()[-1].filter(ImageFilter.GaussianBlur(feather))",
"        px = (w - clothing.width)//2 + x_offset",
"        py = (3*h)//5 + y_offset",
"        combined = person.copy()",
"        combined.paste(clothing, (px, py), mask)",
"        buf = io.BytesIO(); combined.save(buf, format=\\"PNG\\"); buf.seek(0)",
"        return StreamingResponse(buf, media_type=\\"image/png\\")",
"    except Exception as e:",
"        return JSONResponse({\\"error\\": str(e)}, status_code=500)",
]
block = "\\n".join(block_lines) + "\\n"

# Insert block before the health section marker
marker = "\\n# ======== Health check endpoint ========"
idx = s.find(marker)
if idx == -1:
    s = s.rstrip() + "\\n" + block
else:
    s = s[:idx] + "\\n" + block + s[idx:]

p.write_text(s, encoding="utf-8")
print("OK: mocks appended before health marker")
