# Resume Checker AI 🤖

An application that analyzes resumes against job descriptions using Google Gemini 2.5 Flash and ChromaDB. It features a deep "Recruiter Persona" analysis engine that evaluates candidates on specific heuristics, content style, and formatting.

You can run this application as a **Desktop GUI Application** or a **Web Application**.

## 🚀 Features

- **Deep Resume Analysis**:
  - **7-Point Recruiter Check**: Scans for Job Title Match, Product Knowledge, Value Add, and more.
  - **Heuristic Guard**: Flags unprofessional emails (no Hotmail!), layout issues, and "Resume Sins" (like objective sections).
  - **Skill Verification**: Uses Vector Embeddings (ChromaDB) to valid skills against the resume.
- **Two Ways to Run**:
  - **Desktop App (PyQt6)**: A native Windows-style GUI for quick, local analysis.
  - **Web App (React)**: A modern, browser-based dashboard with a premium UI.
- **Robust Backend**:
  - **FastAPI**: High-performance Python backend (for the Web App).
  - **Resilient AI**: Handles API rate limits (including 503 Overload) with smart retries.

## 🛠️ Tech Stack

- **Core Logic**: Python 3.9+, Google Gemini 2.5 Flash, ChromaDB
- **Desktop GUI**: PyQt6
- **Web App**: FastAPI, React, TypeScript, Vite, TailwindCSS, Framer Motion

## 📦 Setup & Installation

1.  **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd resume-checker-ai
    ```

2.  **Install Dependencies**:

    ```bash
    # Create and activate venv
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate # Mac/Linux

    # Install Python dependencies (including PyQt6 and FastAPI)
    pip install -r requirements.txt
    ```

3.  **Set Up API Key**:
    Get a key from [Google AI Studio](https://aistudio.google.com/).
    ```bash
    # Windows (Powershell)
    $env:GOOGLE_API_KEY="your_api_key_here"
    ```

---

## 🖥️ Option 1: Run Desktop App (GUI)

For a simple, native experience without needing a browser:

```bash
python gui_app.py
```

This opens a Windows application where you can select your PDF and view results instantly.

---

## 🌐 Option 2: Run Web Application

For the full premium UI experience with animations:

1.  **Build Frontend** (First time only):

    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

2.  **Start Server**:

    ```bash
    uvicorn main:app --reload
    ```

3.  **Open Browser**:
    Go to **http://localhost:8000**

---

## 📝 Usage

1.  **Upload**: Select/Drag your PDF resume.
2.  **Job Description**: Paste the JD.
3.  **Analyze**: Watch the agents work in parallel to verify skills and apply recruiter heuristics.
4.  **Results**:
    - Check your **7-Point Score**.
    - Review **Red Flags** & **Style Critiques**.
    - See **Strong Matches** and **Missing Skills**.
    - Prepare with custom **Interview Questions**.

![alt text](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHV3b2F3aGFudjRkY3BzNjByOGI3M3o4bmI0NDNwM3JyNDJtd3VvaiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/MDJ9IbxxvDUQM/giphy.gif)
