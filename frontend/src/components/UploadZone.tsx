import React, { useState } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

interface UploadZoneProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

const UploadZone: React.FC<UploadZoneProps> = ({ onFileSelect, selectedFile }) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf") {
        onFileSelect(file);
      } else {
        alert("Please upload a PDF file.");
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
        onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto mb-8">
      <AnimatePresence mode="wait">
        {!selectedFile ? (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={clsx(
                    "border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors duration-200",
                    isDragOver ? "border-primary bg-primary/10" : "border-slate-700 hover:border-slate-500 bg-slate-800/50"
                )}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-upload')?.click()}
            >
                <input 
                    type="file" 
                    id="file-upload" 
                    className="hidden" 
                    accept=".pdf" 
                    onChange={handleChange}
                />
                <div className="flex flex-col items-center justify-center gap-4">
                    <div className="p-4 bg-slate-800 rounded-full">
                        <Upload className="w-8 h-8 text-primary" />
                    </div>
                    <div>
                        <h3 className="text-xl font-semibold text-white">Drop your resume here</h3>
                        <p className="text-slate-400 mt-2">or click to browse (PDF only)</p>
                    </div>
                </div>
            </motion.div>
        ) : (
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="relative bg-slate-800 border border-slate-700 rounded-xl p-6 flex items-center gap-4"
            >
                <div className="p-3 bg-primary/20 rounded-lg">
                    <FileText className="w-8 h-8 text-primary" />
                </div>
                <div className="flex-1">
                    <h3 className="font-medium text-white text-lg">{selectedFile.name}</h3>
                    <p className="text-sm text-slate-400">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button 
                    onClick={(e) => { e.stopPropagation(); onFileSelect(null); }}
                    className="p-2 hover:bg-slate-700 rounded-full transition-colors text-slate-400 hover:text-white"
                >
                    <X className="w-5 h-5" />
                </button>
            </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UploadZone;
