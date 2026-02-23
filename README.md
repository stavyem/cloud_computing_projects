# Multi-Tier Cloud Nutrition & Meal Management System

This repository showcases a full-scale backend system designed for managing dishes, meals, and dietary constraints, built with a microservices-inspired architecture and fully automated CI/CD pipelines.

## 🚀 System Capabilities
* **Nutritional REST API:** A Flask-based service that integrates with external Nutrition APIs (API-Ninjas) to fetch real-time data for dishes.
* **Microservices Architecture:** * **Meals Service:** Manages dish collections and complex meal compositions.
  * **Diets Service:** Handles dietary restrictions and data filtering.
* **Database Management:** Persistent storage using **MongoDB** for flexible data schemas and efficient querying.
* **Reverse Proxy:** **Nginx** configuration used as a gateway to manage traffic across services and enforce access control (GET-only restrictions for specific routes).
* **Containerization:** Full system orchestration using **Docker** and **Docker-Compose** for seamless environment reproducibility.

## 🛠 Tech Stack
* **Backend:** Python (Flask, Flask-RESTful)
* **Data:** MongoDB, PyMongo
* **Infrastructure:** Nginx, Docker, Docker-Compose
* **CI/CD:** GitHub Actions (Automated building, Docker Hub deployment, and Pytest suites)
* **Tools:** Requests, JQ, Pytest

## ⚙️ CI/CD Workflow
The project includes a robust GitHub Actions pipeline that triggers on every push:
1. **Build:** Automatically builds the Docker image and pushes it to Docker Hub.
2. **Integration Testing:** Spins up the containerized service and runs a comprehensive **Pytest** suite to ensure API integrity.
3. **Automated Reporting:** Runs automated health checks and queries against the running service, generating detailed execution logs and artifacts.

## 📂 Project Structure
* `/meals`: Core logic for dish and meal management.
* `/diets`: Independent service for managing dietary information.
* `/reverse`: Nginx configuration for the reverse proxy layer.
* `.github/workflows`: Automation scripts for the full CI/CD lifecycle.

---
*This project was developed as part of a Cloud Computing course, focusing on modern backend engineering standards.*
