import React, { useState, useRef } from "react";
import axios from "axios";

export default function CoachAssistant({ metrics }) {
    const [question, setQuestion] = useState("");
    const [feedback, setFeedback] = useState("");
    const [loading, setLoading] = useState(false);
    const [recording, setRecording] = useState(false);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const API_BASE = "http://localhost:8000";

    const handleAsk = async (query = question) => {
        if (!query || !metrics) return;
        setLoading(true);
        setFeedback("");
        try {
            const response = await axios.post(`${API_BASE}/ai-coach`, {
                question: query,
                metrics: metrics,
            });
            setFeedback(response.data.feedback);
        } catch (error) {
            console.error("AI Coach Error:", error);
            setFeedback("Failed to get response from AI Coach. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            audioChunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorderRef.current.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
                const formData = new FormData();
                formData.append("file", audioBlob, "voice.webm");

                setLoading(true);
                try {
                    const res = await axios.post(`${API_BASE}/transcribe`, formData);
                    const transcription = res.data.text;
                    setQuestion(transcription);
                    handleAsk(transcription);
                } catch (err) {
                    console.error("Transcription Error:", err);
                    setFeedback("Failed to transcribe audio.");
                } finally {
                    setLoading(false);
                }
            };

            mediaRecorderRef.current.start();
            setRecording(true);
        } catch (err) {
            console.error("Microphone Access Error:", err);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            setRecording(false);
        }
    };

    return (
        <div className="mt-8 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl animate-fade-in">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-3 text-indigo-300">
                <span className="flex h-3 w-3 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
                </span>
                AI Coaching Assistant
            </h2>

            <div className="space-y-4">
                <div className="relative">
                    <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask the AI coach (e.g., 'How can I improve my swing?')"
                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-4 pr-24 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all text-gray-200 placeholder:text-gray-600"
                        onKeyDown={(e) => e.key === "Enter" && handleAsk()}
                    />
                    <div className="absolute right-2 top-2 flex gap-2">
                        <button
                            onClick={recording ? stopRecording : startRecording}
                            className={`p-2.5 rounded-lg transition-all ${recording
                                    ? "bg-red-500/20 text-red-500 animate-pulse"
                                    : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                                }`}
                            title={recording ? "Stop Recording" : "Voice Input"}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 005.93 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                            </svg>
                        </button>
                        <button
                            onClick={() => handleAsk()}
                            disabled={loading || !question}
                            className="p-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>

                {loading && (
                    <div className="flex items-center gap-3 text-indigo-400 text-sm animate-pulse px-2">
                        <div className="flex gap-1">
                            <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce"></span>
                        </div>
                        AI Coach is thinking...
                    </div>
                )}

                {feedback && (
                    <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-5 animate-slide-up">
                        <div className="flex items-start gap-4">
                            <div className="bg-indigo-500/20 p-2 rounded-lg text-indigo-400 shrink-0">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zm-1 9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div className="space-y-2">
                                <p className="text-xs uppercase tracking-wider text-indigo-400/60 font-bold">Feedback</p>
                                <div className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                                    {feedback}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {!metrics && !loading && (
                    <p className="text-sm text-gray-500 text-center py-2 italic">
                        Run analysis first to get data-driven coaching feedback.
                    </p>
                )}
            </div>
        </div>
    );
}
