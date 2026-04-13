from fastapi import FastAPI
from .routers import user, auth, twin
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="digital_twin", version="1.0.0")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(twin.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

