# Camera Control IoT API

A FastAPI-based system for managing and controlling ONVIF-compatible IP cameras. This project provides a unified API to control diverse cameras with real-time video streaming and PTZ (Pan-Tilt-Zoom) control through WebSockets.

## Features

- RESTful API for camera CRUD operations
- Real-time video streaming via WebSocket
- PTZ (Pan-Tilt-Zoom) control for ONVIF cameras
- Web-based dashboard for camera management
- SQLite database for camera configuration storage
- Docker support for easy deployment

## Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: SQLite with SQLAlchemy (async)
- **Camera Protocol**: ONVIF
- **Real-time Communication**: WebSockets
- **Video Processing**: OpenCV
- **Frontend**: Vanilla JavaScript with WebSocket client

## Project Structure

```
cam-control-iot/
├── api/                          # Backend API
│   ├── src/
│   │   ├── core/                # Core configurations
│   │   ├── service/
│   │   │   └── camera/          # Camera CRUD operations
│   │   │       ├── route.py     # API routes
│   │   │       ├── curd.py      # Database operations
│   │   │       └── schema.py    # Pydantic schemas
│   │   ├── websocket/
│   │   │   └── camera_control_stream.py  # WebSocket handler
│   │   └── main.py              # FastAPI application
│   ├── pyproject.toml           # Dependencies
│   └── Dockerfile
├── index.html                   # Dashboard UI
├── docker-compose.yaml          # Docker configuration
├── Makefile                     # Development commands
└── README.md
```

## Installation

### Prerequisites

- Python 3.12+
- Poetry (Python package manager)
- Docker & Docker Compose (optional)

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd cam-control-iot
```

2. Start the application:
```bash
make dev
```

This will build and start the API server on `http://localhost:8000`

3. Access the dashboard:
   - Open `index.html` in your browser
   - Or visit `http://localhost:8000/docs` for API documentation

### Manual Setup

1. Navigate to the API directory:
```bash
cd api
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Run the development server:
```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Camera CRUD Operations

#### 1. Create Camera

**Endpoint**: `POST /camera/`

**Request Body**:
```json
{
  "name": "Front Door Camera",
  "ip_address": "192.168.1.100",
  "port": 80,
  "username": "admin",
  "password": "password123",
  "is_active": false,
  "image": null
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Front Door Camera",
  "ip_address": "192.168.1.100",
  "port": 80,
  "username": "admin",
  "password": "password123",
  "is_active": false,
  "image": null
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/camera/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Front Door Camera",
    "ip_address": "192.168.1.100",
    "port": 80,
    "username": "admin",
    "password": "password123",
    "is_active": false
  }'
```

#### 2. Get All Cameras

**Endpoint**: `GET /camera/`

**Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Front Door Camera",
    "ip_address": "192.168.1.100",
    "port": 80,
    "username": "admin",
    "password": "password123",
    "is_active": false,
    "image": null
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/camera/"
```

#### 3. Get Single Camera

**Endpoint**: `GET /camera/{camera_id}`

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Front Door Camera",
  "ip_address": "192.168.1.100",
  "port": 80,
  "username": "admin",
  "password": "password123",
  "is_active": false,
  "image": null
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Camera not found"
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/camera/550e8400-e29b-41d4-a716-446655440000"
```

#### 4. Update Camera

**Endpoint**: `PUT /camera/{camera_id}`

**Request Body** (all fields optional):
```json
{
  "name": "Updated Camera Name",
  "ip_address": "192.168.1.101",
  "port": 8080,
  "username": "newadmin",
  "password": "newpassword",
  "is_active": true,
  "image": "base64_encoded_image"
}
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Camera Name",
  "ip_address": "192.168.1.101",
  "port": 8080,
  "username": "newadmin",
  "password": "newpassword",
  "is_active": true,
  "image": "base64_encoded_image"
}
```

**cURL Example**:
```bash
curl -X PUT "http://localhost:8000/camera/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Camera Name",
    "is_active": true
  }'
```

#### 5. Delete Camera

**Endpoint**: `DELETE /camera/{camera_id}`

**Response** (204 No Content)

**Error Response** (404 Not Found):
```json
{
  "detail": "Camera not found"
}
```

**cURL Example**:
```bash
curl -X DELETE "http://localhost:8000/camera/550e8400-e29b-41d4-a716-446655440000"
```

## WebSocket: Camera Control & Streaming

### WebSocket Endpoint

**URL**: `ws://localhost:8000/camera/{camera_id}/combined`

This WebSocket endpoint provides:
- Real-time video streaming
- PTZ (Pan-Tilt-Zoom) control
- Bidirectional communication with the camera

### Connection Flow

1. **Connect to WebSocket**
```javascript
const ws = new WebSocket('ws://localhost:8000/camera/550e8400-e29b-41d4-a716-446655440000/combined');
```

2. **Handle Connection Events**
```javascript
ws.onopen = () => {
  console.log('Connected to camera');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onclose = () => {
  console.log('Disconnected from camera');
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### Message Types

#### 1. Stream Control

**Start Streaming**:
```javascript
ws.send(JSON.stringify({
  type: 'stream',
  action: 'start'
}));
```

**Server Response**:
```json
{
  "type": "stream_status",
  "status": "started"
}
```

**Stop Streaming**:
```javascript
ws.send(JSON.stringify({
  type: 'stream',
  action: 'stop'
}));
```

**Server Response**:
```json
{
  "type": "stream_status",
  "status": "stopped"
}
```

#### 2. Video Frames

When streaming is active, the server sends video frames:
```json
{
  "type": "frame",
  "frame": "base64_encoded_jpeg_image"
}
```

**Display Frame**:
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'frame') {
    const img = document.getElementById('video-feed');
    img.src = `data:image/jpeg;base64,${data.frame}`;
  }
};
```

#### 3. PTZ Control

**Move Camera** (Pan, Tilt, Zoom):
```javascript
// Values range from -1.0 to 1.0
ws.send(JSON.stringify({
  type: 'control',
  action: 'move',
  pan: 0.5,    // Move right (negative = left)
  tilt: 0.3,   // Move up (negative = down)
  zoom: 0.2    // Zoom in (negative = zoom out)
}));
```

**Server Response**:
```json
{
  "type": "control_ack",
  "action": "move",
  "success": true
}
```

**Stop Movement**:
```javascript
ws.send(JSON.stringify({
  type: 'control',
  action: 'stop'
}));
```

**Server Response**:
```json
{
  "type": "control_ack",
  "action": "stop",
  "success": true
}
```

#### 4. Heartbeat (Keep-Alive)

**Send Ping**:
```javascript
ws.send(JSON.stringify({
  type: 'ping'
}));
```

**Server Response**:
```json
{
  "type": "pong"
}
```

#### 5. Error Handling

**Server Error Response**:
```json
{
  "type": "error",
  "message": "Failed to connect to camera via ONVIF"
}
```

**Info Messages**:
```json
{
  "type": "info",
  "message": "Camera 550e8400-e29b-41d4-a716-446655440000 connected successfully"
}
```

### Complete WebSocket Example

```javascript
class CameraController {
  constructor(cameraId) {
    this.cameraId = cameraId;
    this.ws = null;
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/camera/${this.cameraId}/combined`);

    this.ws.onopen = () => {
      console.log('Connected to camera');
      this.sendPing(); // Start heartbeat
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onclose = () => {
      console.log('Disconnected');
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(data) {
    switch(data.type) {
      case 'frame':
        this.displayFrame(data.frame);
        break;
      case 'stream_status':
        console.log('Stream status:', data.status);
        break;
      case 'control_ack':
        console.log('Control acknowledged:', data.action);
        break;
      case 'error':
        console.error('Error:', data.message);
        break;
      case 'info':
        console.log('Info:', data.message);
        break;
      case 'pong':
        setTimeout(() => this.sendPing(), 30000); // Ping every 30s
        break;
    }
  }

  startStream() {
    this.ws.send(JSON.stringify({
      type: 'stream',
      action: 'start'
    }));
  }

  stopStream() {
    this.ws.send(JSON.stringify({
      type: 'stream',
      action: 'stop'
    }));
  }

  moveCamera(pan, tilt, zoom = 0) {
    this.ws.send(JSON.stringify({
      type: 'control',
      action: 'move',
      pan: Math.max(-1, Math.min(1, pan)),
      tilt: Math.max(-1, Math.min(1, tilt)),
      zoom: Math.max(-1, Math.min(1, zoom))
    }));
  }

  stopMovement() {
    this.ws.send(JSON.stringify({
      type: 'control',
      action: 'stop'
    }));
  }

  sendPing() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'ping' }));
    }
  }

  displayFrame(frameData) {
    const img = document.getElementById('video-feed');
    img.src = `data:image/jpeg;base64,${frameData}`;
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const camera = new CameraController('550e8400-e29b-41d4-a716-446655440000');
camera.connect();

// Start streaming
camera.startStream();

// Move camera up and right
camera.moveCamera(0.5, 0.5);

// Stop movement
camera.stopMovement();

// Zoom in
camera.moveCamera(0, 0, 0.5);

// Stop streaming
camera.stopStream();

// Disconnect
camera.disconnect();
```

## Using the Web Dashboard

1. Open `index.html` in your web browser

2. **Add a Camera**:
   - Fill in the camera details (name, IP, port, credentials)
   - Click "Add Camera"

3. **Connect to Camera**:
   - Click the "Connect" button on the camera panel
   - Wait for connection confirmation

4. **Start Streaming**:
   - Click "Start Stream" to begin video streaming
   - The video feed will appear in the panel

5. **Control Camera (PTZ)**:
   - Use directional buttons for pan/tilt
   - Use zoom buttons to zoom in/out
   - Click the center button to stop movement

6. **Stop Streaming**:
   - Click "Stop Stream" to end the video feed

7. **Disconnect**:
   - Click "Disconnect" to close the WebSocket connection

8. **Remove Camera**:
   - Click "Remove" to delete the camera from the database

## Development Commands

### Using Makefile

```bash
# Start development server with Docker
make dev

# Stop containers
make stop

# View logs
make logs
```

### Using Docker Compose

```bash
# Build and start
docker compose up --build

# Stop
docker compose stop

# Remove containers
docker compose down
```

## Camera Requirements

- ONVIF-compatible IP camera
- Network accessibility (same network or port forwarding)
- Valid credentials (username/password)
- PTZ support (for movement control)

## Troubleshooting

### Cannot Connect to Camera

1. Verify the camera IP address and port
2. Check username and password
3. Ensure camera is on the same network
4. Verify ONVIF is enabled on the camera
5. Check firewall settings

### Streaming Not Working

1. Ensure camera supports RTSP streaming
2. Check network bandwidth
3. Verify camera ONVIF profile compatibility
4. Check server logs for errors

### PTZ Control Not Responding

1. Verify camera supports PTZ via ONVIF
2. Check if PTZ is enabled in camera settings
3. Ensure camera is not in manual mode
4. Review WebSocket messages for errors

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support contact information here]
