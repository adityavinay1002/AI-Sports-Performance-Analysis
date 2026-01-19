import React, { useState } from "react";
import UploadArea from "./components/UploadArea";
import AnalysisCard from "./components/AnalysisCard";
import Results from "./components/Results";
import axios from "axios";

export default function App() {
  const [file, setFile] = useState(null);
  const [selected, setSelected] = useState({
    tracking: true,
    heatmap: true,
    pose: false,
    speed: false,
  });
  const [loading, setLoading] = useState(false);
  const [outputs, setOutputs] = useState(null);
  const [error, setError] = useState(null);

  const handleRun = async () => {
    setError(null);

    // Validation
    if (!file) {
      setError("Please upload a video before running analysis");
      return;
    }

    // Speed analysis requires tracking
    if (selected.speed && !selected.tracking) {
      setError("Speed analysis requires player tracking. Please enable 'Player Detection & Tracking'.");
      return;
    }

    setLoading(true);
    setOutputs(null);

    try {
      const API_BASE = 'http://localhost:8000'

      // Primary flow: upload -> process
      try {
        const formData = new FormData();
        formData.append('file', file);
        const up = await axios.post(`${API_BASE}/upload`, formData)
        const filename = up.data.filename

        const analyses = []
        if (selected.tracking) analyses.push('tracking')
        if (selected.heatmap) analyses.push('heatmap')
        if (selected.pose) analyses.push('pose')
        if (selected.speed) analyses.push('speed')

        const proc = await axios.post(`${API_BASE}/process`, { filename, analyses })
        // Append API Base to URL only if it's not a dummy URL
        const outs = (proc.data.outputs || []).map(o => ({
          ...o,
          url: o.url === '#' ? '#' : `${API_BASE}${o.url}`
        }))
        setOutputs(outs)
        return
      } catch (firstErr) {
        // If primary flow returned 404 / Not Found, fall back to legacy /analyze endpoint
        const status = firstErr?.response?.status
        const text = firstErr?.response?.data || firstErr.message
        console.warn('Primary API flow failed, falling back to /analyze', status, text)
        // continue to fallback
      }

      // Fallback: legacy endpoint that accepts multipart video directly
      try {
        const formData2 = new FormData();
        // some backends expect field name 'video', some 'file' — try 'video' first
        formData2.append('video', file)
        const r = await axios.post('http://localhost:8000/analyze', formData2)
        // Legacy response may contain keys like tracked_video and heatmap (paths)
        const resp = r.data || {}
        const outs = []
        if (resp.tracked_video) outs.push({ name: 'tracked.mp4', url: `${API_BASE}${resp.tracked_video}` })
        if (resp.heatmap) outs.push({ name: 'heatmap.png', url: `${API_BASE}${resp.heatmap}` })
        setOutputs(outs)
        return
      } catch (fbErr) {
        console.error('Fallback /analyze failed', fbErr)
        const msg = fbErr?.response?.data?.detail || fbErr?.response?.data || fbErr.message || 'Analysis failed'
        setError(`Analysis failed: ${msg}`)
        return
      }
    } finally {
      setLoading(false)
    }
  }

  // Clear error when file is selected
  const onFileChange = (f) => {
    setFile(f);
    if (f) setError(null);
  }

  // Validation State for Speed Analysis
  const showSpeedWarning = selected.speed && !selected.tracking;

  return (
    <div className="min-h-screen bg-[#020617] text-gray-100 p-6 selection:bg-blue-500/30">
      {/* Background Gradients */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-900/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-900/20 rounded-full blur-[120px]" />
      </div>

      <div className="relative max-w-6xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-300 mb-3 tracking-tight">
            AI Sports Performance Analysis
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Upload your match footage to analyze player movements, heatmaps, and skeletal tracking with computer vision.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* LEFT PANEL: CONFIGURATION */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-xl">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-blue-200">
                <span className="w-1 h-6 bg-blue-500 rounded-full"></span>
                Input & Configuration
              </h2>

              <UploadArea file={file} setFile={onFileChange} />

              <div className="mt-8 space-y-4">
                <p className="text-sm uppercase tracking-wider text-gray-500 font-semibold mb-2">Select Analyses</p>
                <div className="grid grid-cols-1 gap-3">
                  <AnalysisCard
                    label="Player Detection & Tracking"
                    checked={selected.tracking}
                    onChange={(v) => setSelected({ ...selected, tracking: v })}
                  />

                  <AnalysisCard
                    label="Player Movement Heatmap"
                    checked={selected.heatmap}
                    onChange={(v) => setSelected({ ...selected, heatmap: v })}
                  />

                  <AnalysisCard
                    label="Pose / Skeletal Analysis"
                    checked={selected.pose}
                    onChange={(v) => setSelected({ ...selected, pose: v })}
                  />

                  <AnalysisCard
                    label="Player Speed Analysis"
                    checked={selected.speed}
                    onChange={(v) => setSelected({ ...selected, speed: v })}
                  />
                </div>
              </div>

              {/* Error Message Inline */}
              {error && (
                <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg animate-fade-in flex items-start gap-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-500 shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <p className="text-red-200 text-sm font-medium">{error}</p>
                </div>
              )}

              {/* Speed Analysis Warning */}
              {showSpeedWarning && !error && (
                <div className="mt-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg animate-fade-in flex items-start gap-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <p className="text-amber-200 text-sm font-medium">Speed analysis requires player tracking. Please enable "Player Detection & Tracking".</p>
                </div>
              )}

              <button
                onClick={handleRun}
                disabled={loading}
                className={`
                  relative w-full mt-6 py-4 rounded-xl font-bold text-lg tracking-wide shadow-lg transition-all duration-300
                  ${loading
                    ? "bg-slate-700 cursor-not-allowed opacity-80"
                    : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 hover:shadow-blue-500/25 active:scale-[0.98]"
                  }
                `}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-3">
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing Video...
                  </span>
                ) : (
                  "Run Analysis"
                )}
              </button>
            </div>
          </div>

          {/* RIGHT PANEL: RESULTS */}
          <div className="lg:col-span-7">
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-xl min-h-[500px] flex flex-col">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-emerald-200">
                <span className="w-1 h-6 bg-emerald-500 rounded-full"></span>
                Analysis Results
              </h2>

              <div className="flex-1">
                {!outputs && !loading && (
                  <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-3 opacity-60 min-h-[300px]">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-lg font-medium">Ready to analyze</p>
                    <p className="text-sm max-w-xs text-center">Results will appear here after you upload a video and click run.</p>
                  </div>
                )}

                {loading && (
                  <div className="h-full flex flex-col items-center justify-center space-y-4 min-h-[300px] animate-pulse">
                    <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
                    <p className="text-blue-300 font-medium">Analyzing footage...</p>
                  </div>
                )}

                {outputs && (
                  <Results outputs={outputs} />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

