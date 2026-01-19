import React from "react";

export default function AnalysisCard({ label, checked, onChange }) {
  return (
    <div
      onClick={() => onChange(!checked)}
      className={`
        relative overflow-hidden cursor-pointer rounded-lg border p-4 transition-all duration-300 group
        ${checked
          ? "bg-blue-600/10 border-blue-500/50"
          : "bg-white/5 border-white/5 hover:border-white/20 hover:bg-white/10"
        }
      `}
    >
      <div className="flex items-center justify-between">
        <span className={`font-medium transition-colors ${checked ? "text-blue-200" : "text-gray-300 group-hover:text-white"}`}>
          {label}
        </span>

        <div className={`
          w-6 h-6 rounded-md border flex items-center justify-center transition-all duration-300
          ${checked
            ? "bg-blue-500 border-blue-500 text-white scale-110 shadow-lg shadow-blue-500/40"
            : "border-gray-500 bg-transparent group-hover:border-gray-300"
          }
        `}>
          {checked && (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          )}
        </div>
      </div>

      {/* Subtle background glow effect when checked */}
      {checked && (
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-transparent opacity-50 pointer-events-none" />
      )}
    </div>
  );
}
