import React, { useState } from 'react'

export default function Results({ outputs }) {
  const [modalContent, setModalContent] = useState(null)

  // Data for modal
  const [speedData, setSpeedData] = useState(null)

  if (!outputs || outputs.length === 0) return null; // Handled by App.jsx empty state

  const isVideo = (url) => url.match(/\.(mp4|webm|ogg)$/i)

  const handleView = (item) => {
    if (item.type === 'speed_analysis' && item.data) {
      setSpeedData(item.data)
      setModalContent('speed_dashboard')
    } else {
      setModalContent(item.url)
      setSpeedData(null)
    }
  }

  return (
    <div className="space-y-4 animate-fade-in-up">
      {outputs.map((o, idx) => (
        <div
          key={o.name}
          className="group relative p-4 bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/20 rounded-xl flex items-center justify-between transition-all duration-300 hover:shadow-lg hover:shadow-black/20 hover:-translate-y-0.5"
          style={{ animationDelay: `${idx * 100}ms` }}
        >
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center group-hover:bg-blue-500 group-hover:text-white transition-colors">
              {o.type === 'speed_analysis' ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              ) : isVideo(o.url) ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              )}
            </div>
            <span className="font-medium text-gray-200 group-hover:text-white text-lg tracking-wide">{o.name}</span>
          </div>

          <div className="flex items-center gap-3">

            {/* VIEW BUTTON */}
            <button
              onClick={() => handleView(o)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-semibold shadow-lg shadow-blue-500/20 transition-all hover:scale-105 active:scale-95 flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              View
            </button>

            {/* DOWNLOAD BUTTON */}
            {o.type !== 'speed_analysis' && (
              <a
                href={o.url}
                download
                className="px-4 py-2 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-white/5 hover:border-white/20 rounded-lg text-sm font-semibold transition-all hover:scale-105 active:scale-95 flex items-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4-4m0 0l-4 4m4-4v12" />
                </svg>
                Download
              </a>
            )}
          </div>
        </div>
      ))}

      {/* MODAL */}
      {modalContent && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-sm p-4 animate-fade-in"
          onClick={() => setModalContent(null)}
        >
          {/* Modal Container */}
          <div
            className="relative bg-[#020617] border border-white/10 rounded-2xl max-w-5xl w-full max-h-[90vh] flex flex-col p-1 shadow-2xl shadow-blue-500/10 animate-scale-up"
            onClick={e => e.stopPropagation()}
          >
            {/* Header / Close */}
            <div className="absolute top-4 right-4 z-20">
              <button
                className="p-2 bg-black/60 hover:bg-red-500/80 text-white rounded-full transition-all duration-300 hover:rotate-90"
                onClick={() => setModalContent(null)}
                title="Close"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-auto rounded-xl flex flex-col justify-center bg-black/50 items-center min-h-[400px] p-6">
              {modalContent === 'speed_dashboard' && speedData ? (
                <div className="w-full h-full max-w-4xl space-y-8">
                  <div className="text-center">
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">Player Speed Analysis</h2>
                    <p className="text-gray-400 mt-2">Performance metrics based on movement tracking</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Avg Speed Card */}
                    <div className="bg-white/5 border border-white/10 p-6 rounded-2xl text-center">
                      <p className="text-gray-400 text-sm uppercase tracking-wider font-semibold">Average Speed</p>
                      <div className="mt-2 text-5xl font-bold text-white tracking-tight">
                        {speedData.average_speed} <span className="text-xl text-gray-500 font-normal">m/s</span>
                      </div>
                    </div>

                    {/* Max Speed Card */}
                    <div className="bg-white/5 border border-white/10 p-6 rounded-2xl text-center">
                      <p className="text-gray-400 text-sm uppercase tracking-wider font-semibold">Maximum Speed</p>
                      <div className="mt-2 text-5xl font-bold text-white tracking-tight">
                        {speedData.max_speed} <span className="text-xl text-gray-500 font-normal">m/s</span>
                      </div>
                    </div>
                  </div>

                  {/* Intensity Distribution */}
                  <div className="bg-white/5 border border-white/10 p-8 rounded-2xl">
                    <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                      </svg>
                      Movement Intensity
                    </h3>

                    <div className="space-y-6">
                      {/* Walking */}
                      <div>
                        <div className="flex justify-between items-end mb-1">
                          <span className="text-blue-300 font-medium">Walking/Standing</span>
                          <span className="text-blue-200">{speedData.intensity?.Walking}%</span>
                        </div>
                        <div className="w-full bg-blue-900/30 rounded-full h-3 overflow-hidden">
                          <div className="bg-blue-500 h-full rounded-full transition-all duration-1000 ease-out" style={{ width: `${speedData.intensity?.Walking}%` }}></div>
                        </div>
                      </div>

                      {/* Jogging */}
                      <div>
                        <div className="flex justify-between items-end mb-1">
                          <span className="text-yellow-300 font-medium">Jogging</span>
                          <span className="text-yellow-200">{speedData.intensity?.Jogging}%</span>
                        </div>
                        <div className="w-full bg-yellow-900/30 rounded-full h-3 overflow-hidden">
                          <div className="bg-yellow-500 h-full rounded-full transition-all duration-1000 ease-out" style={{ width: `${speedData.intensity?.Jogging}%` }}></div>
                        </div>
                      </div>

                      {/* Sprinting */}
                      <div>
                        <div className="flex justify-between items-end mb-1">
                          <span className="text-red-400 font-medium">Sprinting</span>
                          <span className="text-red-300">{speedData.intensity?.Sprinting}%</span>
                        </div>
                        <div className="w-full bg-red-900/30 rounded-full h-3 overflow-hidden">
                          <div className="bg-red-500 h-full rounded-full transition-all duration-1000 ease-out" style={{ width: `${speedData.intensity?.Sprinting}%` }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : isVideo(modalContent) ? (
                <video
                  src={modalContent}
                  controls
                  autoPlay
                  className="max-h-[85vh] w-auto rounded-lg shadow-2xl"
                />
              ) : (
                <img
                  src={modalContent}
                  alt="Result"
                  className="max-h-[85vh] w-auto object-contain rounded-lg shadow-2xl"
                />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
