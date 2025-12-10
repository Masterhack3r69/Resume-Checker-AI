import React from 'react';
import { motion } from 'framer-motion';
import { Check, Search } from 'lucide-react';

interface SkillMatchProps {
    strongMatches: Array<{ skill: string; evidence: string }>;
    missingSkills: Array<{ skill: string; recommendation: string }>;
}

const SkillMatch: React.FC<SkillMatchProps> = ({ strongMatches, missingSkills }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
      {/* Strong Matches */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h3 className="text-xl font-semibold mb-4 text-green-400 flex items-center gap-2">
            <Check className="w-6 h-6" /> Strong Skill Matches
        </h3>
        
        <div className="space-y-4">
            {strongMatches.map((item, idx) => (
                <div key={idx} className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
                    <h4 className="font-bold text-white mb-1">{item.skill}</h4>
                    <p className="text-sm text-slate-400 italic">"{item.evidence}"</p>
                </div>
            ))}
            {strongMatches.length === 0 && (
                <p className="text-slate-500 italic">No strong matches found yet.</p>
            )}
        </div>
      </motion.div>

      {/* Missing Skills */}
      <motion.div 
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h3 className="text-xl font-semibold mb-4 text-blue-400 flex items-center gap-2">
            <Search className="w-6 h-6" /> Missing / Weak Skills
        </h3>
        
        <div className="space-y-4">
            {missingSkills.map((item, idx) => (
                <div key={idx} className="bg-blue-950/20 p-4 rounded-lg border border-blue-900/30">
                    <h4 className="font-bold text-blue-200 mb-1">{item.skill}</h4>
                    <p className="text-sm text-blue-300/80">{item.recommendation}</p>
                </div>
            ))}
             {missingSkills.length === 0 && (
                <p className="text-slate-500 italic">No missing skills detected!</p>
            )}
        </div>
      </motion.div>
    </div>
  );
};

export default SkillMatch;
