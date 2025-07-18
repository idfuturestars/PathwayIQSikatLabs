import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const SpeechToTextRecorder = ({ 
  assessmentId, 
  sessionId, 
  questionId, 
  onTranscriptionComplete,
  onError,
  language = 'en'
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [transcriptionText, setTranscriptionText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [thinkAloudSession, setThinkAloudSession] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Start think-aloud session
  const startThinkAloudSession = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${backendUrl}/api/speech-to-text/start-session`,
        {
          assessment_id: assessmentId,
          question_id: questionId,
          language: language,
          enable_analysis: true
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      setThinkAloudSession(response.data);
      return response.data.session_id;
    } catch (error) {
      console.error('Error starting think-aloud session:', error);
      onError?.(error.response?.data?.detail || 'Failed to start session');
      return null;
    }
  };

  // Start recording
  const startRecording = async () => {
    try {
      // Start think-aloud session if not already started
      if (!thinkAloudSession) {
        const sessionId = await startThinkAloudSession();
        if (!sessionId) return;
      }

      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      });
      
      streamRef.current = stream;
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processAudioBlob(audioBlob);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setIsPaused(false);
      
      // Start recording timer
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      onError?.(error.message || 'Failed to start recording');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    
    setIsRecording(false);
    setIsPaused(false);
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  };

  // Pause recording
  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }
  };

  // Resume recording
  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      
      // Resume timer
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    }
  };

  // Process audio blob
  const processAudioBlob = async (audioBlob) => {
    try {
      setIsProcessing(true);
      
      // Convert blob to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        // Send to backend for transcription
        const token = localStorage.getItem('access_token');
        const response = await axios.post(
          `${backendUrl}/api/speech-to-text/transcribe`,
          {
            audio_data: base64Audio,
            assessment_id: assessmentId,
            session_id: sessionId || thinkAloudSession?.session_id,
            language: language,
            context_prompt: `This is a think-aloud response for an educational assessment. The student is explaining their thinking process.`
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        const transcriptionResult = response.data;
        setTranscriptionText(transcriptionResult.text);
        setIsProcessing(false);
        
        // Callback with results
        onTranscriptionComplete?.({
          text: transcriptionResult.text,
          confidence: transcriptionResult.confidence,
          analysis: transcriptionResult.think_aloud_analysis,
          processingTime: transcriptionResult.processing_time
        });
      };
      
      reader.readAsDataURL(audioBlob);
      
    } catch (error) {
      console.error('Error processing audio:', error);
      setIsProcessing(false);
      onError?.(error.response?.data?.detail || 'Failed to process audio');
    }
  };

  // Format time for display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="speech-to-text-recorder bg-gray-900 p-6 rounded-lg border border-gray-700">
      <h3 className="text-xl font-bold text-white mb-4">Think-Aloud Recording</h3>
      
      {/* Recording Status */}
      <div className="mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${
            isRecording ? (isPaused ? 'bg-yellow-500' : 'bg-red-500 animate-pulse') : 'bg-gray-500'
          }`}></div>
          <span className="text-gray-300">
            {isRecording ? (isPaused ? 'Paused' : 'Recording') : 'Ready'}
          </span>
          <span className="text-gray-400 ml-4">
            {formatTime(recordingTime)}
          </span>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="flex flex-wrap gap-3 mb-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={isProcessing}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 disabled:opacity-50"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
            </svg>
            <span>Start Recording</span>
          </button>
        ) : (
          <>
            {!isPaused ? (
              <button
                onClick={pauseRecording}
                className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>Pause</span>
              </button>
            ) : (
              <button
                onClick={resumeRecording}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
                <span>Resume</span>
              </button>
            )}
            
            <button
              onClick={stopRecording}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
              </svg>
              <span>Stop & Process</span>
            </button>
          </>
        )}
      </div>

      {/* Processing Status */}
      {isProcessing && (
        <div className="mb-4 p-3 bg-blue-900 border border-blue-600 rounded-lg">
          <div className="flex items-center space-x-2">
            <svg className="animate-spin h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="text-blue-300">Processing your recording...</span>
          </div>
        </div>
      )}

      {/* Transcription Result */}
      {transcriptionText && (
        <div className="mt-4 p-4 bg-gray-800 border border-gray-600 rounded-lg">
          <h4 className="text-lg font-semibold text-white mb-2">Transcription:</h4>
          <p className="text-gray-300 leading-relaxed">{transcriptionText}</p>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-4 p-3 bg-gray-800 border border-gray-600 rounded-lg">
        <h4 className="text-sm font-semibold text-gray-300 mb-2">Instructions:</h4>
        <ul className="text-sm text-gray-400 space-y-1">
          <li>• Click "Start Recording" to begin your think-aloud response</li>
          <li>• Speak your thoughts clearly as you work through the problem</li>
          <li>• Use "Pause" if you need a moment to think silently</li>
          <li>• Click "Stop & Process" when you're finished to get transcription</li>
        </ul>
      </div>
    </div>
  );
};

export default SpeechToTextRecorder;