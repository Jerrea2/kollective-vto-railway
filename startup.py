import uvicorn

# Force uvicorn to run YOUR real backend (no more stub)
uvicorn.run(
    'src.Kollective-vto2.inference:app',
    host='0.0.0.0',
    port=80,
    log_level='debug',
    proxy_headers=True,
    forwarded_allow_ips='*',
    workers=1
)
