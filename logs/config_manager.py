# config_manager.py
import os
import json
from dataclasses import dataclass, field
from typing import Optional
import yaml

@dataclass
class ConfigManager:
    restart_delay: int = 10
    log_level: str = "INFO"
    health_check_interval: int = 300
    max_restart_attempts: int = 5
    
    # ADD THESE NEW FIELDS FROM YOUR YAML CONFIG
    health_log_retention_days: int = 7 # Added this line
    cpu_threshold: float = 80.0       # Added this line
    memory_threshold: float = 85.0    # Added this line
    disk_threshold: float = 90.0      # Added this line
    error_rate_threshold: float = 0.1 # Added this line
    api_timeout: int = 30             # Added this line
    lead_response_delay: int = 5      # Added this line
    customer_service_hours: str = "9-17" # Added this line
    inventory_check_interval: int = 3600 # Added this line
    alert_email: str = "eddielacrosse2@gmail.com" # Added this line (use a default if no email)
    enable_sms_alerts: bool = False   # Added this line

    # Internal field for config path, not part of the actual configuration values
    _config_path: Optional[str] = field(default=None, repr=False)

    def __post_init__(self):
        if self._config_path and os.path.exists(self._config_path):
            self._load_from_yaml(self._config_path)
        elif self._config_path and not os.path.exists(self._config_path):
            print(f"Warning: Configuration file not found at {self._config_path}. Using default or environment values.")

    def _load_from_yaml(self, config_path: str):
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)

            # Update instance attributes with values from the YAML file
            # Use .get() to safely retrieve values and fall back to current defaults if not present
            self.restart_delay = config_data.get('restart_delay', self.restart_delay)
            self.log_level = config_data.get('log_level', self.log_level)
            self.health_check_interval = config_data.get('health_check_interval', self.health_check_interval)
            self.max_restart_attempts = config_data.get('max_restart_attempts', self.max_restart_attempts)
            
            # Update the NEWLY ADDED FIELDS from YAML
            self.health_log_retention_days = config_data.get('health_log_retention_days', self.health_log_retention_days)
            self.cpu_threshold = config_data.get('cpu_threshold', self.cpu_threshold)
            self.memory_threshold = config_data.get('memory_threshold', self.memory_threshold)
            self.disk_threshold = config_data.get('disk_threshold', self.disk_threshold)
            self.error_rate_threshold = config_data.get('error_rate_threshold', self.error_rate_threshold)
            self.api_timeout = config_data.get('api_timeout', self.api_timeout)
            self.lead_response_delay = config_data.get('lead_response_delay', self.lead_response_delay)
            self.customer_service_hours = config_data.get('customer_service_hours', self.customer_service_hours)
            self.inventory_check_interval = config_data.get('inventory_check_interval', self.inventory_check_interval)
            self.alert_email = config_data.get('alert_email', self.alert_email)
            self.enable_sms_alerts = config_data.get('enable_sms_alerts', self.enable_sms_alerts) # YAML booleans usually map to Python bools automatically

            print(f"Configuration loaded from {config_path}")
        except FileNotFoundError:
            print(f"Error: Config file not found at {config_path}. Using default values.")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML config file {config_path}: {e}. Using default values.")
        except Exception as e:
            print(f"An unexpected error occurred while loading config from {config_path}: {e}. Using default values.")


    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        # This method would also need to be updated if you want environment variables
        # to override these new fields. For brevity, I'm omitting that update here,
        # but keep it in mind.
        return cls(
            restart_delay=int(os.getenv('RESTART_DELAY', 10)),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            health_check_interval=int(os.getenv('HEALTH_CHECK_INTERVAL', 300)),
            max_restart_attempts=int(os.getenv('MAX_RESTART_ATTEMPTS', 5)),
            # Add new fields here if you want them to be configurable via env vars
            health_log_retention_days=int(os.getenv('HEALTH_LOG_RETENTION_DAYS', 7)),
            cpu_threshold=float(os.getenv('CPU_THRESHOLD', 80.0)),
            # ... and so on for all new fields
        )
    
    def get_config(self):
        print("Get Config")
        # This method should also return all current config attributes
        return {
            "restart_delay": self.restart_delay,
            "log_level": self.log_level,
            "health_check_interval": self.health_check_interval,
            "max_restart_attempts": self.max_restart_attempts,
            "health_log_retention_days": self.health_log_retention_days,
            "cpu_threshold": self.cpu_threshold,
            "memory_threshold": self.memory_threshold,
            "disk_threshold": self.disk_threshold,
            "error_rate_threshold": self.error_rate_threshold,
            "api_timeout": self.api_timeout,
            "lead_response_delay": self.lead_response_delay,
            "customer_service_hours": self.customer_service_hours,
            "inventory_check_interval": self.inventory_check_interval,
            "alert_email": self.alert_email,
            "enable_sms_alerts": self.enable_sms_alerts,
        }

    def validate_config(self):
        print("Validate Config")
        # Ensure your validation logic also includes checks for these new fields
        if not isinstance(self.restart_delay, int) or self.restart_delay < 0:
            print(f"Validation Error: restart_delay ({self.restart_delay}) is invalid.")
            return False
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            print(f"Validation Error: log_level ({self.log_level}) is invalid.")
            return False
        if not isinstance(self.health_check_interval, int) or self.health_check_interval < 0:
            print(f"Validation Error: health_check_interval ({self.health_check_interval}) is invalid.")
            return False
        if not isinstance(self.max_restart_attempts, int) or self.max_restart_attempts < 0:
            print(f"Validation Error: max_restart_attempts ({self.max_restart_attempts}) is invalid.")
            return False
        
        # Add validation for new fields
        if not isinstance(self.health_log_retention_days, int) or self.health_log_retention_days < 0:
            print(f"Validation Error: health_log_retention_days ({self.health_log_retention_days}) is invalid.")
            return False
        if not isinstance(self.cpu_threshold, (int, float)) or not (0 <= self.cpu_threshold <= 100):
            print(f"Validation Error: cpu_threshold ({self.cpu_threshold}) is invalid.")
            return False
        if not isinstance(self.memory_threshold, (int, float)) or not (0 <= self.memory_threshold <= 100):
            print(f"Validation Error: memory_threshold ({self.memory_threshold}) is invalid.")
            return False
        if not isinstance(self.disk_threshold, (int, float)) or not (0 <= self.disk_threshold <= 100):
            print(f"Validation Error: disk_threshold ({self.disk_threshold}) is invalid.")
            return False
        if not isinstance(self.error_rate_threshold, (int, float)) or not (0 <= self.error_rate_threshold <= 1):
            print(f"Validation Error: error_rate_threshold ({self.error_rate_threshold}) is invalid (should be between 0 and 1).")
            return False
        if not isinstance(self.api_timeout, int) or self.api_timeout <= 0:
            print(f"Validation Error: api_timeout ({self.api_timeout}) is invalid.")
            return False
        if not isinstance(self.lead_response_delay, int) or self.lead_response_delay < 0:
            print(f"Validation Error: lead_response_delay ({self.lead_response_delay}) is invalid.")
            return False
        # You might want more sophisticated validation for customer_service_hours (e.g., regex)
        if not isinstance(self.customer_service_hours, str) or not self.customer_service_hours:
            print(f"Validation Error: customer_service_hours ({self.customer_service_hours}) is invalid.")
            return False
        if not isinstance(self.inventory_check_interval, int) or self.inventory_check_interval < 0:
            print(f"Validation Error: inventory_check_interval ({self.inventory_check_interval}) is invalid.")
            return False
        if not isinstance(self.alert_email, str) or "@" not in self.alert_email: # Simple email validation
            print(f"Validation Error: alert_email ({self.alert_email}) is invalid.")
            return False
        if not isinstance(self.enable_sms_alerts, bool):
            print(f"Validation Error: enable_sms_alerts ({self.enable_sms_alerts}) is invalid.")
            return False

        print("Configuration validated successfully.")
        return True