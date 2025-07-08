"""
Initializes Llama Index's Google AI integration.
"""

import os
import sys
import custom_console
from llama_index.llms.google_genai import GoogleGenAI

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
