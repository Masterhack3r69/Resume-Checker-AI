
import os
import json
import asyncio
import time
from typing import List, Dict, Any
from google import genai
from google.genai import types
from google.api_core import exceptions

# Initialize Gemini Client
try:
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Warning: GOOGLE_API_KEY might be missing. {e}")
    client = None

class ResumeAnalyzer:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    async def _call_gemini_with_retry(self, func, *args, **kwargs):
        """
        Helper to call Gemini API with exponential backoff.
        """
        max_retries = 3
        delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            except (exceptions.ResourceExhausted, exceptions.ServiceUnavailable) as e:
                if attempt == max_retries:
                    raise e
                print(f"API Error ({type(e).__name__}). Retrying in {delay} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(delay)
                delay *= 2 # Exponential backoff
            except Exception as e:
                # For other errors, re-raise immediately
                raise e

    async def extract_skills(self, job_description: str) -> Dict[str, List[str]]:
        """
        Uses Gemini to extract Hard and Soft skills from the JD.
        Returns a JSON dictionary.
        """
        if not client:
             raise ValueError("Gemini Client not initialized.")

        prompt = f"""
        Analyze the following Job Description and extract the key skills required.
        Return ONLY a JSON object with two keys: "hard_skills" (list of strings) and "soft_skills" (list of strings).
        Do not include any markdown formatting or explanations.

        Job Description:
        {job_description}
        """

        try:
            response = await self._call_gemini_with_retry(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error extracting skills: {e}")
            return {"hard_skills": [], "soft_skills": []}

    async def verify_skills(self, skills: List[str], collection) -> List[Dict[str, Any]]:
        """
        For each skill, query the vector store for evidence.
        """
        results = []
        for skill in skills:
            # Create a simple verification report for each skill
            # We query for the top 1 match to see if there is close evidence
            
            try:
                # We also wrap embedding calls in retry as they also have limits (though different quota)
                matches = await self._call_gemini_with_retry(
                    self.vector_store.query_similar,
                    collection, 
                    skill, 
                    n_results=1
                )
            except Exception as e:
                print(f"Error checking skill {skill}: {e}")
                matches = []

            match_found = False
            evidence_text = ""
            
            if matches:
                evidence_text = matches[0]
                match_found = True # We assume semantic search found something relevant
            
            results.append({
                "skill": skill,
                "found": match_found,
                "evidence": evidence_text
            })
        return results

    async def analyze_recruiter_heuristics(self, resume_text: str, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the resume based on the "4 Persona" interview feedback (heuristics).
        
        Feedback Summary:
        1. Professional Email (no hotmail), No objective/summary, 1 page (<20y exp), Simple address, Filename format, PDF.
        2. 7 Point Tick List: Job Title, Industry, Product, Technical, Qualifications, Value Add, Exp Years.
        3. Single column, Black & White.
        4. Plain/Direct writing, quantifiable achievements, no fancy fonts.
        """
        if not client:
             raise ValueError("Gemini Client not initialized.")
             
        prompt = f"""
        You are a panel of strict, expert recruiters reviewing a resume. 
        You need to evaluate this resume based on specific heuristics and 'pet peeves' collected from top recruiters.
        
        Resume Text (First 3000 chars approx): 
        {resume_text[:3000]}...
        
        Metadata:
        Filename: {file_metadata.get('filename', 'Unknown')}
        Page Count: {file_metadata.get('page_count', 1)}
        
        EVALUATION CRITERIA:
        
        1. **Basics & Formatting**:
           - **Email**: Must be professional (gmail/outlook/domain). NO HOTMAIL.
           - **Length**: Should be 1 page unless experience > 20 years.
           - **Address**: "City, State" only. No full addresses.
           - **Filename**: Should be "FirstName LastName Resume". No "Version 1", "Final", or role names in title.
           - **Objective/Summary**: Should NOT exist.
           - **Layout**: Single column preference (hard to tell from text, but infer if reading order seems jumping).
        
        2. **Content Style**:
           - **Tone**: Plain, direct style. No fluff/thesaurus words.
           - **Quantifiable**: Achievements must have numbers/metrics.
           - **Methodology**: Explain HOW success was achieved, not just what.
        
        3. **The 7-Point Tick List** (Rate these as TRUE/FALSE based on evidence):
           - Job Title Match (Are titles clear/standard?)
           - Industry Match (Is industry experience obvious?)
           - Product Knowledge (Specific products/tools mentioned?)
           - Specialist Technical (Deep technical skills?)
           - Relevant Qualifications (Degrees/Certs visible?)
           - Ability to Add Value (Clear wins/revenue/growth?)
           - No. Years Experience (Easy to find total years?)

        TASK:
        Generate a JSON report with this EXACT structure:
        {{
            "seven_point_summary": {{
                "job_title_match": boolean,
                "industry_match": boolean,
                "product_knowledge": boolean,
                "specialist_technical": boolean,
                "relevant_qualifications": boolean,
                "ability_to_add_value": boolean,
                "years_experience_visible": boolean
            }},
            "heuristic_warnings": [
                // List of strings. Only include if a rule is VIOLATED.
                // Examples: "Filename 'resume_final_v2.pdf' is unprofessional. Rename to 'First Last Resume'.",
                // "Found a Hotmail address. Use Gmail or Outlook.",
                // "Resume is 3 pages long. condense to 1 page.",
                // "Found an 'Objective' section. Delete it and save space."
            ],
            "content_critique": [
                // List of strings. Critiques on writing style, lack of metrics, etc.
                // Example: "Bullet points under 'Software Engineer' lack quantifiable metrics."
            ]
        }}
        
        Return ONLY valid JSON.
        """

        try:
            response = await self._call_gemini_with_retry(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in recruiter heuristics: {e}")
            return {"seven_point_summary": {}, "heuristic_warnings": [], "content_critique": []}

    async def generate_report(self, job_description: str, hard_skills_analysis: List[Dict], soft_skills_analysis: List[Dict], recruiter_analysis: Dict) -> Dict[str, Any]:
        """
        Synthesizes the final report using Gemini.
        """
        if not client:
             raise ValueError("Gemini Client not initialized.")

        # Prepare context for the synthesis agent
        analysis_context = {
            "hard_skills": hard_skills_analysis,
            "soft_skills": soft_skills_analysis,
            "recruiter_heuristics": recruiter_analysis
        }
        
        prompt = f"""
        You are an expert technical recruiter. I have analyzed a candidate's resume against a job description using semantic search AND a strict recruiter heuristics check.
        
        Here is the raw analysis data:
        {json.dumps(analysis_context, indent=2)}

        Job Description Summary:
        {job_description[:500]}... (truncated)

        Task:
        Generate a structured JSON report evaluating the candidate.
        The JSON must have this exact structure:
        {{
            "match_score": <integer_0_to_100>,
            "analysis": {{
                "strong_matches": [<list of matching skills with brief evidence>],
                "missing_skills": [<list of missing skills with recommendations>]
            }},
            "recruiter_feedback": {{
                "tick_list": {{
                     // Copy directly from recruiter_heuristics.seven_point_summary, but ensure keys match exactly
                     "Job Title Match": boolean,
                     "Industry Match": boolean,
                     "Product Knowledge": boolean,
                     "Specialist Technical": boolean,
                     "Relevant Qualifications": boolean,
                     "Ability to Add Value": boolean,
                     "Years Experience": boolean
                }},
                "red_flags": [<list of string warnings from heuristic_warnings>],
                "style_critique": [<list of string critiques from content_critique>]
            }},
            "interview_prep": [<list of 3 tough interview questions based on the gaps or weak matches>]
        }}
        
        Be fair but strict. 
        If 'red_flags' has many items, lower the match_score significantly (e.g. -5 points per red flag).
        Return ONLY valid JSON.
        """

        try:
            response = await self._call_gemini_with_retry(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error generating report: {e}")
            raise e # Raise so main.py handles it

    async def analyze(self, job_description: str, collection, resume_text_full: str, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Extract Skills (Parallelizable)
        extracted_task = self.extract_skills(job_description)
        
        # 2. Recruiter Heuristics (Parallelizable)
        heuristics_task = self.analyze_recruiter_heuristics(resume_text_full, file_metadata)
        
        extracted, heuristics = await asyncio.gather(extracted_task, heuristics_task)
        
        # 3. Verify Skills
        hard_skills_verified = await self.verify_skills(extracted.get("hard_skills", []), collection)
        soft_skills_verified = await self.verify_skills(extracted.get("soft_skills", []), collection)
        
        # 4. Generate Report
        final_report = await self.generate_report(job_description, hard_skills_verified, soft_skills_verified, heuristics)
        
        return final_report

if __name__ == "__main__":
    pass
