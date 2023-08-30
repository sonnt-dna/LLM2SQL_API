
from fastapi import Header, APIRouter, HTTPException, FastAPI, UploadFile, File, Request, Form, Query
from pydantic import BaseModel
import pandas as pd
import json as json
import csv
from io import StringIO
from .predict_handlers import llm2sql
# Create new "APIRouter" object
predict_router = APIRouter()

# Check if the server is running or not
@predict_router.get("/hello")
async def read_main():
    return {"message": "Hello World", "Note": "This is a test"}

# Endpoint to predict
@predict_router.post("/chat", status_code=201)
async def upload_csv(query_params: str):
    # parameter = json.loads(query_params)
    # Validate query_params using QueryParams schema
    try:
        # query_params_in_json = json.dumps(query_params)
        parameter = query_params
    except ValueError as e:
        return {"detail": str(e)}
    except Exception as e:
        return {"detail": "Invalid JSON"}

    predicted_result = llm2sql(parameter)

    return predicted_result