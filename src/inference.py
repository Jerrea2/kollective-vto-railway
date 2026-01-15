import os, sys, time

print("?????? HARD IDENTITY PROBE ??????", flush=True)
print(f"FILE={__file__}", flush=True)
print(f"CWD={os.getcwd()}", flush=True)
print(f"SYS_PATH={sys.path}", flush=True)
print(f"TIME={time.time()}", flush=True)

raise RuntimeError("STOP — THIS IS THE REAL inference.py")
