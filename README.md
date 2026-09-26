
# 💊 MediMate — AI-Powered Medication Assistant

> An AI-powered medication assistant designed to help users manage and understand their medication schedules through conversational AI, tool calling, structured medication data, and voice interaction.

MediMate combines **LLMs, agentic tool calling, PostgreSQL, Supabase, speech-to-text, and text-to-speech** to provide a conversational interface for accessing personalized medication information and schedules.

The project is being developed incrementally, with the current focus on building a reliable AI and database backend before expanding into a complete user-facing application.

---

## 🎯 Problem

Managing multiple medications can become difficult, especially when users need to remember:

- Which medicine to take
- How much to take
- When to take it
- Whether it should be taken before or after food
- Which medicines are scheduled on specific days
- Medication schedules with different frequencies

Traditional reminder systems mainly notify users at fixed times but provide limited conversational interaction.

**MediMate aims to provide a more natural interface where users can simply ask questions about their medication schedule and receive information retrieved directly from their stored medication data.**

---

## 💡 Solution

MediMate uses an LLM-powered agent that can decide when it needs medication information and call specialized tools to retrieve the required data from a structured PostgreSQL database.

Instead of allowing the LLM to generate medication information from its own knowledge, medication-related responses are grounded in the user's stored data.

### Example Workflow

```text
User
 │
 │ "What medicines do I take at 8 PM?"
 ↓
Gemini AI Agent
 │
 ↓
Tool Selection
 │
 ↓
get_medicines_by_time()
 │
 ↓
Supabase / PostgreSQL
 │
 ↓
Structured Medication Data
 │
 ↓
Gemini AI Agent
 │
 ↓
Clear Response
````

---

# 🏗️ Project Architecture

```text
                         ┌─────────────────────┐
                         │       User          │
                         └──────────┬──────────┘
                                    │
                          Text / Voice Input
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                 Text Input                    Voice Input
                    │                               │
                    │                     Gemini Live STT
                    │                               │
                    │                         Text Transcript
                    │                               │
                    └───────────────┬───────────────┘
                                    ↓
                         ┌─────────────────────┐
                         │    Gemini Agent     │
                         │ Gemini 3.1 Flash    │
                         │       Lite          │
                         └──────────┬──────────┘
                                    │
                              Tool Calling
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ↓                      ↓                      ↓
      Get All Medicines       Get Medicine          Get by Day /
                              by Name               Get by Time
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    ↓
                         ┌─────────────────────┐
                         │       Supabase      │
                         │    PostgreSQL DB    │
                         └──────────┬──────────┘
                                    │
                           Structured Results
                                    ↓
                         ┌─────────────────────┐
                         │    Gemini Agent     │
                         └──────────┬──────────┘
                                    ↓
                              Text Response
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                       Text                  Voice
                         │                     │
                         │              Gemini TTS
                         │                     │
                         └──────────┬──────────┘
                                    ↓
                                  User
```

---

# 🧠 Core Features

## 🤖 Conversational AI

Users can interact with MediMate using natural language instead of navigating through medication records manually.

Examples:

```text
"What medicines am I taking?"

"What do I need to take at 8 PM?"

"What medicines do I take on Monday?"

"Tell me everything about Metformin."
```

---

## 🔧 LLM Tool Calling

The AI agent has access to specialized medication tools:

| Tool                      | Purpose                                             |
| ------------------------- | --------------------------------------------------- |
| `get_medicines()`         | Retrieves the complete medication list              |
| `get_medicine_by_name()`  | Retrieves information for a specific medicine       |
| `get_medicines_by_day()`  | Retrieves medicines scheduled for a particular day  |
| `get_medicines_by_time()` | Retrieves medicines scheduled for a particular time |
| `get_due_medicines()`     | Retrieves medicines due at the current time         |

The agent determines which tool or combination of tools is required to answer the user's request.

---

## 🔄 Multi-Tool Workflows

MediMate supports workflows where a single user request requires multiple tools.

Example:

```text
"What medicines do I take today,
and which ones do I take at 8 PM?"
```

The agent can retrieve:

```text
Today's medication schedule
          +
8 PM medication schedule
          ↓
      Combined context
          ↓
      Final response
```

---

## 🗄️ Structured Medication Database

Medication information is stored in PostgreSQL through Supabase rather than as unstructured text.

```text
profiles
   │
   └── medications
          │
          └── medication_schedules
```

Medication records can contain:

* Medicine name
* Dosage / strength
* Purpose
* Prescribed-for information
* Instructions
* Dose quantity
* Dose unit
* Scheduled time
* Frequency
* Duration
* Days of the week
* Meal relationship
* Meal timing offsets

This structure allows the AI tools to retrieve precise schedule information.

---

## 🎤 Voice Interaction

MediMate supports an optional voice workflow:

```text
🎤 User Speech
      ↓
Gemini Live Transcription
      ↓
Text Transcript
      ↓
Gemini AI Agent
      ↓
Tool Calling
      ↓
Supabase
      ↓
Text Response
      ↓
Gemini TTS
      ↓
🔊 Spoken Response
```

The text response remains visible while the same response is converted into speech.

---

# 🛡️ Safety-Oriented Design

MediMate is designed as a **medication information and reminder assistant**, not a medical decision-making system.

The AI is instructed to:

* Use stored medication information when available
* Avoid inventing medication details
* Never modify prescribed dosages
* Never recommend changing medication schedules
* Clearly indicate when requested information is unavailable
* Present medication and schedule information in simple language

The system is intended to retrieve and communicate **user-provided medication information**, not replace a doctor or pharmacist.

---

# 🛠️ Tech Stack

### AI / LLM

* Google Gemini
* Gemini 3.1 Flash Lite
* Gemini Live Transcription
* Gemini 3.1 Flash TTS

### Backend

* Python
* OpenAI-compatible Gemini API
* Function / Tool Calling

### Database

* PostgreSQL
* Supabase

### Voice

* Gemini Live
* `sounddevice`
* Speech-to-Text
* Text-to-Speech

### Development

* Python
* Jupyter Notebook for experimentation
* Modular Python backend

### Frontend

* Streamlit *(being implemented)*

---

# 📁 Project Structure

```text
AI-MEDICATION-ASSISTANT/
│
├── app/
│   ├── database/
│   │
│   ├── tools/
│   │
│   ├── prompts/
│   │   └── system_prompt.py
│   │
│   ├── utils/
│   │   ├── voice.py
│   │   └── tts.py
│   │
│   └── main.py
│
├── data/
│
├── ui/
│
├── main.ipynb
│
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

---

# 🔄 Development Roadmap

MediMate is being developed incrementally.

## Phase 1 — Basic LLM Assistant

* [x] Gemini integration
* [x] Basic conversational responses
* [x] Safety-oriented system prompt

## Phase 2 — Tool Calling

* [x] Function/tool schemas
* [x] Tool execution loop
* [x] Medication retrieval tools

## Phase 3 — Medication Database

* [x] Supabase PostgreSQL integration
* [x] Medication schema
* [x] Medication schedule schema
* [x] Structured medication retrieval

## Phase 4 — Time-Aware Medication Retrieval

* [x] Retrieve medications by time
* [x] Retrieve currently due medications
* [x] Date-range handling
* [x] Day-based schedule handling

## Phase 5 — Multi-Tool Workflow

* [x] Multiple tool calls in a single request
* [x] Combined tool results
* [x] Context-aware final responses

## Phase 6 — Voice Interaction

* [x] Real-time speech-to-text
* [x] Voice → text → agent pipeline
* [x] Text-to-speech
* [x] Voice response pipeline

## Phase 7 — User Authentication & Application UI

* [ ] Supabase authentication
* [ ] User-specific medication access
* [ ] Dashboard
* [ ] Medication management interface
* [ ] Account center
* [ ] Streamlit frontend

## Phase 8 — Real Medicine Image Retrieval

* [ ] Medicine name → real medicine/package image
* [ ] Reliable image sources
* [ ] Image display in medication interface

## Phase 9 — Multimodal Medication Understanding

* [ ] Image-based medication input
* [ ] Multimodal model integration
* [ ] Safety-aware visual interpretation

## Phase 10 — Agentic Medication Assistant

* [ ] Expanded agentic workflows
* [ ] Multiple specialized tools
* [ ] Context-aware medication interactions

## Future

* [ ] RAG layer for trusted medication information
* [ ] Additional personalization
* [ ] Production-ready security and deployment

---

# 🚀 Current Status

**MediMate's core AI and database backend is functional.**

The current system supports:

```text
Natural Language
      ↓
Gemini Agent
      ↓
Tool Calling
      ↓
Supabase PostgreSQL
      ↓
Structured Medication Data
      ↓
AI Response
```

Voice interaction has also been integrated:

```text
Voice
 ↓
Gemini Live STT
 ↓
AI Agent
 ↓
Tools
 ↓
Supabase
 ↓
Response
 ↓
Gemini TTS
```

The next development stage is the **user-facing application layer**, beginning with authentication and a Streamlit dashboard.

---

# ⚠️ Development Note

The current database contains **synthetic medication records for development and testing**. The application is not intended to provide medical diagnosis, prescribing, or dosage recommendations.

---

# 📌 Project Goal

MediMate is being developed as an exploration of how **LLMs, tool calling, structured databases, voice interfaces, and agentic workflows** can be combined to build a practical AI application around a real-world problem.

```
```
