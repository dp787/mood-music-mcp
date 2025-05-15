import subprocess
import sys
import time
import os
import requests
import logging
from threading import Thread
from queue import Queue
import importlib.util
import pathlib
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_available_port(start_port=8000, max_port=8020):
    """Find an available port in the given range."""
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available ports in range {start_port}-{max_port}")

def check_server_health(port):
    """Check if server is responding on the given port."""
    try:
        response = requests.get(f"http://127.0.0.1:{port}")
        return response.status_code == 200
    except:
        return False

def stream_output(pipe, queue):
    """Read output from pipe and put it in queue."""
    try:
        with pipe:
            for line in iter(pipe.readline, ''):
                queue.put(line.strip())
    except Exception as e:
        logger.error(f"Error reading pipe: {str(e)}")
    finally:
        queue.put(None)

def start_server():
    logger.info("Starting MCP Server...")
    
    # Find an available port
    try:
        port = find_available_port()
        logger.info(f"Found available port: {port}")
    except RuntimeError as e:
        logger.error(f"Failed to find available port: {str(e)}")
        return None
    
    # Start server process
    server_process = subprocess.Popen(
        [sys.executable, "-c", f"""
import sys
import os
sys.path.append(os.path.abspath('.'))
from server.main import start_server
start_server({port})
"""],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Create queues for stdout and stderr
    stdout_queue = Queue()
    stderr_queue = Queue()
    
    # Start threads to read output
    Thread(target=stream_output, args=[server_process.stdout, stdout_queue], daemon=True).start()
    Thread(target=stream_output, args=[server_process.stderr, stderr_queue], daemon=True).start()
    
    # Wait for server to start
    retries = 0
    max_retries = 10
    server_started = False
    
    while not server_started and retries < max_retries:
        # Check queues for output
        while True:
            # Check stdout
            try:
                line = stdout_queue.get_nowait()
                if line is None:
                    break
                logger.info(f"Server stdout: {line}")
            except:
                break
                
            # Check stderr
            try:
                line = stderr_queue.get_nowait()
                if line is None:
                    break
                logger.error(f"Server stderr: {line}")
            except:
                break
        
        # Check if server is responding
        if check_server_health(port):
            server_started = True
            break
            
        time.sleep(1)
        retries += 1
        logger.info(f"Waiting for server to start... (attempt {retries}/{max_retries})")
    
    if not server_started:
        logger.error("Failed to start server!")
        # Dump any remaining output
        while True:
            try:
                line = stderr_queue.get_nowait()
                if line is None:
                    break
                logger.error(f"Server stderr: {line}")
            except:
                break
        return None
    
    logger.info("Server started successfully!")
    return server_process

def start_client():
    logger.info("Starting Mood Music Client...")
    client_process = subprocess.Popen(
        [sys.executable, "-m", "client.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return client_process

def main():
    # Check if .env file exists
    if not os.path.exists('.env'):
        logger.error("Error: .env file not found!")
        logger.error("Please create a .env file with your OpenAI API key.")
        logger.error("Add OPENAI_API_KEY=your_api_key to the .env file.")
        sys.exit(1)

    try:
        # Start server first
        server = start_server()
        if not server:
            sys.exit(1)
            
        # Start client
        client = start_client()
        
        # Monitor processes
        while True:
            # Check if either process has terminated
            if server.poll() is not None:
                logger.error("Server process terminated unexpectedly!")
                break
            if client.poll() is not None:
                logger.error("Client process terminated unexpectedly!")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        # Cleanup
        try:
            if 'server' in locals():
                server.terminate()
                server.wait(timeout=5)
            if 'client' in locals():
                client.terminate()
                client.wait(timeout=5)
        except:
            logger.error("Error during cleanup")

if __name__ == "__main__":
    main() 