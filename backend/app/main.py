from fastapi import FastAPI
from app.api import events
from app.db.models import Base
from app.db.session import engine

app = FastAPI(title="AI Event Scoring & Traceability System")

app.include_router(events.router, tags=["events"])

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "AI Event Scoring API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
