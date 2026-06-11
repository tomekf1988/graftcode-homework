import uvicorn

uvicorn.run(
    "order_service.api.app:app",
    host="0.0.0.0",
    port=8000,
    reload=False,
)
