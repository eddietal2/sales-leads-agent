"""
Dedicated module for 24/7 operation for Agent
"""
import asyncio
import logging
import signal
import sys
import os
from datetime import datetime
from typing import Callable, Optional
import traceback
import custom_console

from logs.health_monitor import HealthMonitor
from logs.config_manager import ConfigManager

class AgentManager:
    def __init__(self, agent_function: Callable, config_path: str = "config.yaml"):
        # Load configuration
        self.config_manager = ConfigManager(_config_path=config_path)
        if not self.config_manager.validate_config():
            raise ValueError("Invalid configuration")
        
        self.config = self.config_manager.get_config()

        self.agent_function = agent_function
        self.running = False
        self.restart_count = 0

        # Setup logging
        self.setup_logging()
        # Initialize the logger for AgentManager AFTER setup_logging
        self.logger = logging.getLogger(f'{custom_console.COLOR_CYAN}AgentManager{custom_console.RESET_COLOR}')
        self.logger.info("AgentManager initialized.")
        
        # Initialize health monitor
        self.health_monitor = HealthMonitor(
            check_interval=self.config_manager.health_check_interval,
            log_retention_days=self.config_manager.health_log_retention_days,
            cpu_threshold=self.config_manager.cpu_threshold,      # Corrected
            memory_threshold=self.config_manager.memory_threshold,  # Corrected
            disk_threshold=self.config_manager.disk_threshold,      # Corrected
            error_rate_threshold=self.config_manager.error_rate_threshold, # Corrected
            api_timeout=self.config_manager.api_timeout            # Corrected
            # Add any other relevant config values from config_manager to health_monitor's init
        )
        
        self.setup_logging()
        self.setup_signal_handlers()

    def setup_logging(self):
        """Configure logging based on config"""
        # Access log_level directly from the config_manager instance
        log_level_str = self.config_manager.log_level.upper() 
        
        # Use getattr to safely convert the string log level to a logging constant
        log_level = getattr(logging, log_level_str, logging.INFO)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir) # Or just script_dir if you want logs directly in 'logs' folder
        os.makedirs(log_dir, exist_ok=True) # Ensure log directory exists
        log_file_path = os.path.join(log_dir, 'autopilot_agent.log')

        # --- Add a print statement to verify the path ---
        print(f"DEBUG: Attempting to write logs to: {log_file_path}")
        # --- End print statement ---

        if not logging.root.handlers:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file_path),
                    logging.StreamHandler()
                ]
            )
        # Optional: Add a confirmation log
        logging.getLogger(__name__).info(f"Logging initialized with level: {logging.getLevelName(log_level)}")
    
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
        """Start the 24/7 daemon process with health monitoring"""
        self.running = True
        self.restart_count = 0
        
        # Start health monitoring in background
        health_task = asyncio.create_task(self.health_monitor.start_monitoring())
        
        self.logger.info("Starting AutoPilot Agent Daemon with health monitoring...")
        
        try:
            while self.running:
                try:
                    self.logger.info("Initializing agent...")
                    
                    # Record the start of a request
                    # Note: record_request is a regular method, not async
                    self.health_monitor.record_request(success=True)
                    
                    # Run the main agent function
                    await self.agent_function()
                    
                    # Reset restart count on successful completion
                    self.restart_count = 0
                    
                    # If agent_function returns, restart after delay
                    if self.running:
                        self.logger.info(f"Agent completed. Restarting in {self.config_manager.restart_delay} seconds...") # Corrected
                        await asyncio.sleep(self.config_manager.restart_delay) # Corrected
                        
                except KeyboardInterrupt:
                    self.logger.info("Received keyboard interrupt. Shutting down...")
                    break
                    
                except Exception as e:
                    # Record the error
                    self.health_monitor.record_request(success=False)
                    
                    self.logger.error(f"Agent crashed: {str(e)}")
                    self.logger.error(f"Traceback: {traceback.format_exc()}")
                    
                    # Increment restart count
                    self.restart_count += 1
                    
                    # Check if we've exceeded max restart attempts
                    if self.restart_count >= self.config_manager.max_restart_attempts: # Corrected
                        self.logger.critical(
                            f"Max restart attempts ({self.config_manager.max_restart_attempts}) exceeded. " # Corrected
                            "Stopping daemon."
                        )
                        break
                    
                    if self.running:
                        self.logger.info(
                            f"Restarting in {self.config_manager.restart_delay} seconds... " # Corrected
                            f"(Attempt {self.restart_count}/{self.config_manager.max_restart_attempts})" # Corrected
                        )
                        await asyncio.sleep(self.config_manager.restart_delay) # Corrected
            
        finally:
            # Stop health monitoring
            health_task.cancel()
            try:
                await health_task
            except asyncio.CancelledError:
                pass
            
            self.logger.info("Agent daemon stopped.")
    
    async def reload_config(self):
        """Reload configuration without stopping the daemon"""
        try:
            self.config_manager.reload_config()
            if not self.config_manager.validate_config():
                self.logger.error("Configuration validation failed during reload")
                return False
            
            old_config = self.config
            self.config = self.config_manager.get_config()
            
            # Update health monitor thresholds
            self.health_monitor.cpu_threshold = self.config.cpu_threshold
            self.health_monitor.memory_threshold = self.config.memory_threshold
            self.health_monitor.disk_threshold = self.config.disk_threshold
            self.health_monitor.error_rate_threshold = self.config.error_rate_threshold
            
            # Update logging level if changed
            if old_config.log_level != self.config.log_level:
                log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
                self.logger.setLevel(log_level)
            
            self.logger.info("Configuration reloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get comprehensive agent status"""
        health_status = self.health_monitor.get_current_status()
        
        return {
            'running': self.running,
            'timestamp': datetime.now().isoformat(),
            'restart_count': self.restart_count,
            'max_restart_attempts': self.config.max_restart_attempts,
            'restart_delay': self.config.restart_delay,
            'health': health_status,
            'config': {
                'log_level': self.config.log_level,
                'health_check_interval': self.config.health_check_interval,
                'cpu_threshold': self.config.cpu_threshold,
                'memory_threshold': self.config.memory_threshold,
                'disk_threshold': self.config.disk_threshold,
                'error_rate_threshold': self.config.error_rate_threshold,
            }
        }
    
    async def health_check(self) -> dict:
        """Perform immediate health check"""
        return await self.health_monitor.check_system_health()
    
async def main():
    custom_console.clear_console()
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
