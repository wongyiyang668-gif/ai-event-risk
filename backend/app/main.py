from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import events, ingestion
from app.db.models import Base
from app.db.session import engine

app = FastAPI(title="AI Event Scoring & Traceability System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, tags=["events"])
app.include_router(ingestion.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "AI Event Scoring API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
