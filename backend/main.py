from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
# from supabase import create_client, Client  # Commented out
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Initialize Supabase client
# supabase: Client = create_client(    # Commented out
#     os.getenv("SUPABASE_URL"),
#     os.getenv("SUPABASE_KEY")
# )

# Use in-memory storage for now
orders = {}
order_counter = 1

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-frontend-domain.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class OrderItem(BaseModel):
    item: str
    quantity: int

class Order(BaseModel):
    id: int
    items: List[OrderItem]
    total_items: int

class UserRequest(BaseModel):
    user_input: str


# Some input validations are added on the AI prompt.
SYSTEM_PROMPT = """You are a drive-thru order processing assistant. Process customer orders and cancellation requests precisely.

MENU ITEMS ONLY:
- burgers
- fries
- drinks

RULES:
1. Only accept orders for menu items listed above
2. Ignore any non-menu items in the request
3. If quantity is 0 or negative, do not include that item
4. For cancellations, extract the order ID number
5. Allow user to cancel previous orders
6. If no valid items remain after processing, return empty items list

For orders, respond with JSON, where item_name can only be either "burgers", "fries", or "drinks":
{"type": "order", "items": [{"item": "item_name", "quantity": number}]}

For cancellations, respond with JSON:
{"type": "cancel", "order_id": number}

Respond with valid JSON only."""

def generate_response(prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "prompt": f"{SYSTEM_PROMPT}\n\nCustomer request: {prompt}\nResponse:",
        "max_tokens": 100,
        "temperature": 0.1,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["\n", "</s>"]
    }
    
    try:
        response = requests.post(
            "https://api.together.xyz/inference",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            text_response = response.json()["output"]["choices"][0]["text"]
            # Extract JSON from response
            start = text_response.find('{')
            end = text_response.rfind('}') + 1
            json_str = text_response[start:end]
            return json.loads(json_str)
        else:
            raise HTTPException(status_code=500, detail="API request failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# dummy route for testing
@app.get("/")
async def read_root():
    return {"message": "Drive-thru ordering system API"}

# GET route to get all orders
@app.get("/orders")
async def get_orders():
    # return supabase.table("orders").select("*").execute()  # Commented out
    return list(orders.values())  # Use in-memory storage instead

# POST route to process user requests
@app.post("/process-request")
async def process_request(request: UserRequest):
    try:
        response = generate_response(request.user_input)
        global order_counter
        
        if response["type"] == "order":
            order = Order(
                id=order_counter,
                items=[OrderItem(**item) for item in response["items"]],
                total_items=sum(item["quantity"] for item in response["items"])
            )
            # result = supabase.table("orders").insert(order_data).execute()  # Commented out
            orders[order_counter] = order  # Use in-memory storage
            order_counter += 1
            return {"message": "Order placed successfully", "order": order}
            
        elif response["type"] == "cancel":
            order_id = response["order_id"]
            # result = supabase.table("orders").delete().eq("id", order_id).execute()  # Commented out
            if order_id in orders:  # Use in-memory storage
                del orders[order_id]
                return {"message": f"Order #{order_id} cancelled successfully"}
            else:
                return {"message": f"Order #{order_id} not found"}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)