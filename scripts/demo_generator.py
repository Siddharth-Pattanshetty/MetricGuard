import os
import time
import requests
import random
from datetime import datetime, timezone

# URL of the MetricGuard backend (configurable via environment variable for Docker)
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CONTINUOUS_MODE = os.getenv("CONTINUOUS_MODE", "false").lower() == "true"


def send_metric(cpu, ram, disk):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "cpu_usage": cpu,
        "ram_usage": ram,
        "disk_usage": disk,
        "disk_read_speed": "12 MB",
        "disk_write_speed": "5 MB",
        "network_upload_speed": "500 KB",
        "network_download_speed": "1.2 MB",
        "process_count": random.randint(150, 200),
        "system_load": random.uniform(1.0, 2.0),
        "system_uptime": "10h 30m"
    }
    try:
        response = requests.post(f"{BASE_URL}/metrics/", json=payload)
        print(f"Sent Metric [CPU: {cpu}%, RAM: {ram}%, Disk: {disk}%] -> Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending metric: {e}")

def send_log(level, service, message):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": level,
        "service_name": service,
        "message": message
    }
    try:
        response = requests.post(f"{BASE_URL}/logs/", json=payload)
        print(f"Sent Log [{level} from {service}]: {message} -> Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending log: {e}")

def run_demo():
    print("==========================================")
    print("🚀 MetricGuard Live Demo Generator")
    print("==========================================")
    print("Generating baseline traffic for 10 seconds...")
    
    # 1. Generate normal baseline metrics
    for _ in range(5):
        send_metric(cpu=random.uniform(10, 30), ram=random.uniform(40, 50), disk=random.uniform(40, 45))
        time.sleep(2)

    print("\n⚠️ TRIGGERING ANOMALY: CPU Spike on datanode!")
    # 2. Trigger CPU anomaly + Error log
    for _ in range(3):
        send_metric(cpu=random.uniform(95, 99), ram=random.uniform(45, 50), disk=random.uniform(42, 45))
        time.sleep(1)
        
    send_log("ERROR", "datanode", "High CPU temperature detected, thermal throttling engaged.")
    time.sleep(1)
    
    print("\n⚠️ TRIGGERING ANOMALY: Database Outage Log")
    send_log("CRITICAL", "storage", "Connection refused: Unable to connect to backend storage.")
    
    print("\n✅ Demo sequence complete. Check the MetricGuard dashboard and Incident views!")

if __name__ == "__main__":
    if CONTINUOUS_MODE:
        print("Running in continuous mode...")
        while True:
            run_demo()
            time.sleep(10)
    else:
        run_demo()
