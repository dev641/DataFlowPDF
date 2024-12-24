import subprocess
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class ServiceManager:
    def __init__(self):
        log.info("Initializing ServiceManager")
        pass

    def start_service(self, service_name):
        log.info(f"Checking service status for: {service_name}")
        if self.query_service(
            service_name
        ):  # Check service status before starting
            log.info(f"Service {service_name} is already running")
        else:
            log.debug(
                f"Service {service_name} not running, attempting to start"
            )
            try:
                log.info(
                    f"Executing subprocess command to start {service_name}"
                )
                subprocess.run(["sc", "start", service_name], check=True)
                log.info(f"Successfully started service: {service_name}")
            except subprocess.CalledProcessError as e:
                log.error(
                    f"Failed to start service {service_name}. Error: {str(e)}"
                )
                print(f"Failed to start {service_name}: {e}")

    def stop_service(self, service_name, run_as_admin=True):
        try:
            log.info(f"Attempting to stop service: {service_name}")
            if run_as_admin:
                log.debug(f"Running stop command as admin for {service_name}")
                self.run_as_admin(["sc", "stop", service_name])
            log.debug(f"Running stop command as admin for {service_name}")
            subprocess.run(["sc", "stop", service_name], check=True)
            log.info(f"Service {service_name} stopped successfully")
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop {service_name}: {e}")
            log.error(f"Failed to stop service {service_name}: {e}")

    # Function to run commands as Administrator
    def run_as_admin(self, command):
        try:
            log.info(f"Attempting to run command as administrator: {command}")
            result = subprocess.run(
                ["runas", "/user:Administrator", *command],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.log.info(
                    "Command executed successfully with return code 0"
                )
                self.log.debug(f"Command output: {result.stdout}")
            else:
                self.log.warning(
                    f"Command returned non-zero exit code: {result.returncode}"
                )
                self.log.debug(f"Command error output: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to run command as admin: {e}")
            log.error(f"Failed to run command as admin: {e}")

    def query_service(self, service_name, run_as_admin=False):
        try:
            log.info(f"Querying service status for: {service_name}")
            result = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            if "RUNNING" in result.stdout:
                log.info(f"Service {service_name} is running")
                return True
            log.info(f"Service {service_name} is not running")
            return False
        except subprocess.CalledProcessError as e:
            log.error(
                f"Failed to query service {service_name}. Error: {str(e)}"
            )
            print(f"Failed to query {service_name}: {e}")
            return False
