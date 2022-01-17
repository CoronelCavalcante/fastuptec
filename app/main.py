from fastapi import FastAPI
from .routers import OrdemServico


app = FastAPI()

app.include_router(OrdemServico.rounter)



@app.get("/")
def root():
    return {"message": f"Hello World"}
