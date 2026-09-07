# 🤖 Agentic Customer Support System

### Deterministic Guardrails & Human-in-the-Loop (HITL)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat\&logo=python\&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful_Workflows-FF6F00?style=flat)](https://www.langchain.com/langgraph)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.5_Flash-4285F4?style=flat\&logo=google\&logoColor=white)](https://ai.google.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat\&logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-SQLite-003545?style=flat\&logo=sqlite\&logoColor=white)](https://sqlmodel.tiangolo.com/)
[![uv](https://img.shields.io/badge/Package_Manager-uv-DE5D43?style=flat)](https://github.com/astral-sh/uv)

An enterprise-style, stateful AI customer support system designed to safely automate customer-service workflows while preventing LLMs from directly making unsafe financial decisions.

The system combines **LangGraph**, **Google Gemini**, **FastAPI**, **SQLModel**, **SQLite**, and **Server-Sent Events (SSE)** with deterministic business rules and Human-in-the-Loop (HITL) approval.

---

## 📌 Table of Contents

* [Overview](#-overview)
* [Problem](#-the-problem)
* [Key Features](#-key-features)
* [System Architecture](#️-system-architecture)
* [Workflow](#-workflow)
* [Project Structure](#-project-structure)
* [Tech Stack](#️-tech-stack)
* [Prerequisites](#-prerequisites)
* [Installation](#️-installation)
* [Environment Variables](#-environment-variables)
* [Running the Application](#-running-the-application)
* [Test Data](#-pre-seeded-test-data)
* [Example Scenarios](#-example-scenarios)
* [API Documentation](#-api-documentation)
* [Safety Design](#️-safety-design)
* [Future Improvements](#-future-improvements)
* [License](#-license)

---

# 🎯 Overview

This project demonstrates how to build an **agentic customer-support workflow** where an LLM is responsible for understanding customer requests, but **critical business decisions remain deterministic**.

Instead of allowing the LLM to directly issue refunds or modify orders, the workflow separates:

1. **LLM reasoning**
2. **Deterministic policy validation**
3. **Database execution**
4. **Human approval**

This architecture significantly reduces the risk of hallucinations and unauthorized financial operations.

---

# 🚨 The Problem

Traditional customer-support chatbots are often simple LLM wrappers.

While this works well for general questions, giving an LLM direct access to financial operations can introduce serious risks.

### Major Problems

* **LLM hallucinations**

  * The model may misunderstand company policies.
  * It may incorrectly interpret a customer's request.

* **Unauthorized financial operations**

  * An unrestricted agent could potentially issue refunds that exceed business limits.

* **Lack of deterministic controls**

  * Important financial rules should not depend entirely on probabilistic LLM output.

* **Lack of human oversight**

  * High-value refunds and angry customers may require managerial approval.

### Solution

This project uses a **hybrid architecture**:

```text
LLM
 │
 │ Understands request
 ▼
Triage
 │
 ▼
Deterministic Policy Guardrail
 │
 ├───────────────┐
 │               │
 ▼               ▼
Policy Passed    Policy Violation
 │               │
 ▼               ▼
Execution        Human Review
 │               │
 ▼               ▼
SQLite           Admin Portal
```

The LLM can **recommend and classify**, but deterministic Python logic decides whether an operation is allowed.

---

# ✨ Key Features

## 🛡️ Deterministic Policy Guardrails

Refund operations are protected by hard-coded business rules.

For example:

```text
Refund <= $100
        ↓
Automatic processing allowed

Refund > $100
        ↓
Human approval required
```

The LLM cannot override these rules.

---

## 🙋 Human-in-the-Loop (HITL)

The workflow automatically escalates sensitive requests.

A review ticket is created when:

* Refund amount exceeds `$100`
* Customer sentiment is `ANGRY`
* The request violates business rules
* Manual approval is required

The manager can then:

```text
Approve → Execute operation
Reject  → Close request
```

---

## 💾 SQLite Database Persistence

The application uses:

* **SQLModel**
* **SQLite**

to store orders and review tickets.

Example order lifecycle:

```text
PROCESSING
     ↓
REFUND REQUEST
     ↓
POLICY CHECK
     ↓
APPROVED
     ↓
REFUNDED
```

The database is seeded automatically with test data when the application starts.

---

## 📡 Real-Time SSE Streaming

The application uses **Server-Sent Events (SSE)** to stream workflow activity to the frontend.

The UI can receive events such as:

```text
Triage started
        ↓
Customer sentiment detected
        ↓
Policy check started
        ↓
Policy passed
        ↓
Refund tool executed
        ↓
Database updated
```

This provides visibility into the agent's workflow execution.

---

## ⚡ Fast Development Environment

The project uses **uv** for dependency management and execution.

Benefits include:

* Fast dependency installation
* Deterministic environments
* Modern Python package management
* Fast application startup

---

# 🏗️ System Architecture

```text
                  ┌─────────────────────────┐
                  │   Customer Chat UI      │
                  │      index.html         │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │      Triage Node        │
                  │    Gemini Structured    │
                  │        Output           │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │  Policy Guardrail Node  │
                  │   Deterministic Python  │
                  └────────────┬────────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
            Policy Passed              Policy Violation
                  │                         │
                  ▼                         ▼
       ┌───────────────────┐      ┌────────────────────┐
       │  Execution Node   │      │ Human Review Node  │
       │                   │      │                    │
       │ SQLite Tools      │      │ Create DB Ticket   │
       └─────────┬─────────┘      └──────────┬─────────┘
                 │                           │
                 ▼                           ▼
       ┌───────────────────┐       ┌────────────────────┐
       │   SQLite Database │       │    Admin Portal    │
       │                   │       │     admin.html     │
       │ Orders            │       │                    │
       │ Review Tickets    │       │ Approve / Reject   │
       └───────────────────┘       └────────────────────┘
```

---

# 🔄 Workflow

The workflow follows these stages:

### 1. Customer Request

The customer submits a request through the chatbot.

Example:

```text
"I want a refund for order ORD-8821."
```

---

### 2. Triage

Gemini analyzes the request and produces structured information such as:

```text
Intent: refund
Order ID: ORD-8821
Sentiment: CALM
Amount: $89.99
```

---

### 3. Policy Guardrail

The request is passed to deterministic Python logic.

Example:

```text
Amount = $89.99
Limit  = $100

$89.99 <= $100
```

Therefore:

```text
POLICY PASSED
```

---

### 4. Execution

The execution node invokes the appropriate database tool.

Example:

```text
process_refund("ORD-8821")
```

The order status changes:

```text
PROCESSING → REFUNDED
```

---

### 5. Human Review

If the request violates policy:

```text
Amount > $100
```

or:

```text
Sentiment = ANGRY
```

the workflow stops automatic execution.

Instead:

```text
Customer Request
       ↓
Policy Violation
       ↓
Review Ticket Created
       ↓
Admin Portal
       ↓
Manager Decision
```

---

# 📂 Project Structure

```text
agentic-workflow-demo/
│
├── app/
│   ├── __init__.py
│   │
│   ├── database.py
│   │   └── SQLite engine, sessions, and database seeding
│   │
│   ├── models.py
│   │   └── SQLModel schemas for Order and ReviewTicket
│   │
│   ├── static/
│   │   ├── index.html
│   │   │   └── Customer support chatbot UI
│   │   │
│   │   └── admin.html
│   │       └── Manager/Admin HITL dashboard
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   │   └── LangGraph state and Pydantic models
│   │   │
│   │   ├── nodes.py
│   │   │   └── Triage, guardrail, and execution nodes
│   │   │
│   │   └── graph.py
│   │       └── LangGraph workflow assembly
│   │
│   └── tools/
│       ├── __init__.py
│       └── order_tools.py
│           └── Database tools for orders/refunds/address updates
│
├── .env
├── .gitignore
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

# 🛠️ Tech Stack

| Technology              | Purpose                   |
| ----------------------- | ------------------------- |
| **Python 3.11+**        | Core programming language |
| **LangGraph**           | Stateful agent workflow   |
| **Google Gemini**       | LLM-based request triage  |
| **FastAPI**             | Backend API server        |
| **SQLModel**            | Database ORM / models     |
| **SQLite**              | Persistent database       |
| **Pydantic**            | Structured validation     |
| **SSE**                 | Real-time event streaming |
| **HTML/CSS/JavaScript** | Frontend                  |
| **uv**                  | Dependency management     |

---

# 📋 Prerequisites

Before running the project, make sure you have:

* Python 3.11+
* Git
* uv
* Google Gemini API key

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/HackStreetBoy11/Agentic_Customer_Support_System.git
```

Navigate into the project:

```bash
cd Agentic_Customer_Support_System
```

---

## 2. Create the Environment

If you are using `uv`:

```bash
uv venv
```

Activate the environment.

### Windows

```powershell
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

Using `requirements.txt`:

```bash
uv pip install -r requirements.txt
```

Alternatively, if your dependencies are defined in `pyproject.toml`, you can use:

```bash
uv sync
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

### Windows PowerShell

```powershell
New-Item -ItemType File -Name .env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> ⚠️ Never commit your `.env` file to GitHub.

Make sure `.gitignore` contains:

```text
.env
*.db
__pycache__/
.venv/
```

---

# 🚀 Running the Application

Start the FastAPI server:

```bash
uv run uvicorn main:app --reload --port 8000
```

If everything is configured correctly, the server should start on:

```text
http://127.0.0.1:8000
```

---

# 🌐 Application Interfaces

### 💬 Customer Support Chatbot

```text
http://127.0.0.1:8000/static/index.html
```

Use this interface to:

* Ask questions
* Request refunds
* Request address updates
* Test different customer scenarios

---

### 🛡️ Admin / Manager Dashboard

```text
http://127.0.0.1:8000/static/admin.html
```

Use this interface to:

* View pending review tickets
* Review escalated requests
* Approve requests
* Reject requests

---

### 📑 Swagger API Documentation

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically provides interactive API documentation through Swagger UI.

---

# 🧪 Pre-Seeded Test Data

When the application starts, `app/database.py` initializes the SQLite database with sample orders.

| Order ID   | Item                |    Amount | Status     | Expected Behavior              |
| ---------- | ------------------- | --------: | ---------- | ------------------------------ |
| `ORD-8821` | Mechanical Keyboard |  `$89.99` | PROCESSING | Auto-approved refund           |
| `ORD-9940` | Gaming Monitor 27"  | `$349.50` | PROCESSING | HITL escalation                |
| `ORD-1102` | Wireless Mouse      |  `$25.00` | DELIVERED  | Refund/address update rejected |

---

# 🧪 Example Scenarios

## Scenario 1 — Automatic Refund

### Request

```text
"I want a refund for order ORD-8821."
```

Order amount:

```text
$89.99
```

Policy:

```text
$89.99 <= $100
```

Result:

```text
✅ Policy Passed
↓
Execution Node
↓
Refund Processed
↓
PROCESSING → REFUNDED
```

---

## Scenario 2 — High-Value Refund

### Request

```text
"I want a refund for order ORD-9940."
```

Order amount:

```text
$349.50
```

Policy:

```text
$349.50 > $100
```

Result:

```text
⚠️ Policy Violation
↓
Automation Stopped
↓
Review Ticket Created
↓
Admin Portal
↓
Manager Approval Required
```

---

## Scenario 3 — Angry Customer

Example:

```text
"This is ridiculous! I want my money back immediately!"
```

If the triage node classifies the customer as:

```text
ANGRY
```

the deterministic guardrail can route the request to:

```text
Human Review
```

This prevents sensitive situations from being handled entirely automatically.

---

## Scenario 4 — Invalid Order State

Order:

```text
ORD-1102
Status: DELIVERED
```

A refund or address update request is rejected according to the tool/business logic.

```text
Request
  ↓
Order Lookup
  ↓
Status = DELIVERED
  ↓
Operation Rejected
```

---

# 🛡️ Safety Design

One of the main design principles of this project is:

> **The LLM should not be the final authority for financial operations.**

The architecture separates AI reasoning from business-critical execution.

### LLM Responsibilities

The LLM can:

* Understand customer messages
* Identify intent
* Extract order IDs
* Determine sentiment
* Produce structured information

### Deterministic Code Responsibilities

Python logic controls:

* Refund limits
* Order status validation
* Allowed operations
* HITL escalation
* Database modifications

Therefore:

```text
              LLM
               │
               ▼
       Understand Request
               │
               ▼
      Structured Information
               │
               ▼
      Deterministic Rules
               │
       ┌───────┴───────┐
       ▼               ▼
     ALLOW           BLOCK
       │               │
       ▼               ▼
   DB Tool          Human Review
```

This provides an important safety boundary between probabilistic AI reasoning and deterministic financial execution.

---

# 📡 Real-Time Event Streaming

The application uses Server-Sent Events to provide real-time workflow updates.

Example event stream:

```text
event: node
data: Triage started

event: node
data: Policy validation started

event: node
data: Policy passed

event: tool
data: process_refund executed

event: database
data: Order status updated

event: complete
data: Refund completed
```

This allows the frontend to visualize what the agent is doing.

---


# 📊 Why This Architecture?

The project demonstrates a practical approach to building **safe agentic AI systems**.

Instead of:

```text
User → LLM → Database
```

the system uses:

```text
User
 ↓
LLM
 ↓
Structured Output
 ↓
Deterministic Guardrails
 ↓
 ┌──────────────┐
 │              │
 ▼              ▼
Safe          Unsafe
 │              │
 ▼              ▼
Tool          Human
Execution     Review
```

This makes the system more predictable, auditable, and suitable for workflows where incorrect actions can have financial consequences.

---

# 📄 License

This project is intended for educational, experimental, and portfolio purposes.

Add your preferred license here, for example:

```text
MIT License
```

---

# 👨‍💻 Author

**HackStreetBoy11**

GitHub:

https://github.com/HackStreetBoy11

Repository:

https://github.com/HackStreetBoy11/Agentic_Customer_Support_System
