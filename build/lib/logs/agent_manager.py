"""
Dedicated module for 24/7 operation for Agent
"""
import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Callable, Optional
import traceback
import custom_console

from health_monitor import HealthMonitor
from config_manager import ConfigManager

class AgentManager:
    def __init__(self, agent_function: Callable, config_path: str = "config.yaml"):
        # Load configuration
        self.config_manager = ConfigManager(config_path)
        if not self.config_manager.validate_config():
            raise ValueError("Invalid configuration")
        
        self.config = self.config_manager.get_config()
        self.agent_function = agent_function
        self.running = False
        self.restart_count = 0
        
        # Initialize health monitor
        self.health_monitor = HealthMonitor(
            check_interval=self.config.health_check_interval,
            log_retention_days=self.config.health_log_retention_days
        )
        
        # Set health thresholds from config
        self.health_monitor.cpu_threshold = self.config.cpu_threshold
        self.health_monitor.memory_threshold = self.config.memory_threshold
        self.health_monitor.disk_threshold = self.config.disk_threshold
        self.health_monitor.error_rate_threshold = self.config.error_rate_threshold
        
        self.setup_logging()
        self.setup_signal_handlers()

    def setup_logging(self):
        """Configure logging for the agent"""
        logging.basicConfig(
            # DEBUG < INFO < WARNING < ERROR < CRITICAL
            # Only logs INFO level and above (ignores DEBUG messages)
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('autopilot_agent.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AutoPilotAgent')
    
    def setup_signal_handlers(self):
        """
        Handle graceful shutdown signals and crash recovery
        ~ Save data, Close database connections, 
        Send "going offline" notifications, Finish current tasks, etc.
        """
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.running = False

    async def start_daemon(self):
        """Start the 24/7 daemon process"""
        self.running = True
        self.logger.info("Starting AutoPilot Agent Daemon...")
        
        while self.running:
            try:
                self.logger.info("Initializing agent...")
                await self.agent_function()
                
                # If agent_function returns, it means it completed
                # For 24/7 operation, you might want to restart or wait
                if self.running:
                    self.logger.info("Agent completed. Restarting in 5 seconds...")
                    await asyncio.sleep(5)
                    
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt. Shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Agent crashed: {str(e)}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                
                if self.running:
                    self.logger.info(f"Restarting in {self.restart_delay} seconds...")
                    await asyncio.sleep(self.restart_delay)
        
        self.logger.info("Agent daemon stopped.")
    
    def get_status(self) -> dict:
        """Get current agent status"""
        return {
            'running': self.running,
            'timestamp': datetime.now().isoformat(),
            'restart_delay': self.restart_delay
        }
    
async def main():
    custom_console.clear_console()
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
