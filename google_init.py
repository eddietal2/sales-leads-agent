"""
Initializes Llama Index's Google AI integration.
"""

import os
import sys
import custom_console
from llama_index.llms.google_genai import GoogleGenAI
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

def handle_google_ai_error(e):
    error_str = str(e)
    
    if "API key not valid" in error_str:
        return f"{custom_console.COLOR_RED}❌ Invalid API Key\n{custom_console.RESET_COLOR}Check your GOOGLE_API_KEY environment variable"
    elif "quota exceeded" in error_str.lower():
        return f"{custom_console.COLOR_RED}❌ Quota Exceeded\n{custom_console.RESET_COLOR}You've hit your API usage limit"
    elif "permission denied" in error_str.lower():
        return f"{custom_console.COLOR_RED}❌ Permission Denied\n{custom_console.RESET_COLOR}API key lacks required permissions"
    else:
        return f"{custom_console.COLOR_RED}❌ Google AI Error:\n{custom_console.RESET_COLOR}{e}"

# Check for API key first
if not GOOGLE_API_KEY:
    print(f"{custom_console.COLOR_RED}❌ No API Key Found")
    print(f"{custom_console.RESET_COLOR}Please set your GOOGLE_API_KEY environment variable")
    sys.exit(1)

# Initialize Google API Key & Model with error handling
try:
    llm = GoogleGenAI(
        # https://ai.google.dev/gemini-api/docs/models
        model="models/gemini-2.5-pro",
        api_key=GOOGLE_API_KEY,
    )
    print(f"{custom_console.COLOR_GREEN}✅ Google AI initialized successfully (gemini-2.5-pro){custom_console.RESET_COLOR}\n")
except Exception as e:
    print(handle_google_ai_error(e))
    sys.exit(1)

async def process_leads(): # Make it async if it performs async operations (like llm.acomplete)
    if llm is None:
        raise RuntimeError("LLM not initialized. Cannot process leads.")
    print("Processing leads using Google AI...")
    # This is where your actual lead processing logic would go
    # For example:
    # leads_data = await fetch_leads_from_db()
    # for lead in leads_data:
    #    response = await llm.acomplete(f"Generate a sales pitch for {lead['name']} for product X.")
    #    print(f"Pitch for {lead['name']}: {response}")
    print("Leads processing complete.")

async def handle_customer_service():
    if llm is None:
        raise RuntimeError("LLM not initialized. Cannot handle customer service.")
    print("Handling customer service queries using Google AI...")
    # This is where your customer service logic would go
    # For example:
    # query = await get_customer_query_from_queue()
    # response = await llm.acomplete(f"Generate a helpful response to the customer query: '{query}'")
    # await send_response_to_customer(response)
    print("Customer service handling complete.")

async def check_inventory():
    if llm is None:
        raise RuntimeError("LLM not initialized. Cannot check inventory.")
    print("Checking inventory using Google AI...")
    # This is where your inventory checking logic would go.
    # It might involve querying a database or an API, and then potentially using the LLM
    # to interpret the results or generate alerts.
    # Example:
    # inventory_data = await inventory_api.get_stock_levels()
    # prompt = f"Analyze inventory data: {inventory_data} and identify any low stock items that need urgent reordering."
    # analysis = await llm.acomplete(prompt)
    # print("Inventory analysis:", analysis)
    print("Inventory check complete.")

def main():
    print(f"{custom_console.COLOR_YELLOW}Connecting to Google AI via Google LLM Init Module{custom_console.RESET_COLOR}")
    print(f"{llm}\n")
    question = "What is Today's Weather in the United States?"
    response = llm.complete(question)
    print(f"{custom_console.COLOR_CYAN}Question: {custom_console.RESET_COLOR}", question)
    print(f"{custom_console.COLOR_CYAN}Answer: {custom_console.RESET_COLOR}", response)

if __name__ == "__main__":
    custom_console.clear_console()
    main()
