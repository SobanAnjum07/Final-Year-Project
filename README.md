# Final-Year-Project

Welcome to the Final Year Project repository. This project is a comprehensive implementation of a Django-based application with a focus on a Retrieval-Augmented Generation (RAG) chatbot.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [System Design](#system-design)
- [Technical Details](#technical-details)
- [Pros and Cons](#pros-and-cons)
- [Contributors](#contributors)
- [License](#license)

## Project Overview
This project is developed as part of the final year requirements. It integrates various technologies to create a robust and scalable application. The primary focus is on implementing a chatbot using the RAG framework.

## Features
- **Django Framework**: Utilizes Django for rapid development and clean design.
- **RAG Chatbot**: Implements a chatbot using Retrieval-Augmented Generation for enhanced interaction.
- **FAISS Indexing**: Efficient similarity search and clustering of dense vectors.
- **OpenAI Integration**: Leverages GPT-3.5-turbo for natural language processing.

## Installation
To set up the project locally, follow these steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/SobanAnjum07/Final-Year-Project.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Final-Year-Project
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```
5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Configure the necessary environment variables in a `.env` file.
## Usage
To run the Django application, use the following command:
```bash
python manage.py runserver
```
The application will be accessible at `h
   pip install -r requirements.txt
   ```
6. Configure the necessary environment variables in a `.env` file.
## Usage
To run the Django application, use the following command:
```bash
python manage.py runserver
```
The application will be accessible at `URL_ADDRESS:8000`.
## System Design
The system design includes the following components:
- Django Framework: A web application framework for rapid development.
- RAG Chatbot: Implements a chatbot using Retrieval-Augmented Generation.
- FAISS Indexing: Efficient similarity search and clustering of dense vectors.
- OpenAI Integration: Leverages GPT-3.5-turbo for natural language processing.
## Technical Details
The project is built using the following technologies:
- Python: The programming language used for development.
- Django: A high-level Python web framework.
- FAISS: A library for efficient similarity search and clustering of dense vectors.
- OpenAI: A platform for natural language processing.
## Pros and Cons
### Pros
- Efficient similarity search and clustering of dense vectors.
- Natural language processing capabilities.
- Scalable and maintainable architecture.
### Cons
- Limited scalability for large datasets.
- Dependency on external services.
- Potential for security vulnerabilities.
## Contributors
- Muhammad Soban Anjum - BSDSF21A007 (Team Lead)
- Abdul Rehman Amer - BSDSF21A001
- Nauman Ishaq - BSDSF21A044