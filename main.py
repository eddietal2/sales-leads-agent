import custom_console
import os
import sys

async def main():
        custom_console.clear_console()
        custom_console.simple_initializer_spinner(3,f"\n✅ Initial Program Loading complete!\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())