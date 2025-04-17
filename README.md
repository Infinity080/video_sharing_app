# Watch2Gether Clone (Simple Template)

This is a basic template for a Watch2Gether-style web application. It allows multiple users to watch a video together in sync, with real-time updates powered by WebSockets.

## Tech Stack

**Backend**
- Python
- Flask
- SQLite
- Flask-SocketIO

**Frontend**
- HTML
- JavaScript
- WebSockets (Socket.IO)

## Features

- Simple video sync
- Real-time play/pause control
- Minimal UI for demonstration
- Display of current users' ip addresses
- Lightweight and easy to customize

## Getting Started

### Prerequisites

- Python 3.X
- pip

### Installation

Clone the repo:

```bash
git clone https://github.com/Infinity080/video_sharing_app.git
cd video_sharing_app
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the App

```bash
python app.py
```

Open your browser and go to:

```
http://localhost:5000
```

### Database

The app uses SQLite. The database file is created automatically when the server starts.

## Project Structure

```
watch2gether-clone/
│
├── app.py               # Flask application with socket handling
├── templates/
│   └── index.html       # Simple UI
├── database.db          # SQLite database (auto-generated)
└── requirements.txt     # Python dependencies
```

## License

MIT License
