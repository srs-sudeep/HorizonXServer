import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI(debug=os.getenv("DEBUG", "false").lower() == "true")

# Not safe! Add your own allowed domains
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define what you getting
class Stuff(BaseModel):
    content: str


# Example GET route for app
@app.get("/")
def read_root():
    return {"Message": "Hello World! FastAPI is working."}


# Example POST route for app
@app.post("/getdata/")
async def create_secret(payload: Stuff):
    with open("output_file.txt", "a") as f:
        now = datetime.now()
        formatted_date = now.strftime("%B %d, %Y at %I:%M %p")
        f.write(formatted_date + ": " + payload.content)
        f.write("\n")
    return payload.content
