from fastapi import FastAPI
from pdf_router import router as pdf_router
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(pdf_router)
# Enable CORS to allow requests from frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Run the server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 

    url = "http://localhost:8000/upload_pdf" 
    with httpx.Client() as client:
        response = client.post(url)  
