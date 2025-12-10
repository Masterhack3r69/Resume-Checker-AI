import React from 'react';
import { CheckCircle, XCircle, AlertTriangle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface RecruiterFeedbackProps {
    checklist: Record<string, boolean>;
    redFlags: string[];
    critiques: string[];
}

const RecruiterFeedback: React.FC<RecruiterFeedbackProps> = ({ checklist, redFlags, critiques }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* 7-Point Tick List */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <span className="text-primary">📋</span> The 7-Point Recruiter Tick List
        </h3>
        <p className="text-sm text-slate-400 mb-6">Recruiters scan these 7 key areas in seconds.</p>
        
        <div className="space-y-3">
            {Object.entries(checklist).map(([item, passed], idx) => (
                <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-slate-800/80">
                    <span className="text-slate-300 font-medium">{item}</span>
                    {passed ? (
                        <div className="flex items-center gap-2 text-green-400">
                            <CheckCircle className="w-5 h-5" />
                            <span className="text-sm font-bold">MATCH</span>
                        </div>
                    ) : (
                        <div className="flex items-center gap-2 text-red-400">
                            <XCircle className="w-5 h-5" />
                            <span className="text-sm font-bold">MISSING</span>
                        </div>
                    )}
                </div>
            ))}
        </div>
      </motion.div>

      {/* Red Flags & Critiques */}
      <div className="space-y-6">
         {/* Red Flags */}
         {redFlags.length > 0 && (
             <motion.div 
               initial={{ opacity: 0, y: 20 }}
               animate={{ opacity: 1, y: 0 }}
               className="bg-red-950/30 border border-red-900/50 rounded-xl p-6"
             >
                <h3 className="text-xl font-semibold text-red-400 mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-6 h-6" /> Immediate Red Flags
                </h3>
                <ul className="space-y-3">
                    {redFlags.map((flag, idx) => (
                        <li key={idx} className="flex items-start gap-3 text-red-200 bg-red-900/20 p-3 rounded-lg border border-red-900/30">
                            <XCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                            <span>{flag}</span>
                        </li>
                    ))}
                </ul>
             </motion.div>
         )}

         {/* Content Critiques */}
         {critiques.length > 0 && (
             <motion.div 
               initial={{ opacity: 0, y: 20 }}
               animate={{ opacity: 1, y: 0 }}
               className="bg-amber-950/30 border border-amber-900/50 rounded-xl p-6"
             >
                <h3 className="text-xl font-semibold text-amber-400 mb-4 flex items-center gap-2">
                    <AlertCircle className="w-6 h-6" /> Stylistic & Content Advice
                </h3>
                <ul className="space-y-3">
                    {critiques.map((critique, idx) => (
                        <li key={idx} className="flex items-start gap-3 text-amber-200 bg-amber-900/20 p-3 rounded-lg border border-amber-900/30">
                             <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2 flex-shrink-0" />
                            <span>{critique}</span>
                        </li>
                    ))}
                </ul>
             </motion.div>
         )}
      </div>
    </div>
  );
};

export default RecruiterFeedback;
