from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
# from supabase import create_client, Client  # Commented out
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import requests
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

load_dotenv()
app = FastAPI()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

# Initialize database
def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    items JSONB NOT NULL,
                    total_items INTEGER NOT NULL,
                    order_number INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()

# Call init_db at startup
init_db()

# Use in-memory storage for now
orders = {}
order_counter = 1

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://appealing-determination-production.up.railway.app"
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
    user_id: str

class UserRequest(BaseModel):
    user_input: str
    user_id: str


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
4. For cancellations, extract the order_number from phrases like "cancel order 5" or "cancel #5"
5. Allow user to cancel previous orders
6. If no valid items remain after processing, return empty items list

For orders, respond with JSON, where item_name can only be either "burgers", "fries", or "drinks":
{"type": "order", "items": [{"item": "item_name", "quantity": number}]}

For cancellations, respond with JSON:
{"type": "cancel", "order_number": number}

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

@app.get("/orders/{user_id}")
async def get_user_orders(user_id: str):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,)
            )
            return cur.fetchall()

# POST route to process user requests
@app.post("/process-request")
async def process_request(request: UserRequest):
    try:
        response = generate_response(request.user_input)
        
        if response["type"] == "order":
            items = [OrderItem(**item) for item in response["items"]]
            total_items = sum(item.quantity for item in items)
            
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # First, get the current max order number for this user
                    cur.execute("""
                        SELECT COALESCE(MAX(order_number), 0) + 1 as next_order_number
                        FROM orders 
                        WHERE user_id = %s
                    """, (request.user_id,))
                    next_order_number = cur.fetchone()['next_order_number']
                    
                    # Insert new order with the user-specific order number
                    cur.execute("""
                        INSERT INTO orders (user_id, items, total_items, order_number)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                    """, (
                        request.user_id,
                        json.dumps([{"item": item.item, "quantity": item.quantity} for item in items]),
                        total_items,
                        next_order_number
                    ))
                    new_order = cur.fetchone()
                    conn.commit()
                    
            return {"message": "Order placed successfully", "order": new_order}
            
        elif response["type"] == "cancel":
            order_number = response["order_number"]
            
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # First verify the order belongs to the user
                    cur.execute(
                        "SELECT id FROM orders WHERE order_number = %s AND user_id = %s",
                        (order_number, request.user_id)
                    )
                    if not cur.fetchone():
                        raise HTTPException(
                            status_code=404,
                            detail=f"Order #{order_number} not found or doesn't belong to you"
                        )
                    
                    # Delete the order
                    cur.execute(
                        "DELETE FROM orders WHERE order_number = %s AND user_id = %s",
                        (order_number, request.user_id)
                    )
                    conn.commit()
                    
            return {"message": f"Order #{order_number} cancelled successfully"}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)