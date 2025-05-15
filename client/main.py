import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import websockets
import asyncio
import threading
from queue import Queue
import webbrowser
from typing import Optional
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configure the window
        self.title("🎵 Mood Music Recommendations")
        self.geometry("1000x800")
        self.configure(bg="#1E1E2E")  # Dark theme background
        
        # Initialize websocket
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.message_queue = Queue()
        self.is_connected = False
        self.port = None

        # Create and configure styles
        self.style = ttk.Style()
        self.style.configure("Modern.TFrame", background="#1E1E2E")
        self.style.configure("Header.TFrame", background="#2D2D44", padding=20)
        self.style.configure("Input.TFrame", background="#2D2D44", padding=20)
        self.style.configure("Modern.TButton",
                           padding=(25, 12),
                           font=("Segoe UI", 11, "bold"))
        self.style.configure("Status.TLabel",
                           background="#1E1E2E",
                           foreground="#A9B1D6",
                           font=("Segoe UI", 10),
                           padding=10)
        self.style.configure("Title.TLabel",
                           background="#2D2D44",
                           foreground="#A9B1D6",
                           font=("Segoe UI", 24, "bold"),
                           padding=5)
        self.style.configure("Subtitle.TLabel",
                           background="#2D2D44",
                           foreground="#7AA2F7",
                           font=("Segoe UI", 12),
                           padding=5)

        self.create_widgets()
        
        # Start websocket connection
        self.connect_websocket()
        
        # Update UI periodically
        self.update_ui()

    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self, style="Modern.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header frame
        self.header_frame = ttk.Frame(self.main_frame, style="Header.TFrame")
        self.header_frame.pack(fill=tk.X, padx=0, pady=(0, 20))

        # Title and subtitle
        self.title_label = ttk.Label(self.header_frame,
                                   text="🎵 Mood Music Explorer",
                                   style="Title.TLabel")
        self.title_label.pack(fill=tk.X, pady=(0, 5))

        self.subtitle_label = ttk.Label(self.header_frame,
                                      text="Discover music that matches your emotions",
                                      style="Subtitle.TLabel")
        self.subtitle_label.pack(fill=tk.X)

        # Content frame
        self.content_frame = ttk.Frame(self.main_frame, style="Modern.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=30)

        # Status label with icon
        self.status_label = ttk.Label(self.content_frame,
                                    text="⚪ Status: Disconnected",
                                    style="Status.TLabel")
        self.status_label.pack(fill=tk.X, pady=(0, 20))

        # Mood input frame with gradient effect
        self.input_frame = ttk.Frame(self.content_frame, style="Input.TFrame")
        self.input_frame.pack(fill=tk.X, pady=(0, 20))

        # Mood entry with placeholder
        self.mood_entry = ttk.Entry(self.input_frame, 
                                  width=50,
                                  font=("Segoe UI", 12))
        self.mood_entry.pack(side=tk.LEFT, padx=(0, 15), ipady=8)
        self.mood_entry.insert(0, "Enter your mood...")
        self.mood_entry.bind("<FocusIn>", self.on_entry_click)
        self.mood_entry.bind("<Return>", lambda e: self.send_mood())

        # Send button with icon
        self.send_button = ttk.Button(self.input_frame,
                                    text="🔍 Get Recommendations",
                                    command=self.send_mood,
                                    style="Modern.TButton")
        self.send_button.pack(side=tk.LEFT)

        # Create output area with custom styling
        self.output_frame = ttk.Frame(self.content_frame, style="Modern.TFrame")
        self.output_frame.pack(fill=tk.BOTH, expand=True)

        # Results text area
        self.results_area = scrolledtext.ScrolledText(
            self.output_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#2D2D44",  # Darker background for contrast
            fg="#A9B1D6",  # Light text color
            insertbackground="#7AA2F7",  # Cursor color
            selectbackground="#7AA2F7",  # Selection background
            selectforeground="#FFFFFF",  # Selection text color
            padx=20,
            pady=20
        )
        self.results_area.pack(fill=tk.BOTH, expand=True)
        
        # Initially disable the button until connected
        self.send_button.state(['disabled'])

    def on_entry_click(self, event):
        """Handle entry field click."""
        if self.mood_entry.get() == "Enter your mood...":
            self.mood_entry.delete(0, tk.END)
            self.mood_entry.config(foreground='black')

    def update_ui(self):
        """Update UI elements based on connection state."""
        if self.is_connected:
            self.send_button.state(['!disabled'])
            self.status_label.config(text="🟢 Connected and Ready")
            self.status_label.config(foreground="#9ECE6A")  # Green color
        else:
            self.send_button.state(['disabled'])
            self.status_label.config(text="🔴 Disconnected")
            self.status_label.config(foreground="#F7768E")  # Red color
        
        # Schedule next update
        self.after(1000, self.update_ui)

    async def find_server_port(self, start_port=8000, max_port=8020):
        """Try to connect to different ports to find the server."""
        for port in range(start_port, max_port + 1):
            try:
                url = f"ws://127.0.0.1:{port}/ws"
                logger.info(f"Trying to connect to {url}")
                async with websockets.connect(url, timeout=1) as ws:
                    self.port = port
                    logger.info(f"Found server on port {port}")
                    return port
            except:
                continue
        return None

    def connect_websocket(self):
        def run_websocket():
            asyncio.run(self.websocket_loop())

        threading.Thread(target=run_websocket, daemon=True).start()

    async def websocket_loop(self):
        while True:
            try:
                if not self.port:
                    self.port = await self.find_server_port(start_port=8000, max_port=8020)
                    if not self.port:
                        logger.error("Could not find server on any port")
                        self.results_area.delete(1.0, tk.END)
                        self.results_area.insert(tk.END, "Could not connect to server. Is the server running?\n")
                        await asyncio.sleep(5)
                        continue

                url = f"ws://127.0.0.1:{self.port}/ws"
                logger.info(f"Attempting to connect to WebSocket server at {url}")
                
                async with websockets.connect(url) as websocket:
                    self.ws = websocket
                    self.is_connected = True
                    logger.info("Successfully connected to WebSocket server")
                    
                    # Update UI to show connected status
                    self.results_area.delete(1.0, tk.END)
                    self.results_area.insert(tk.END, "Connected to server! You can now enter your mood.\n")

                    while True:
                        try:
                            message = await websocket.recv()
                            logger.info(f"Received message: {message}")
                            self.handle_message(message)
                        except websockets.ConnectionClosed:
                            logger.error("WebSocket connection closed")
                            break
                        except Exception as e:
                            logger.error(f"Error receiving message: {str(e)}")
                            break

            except Exception as e:
                self.is_connected = False
                self.ws = None
                self.port = None  # Reset port so we try finding the server again
                error_msg = f"Connection error: {str(e)}"
                logger.error(error_msg)
                self.results_area.delete(1.0, tk.END)
                self.results_area.insert(tk.END, f"Lost connection to server. Retrying...\n")
                await asyncio.sleep(5)  # Wait before retrying

    def send_mood(self):
        """Send mood to server and update UI."""
        if not self.is_connected or not self.ws:
            self.results_area.delete(1.0, tk.END)
            self.results_area.insert(tk.END, "Not connected to server. Please wait...\n")
            return

        mood = self.mood_entry.get()
        if mood and mood != "Enter your mood...":
            # Disable button while processing
            self.send_button.state(['disabled'])
            self.send_button.config(text="Getting recommendations...")
            
            message = {
                "command": "MOOD",
                "params": {"mood": mood}
            }
            
            logger.info(f"Sending mood request: {mood}")
            
            # Create a new event loop for this thread
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.ws.send(json.dumps(message)))
                
                # Clear the entry field
                self.mood_entry.delete(0, tk.END)
                self.mood_entry.insert(0, "Enter your mood...")
                
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                self.results_area.delete(1.0, tk.END)
                self.results_area.insert(tk.END, f"Error: {str(e)}\n")
            finally:
                # Re-enable button
                self.send_button.state(['!disabled'])
                self.send_button.config(text="Get Recommendations")
                loop.close()

    def handle_message(self, message):
        """Handle incoming messages from server."""
        try:
            data = json.loads(message)
            
            if data["status"] == "success":
                self.results_area.delete(1.0, tk.END)
                
                # Add header with mood
                header = f"🎵 Music Recommendations for: {data['mood'].title()}\n"
                self.results_area.insert(tk.END, header, "header")
                self.results_area.tag_configure("header", 
                                              font=("Segoe UI", 14, "bold"),
                                              foreground="#7AA2F7")
                
                # Add separator
                self.results_area.insert(tk.END, "═" * 60 + "\n\n")
                
                for i, song in enumerate(data["recommendations"], 1):
                    # Song number and title
                    song_header = f"{i}. {song['name']}\n"
                    self.results_area.insert(tk.END, song_header, "song_title")
                    self.results_area.tag_configure("song_title", 
                                                  font=("Segoe UI", 12, "bold"),
                                                  foreground="#BB9AF7")
                    
                    # Artist
                    artist_text = f"   👤 {song['artist']}\n"
                    self.results_area.insert(tk.END, artist_text, "artist")
                    self.results_area.tag_configure("artist", 
                                                  font=("Segoe UI", 11),
                                                  foreground="#7DCFFF")
                    
                    # Reason
                    reason_text = f"   💭 {song['reason']}\n"
                    self.results_area.insert(tk.END, reason_text, "reason")
                    self.results_area.tag_configure("reason", 
                                                  font=("Segoe UI", 10, "italic"),
                                                  foreground="#9ECE6A")
                    
                    # Separator
                    self.results_area.insert(tk.END, "   " + "─" * 40 + "\n\n")
                
                logger.info("Successfully displayed recommendations")
                
            else:
                error_msg = f"❌ Error: {data.get('message', 'Unknown error')}"
                self.results_area.delete(1.0, tk.END)
                self.results_area.insert(tk.END, error_msg + "\n", "error")
                self.results_area.tag_configure("error", 
                                              foreground="#F7768E",
                                              font=("Segoe UI", 11, "bold"))
                logger.error(error_msg)
                
        except Exception as e:
            error_msg = f"❌ Error processing response: {str(e)}"
            self.results_area.delete(1.0, tk.END)
            self.results_area.insert(tk.END, error_msg + "\n", "error")
            self.results_area.tag_configure("error", 
                                          foreground="#F7768E",
                                          font=("Segoe UI", 11, "bold"))
            logger.error(error_msg)

if __name__ == "__main__":
    app = ModernUI()
    app.mainloop() 