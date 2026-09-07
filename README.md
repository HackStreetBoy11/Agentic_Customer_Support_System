# 🤖 Agentic Customer Support System with Deterministic Guardrails & Human-in-the-Loop (HITL)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful_Workflows-FF6F00?style=flat)](https://www.langchain.com/langgraph)
[![Gemini 3.5 Flash](https://img.shields.io/badge/Google_Gemini-3.5_Flash-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-SQLite-003545?style=flat&logo=sqlite&logoColor=white)](https://sqlmodel.tiangolo.com/)
[![uv](https://img.shields.io/badge/Package_Manager-uv-DE5D43?style=flat)](https://github.com/astral-sh/uv)

An enterprise-grade, stateful AI Customer Support Agent designed to eliminate **LLM hallucinations in financial transactions**. Built with **LangGraph**, **Google Gemini 3.5 Flash**, **FastAPI**, **SQLModel**, and **Server-Sent Events (SSE)**.

---

## 🎯 The Problem

Most customer support chatbots built today are static LLM wrappers. While they handle simple Q&A well, granting them direct access to perform backend operations (like issuing financial refunds) introduces critical risks:
* **LLM Hallucinations:** Unrestricted agents can misinterpret policy and process unauthorized refunds.
* **Security & Financial Losses:** Lack of deterministic controls can lead to unauthorized balance updates.
* **Lack of Human Oversight:** Edge cases and angry customers receive robotic, automated responses rather than escalation to management.

---

## ✨ Key Features & Solutions

* **🛡️ Deterministic Policy Guardrails:** Pure Python safety checks enforce hard business rules (e.g., automated refunds are capped at **$100.00**).
* **🙋‍♂️ Human-in-the-Loop (HITL) Workflow:** Any refund exceeding $100 or originating from an **ANGRY** customer automatically halts automation and routes a ticket to the Admin Portal for human review.
* **💾 Real SQL Database Persistence:** Uses **SQLModel** and **SQLite** to execute live order lookups, address updates, and status changes (`PROCESSING` $\rightarrow$ `REFUNDED`).
* **📡 Real-time SSE Streaming:** Uses **Server-Sent Events (SSE)** to stream node execution steps, tool calls, and LLM tokens to the UI in real time.
* **⚡ Ultra-Fast Environment Setup:** Powered by **`uv`**, Rust-based dependency resolution and execution manager.

---

## 🏗️ System Architecture & Workflow

```text
               +-----------------------+
               |  User Chat Input UI   |
               +-----------+-----------+
                           |
                           v
              +------------+------------+
              |      Triage Node        |
              | (Gemini Structured Out) |
              +------------+------------+
                           |
                           v
              +------------+------------+
              |  Policy Guardrail Node  |
              |   (Deterministic Logic) |
              +------------+------------+
                           |
            +--------------+--------------+
            |                             |
 [Policy Violation: >$100              [Policy Passed: <=$100
   or ANGRY Sentiment]                 & CALM Sentiment]
            |                             |
            v                             v
+-----------+-----------+    +------------+------------+
|   Human Review Node   |    |     Execution Node      |
| (Creates DB Ticket &  |    |  (Binds SQLite Tools)   |
| Routes to Admin UI)   |    +------------+------------+
+-----------+-----------+                 |
            |                             v
            v                +------------+------------+
+-----------+-----------+    |    SQLite Tool Node     |
|   Admin Portal (HITL) |    | (process_refund, etc.)  |
| (Manager Approve/Reject|    +-------------------------+
+-----------------------+
