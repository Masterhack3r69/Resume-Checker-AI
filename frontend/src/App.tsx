import { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { PlayCircle, Award, Loader2, UploadCloud, FileText, CheckCircle2, AlertTriangle, XCircle, Sparkles } from 'lucide-react';
import clsx from 'clsx';

// Components (We will inline simple versions if complex ones need refactoring, but keeping imports for now)
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
        const response = await axios.post('http://localhost:8000/analyze', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        setResult(response.data);
    } catch (err: any) {
        console.error(err);
        setError(err.response?.data?.detail || "An error occurred during analysis. Ensure backend is running.");
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-slate-100 selection:bg-primary/30 relative overflow-hidden font-sans">
      
      {/* Dynamic Background Blobs */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-0 -right-4 w-72 h-72 bg-primary rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative max-w-7xl mx-auto px-6 py-12 space-y-16">
        
        {/* Header */}
        <header className="text-center space-y-6">
            <motion.div 
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="inline-flex items-center justify-center p-4 rounded-3xl bg-gradient-to-br from-surfaceHighlight/50 to-surface/50 backdrop-blur-xl border border-white/10 shadow-2xl"
            >
                <div className="p-3 rounded-2xl bg-gradient-to-br from-primary to-purple-600 shadow-lg shadow-primary/20">
                    <Award className="w-8 h-8 text-white" />
                </div>
            </motion.div>
            
            <div className="space-y-2">
                <motion.h1 
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="text-5xl md:text-6xl font-black tracking-tight"
                >
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-100 to-slate-400">
                        Resume Analyzer
                    </span>
                    <span className="text-primary">.AI</span>
                </motion.h1>
                <motion.p 
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.1 }}
                    className="text-xl text-slate-400 max-w-2xl mx-auto font-light leading-relaxed"
                >
                    Premium AI-powered recruiter insights. <span className="text-slate-200 font-medium">Be the top 1% candidate.</span>
                </motion.p>
            </div>
        </header>

        {/* Input Section */}
        <motion.div 
            className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
        >
            {/* Upload Card */}
            <div className="group relative">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-purple-600 rounded-2xl opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
                <div className="relative h-full bg-surface/80 backdrop-blur-xl border border-white/10 rounded-2xl p-8 space-y-6 shadow-2xl">
                    <div className="flex items-center gap-4 mb-2">
                        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-surfaceHighlight border border-white/5 text-primary font-bold shadow-inner">1</div>
                        <h2 className="text-2xl font-bold text-white">Upload Resume</h2>
                    </div>
                    
                    <UploadZone onFileSelect={setFile} selectedFile={file} />
                </div>
            </div>

            {/* Job Description Card */}
            <div className="group relative">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
                <div className="relative h-full bg-surface/80 backdrop-blur-xl border border-white/10 rounded-2xl p-8 space-y-6 shadow-2xl">
                    <div className="flex items-center gap-4 mb-2">
                         <div className="flex items-center justify-center w-10 h-10 rounded-full bg-surfaceHighlight border border-white/5 text-primary font-bold shadow-inner">2</div>
                        <h2 className="text-2xl font-bold text-white">Job Description</h2>
                    </div>
                    
                    <textarea
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        placeholder="Paste the job description here (JD)..."
                        className="w-full h-64 bg-background/50 border border-white/10 rounded-xl p-6 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all resize-none text-slate-200 placeholder:text-slate-600 font-mono text-sm leading-relaxed"
                    />
                </div>
            </div>
        </motion.div>

        {/* Action Button */}
        <motion.div 
            className="flex justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
        >
            <button
                onClick={handleAnalyze}
                disabled={loading || !file || !jobDescription}
                className="group relative px-10 py-5 bg-gradient-to-r from-primary to-indigo-600 hover:from-primaryHover hover:to-indigo-700 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed rounded-2xl font-bold text-xl text-white transition-all duration-300 shadow-xl hover:shadow-primary/40 flex items-center gap-4 overflow-hidden transform hover:scale-105 active:scale-95"
            >
                {loading ? (
                    <>
                        <Loader2 className="w-6 h-6 animate-spin" />
                        <span className="animate-pulse">Analyzing...</span>
                    </>
                ) : (
                    <>
                        Start Analysis
                        <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform text-indigo-200" />
                    </>
                )}
            </button>
        </motion.div>

        {/* Error Message */}
        <AnimatePresence>
            {error && (
                <motion.div 
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="p-4 bg-red-500/10 border border-red-500/20 backdrop-blur-sm rounded-xl text-red-300 text-center max-w-2xl mx-auto flex items-center justify-center gap-3"
                >
                    <AlertTriangle className="w-5 h-5" />
                    {error}
                </motion.div>
            )}
        </AnimatePresence>

        {/* Results Section */}
        <AnimatePresence>
            {result && (
                <motion.div 
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, type: "spring", bounce: 0.3 }}
                    className="space-y-16 pt-8 border-t border-white/5"
                >
                    {/* Score Circle */}
                    <div className="flex flex-col items-center justify-center space-y-6">
                        <div className="relative w-56 h-56 flex items-center justify-center group">
                            {/* Outer Glow */}
                            <div className={clsx(
                                "absolute inset-0 rounded-full blur-2xl opacity-20 transition-colors duration-1000",
                                result.match_score > 80 ? "bg-green-500" : result.match_score > 50 ? "bg-yellow-500" : "bg-red-500"
                            )}></div>
                            
                            <svg className="w-full h-full transform -rotate-90 drop-shadow-2xl">
                                <circle cx="112" cy="112" r="100" stroke="currentColor" strokeWidth="16" fill="transparent" className="text-surfaceHighlight" />
                                <circle 
                                    cx="112" 
                                    cy="112" 
                                    r="100" 
                                    stroke="currentColor" 
                                    strokeWidth="16" 
                                    fill="transparent" 
                                    strokeDasharray={2 * Math.PI * 100}
                                    strokeDashoffset={2 * Math.PI * 100 * (1 - result.match_score / 100)}
                                    // Linecap round for smoother look
                                    strokeLinecap="round"
                                    className={clsx(
                                        result.match_score > 80 ? "text-success" : 
                                        result.match_score > 50 ? "text-warning" : "text-danger",
                                        "transition-all duration-1000 ease-out"
                                    )} 
                                />
                            </svg>
                            <div className="absolute flex flex-col items-center">
                                <span className={clsx(
                                    "text-6xl font-black tracking-tighter",
                                    result.match_score > 80 ? "text-success" : result.match_score > 50 ? "text-warning" : "text-danger"
                                )}>{result.match_score}%</span>
                                <span className="text-sm text-slate-400 uppercase tracking-widest font-bold mt-2">Match Rate</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                        {/* Recruiter Feedback Component */}
                        <div className="bg-surface/50 backdrop-blur-md rounded-2xl border border-white/5 p-6 shadow-xl">
                            <RecruiterFeedback 
                                checklist={result.recruiter_feedback.tick_list}
                                redFlags={result.recruiter_feedback.red_flags}
                                critiques={result.recruiter_feedback.style_critique}
                            />
                        </div>

                        {/* Skill Match Component */}
                        <div className="bg-surface/50 backdrop-blur-md rounded-2xl border border-white/5 p-6 shadow-xl">
                            <SkillMatch 
                                strongMatches={result.analysis.strong_matches}
                                missingSkills={result.analysis.missing_skills}
                            />
                        </div>
                    </div>

                    {/* Interview Prep */}
                    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-surfaceHighlight to-surface border border-white/10 p-8 lg:p-10 shadow-2xl">
                        <div className="absolute top-0 right-0 p-12 bg-primary/10 rounded-full blur-3xl -mr-12 -mt-12"></div>
                        
                        <div className="relative z-10">
                            <h3 className="text-3xl font-bold mb-8 text-white flex items-center gap-3">
                                <span className="p-2 rounded-lg bg-primary/20 text-primary"><FileText className="w-6 h-6"/></span>
                                Personalized Interview Prep
                            </h3>
                            <div className="grid gap-4 md:grid-cols-2">
                                {result.interview_prep.map((q, idx) => (
                                    <motion.div 
                                        key={idx} 
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: 0.1 * idx }}
                                        className="p-5 bg-background/60 backdrop-blur-sm rounded-xl border border-white/5 hover:border-primary/50 transition-colors group"
                                    >
                                        <div className="flex gap-4">
                                            <span className="text-primary/50 font-mono text-xl group-hover:text-primary transition-colors">0{idx + 1}</span>
                                            <p className="text-lg text-slate-200 font-medium leading-relaxed">"{q}"</p>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </div>

                </motion.div>
            )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
