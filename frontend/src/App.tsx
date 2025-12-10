import { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { PlayCircle, Award, Loader2 } from 'lucide-react';
import clsx from 'clsx';

// Components
import UploadZone from './components/UploadZone';
import RecruiterFeedback from './components/RecruiterFeedback';
import SkillMatch from './components/SkillMatch';

// Types
interface AnalysisResult {
    match_score: number;
    analysis: {
        strong_matches: Array<{ skill: string; evidence: string }>;
        missing_skills: Array<{ skill: string; recommendation: string }>;
    };
    recruiter_feedback: {
        tick_list: Record<string, boolean>;
        red_flags: string[];
        style_critique: string[];
    };
    interview_prep: string[];
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!file || !jobDescription) {
        setError("Please provide both a resume and a job description.");
        return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);

    try {
        const response = await axios.post('/analyze', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        setResult(response.data);
    } catch (err: any) {
        console.error(err);
        setError(err.response?.data?.detail || "An error occurred during analysis.");
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-12">
        
        {/* Header */}
        <header className="text-center space-y-4">
            <div className="inline-block p-4 rounded-2xl bg-gradient-to-br from-primary to-purple-600 shadow-2xl shadow-primary/20">
                <Award className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                Resume Analyzer AI
            </h1>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
                Get premium recruiter insights, 7-point checks, and deep skill matching powered by Gemini 2.5.
            </p>
        </header>

        {/* Input Section */}
        <motion.div 
            className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
        >
            <div className="space-y-6">
                <h2 className="text-2xl font-bold flex items-center gap-2">
                    <span className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-800 text-sm border border-slate-700">1</span>
                    Upload Resume
                </h2>
                <UploadZone onFileSelect={setFile} selectedFile={file} />
            </div>

            <div className="space-y-6">
                <h2 className="text-2xl font-bold flex items-center gap-2">
                     <span className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-800 text-sm border border-slate-700">2</span>
                    Job Description
                </h2>
                <textarea
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste the job description here..."
                    className="w-full h-64 bg-slate-800/50 border border-slate-700 rounded-xl p-6 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all resize-none text-slate-300 placeholder:text-slate-600"
                />
            </div>
        </motion.div>

        {/* Action Button */}
        <div className="flex justify-center">
            <button
                onClick={handleAnalyze}
                disabled={loading || !file || !jobDescription}
                className="group relative px-8 py-4 bg-primary hover:bg-blue-600 disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed rounded-full font-bold text-lg transition-all duration-200 shadow-lg hover:shadow-primary/50 flex items-center gap-3 overflow-hidden"
            >
                {loading ? (
                    <>
                        <Loader2 className="w-6 h-6 animate-spin" />
                        Analyzing via AI Agents...
                    </>
                ) : (
                    <>
                        Start Analysis
                        <PlayCircle className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                    </>
                )}
            </button>
        </div>

        {/* Error Message */}
        {error && (
            <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-4 bg-red-950/50 border border-red-900 rounded-xl text-red-200 text-center"
            >
                {error}
            </motion.div>
        )}

        {/* Results Section */}
        {result && (
            <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-12 pt-12 border-t border-slate-800"
            >
                <div className="flex items-center justify-center">
                    <div className="relative w-48 h-48 flex items-center justify-center">
                        <svg className="w-full h-full transform -rotate-90">
                            <circle cx="96" cy="96" r="88" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-slate-800" />
                            <circle 
                                cx="96" 
                                cy="96" 
                                r="88" 
                                stroke="currentColor" 
                                strokeWidth="12" 
                                fill="transparent" 
                                strokeDasharray={2 * Math.PI * 88}
                                strokeDashoffset={2 * Math.PI * 88 * (1 - result.match_score / 100)}
                                className={clsx(
                                    result.match_score > 80 ? "text-green-500" : 
                                    result.match_score > 50 ? "text-yellow-500" : "text-red-500",
                                    "transition-all duration-1000 ease-out"
                                )} 
                            />
                        </svg>
                        <div className="absolute flex flex-col items-center">
                            <span className="text-4xl font-black text-white">{result.match_score}%</span>
                            <span className="text-sm text-slate-400 uppercase tracking-wider font-semibold">Match Score</span>
                        </div>
                    </div>
                </div>

                {/* Recruiter Feedback Component */}
                <RecruiterFeedback 
                    checklist={result.recruiter_feedback.tick_list}
                    redFlags={result.recruiter_feedback.red_flags}
                    critiques={result.recruiter_feedback.style_critique}
                />

                {/* Skill Match Component */}
                <SkillMatch 
                    strongMatches={result.analysis.strong_matches}
                    missingSkills={result.analysis.missing_skills}
                />

                {/* Interview Prep */}
                <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-8 border border-slate-700">
                    <h3 className="text-2xl font-bold mb-6 text-white">🎤 Interview Prep Questions</h3>
                    <div className="grid gap-4">
                        {result.interview_prep.map((q, idx) => (
                            <div key={idx} className="p-4 bg-black/20 rounded-xl border-l-4 border-primary">
                                <p className="text-lg text-slate-200">"{q}"</p>
                            </div>
                        ))}
                    </div>
                </div>

            </motion.div>
        )}
      </div>
    </div>
  );
}

export default App;
