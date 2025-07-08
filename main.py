import custom_console
import os
import sys
import asyncio
import google_init as google
from logs import agent_manager
from logs.agent_manager import AgentManager

async def agent_main():
    """Main agent logic - this is what runs 24/7"""
    await init_agent()

async def init_agent():
     # Your main agent logic here
    answer = google.llm.complete("What is 2 x 2?")  # Assuming this is your continuous agent loop
    print(f"{custom_console.COLOR_YELLOW}Answer: {custom_console.RESET_COLOR}{answer}", flush=True)
    
async def main():
    # Create the agent manager
    manager = agent_manager.AgentManager(agent_function=agent_main, restart_delay=10)
    
    # Start the 24/7 daemon
    await manager.start_daemon()

if __name__ == "__main__":
    custom_console.clear_console()
    asyncio.run(main())