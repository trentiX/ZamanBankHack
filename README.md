ZamanBankHack Prototype Setup Instructions
This document provides step-by-step instructions for the hackathon jury to set up and run our prototype locally. During the pitch, our team will handle all setup and demonstrations, but these steps allow you to test the project independently. The prototype consists of three main components: a web interface with a WebGL game, a backend server, and an AI assistant accessible via API endpoints exposed through ngrok.
Prerequisites
Before starting, ensure you have the following installed:

Node.js (v16 or higher, includes npm)
Python (v3.8 or higher)
ngrok (for tunneling the backend API)
A modern web browser (e.g., Chrome, Firefox)

Setup and Running Instructions
Step 1: Set Up ngrok for Backend API Tunneling

Download and install ngrok from ngrok.com.
Place the ngrok.exe executable in the C:\ngrok\ directory.
Open a terminal and navigate to the ngrok directory:cd C:\ngrok


Configure your ngrok authtoken (replace YOUR_TOKEN with your actual ngrok token):.\ngrok.exe config add-authtoken YOUR_TOKEN


Start an ngrok tunnel to expose port 8000 (used by the backend):.\ngrok.exe http 8000


Note the ngrok forwarding URL (e.g., https://<random>.ngrok.io). You will use this in Step 4.

Step 2: Run the Web Interface and WebGL Game

Download and install Node.js from nodejs.org if not already installed.
Clone or download the prototype repository to your local machine.
Open a terminal and navigate to the prototype’s root directory (where server.js is located).
Initialize a Node.js project and install required dependencies:npm init -y
npm install express compression


Start the web server:node server.js


Open a browser and navigate to http://localhost:8001 to access the web interface, which includes the WebGL game.

Note: The WebGL game is served through the web interface and does not require additional setup. Ensure the browser supports WebGL (most modern browsers do).
Step 3: Run the Backend

Ensure Python is installed and accessible from the terminal.
In a new terminal, navigate to the prototype’s root directory.
Run the backend server by executing:python Bank_config.py


The backend will start on port 8000, ready to handle API requests via the ngrok tunnel.

Step 4: Interact with the AI Assistant

In the web interface (http://localhost:8001), locate the text input field for the API endpoint.
Enter the ngrok forwarding URL from Step 1 (e.g., https://<random>.ngrok.io) appended with one of the following endpoints:
/analyst/analyze-finances (from npc_analyst.py): For financial analysis.
/banker/suggest-services (from npc_banker.py): For service suggestions.
/support/ask-banker (from npc_support.py): For support queries.Example: https://<random>.ngrok.io/analyst/analyze-finances


Submit the endpoint in the text field to connect to the chosen AI assistant functionality.

Step 5: Interact with the AI Assistant

Once the endpoint is submitted, the web interface will connect to the AI assistant.
Engage with the AI assistant through the interface to explore its features, such as financial analysis, service suggestions, or support queries.

Dependencies
Below is a list of all dependencies and libraries required to run the prototype:
Web (Node.js)

Node.js: Runtime environment for the web server and WebGL game.
express: Web framework for Node.js (used in server.js for serving the web interface).
compression: Middleware for compressing HTTP responses.

Backend (Python)

Python: Runtime for the backend server (Bank_config.py).
(Additional Python libraries, if any, are not specified in the provided instructions. Update this section if specific libraries like Flask or FastAPI are used in Bank_config.py, npc_analyst.py, npc_banker.py, or npc_support.py.)

Tunneling

ngrok: Tool for exposing the local backend server to the internet.

WebGL Game

No additional dependencies are required, as the WebGL game is assumed to be bundled within the web interface (served via server.js) and relies on browser WebGL support.

Notes

Ensure all terminals remain open while testing (one for ngrok, one for the Node.js server, and one for the Python backend).
If you encounter issues, verify that ports 8000 (backend) and 8001 (web) are not in use by other applications.
For the pitch, our team will handle all setup and demonstrate the prototype seamlessly.

Thank you for evaluating our project!
