from pathlib import Path
p = Path("tryon_pipeline.py")
b = p.read_bytes()
# Remove raw UTF-8 BOM bytes if present
if b.startswith(b"\xEF\xBB\xBF"):
    b = b[3:]
# Decode safely and remove any stray BOM chars or the visible "ï»¿" if it was saved literally
text = b.decode("utf-8", errors="replace")
text = text.lstrip("\ufeff")
if text.startswith("ï»¿"):
    text = text[3:]
# Write back as clean UTF-8 (no BOM)
p.write_text(text, encoding="utf-8")
print("BOM stripped. Preview:", repr(text[:40]))
