# health_monitor.py
import asyncio
import aiohttp
import logging
from datetime import datetime
from collections import deque # For record_request to store recent requests

class HealthMonitor:
    def __init__(
        self,
        check_interval: int = 300,
        log_retention_days: int = 7,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 85.0,
        disk_threshold: float = 90.0,
        error_rate_threshold: float = 0.1,
        api_timeout: int = 30,
        # Add any other relevant thresholds/settings HealthMonitor might need from config
    ):
        self.check_interval = check_interval
        self.log_retention_days = log_retention_days
        
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.error_rate_threshold = error_rate_threshold
        self.api_timeout = api_timeout

        self.logger = logging.getLogger('HealthMonitor')
        
        # For tracking request success/failure for error rate
        self.request_history = deque(maxlen=100) # Store last 100 requests, adjust as needed

    async def check_system_health(self):
        """Perform system health checks"""
        self.logger.debug("Performing system health checks...") # Changed to debug for less verbosity
        checks = {
            'memory_usage': self._check_memory(),
            'disk_space': self._check_disk_space(),
            'api_connectivity': await self._check_api_connectivity(),
            'error_rate': self._calculate_error_rate() # Added error rate check
        }
        
        # Example of using thresholds and logging warnings
        if checks.get('memory_usage', 0) > self.memory_threshold:
            self.logger.warning(f"Memory usage ({checks['memory_usage']}%) exceeds threshold ({self.memory_threshold}%)")
        if checks.get('disk_space', 0) > self.disk_threshold:
            self.logger.warning(f"Disk space usage ({checks['disk_space']}%) exceeds threshold ({self.disk_threshold}%)")
        if not checks.get('api_connectivity'): # Assuming False means failure
            self.logger.critical(f"API connectivity check failed.")
        if checks.get('error_rate', 0) > self.error_rate_threshold:
            self.logger.warning(f"Error rate ({checks['error_rate']:.2f}) exceeds threshold ({self.error_rate_threshold:.2f})")
            
        return checks
    
    def _check_memory(self):
        try:
            import psutil # Make sure psutil is installed: pip install psutil
            mem = psutil.virtual_memory()
            percentage = mem.percent
            self.logger.debug(f"Current memory usage: {percentage}%")
            return percentage
        except ImportError:
            self.logger.warning("psutil not installed, cannot check memory usage.")
            return 0 # Or None, or raise an exception
        except Exception as e:
            self.logger.error(f"Error checking memory: {e}")
            return 0

    def _check_disk_space(self):
        try:
            import psutil # Make sure psutil is installed
            # Check disk usage for the root/system partition. Adjust as needed for specific paths.
            disk = psutil.disk_usage('/') 
            percentage = disk.percent
            self.logger.debug(f"Current disk space usage: {percentage}%")
            return percentage
        except ImportError:
            self.logger.warning("psutil not installed, cannot check disk space.")
            return 0
        except Exception as e:
            self.logger.error(f"Error checking disk space: {e}")
            return 0
    
    async def _check_api_connectivity(self):
        url = "https://www.google.com" # Example public URL to check general internet/API connectivity
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.api_timeout) as response:
                    if response.status == 200:
                        self.logger.debug(f"API connectivity to {url} successful.")
                        return True
                    else:
                        self.logger.warning(f"API connectivity to {url} failed with status: {response.status}")
                        return False
        except aiohttp.ClientError as e:
            self.logger.error(f"API connectivity to {url} failed: {e}")
            return False
        except asyncio.TimeoutError:
            self.logger.error(f"API connectivity to {url} timed out after {self.api_timeout} seconds.")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during API connectivity check: {e}")
            return False

    def record_request(self, success: bool):
        """Records the success or failure of an agent request."""
        self.request_history.append(success)
        self.logger.debug(f"Request recorded: {'Success' if success else 'Failure'}. History size: {len(self.request_history)}")

    def _calculate_error_rate(self) -> float:
        """Calculates the error rate based on recent request history."""
        if not self.request_history:
            return 0.0
        
        failures = self.request_history.count(False)
        total = len(self.request_history)
        error_rate = failures / total
        self.logger.debug(f"Calculated error rate: {error_rate:.2f} ({failures}/{total} failures)")
        return error_rate

    # This method was missing and causing the error!
    async def start_monitoring(self):
        self.logger.info(f"Starting health monitoring with interval: {self.check_interval} seconds.")
        while True:
            health_status = await self.check_system_health()
            self.logger.info(f"Health check results: {health_status}")
            # Here you would implement logic for logging retention, alerting, etc.
            # Log retention would typically be handled by a log rotation system or external logging service.
            # You could add logic here to trigger alerts if thresholds are exceeded.
            await asyncio.sleep(self.check_interval)