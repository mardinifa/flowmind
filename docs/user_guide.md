# FlowMind User Guide

## 1. Overview

FlowMind is a human-in-the-loop loan-processing prototype developed for
ClearPath Capital. It processes small-business loan applications and routes
them to one of three outcomes:

- autonomous conditional approval;
- autonomous decline;
- escalation to a human loan officer.

FlowMind is an educational prototype and must not be used for real lending
decisions without proper validation, security controls and regulatory review.

## 2. System Requirements

The following are required:

- Python 3.11 or later;
- Git;
- a modern web browser;
- internet access for installing Python packages.

The following are optional:

- Ollama with Llama 3 for the manual AI letter demonstration;
- Docker Desktop and n8n for external workflow orchestration;
- Supabase for remote database storage.

## 3. Download the Project

Open PowerShell and run:

```powershell
cd C:\Users\ADMIN
git clone https://github.com/mardinifa/flowmind
cd flowmind
```
