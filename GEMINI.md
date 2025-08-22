
# GEMINI.md

## Project Overview

This is a Python-based web application for a smart lamp called "Tongling Smart Lamp System". The system provides a comprehensive set of features including:

*   **Smart Lamp Control:** Control the lamp's brightness and color temperature.
*   **Posture & Eye Health Monitoring:** Real-time posture detection and eye usage analysis.
*   **AI Voice Assistant:** Voice interaction for controlling the lamp and having conversations.
*   **Parental Guardian System:** Scheduled messaging and remote monitoring.
*   **Serial Communication:** Communication with the lamp hardware.
*   **Web Management Interface:** A web-based interface for managing and monitoring the system.

The backend is built with **FastAPI**, and it appears to be in the process of migrating from Flask. It uses a **MySQL** database for data storage and **WebSockets** and **Server-Sent Events (SSE)** for real-time communication. The frontend is likely a modern JavaScript framework (such as React, Vue, or Svelte) based on the file structure.

The application also incorporates several AI/ML features:
*   **Computer Vision:** **OpenCV** and **MediaPipe** are used for posture detection.
*   **Emotion Detection:** A custom emotion detection module using **RKNN**.
*   **Chatbot:** The `dashscope` library is used for the voice assistant.

## Building and Running

### 1. Environment Setup

The project uses Python 3.9+. You can set up the environment using either `conda` or `pip`.

**Using conda:**

```bash
# Create conda environment
conda env create -f environment.yml
conda activate pyserver
```

**Using pip:**

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

The application requires a MySQL database. Create a database and a user with the following commands:

```sql
CREATE DATABASE serial_data;
CREATE USER 'serial_user'@'localhost' IDENTIFIED BY 'Serial123!';
GRANT ALL PRIVILEGES ON serial_data.* TO 'serial_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configuration

*   **Database:** Edit the `DB_CONFIG` in `config.py` with your database credentials.
*   **Voice Assistant:** Configure your API key in `Audio/config.json`.

### 4. Running the Application

To start the application, run the following command:

```bash
python app.py
```

The application will be available at `http://0.0.0.0:5100`.

## Development Conventions

*   **Modular Structure:** The project is organized into modules, with each module responsible for a specific feature.
*   **Separation of Concerns:** There is a clear separation between the backend and frontend code.
*   **Commit Messages:** The `README.md` suggests using semantic commit messages (e.g., `feat:`, `fix:`, `docs:`).
*   **Framework Migration:** The project is migrating from Flask to FastAPI. New backend code should be written using FastAPI.
