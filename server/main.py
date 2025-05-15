from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging
import sys
import uvicorn
import socket
import openai
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
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

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Mood Music MCP Server")

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI async client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

manager = ConnectionManager()

async def get_music_recommendations(mood: str) -> List[Dict]:
    """Get music recommendations from OpenAI based on mood."""
    try:
        # Create a prompt for ChatGPT
        prompt = f"""Given the mood '{mood}', suggest 5 songs that match this emotion. 
        For each song, provide:
        1. The song name
        2. The artist name
        3. A brief explanation of why it matches the mood
        
        Format your response as a JSON object with a 'songs' array containing objects with:
        - name: song name
        - artist: artist name
        - reason: explanation
        """
        
        # Get recommendations from ChatGPT
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a music recommendation expert who provides song suggestions based on moods. Always respond with valid JSON containing a 'songs' array."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        # Parse the response
        content = completion.choices[0].message.content
        recommendations = json.loads(content)
        return recommendations.get("songs", [])
        
    except Exception as e:
        logger.error(f"Error getting recommendations from OpenAI: {str(e)}")
        raise e

async def process_mood_command(mood: str) -> Dict:
    """Process the MOOD command and return music recommendations."""
    try:
        # Simple mood processing - just lowercase and match
        mood_lower = mood.lower()
        logger.info(f"Processing mood: {mood_lower}")
        
        # Get recommendations from OpenAI
        recommendations = await get_music_recommendations(mood_lower)
        
        if not recommendations:
            raise Exception("No recommendations found for the given mood")
            
        return {
            "status": "success",
            "mood": mood_lower,
            "recommendations": recommendations
        }
            
    except Exception as e:
        error_msg = f"Error processing mood command: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                if message.get("command") == "MOOD":
                    response = await process_mood_command(message["params"].get("mood", ""))
                    await websocket.send_json(response)
                else:
                    await websocket.send_json({
                        "status": "error",
                        "message": f"Unknown command: {message.get('command')}"
                    })
            
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({
                    "status": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "online", "service": "Mood Music MCP Server"}

def start_server(port=None):
    """Start the FastAPI server"""
    if port is None:
        port = find_available_port()
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    try:
        port = find_available_port()
        logger.info(f"Starting server on 127.0.0.1:{port}")
        start_server(port)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1) 