import psutil
import time
from datetime import datetime

def system_stats():
    try:
        print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
        print(f"Memory Usage: {psutil.virtual_memory().percent}%")
        print(f"Disk Usage: {psutil.disk_usage('/').percent}%")
        print("-" * 50)
        
        # Get top 5 longest running processes
        get_long_running_processes()

    except Exception as e:
        print(f"Error fetching system stats: {e}")

def get_long_running_processes():
    try:
        processes = []
        for proc in psutil.process_iter(attrs=['pid', 'name', 'create_time']):
            try:
                create_time = datetime.fromtimestamp(proc.info['create_time'])  # Convert timestamp to datetime
                processes.append((proc.info['pid'], proc.info['name'], create_time))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue  # Skip processes that no longer exist or are restricted

        # Sort by start time (oldest first) and get top 5
        processes.sort(key=lambda x: x[2])
        top_5 = processes[:5]

        print("Top 5 Longest Running Processes:")
        for pid, name, start_time in top_5:
            print(f"PID: {pid} | Name: {name} | Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)

    except Exception as e:
        print(f"Error fetching process info: {e}")

if __name__ == "__main__":
    while True:  # Continuous monitoring
        system_stats()
        time.sleep(5)  # Refresh every 5 seconds
