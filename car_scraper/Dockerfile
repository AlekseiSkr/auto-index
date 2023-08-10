# Use an official Python runtime as the parent image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install Scrapy and Scrapy Splash
RUN pip install scrapy scrapy-splash

# Run your spider when the container launches
CMD ["scrapy", "crawl", "car_spyder.py"]
