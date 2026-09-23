#!/bin/bash

# Update system
apt update -y

# Install basic tools
apt install -y curl wget nano

# Install Docker
apt install -y docker.io

# Start Docker service
systemctl start docker
systemctl enable docker

# Allow ubuntu user to use docker
usermod -aG docker ubuntu

# Create lab directory
mkdir -p /home/ubuntu/lab
cd /home/ubuntu/lab

# Create some initial files for Linux questions
touch file1.txt file2.txt
mkdir dir1 dir2

# Pull Docker images for faster execution later
docker pull nginx
docker pull alpine

# Create progress tracking file
touch /home/ubuntu/progress.log

echo "Environment setup completed"