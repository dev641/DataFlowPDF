import subprocess


class ServiceManager:
    def __init__(self):
        pass

    def start_service(self, service_name):
        if self.query_service(
            service_name
        ):  # Check service status before starting
            print(f"{service_name} is already running.")
        else:
            try:
                subprocess.run(["sc", "start", service_name], check=True)
                print(f"{service_name} started successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Failed to start {service_name}: {e}")

    def stop_service(self, service_name, run_as_admin=True):
        try:
            if run_as_admin:
                self.run_as_admin(["sc", "stop", service_name])
            subprocess.run(["sc", "stop", service_name], check=True)
            print(f"{service_name} stopped successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop {service_name}: {e}")

    # Function to run commands as Administrator
    def run_as_admin(self, command):
        try:
            result = subprocess.run(
                ["runas", "/user:Administrator", *command],
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            print(result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run command as admin: {e}")

    def query_service(self, service_name, run_as_admin=False):
        try:
            result = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            if "RUNNING" in result.stdout:
                return True
            return False
        except subprocess.CalledProcessError as e:
            print(f"Failed to query {service_name}: {e}")
            return False
