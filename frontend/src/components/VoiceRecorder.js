import React, { useState, useEffect, useRef } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { useAuth } from '../contexts/AuthContext';
import {
  MicrophoneIcon,
  StopIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const VoiceRecorder = ({ 
  onTranscriptUpdate, 
  onVoiceProcessingComplete,
  questionId = null,
  sessionId = null,
  autoSubmit = false,
  className = ""
}) => {
  const { user } = useAuth();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [error, setError] = useState('');
  const [permissionGranted, setPermissionGranted] = useState(false);
  const [userAge, setUserAge] = useState(null);
  const [parentalConsent, setParentalConsent] = useState(false);
  const [showConsentForm, setShowConsentForm] = useState(false);
  const [consentVerified, setConsentVerified] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  useEffect(() => {
    if (transcript && onTranscriptUpdate) {
      onTranscriptUpdate(transcript);
    }
  }, [transcript, onTranscriptUpdate]);

  const checkMicrophonePermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setPermissionGranted(true);
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (err) {
      setError('Microphone permission denied. Please allow microphone access.');
      return false;
    }
  };

  const startRecording = async () => {
    try {
      setError('');
      
      // Check for browser support
      if (!browserSupportsSpeechRecognition) {
        setError('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
        return;
      }

      // Check age and consent requirements
      if (userAge !== null && userAge < 18 && !consentVerified) {
        setShowConsentForm(true);
        return;
      }

      // Check microphone permission
      if (!permissionGranted) {
        const granted = await checkMicrophonePermission();
        if (!granted) return;
      }

      // Start audio recording
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        }
      });
      
      streamRef.current = stream;
      
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
        setAudioBlob(audioBlob);
        
        if (autoSubmit) {
          await processVoiceData(audioBlob);
        }
      };
      
      mediaRecorder.start(1000); // Collect data every second
      setIsRecording(true);
      
      // Start speech recognition for real-time feedback
      SpeechRecognition.startListening({
        continuous: true,
        interimResults: true,
        language: 'en-US'
      });
      
    } catch (err) {
      setError(`Recording error: ${err.message}`);
      console.error('Recording error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    
    SpeechRecognition.stopListening();
    setIsRecording(false);
  };

  const processVoiceData = async (audioBlob) => {
    try {
      setIsProcessing(true);
      setError('');
      
      // Convert audio blob to base64
      const reader = new FileReader();
      reader.onload = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        try {
          const endpoint = questionId && sessionId 
            ? `${process.env.REACT_APP_BACKEND_URL}/api/ai/voice-think-aloud`
            : `${process.env.REACT_APP_BACKEND_URL}/api/ai/voice-to-text`;
          
          const requestData = questionId && sessionId ? {
            audio_data: base64Audio,
            question_id: questionId,
            session_id: sessionId,
            user_age: userAge,
            parental_consent: parentalConsent
          } : {
            audio_data: base64Audio,
            user_age: userAge,
            parental_consent: parentalConsent,
            session_context: {
              question_id: questionId,
              session_id: sessionId
            }
          };
          
          const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(requestData)
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const result = await response.json();
          
          if (onVoiceProcessingComplete) {
            onVoiceProcessingComplete(result);
          }
          
        } catch (err) {
          setError(`Processing error: ${err.message}`);
          console.error('Voice processing error:', err);
        } finally {
          setIsProcessing(false);
        }
      };
      
      reader.readAsDataURL(audioBlob);
      
    } catch (err) {
      setError(`Processing error: ${err.message}`);
      setIsProcessing(false);
    }
  };

  const handleManualSubmit = () => {
    if (audioBlob) {
      processVoiceData(audioBlob);
    }
  };

  const handleConsentSubmit = async () => {
    if (userAge < 18 && !parentalConsent) {
      setError('Parental consent is required for users under 18');
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai/consent-verification`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          user_age: userAge,
          parental_consent: parentalConsent
        })
      });
      
      const result = await response.json();
      
      if (result.can_process_voice) {
        setConsentVerified(true);
        setShowConsentForm(false);
        setError('');
        // Automatically start recording after consent
        startRecording();
      } else {
        setError('Unable to process voice data without proper consent');
      }
      
    } catch (err) {
      setError(`Consent verification error: ${err.message}`);
    }
  };

  const clearRecording = () => {
    setAudioBlob(null);
    resetTranscript();
    setError('');
  };

  // Age verification form
  if (showConsentForm) {
    return (
      <div className={`voice-recorder-container ${className}`}>
        <div className="pathwayiq-card">
          <h3 className="text-lg font-semibold text-white mb-4">Age Verification Required</h3>
          
          <div className="space-y-4">
            <div>
              <label className="form-label">Your Age</label>
              <input
                type="number"
                value={userAge || ''}
                onChange={(e) => setUserAge(parseInt(e.target.value))}
                className="form-input"
                placeholder="Enter your age"
                min="5"
                max="120"
              />
            </div>
            
            {userAge && userAge < 18 && (
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-3">
                  <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />
                  <span className="text-yellow-300 font-medium">Parental Consent Required</span>
                </div>
                <p className="text-yellow-200 text-sm mb-3">
                  Users under 18 need parental consent to use voice recording features.
                </p>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={parentalConsent}
                    onChange={(e) => setParentalConsent(e.target.checked)}
                    className="form-checkbox"
                  />
                  <span className="text-white text-sm">
                    I have parental consent to use voice recording
                  </span>
                </label>
              </div>
            )}
            
            <div className="flex space-x-3">
              <button
                onClick={handleConsentSubmit}
                disabled={!userAge || (userAge < 18 && !parentalConsent)}
                className="btn-primary flex-1"
              >
                <CheckCircleIcon className="w-4 h-4 mr-2" />
                Verify & Continue
              </button>
              <button
                onClick={() => setShowConsentForm(false)}
                className="btn-secondary"
              >
                <XMarkIcon className="w-4 h-4 mr-2" />
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`voice-recorder-container ${className}`}>
      <div className="pathwayiq-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Voice Recording</h3>
          {!userAge && (
            <button
              onClick={() => setShowConsentForm(true)}
              className="btn-secondary text-sm"
            >
              Set Age
            </button>
          )}
        </div>
        
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4">
            <div className="flex items-center space-x-2">
              <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
              <span className="text-red-300 text-sm">{error}</span>
            </div>
          </div>
        )}
        
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isProcessing}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-green-500 hover:bg-green-600 text-white'
              }`}
            >
              {isRecording ? (
                <>
                  <StopIcon className="w-5 h-5" />
                  <span>Stop Recording</span>
                </>
              ) : (
                <>
                  <MicrophoneIcon className="w-5 h-5" />
                  <span>Start Recording</span>
                </>
              )}
            </button>
            
            {listening && (
              <div className="flex items-center space-x-2 text-green-400">
                <SpeakerWaveIcon className="w-5 h-5 animate-pulse" />
                <span className="text-sm">Listening...</span>
              </div>
            )}
            
            {!listening && transcript && (
              <div className="flex items-center space-x-2 text-gray-400">
                <SpeakerXMarkIcon className="w-5 h-5" />
                <span className="text-sm">Not listening</span>
              </div>
            )}
          </div>
          
          {transcript && (
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Live Transcript:</span>
                <button
                  onClick={clearRecording}
                  className="text-red-400 hover:text-red-300 text-sm"
                >
                  Clear
                </button>
              </div>
              <p className="text-white text-sm leading-relaxed">{transcript}</p>
            </div>
          )}
          
          {audioBlob && !autoSubmit && (
            <div className="flex space-x-3">
              <button
                onClick={handleManualSubmit}
                disabled={isProcessing}
                className="btn-primary flex-1"
              >
                {isProcessing ? (
                  <div className="loading-spinner w-4 h-4 mr-2"></div>
                ) : (
                  <CheckCircleIcon className="w-4 h-4 mr-2" />
                )}
                {isProcessing ? 'Processing...' : 'Submit Recording'}
              </button>
            </div>
          )}
          
          {isProcessing && (
            <div className="flex items-center space-x-2 text-blue-400">
              <div className="loading-spinner w-4 h-4"></div>
              <span className="text-sm">Processing voice data...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VoiceRecorder;