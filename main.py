import custom_console
import os
import sys
import google_init
import asyncio
from logs.agent_manager import AgentManager
import agent_tasks

async def agent_main():
    '''Main agent logic - this is what runs for one cycle of operations'''
    # No custom_console.clear_console() or simple_initializer_spinner here,
    # as these are usually one-time startup visuals handled by the main entry point.
    
    # Your main agent logic here for ONE ITERATION
    try:
        # Process leads
        await agent_tasks.process_leads()
        
        # Handle customer service
        await agent_tasks.handle_customer_service()
        
        # Check inventory
        await agent_tasks.check_inventory()
        
        # No small delay here if AgentManager handles the loop and delay
        # The AgentManager.start_daemon already has a sleep or restart_delay

        await init_agent()
        
    except Exception as e:
        # Re-raise the exception so AgentManager's error handling can catch it
        raise e
    
async def init_agent():
     # Your main agent logic here
    answer = google_init.llm.complete("What is 2 x 2?")  # Assuming this is your continuous agent loop
    print(f"{custom_console.COLOR_YELLOW}Answer: {custom_console.RESET_COLOR}{answer}", flush=True)

async def main():
    custom_console.clear_console()
    custom_console.simple_initializer_spinner(3, f"\n✅ Initial Program Loading complete!\n")
    
    # Create the agent manager with config file
    # Pass agent_main as the function to be managed
    manager = AgentManager(agent_function=agent_main, config_path="config.yaml")
    
    # Start the 24/7 daemon managed by AgentManager
    await manager.start_daemon()

if __name__ == "__main__":
    asyncio.run(main())