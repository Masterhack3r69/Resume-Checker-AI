import streamlit as st
import requests
import json

# Configuration
API_URL = "http://localhost:8000/analyze"

st.set_page_config(page_title="Resume Checker AI", layout="wide")

st.title("🤖 Resume Checker AI")
st.markdown("### Reverse RAG based Resume Analyzer")

# Layout
col1, col2 = st.columns(2)

with col1:
    st.header("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

    st.header("2. Job Description")
    job_description = st.text_area("Paste the Job Description here", height=300)

    analyze_btn = st.button("Analyze Resume", type="primary")

with col2:
    st.header("Results")
    
    if analyze_btn:
        if not uploaded_file:
            st.error("Please upload a resume.")
        elif not job_description:
            st.error("Please provide a job description.")
        else:
            with st.spinner("Analyzing... Extracting skills, verifying matches..."):
                try:
                    # Prepare the request
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    data = {"job_description": job_description}
                    
                    response = requests.post(API_URL, files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display Score
                        score = result.get("match_score", 0)
                        st.metric(label="Match Score", value=f"{score}%")
                        
                        # Display Analysis
                        analysis = result.get("analysis", {})
                        
                        st.subheader("✅ Strong Matches")
                        for item in analysis.get("strong_matches", []):
                            with st.expander(f"**{item.get('skill', 'Unknown')}**"):
                                st.write(f"_{item.get('evidence', '')}_")
                                
                        st.subheader("⚠️ Missing / Weak Skills")
                        for item in analysis.get("missing_skills", []):
                            st.write(f"- **{item.get('skill', 'Unknown')}**: {item.get('recommendation', '')}")

                        st.subheader("🎤 Interview Prep")
                        for question in result.get("interview_prep", []):
                            st.info(question)
                            
                    else:
                        st.error(f"Error: {response.text}")
                        
                except Exception as e:
                    st.error(f"Connection Error: {e}. Is the backend running?")

st.markdown("---")
st.caption("Powered by Gemini 2.5 Flash & ChromaDB")
