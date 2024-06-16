# Use the official Python image from the Docker Hub
FROM python:3

# Set the working directory
WORKDIR /app

# # Install system dependencies including libGL, libEGL, and other required libraries for X11 and Qt
# RUN apt-get update && \
#     apt-get install -y \
#     build-essential \
#     curl \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     libx11-dev \
#     libegl1 \
#     ffmpeg \
#     libsm6 \
#     libxext6 \
#     libxkbcommon-x11-0 \
#     libxcb1 \
#     libxcb-xinerama0 \
#     libxcb-cursor0 \
#     libxcb-icccm4 \
#     libdbus-1-3 \
#     libxcomposite1 \
#     libxcursor1 \
#     libxdamage1 \
#     libxrandr2 \
#     libxi6 \
#     libxtst6 \
#     libfontconfig1 \
#     xauth \
#     x11-apps \
#     && rm -rf /var/lib/apt/lists/*

# # Set environment variables for Qt and X11 forwarding
# ENV DISPLAY=unix$DISPLAY
# ENV QT_QPA_PLATFORM_PLUGIN_PATH=/usr/local/qt/plugins/platforms
# ENV QT_DEBUG_PLUGINS=1

# Install Python dependencies
RUN pip install \
    psutil \
    numpy \
    pandas \
    pandas-ta \
    requests \
    requests-oauthlib \
    openpyxl \
    pyside6 \
    pyside6-essentials \
    pyside6-addons

# Copy the application code into the container at /app
COPY Pyside6_UI_Classes/ Pyside6_UI_Classes/
COPY Database_Connec_Class/ Database_Connec_Class/
COPY SEC_API_Filling_Class/ SEC_API_Filling_Class/
COPY Main_App_Starter.py .

# Run the application
CMD ["python", "Main_App_Starter.py"]
