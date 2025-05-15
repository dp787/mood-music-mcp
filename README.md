# 🎵 Mood Music Explorer

A modern application that recommends music based on your mood using AI. This project uses OpenAI's GPT model to provide personalized song recommendations that match your emotional state.

## ✨ Features

- 🎯 Real-time mood-based music recommendations
- 🤖 AI-powered song suggestions using OpenAI's GPT model
- 💫 Modern, user-friendly interface
- 🔄 WebSocket-based real-time communication
- 🎨 Beautiful dark theme design

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dp787/mood-music-mcp.git
cd mood-music-mcp
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your OpenAI API key:
```env
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

1. Start the server and client using the run script:
```bash
python run.py
```

This will:
- Start the WebSocket server
- Launch the GUI client
- Automatically connect the client to the server

## 🎮 How to Use

1. Once the application starts, you'll see the main window with a status indicator
2. Enter your current mood in the text field (e.g., "happy", "melancholic", "energetic")
3. Click "Get Recommendations" or press Enter
4. The application will display 5 song recommendations that match your mood, including:
   - Song name
   - Artist
   - Why the song matches your mood

## 🏗️ Architecture

The project consists of two main components:

### Server (`server/main.py`)
- FastAPI WebSocket server
- OpenAI integration for music recommendations
- Asynchronous request handling
- Port auto-discovery

### Client (`client/main.py`)
- Modern Tkinter-based GUI
- Real-time WebSocket communication
- Beautiful dark theme interface
- Responsive design

## 🛠️ Technical Details

- **Backend Framework**: FastAPI
- **Frontend**: Tkinter with custom styling
- **AI Integration**: OpenAI GPT-3.5 Turbo
- **Communication**: WebSocket protocol
- **Async Support**: asyncio and websockets
- **Error Handling**: Comprehensive error management

## 🎨 UI Features

- Dark theme with modern color scheme
- Responsive text areas
- Status indicators
- Loading states
- Formatted song recommendations
- Error handling with visual feedback

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- OpenAI for their powerful GPT API
- FastAPI for the efficient web framework
- The Python community for excellent libraries 