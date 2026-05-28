from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import predict, explore

app = FastAPI(title="BioMine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/api")
app.include_router(explore.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}
