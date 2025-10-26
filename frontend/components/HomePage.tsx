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
    <div className="relative min-h-screen flex flex-col items-center justify-start pt-20 p-6 overflow-hidden">
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
      <div className="relative z-10 text-center space-y-12">
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold text-black leading-relaxed">
            Have a problem?
            <br />
            Ask the Bears.
          </h1>
        </div>

        <div className="flex flex-col items-center space-y-8">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`relative w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 cursor-pointer ${
              isRecording
                ? "bg-red-500 hover:bg-red-600 scale-100"
                : "bg-white hover:bg-gray-100 hover:scale-105"
            }`}
            aria-label={isRecording ? "Stop recording" : "Start recording"}
          >
            {isRecording && (
              <div className="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-75"></div>
            )}
            <div className="relative">
              {isRecording ? (
                <div className="w-8 h-8 bg-white rounded-sm"></div>
              ) : (
                <svg
                  className="w-12 h-12 text-black"
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

          {isRecording && (
            <div className="flex flex-col items-center space-y-2 animate-in fade-in duration-300">
              <div className="text-2xl text-black font-mono tabular-nums">
                {formatTime(recordingTime)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
