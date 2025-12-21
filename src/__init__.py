print("=================================================")
print("[VTO] 🚨 IDENTITY GATE PASSED (FORCED IMPORT) 🚨")
import os, sys
print("[VTO] CWD:", os.getcwd())
print("[VTO] sys.path:")
for p in sys.path:
    print("   ", p)
print("=================================================")
