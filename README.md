# Resume Checker AI 🤖

An application that analyzes resumes against job descriptions using Google Gemini and ChromaDB. It features a deep "Recruiter Persona" analysis engine that evaluates candidates on specific heuristics, content style, and formatting.

## 🚀 Features

- **Deep Resume Analysis**:
  - **7-Point Recruiter Check**: Scans for Job Title Match, Product Knowledge, Value Add, and more.
  - **Heuristic Guard**: Flags unprofessional emails (no Hotmail!), layout issues, and "Resume Sins" (like objective sections).
  - **Skill Verification**: Uses Vector Embeddings (ChromaDB) to valid skills against the resume.
- **Modern User Interface**:
  - **Modern Dashboard**: Built with **React, TypeScript, and TailwindCSS**.
  - **Interactive Feedback**: Visual tick lists and red flag warnings.
  - **Animations**: Smooth transitions using Framer Motion.
- **Robust Backend**:
  - **FastAPI**: High-performance Python backend.
  - **Resilient AI**: Handles API rate limits (including 503 Overload) with smart retries.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.9+, Google Gemini, ChromaDB
- **Frontend**: React, TypeScript, Vite, TailwindCSS, Lucide Icons, Framer Motion

## 📦 Setup & Installation

1.  **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd resume-checker-ai
    ```

2.  **Backend Setup**:

    ```bash
    # Create and activate venv
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate # Mac/Linux

    # Install Python dependencies
    pip install -r requirements.txt
    ```

3.  **Frontend Setup**:

    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

4.  **Set Up API Key**:
    Get a key from [Google AI Studio](https://aistudio.google.com/).
    ```bash
    # Windows (Powershell)
    $env:GOOGLE_API_KEY="your_api_key_here"
    ```

## 🏃‍♂️ How to Run

Since the React app is built and served by FastAPI, you only need to run the backend!

```bash
uvicorn main:app --reload
```

Then open your browser to: **http://localhost:8000**

## 📝 Usage

1.  **Upload**: Drag & Drop your PDF resume.
2.  **Job Description**: Paste the JD.
3.  **Analyze**: Watch the agents work in parallel to verify skills and apply recruiter heuristics.
4.  **Results**:
    - Check your **7-Point Score**.
    - Review **Red Flags** & **Style Critiques**.
    - See **Strong Matches** and **Missing Skills**.
    - Prepare with custom **Interview Questions**.

![alt text](image-1.png)
