import React, { useRef, useState } from "react";

export default function UploadArea({ file, setFile }) {
  const inputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div
      onClick={() => inputRef.current.click()}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        relative group cursor-pointer border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ease-out
        ${isDragOver
          ? "border-blue-400 bg-blue-500/10 scale-[1.02]"
          : "border-white/10 hover:border-blue-400/50 hover:bg-white/5"
        }
      `}
    >
      <input
        type="file"
        ref={inputRef}
        onChange={(e) => setFile(e.target.files[0])}
        className="hidden"
        accept="video/*"
      />

      {file ? (
        <div className="animate-fade-in py-2">
          <div className="w-16 h-16 mx-auto mb-3 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-emerald-300 font-semibold text-lg">Video Selected</p>
          <p className="text-gray-400 text-sm mt-1 truncate max-w-[250px] mx-auto">{file.name}</p>
          <p className="text-xs text-blue-400 mt-3 font-medium hover:text-blue-300 transition-colors">Click or Drag to replace</p>
        </div>
      ) : (
        <div className="py-2 space-y-3">
          <div className={`
                w-16 h-16 mx-auto rounded-full flex items-center justify-center transition-all duration-300
                ${isDragOver ? "bg-blue-500 text-white shadow-lg shadow-blue-500/50" : "bg-white/10 text-gray-400 group-hover:text-blue-400 group-hover:bg-blue-500/20"}
            `}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>

          <div>
            <p className="text-lg font-medium text-gray-200 group-hover:text-white transition-colors">
              Upload Match Footage
            </p>
            <p className="text-sm text-gray-500 group-hover:text-gray-400 mt-1">
              Drag & drop or click to browse
            </p>
          </div>
          <p className="text-xs text-gray-600 font-mono pt-2">MP4, MKV, MOV supported</p>
        </div>
      )}
    </div>
  );
}
