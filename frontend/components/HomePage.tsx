"use client";

import { useState, useRef, useCallback } from "react";
import Spline from '@splinetool/react-spline';
import Image from "next/image";

interface HomePageProps {
  onRecordingComplete: (blob: Blob) => void;
}

export default function HomePage({ onRecordingComplete }: HomePageProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        onRecordingComplete(blob);

        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("Could not access microphone. Please check your permissions.");
    }
  }, [onRecordingComplete]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }, [isRecording]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="relative min-h-screen flex flex-col overflow-hidden">
      {/* recording border indicator */}
      {isRecording && (
        <>
          <div className="fixed inset-0 pointer-events-none z-50 border-8 border-red-500 animate-pulse"></div>
          <div className="fixed inset-0 pointer-events-none z-50 border-4 border-red-400 opacity-50 animate-ping"></div>
        </>
      )}
      
      {/* background layers */}
      <div className="absolute inset-0 -z-10">
        <Image
          src="/home.png"
          alt="Background"
          fill
          className="object-cover"
          priority
        />
      </div>
      <div className="absolute inset-0 z-0">
        <Spline
          scene="https://prod.spline.design/0km-REa2nFnxr6je/scene.splinecode"
        />
      </div>

      {/* header section */}
      <div className="relative z-10 pt-8 flex flex-col items-center pointer-events-none">
        {/* title */}
        <h1 className="text-5xl md:text-6xl font-bold text-black/80 mb-4">
          Fuzzy Logic
        </h1>
        
        {/* subtitle with microphone button */}
        <div className="flex items-center justify-center">
          <h2 className="text-2xl md:text-3xl font-bold text-black/80">
            Have a problem? Ask the Bears.
          </h2>
          <div className="relative ml-4 group pointer-events-auto">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              className={`relative w-16 h-16 rounded-full flex items-center justify-center transition-all duration-500 ease-out cursor-pointer shadow-2xl ${
                isRecording
                  ? "bg-red-500 hover:bg-red-600 scale-110 shadow-red-500/50"
                  : "bg-white hover:bg-gray-100 hover:scale-110 shadow-black/20 animate-[pulse_3s_ease-in-out_infinite]"
              }`}
              style={{ pointerEvents: 'auto' }}
              aria-label={isRecording ? "Stop recording" : "Start recording"}
            >
              {isRecording && (
                <div className="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-75 pointer-events-none"></div>
              )}
              <div className="relative transition-transform duration-300 pointer-events-none">
                {isRecording ? (
                  <div className="w-4 h-4 bg-white rounded-sm"></div>
                ) : (
                  <svg
                    className="w-6 h-6 text-black"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                  </svg>
                )}
              </div>
            </button>
            
            {/* tooltip hint */}
            {!isRecording && (
              <div className="absolute -bottom-12 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap">
                <div className="bg-black/80 text-white text-sm py-2 px-3 rounded-lg shadow-lg">
                  Click to speak
                  <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-black/80 rotate-45"></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* recording timer */}
      {isRecording && (
        <div className="relative z-10 flex flex-col items-center space-y-2 mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pointer-events-none">
          <div className="text-3xl text-black font-mono tabular-nums font-bold">
            {formatTime(recordingTime)}
          </div>
          <p className="text-black/60 text-sm">Recording...</p>
        </div>
      )}
    </div>
  );
}
