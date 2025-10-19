<p align="center">
      https://ibb.co.com/dwnNRHfH
</p>

<p align="center">
   <img alt="Static Badge" src="https://img.shields.io/badge/Views-729-009FB7">
   <img alt="Static Badge" src="https://img.shields.io/badge/Downloads-279-7678ED">
   <img src="https://img.shields.io/badge/Engine-Unity%202022.3.16f1-violet" alt="Unity Version">
   <img src="https://img.shields.io/badge/Version-v1.3-698f3f" alt="Game Version">
   <img src="https://img.shields.io/badge/License-MIT-f2542d" alt="License">
   <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/trentiX/KTed">
   <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/trentiX/KTed">
</p>



# ZamanBankHack Prototype Setup Instructions

This document provides step-by-step instructions for the hackathon jury to set up and run our prototype locally. During the pitch, our team will handle all setup and demonstrations, but these steps allow you to test the project independently. The prototype consists of three main components: a web interface with a WebGL game, a backend server, and an AI assistant accessible via API endpoints exposed through ngrok.

## Prerequisites
Before starting, ensure you have the following installed:
- **Node.js** (v16 or higher, includes npm)
- **Python** (v3.8 or higher)
- **ngrok** (for tunneling the backend API)
- A modern web browser (e.g., Chrome, Firefox)

## Setup and Running Instructions

### Step 1: Set Up ngrok for Backend API Tunneling
1. Download and install **ngrok** from [ngrok.com](https://ngrok.com/download).
2. Place the `ngrok.exe` executable in the `C:\ngrok\` directory.
3. Open a terminal and navigate to the ngrok directory:
   ```
   cd C:\ngrok
   ```
4. Configure your ngrok authtoken (replace `YOUR_TOKEN` with your actual ngrok token):
   ```
   .\ngrok.exe config add-authtoken YOUR_TOKEN
   ```
5. Start an ngrok tunnel to expose port 8000 (used by the backend):
   ```
   .\ngrok.exe http 8000
   ```
6. Note the ngrok forwarding URL (e.g., `https://<random>.ngrok.io`). You will use this in Step 4.

### Step 2: Run the Web Interface and WebGL Game
1. Download and install **Node.js** from [nodejs.org](https://nodejs.org) if not already installed.
2. Clone or download the prototype repository to your local machine.
3. Open a terminal and navigate to the prototype’s root directory (where `server.js` is located).
4. Initialize a Node.js project and install required dependencies:
   ```
   npm init -y
   npm install express compression
   ```
5. Start the web server:
   ```
   node server.js
   ```
6. Open a browser and navigate to `http://localhost:8001` to access the web interface, which includes the WebGL game.

**Note**: The WebGL game is served through the web interface and does not require additional setup. Ensure the browser supports WebGL (most modern browsers do).

### Step 3: Run the Backend
1. Ensure **Python** (v3.8 or higher) is installed and accessible from the terminal.
2. Install the required Python dependencies in a terminal:
   ```
   pip install fastapi uvicorn pandas numpy scikit-learn requests python-multipart
   ```
3. In a new terminal, navigate to the prototype’s root directory (where `Bank_config.py` is located).
4. Run the backend server using Uvicorn:
   ```
   uvicorn Bank_config:app --host 0.0.0.0 --port 8000
   ```
5. The backend will start on port 8000, ready to handle API requests via the ngrok tunnel.

### Step 4: Interact with the AI Assistant
1. In the web interface (`http://localhost:8001`), locate the text input field for the API endpoint.
2. Enter the ngrok forwarding URL from Step 1 (e.g., `https://<random>.ngrok.io`) appended with one of the following endpoints:
   - `/analyst/analyze-finances` (from `npc_analyst.py`): For financial analysis.
   - `/banker/suggest-services` (from `npc_banker.py`): For service suggestions.
   - `/support/ask-banker` (from `npc_support.py`): For support queries.
   Example: `https://<random>.ngrok.io/analyst/analyze-finances`
3. Submit the endpoint in the text field to connect to the chosen AI assistant functionality.

### Step 5: Interact with the AI Assistant
1. Once the endpoint is submitted, the web interface will connect to the AI assistant.
2. Engage with the AI assistant through the interface to explore its features, such as financial analysis, service suggestions, or support queries.

## Dependencies
Below is a list of all dependencies and libraries required to run the prototype:

### Web (Node.js)
- **Node.js**: Runtime environment for the web server and WebGL game.
- **express**: Web framework for Node.js (used in `server.js` for serving the web interface).
- **compression**: Middleware for compressing HTTP responses.

### Backend (Python)
- **Python**: Runtime for the backend server (`Bank_config.py`).
- **fastapi**: Framework for creating the API endpoints.
- **uvicorn**: ASGI server for running the FastAPI application.
- **pandas**: Used for data processing and analysis with DataFrames.
- **numpy**: Supports numerical operations.
- **scikit-learn**: Used for machine learning tasks, specifically SimpleImputer in this project.
- **requests**: Enables HTTP requests to other services.
- **python-multipart**: Handles form data processing with FastAPI.

### Tunneling
- **ngrok**: Tool for exposing the local backend server to the internet via a public URL.

### WebGL Game
- No additional dependencies are required, as the WebGL game is assumed to be bundled within the web interface (served via `server.js`) and relies on browser WebGL support.

## Notes
- Ensure all terminals remain open while testing (one for ngrok, one for the Node.js server, and one for the Python backend).
- If you encounter issues, verify that ports 8000 (backend) and 8001 (web) are not in use by other applications.
- For the pitch, our team will handle all setup and demonstrate the prototype seamlessly.

Thank you for evaluating our project!
