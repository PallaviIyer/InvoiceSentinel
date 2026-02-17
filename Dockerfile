# Use official Python slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Streamlit uses 8501 by default
EXPOSE 8501

# We use a script to start both the UI and the Scheduler
CMD ["sh", "-c", "python scheduler.py & streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]

# Command to run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]