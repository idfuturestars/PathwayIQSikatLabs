import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const VoiceRecorder = ({ onTranscription, onEmotionalAnalysis }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [transcription, setTranscription] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const { user } = useAuth();

  useEffect(() => {
    return () => {
      if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
        mediaRecorder.current.stop();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        await processAudio(audioBlob);
        
        // Stop all tracks to turn off the microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      
      // Simulate audio level monitoring
      const interval = setInterval(() => {
        setAudioLevel(Math.random() * 100);
      }, 100);

      setTimeout(() => clearInterval(interval), 10000); // Stop after 10 seconds max
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      setIsRecording(false);
      setAudioLevel(0);
    }
  };

  const processAudio = async (audioBlob) => {
    setIsProcessing(true);
    
    try {
      // Convert audio to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        // Send to backend for processing
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai/voice-to-text`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            audio_data: base64Audio,
            session_context: {
              user_id: user?.id,
              timestamp: new Date().toISOString()
            }
          })
        });

        if (response.ok) {
          const result = await response.json();
          setTranscription(result.transcribed_text);
          
          if (onTranscription) {
            onTranscription(result.transcribed_text);
          }
          
          if (onEmotionalAnalysis) {
            onEmotionalAnalysis({
              emotional_state: result.emotional_state,
              learning_style: result.learning_style,
              confidence_score: result.confidence_score
            });
          }
        } else {
          console.error('Voice processing failed');
          setTranscription('Voice processing failed. Please try again.');
        }
      };
      
      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error('Error processing audio:', error);
      setTranscription('Error processing audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="voice-recorder bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Voice Assistant</h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-300">Ready</span>
        </div>
      </div>

      {/* Recording Controls */}
      <div className="flex items-center justify-center space-x-4 mb-6">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200 ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600 scale-110' 
              : 'bg-blue-500 hover:bg-blue-600'
          } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isProcessing ? (
            <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : isRecording ? (
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <rect x="6" y="6" width="8" height="8" />
            </svg>
          ) : (
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
            </svg>
          )}
        </button>
        
        <div className="text-center">
          <div className="text-sm text-gray-300">
            {isRecording ? 'Recording...' : isProcessing ? 'Processing...' : 'Click to record'}
          </div>
          {isRecording && (
            <div className="mt-2 flex justify-center">
              <div className="flex space-x-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className={`w-1 bg-blue-500 rounded-full animate-pulse ${
                      audioLevel > i * 20 ? 'h-4' : 'h-2'
                    }`}
                    style={{ animationDelay: `${i * 0.1}s` }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Transcription Display */}
      {transcription && (
        <div className="bg-gray-700 rounded-lg p-4 mb-4">
          <h4 className="text-sm font-medium text-gray-300 mb-2">Transcription:</h4>
          <p className="text-white text-sm leading-relaxed">{transcription}</p>
        </div>
      )}

      {/* Instructions */}
      <div className="text-xs text-gray-400 text-center">
        <p>Click the microphone to start recording your thoughts</p>
        <p className="mt-1">The AI will analyze your voice for emotional context and learning style</p>
      </div>
    </div>
  );
};

export default VoiceRecorder;