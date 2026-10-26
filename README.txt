# CloudVault — Cloud-Based File Storage System

## Project Overview
CloudVault is a cloud-style file storage system built using Docker containers, Flask, and MinIO object storage.

## Technologies Used
- Docker and Docker Desktop
- Python and Flask
- MinIO object storage
- HTML and CSS

## Main Features
- Upload files through a web dashboard
- List stored files
- Download uploaded files
- Store files persistently
- Monitor container status, resource usage, and logs

## Project Files
- app.py — Web application
- Dockerfile — Instructions for building the application image
- requirements.txt — Python dependencies
- student-files-policy.json — Object storage access policy

## Running the Project
The application currently runs locally on the project developer's computer. The web dashboard is available at:

http://localhost:5000

MinIO Console:

http://localhost:9001

A complete setup on another computer requires Docker, MinIO configuration, and application configuration.

## Testing
File upload, download, persistence, container status, resource monitoring, and application logs were tested successfully.

## Security Note
This is an educational demonstration, not a production-ready secure storage service. Production deployment would require authentication, HTTPS, secure secret management, and a production web server.

## Conclusion
CloudVault demonstrates how Docker containers and object storage can be combined to build and monitor a cloud-style file storage application.

## Setup Requirements
- Windows 10/11
- Docker Desktop installed and running

## Configuration
Before running the application, configure the following environment variables for the web container:
- MINIO_ENDPOINT
- MINIO_ACCESS_KEY
- MINIO_SECRET_KEY

Use your own MinIO credentials. The `.env.example` file contains placeholders only.

## Important
The submitted application code has been configured to read MinIO credentials from environment variables. A complete deployment also requires a MinIO container, a `student-files` bucket, and suitable access permissions.

The project has been tested locally on the developer's computer. The included files are a project submission, not yet a one-click deployment package.

## Security
Do not publish credentials or expose this educational demo to the public internet. Production use requires authentication, HTTPS, secure secret management, and a production web server.
