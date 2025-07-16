# config_manager.py
import os
import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentConfig:
    restart_delay: int = 10
    log_level: str = "INFO"
    health_check_interval: int = 300
    max_restart_attempts: int = 5
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            restart_delay=int(os.getenv('RESTART_DELAY', 10)),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            health_check_interval=int(os.getenv('HEALTH_CHECK_INTERVAL', 300)),
            max_restart_attempts=int(os.getenv('MAX_RESTART_ATTEMPTS', 5))
        )