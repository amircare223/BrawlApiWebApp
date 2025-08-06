import subprocess
import threading
import time

def run_api():
    """Run the FastAPI server"""
    subprocess.run(["python", "api.py"])

def run_webapp():
    """Run the Flask web application"""
    time.sleep(2)  # Wait a moment for API to start
    subprocess.run(["python", "app.py"])

if __name__ == "__main__":
    # Start API in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Start the web app in the main thread
    run_webapp()
