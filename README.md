# Mood Music MCP Server

A sophisticated MCP (Message Control Protocol) server that provides mood-based music recommendations. This project combines the power of sentiment analysis, the Spotify API, and a custom MCP protocol to deliver personalized music suggestions based on your emotional state.

## Features

- 🎵 Mood-based music recommendations
- 🤖 Natural language mood processing
- 🎯 Spotify API integration
- 💻 Beautiful desktop client interface
- 🔄 Custom MCP protocol implementation

## MCP Protocol Commands

The server accepts the following commands:

- `MOOD <mood>` - Get music recommendations based on a mood
- `GENRE <genre>` - Filter recommendations by genre
- `ARTIST <artist_name>` - Get mood-related songs from a specific artist
- `RANDOM` - Get random mood-based suggestions

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/music-mcp.git
cd music-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with your Spotify API credentials:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

4. Start the server:
```bash
python -m server.main
```

5. Launch the client:
```bash
python -m client.main
```

## Architecture

- `server/` - MCP server implementation using FastAPI
- `client/` - Desktop client application
- `models/` - Data models and sentiment analysis
- `utils/` - Helper functions and utilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 