from fastapi import FastAPI, Query
import requests
import openai
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from serpapi import GoogleSearch
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



SERPAPI_KEY = os.environ.get("SERPAPI_KEY") 
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def product_query(client, query: str) -> str:
    prompt = f"Take this query and return the product name that the user wants buy {query}, return only the product name"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are an AI shoping assistant finding out the product the user wants to buy"},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
    

@app.get("/search")
def search_google_shopping(query: str = Query(..., title="Search Query")):
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    p_query = product_query(client, query)
    print(p_query)
    params = {
    "engine": "google_shopping",
    "q": p_query,
    "hl": "en",
    "gl": "us",
    "api_key": SERPAPI_KEY,
    "num": 10,
    }
    search = GoogleSearch(params)
    response = search.get_dict()
    print(response)
    
    if True:
        data = response.get("shopping_results", [])
        products = []
        for item in response.get("shopping_results", [])[:8]:  # Get top 5 results
            products.append({
            "title": item.get("title", "No title available"),
            "link": item.get("product_link", "No link available"),
            "image": item.get("thumbnail", ""),
            "price": item.get("price", "Price not available"),
            "old_price": item.get("old_price", None),
            "store": item.get("source", "Unknown Store"),
            "rating": item.get("rating", "No rating"),
            "reviews": item.get("reviews", "No reviews"),
            "discount": item.get("tag", ""),
            "delivery": item.get("delivery", "Delivery info not available")
        }
        )
        print(products)
    try:
        llm_prompt = f"Suggest some insights or advice for shopping for '{query}' products."
        llm_result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that enhances search queries."},
            {"role": "user", "content": f"{llm_prompt}"}
        ]
        )
        try: 
            llm_response = llm_result.choices[0].message.content
            print(llm_response, 1)
        except:
            llm_response = llm_result.choices[0].message
    except Exception as e:
        llm_response = f"Error generating response from LLM: {str(e)}"
    
    return {"products": products, "llm_response": llm_response}
