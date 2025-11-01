# Real-Time Wikipedia Edit Stream Dashboard

## Overview

This project visualizes real-time Wikipedia edit activity, distinguishing between human and bot edits. It uses a modern data pipeline:
**Wikipedia → Kafka → Spark → Redis → Dash Dashboard**

## Features

- Streams live Wikipedia edits using SSE
- Processes and aggregates data with Apache Spark
- Stores results in Redis for fast access
- Interactive dashboard built with Dash and Plotly
- Easy setup with Docker Compose

## Prerequisites

- **Windows, Mac, or Linux**
- **Docker Desktop** (includes Docker Compose)
- **Python 3.8+** (recommended: use a virtual environment)
- **Java 11** (required for Spark)
- **Git** (to clone the repo)

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/wikipedia-stream-dashboard.git
cd wikipedia-stream-dashboard
```

### 2. Install Docker Desktop

- Download and install Docker Desktop: https://www.docker.com/products/docker-desktop
- Start Docker Desktop

### 3. Install Java 11

- Download and install OpenJDK 11: https://adoptium.net/temurin/releases/?version=11
- Set JAVA_HOME environment variable (see [Java setup guide](#java-setup-guide) below)

### 4. Create and Activate Python Virtual Environment

```sh
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 5. Install Python Dependencies

```sh
pip install -r requirements.txt
```

### 6. Start Backend Services

```sh
docker-compose up -d
```
This will start Kafka, Zookeeper, and Redis containers.

### 7. Run the Data Pipeline

You can use the provided batch script (Windows):

```sh
run_stream_pipeline.bat
```

Or run each step manually:

```sh
# Activate venv first!
python producer.py      # Streams Wikipedia edits to Kafka
python processor.py     # Processes Kafka messages and writes to Redis
python dashboard.py     # Starts the Dash dashboard
```

### 8. View the Dashboard

Open your browser and go to:
[http://127.0.0.1:8050/](http://127.0.0.1:8050/)

---

## Java Setup Guide

**Windows:**
- Download MSI installer from [Adoptium](https://adoptium.net/temurin/releases/?version=11)
- Install to `C:\Program Files\Eclipse Adoptium\jdk-11.x.x`
- Set JAVA_HOME:
  ```bat
  setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-11.x.x"
  setx PATH "%JAVA_HOME%\\bin;%PATH%"
  ```

**Mac/Linux:**
- Use Homebrew or apt:
  ```sh
  brew install openjdk@11
  export JAVA_HOME="$(/usr/libexec/java_home -v 11)"
  export PATH="$JAVA_HOME/bin:$PATH"
  ```

---

## Troubleshooting

- **Kafka/Redis not starting?**
  Make sure Docker Desktop is running.
- **Java errors?**
  Check that Java 11 is installed and JAVA_HOME is set.
- **No data in dashboard?**
  Check producer and processor logs for errors.
- **Firewall/Network issues?**
  Run `wikipedia_connectivity_check.py` to test your connection to Wikipedia's stream.

---

## Demo

![Demo](assets/wikipedia-realtime.gif)
---

## Project Structure

```
.
├── assets/
│   └── style.css
├── dashboard.py
├── docker-compose.yml
├── processor.py
├── producer.py
├── requirements.txt
├── run_stream_pipeline.bat
├── wikipedia_connectivity_check.py
├── LICENSE
└── README.md
```

---

## License

This project is licensed under the [MIT License](LICENSE).

Copyright (c) 2025 Animesh Raj

You are free to use, modify, and distribute this code with attribution. See the LICENSE file for details.

---

## Credits

- Wikipedia SSE stream
- Apache Kafka, Spark, Redis
- Dash and Plotly


