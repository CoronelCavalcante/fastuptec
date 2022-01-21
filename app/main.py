from fastapi import FastAPI
from .routers import ordemServico, user, auth
from . import models
from .database import engine
from fastapi.middleware.cors import CORSMiddleware


#models.Base.metadata.create_all(bind=engine) nao é mais usado


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(ordemServico.rounter)
app.include_router(user.router)
app.include_router(auth.router)



@app.get("/")
def root():
    return {"message": f"Hello World!123123123"}
