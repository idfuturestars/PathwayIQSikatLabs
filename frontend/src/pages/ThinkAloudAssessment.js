import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import SpeechToTextRecorder from '../components/SpeechToTextRecorder';
import axios from 'axios';

const ThinkAloudAssessment = () => {
  const { user } = useAuth();
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [transcriptions, setTranscriptions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [assessmentId, setAssessmentId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [customAnswer, setCustomAnswer] = useState('');
  const [assessmentComplete, setAssessmentComplete] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Initialize assessment
  useEffect(() => {
    initializeAssessment();
  }, []);

  const initializeAssessment = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      
      // Start adaptive assessment
      const assessmentResponse = await axios.post(
        `${backendUrl}/api/adaptive-assessment/start`,
        {
          subject: 'mathematics',
          target_grade_level: 'grade_8',
          assessment_type: 'think_aloud',
          enable_think_aloud: true,
          enable_ai_help_tracking: true,
          max_questions: 5
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setSessionId(assessmentResponse.data.session_id);
      setAssessmentId(assessmentResponse.data.session_id); // Using session_id as assessment_id
      
      // Get first question
      await getNextQuestion(assessmentResponse.data.session_id);
      
    } catch (error) {
      console.error('Error initializing assessment:', error);
      setError('Failed to initialize assessment');
    } finally {
      setIsLoading(false);
    }
  };

  const getNextQuestion = async (sessionId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `${backendUrl}/api/adaptive-assessment/${sessionId}/next-question`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data.session_complete) {
        setAssessmentComplete(true);
        return;
      }

      setCurrentQuestion(response.data);
      setSelectedAnswer('');
      setCustomAnswer('');
      
    } catch (error) {
      console.error('Error getting next question:', error);
      setError('Failed to get next question');
    }
  };

  const handleTranscriptionComplete = (transcriptionData) => {
    setTranscriptions(prev => [...prev, {
      questionId: currentQuestion.id,
      text: transcriptionData.text,
      confidence: transcriptionData.confidence,
      analysis: transcriptionData.analysis,
      processingTime: transcriptionData.processingTime,
      timestamp: new Date().toISOString()
    }]);
  };

  const handleTranscriptionError = (error) => {
    setError(error);
  };

  const submitAnswer = async () => {
    if (!selectedAnswer && !customAnswer) {
      setError('Please select or enter an answer');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const answer = selectedAnswer || customAnswer;
      
      // Get think-aloud data for this question
      const questionTranscriptions = transcriptions.filter(t => t.questionId === currentQuestion.id);
      const thinkAloudData = questionTranscriptions.length > 0 ? {
        question_id: currentQuestion.id,
        reasoning: questionTranscriptions.map(t => t.text).join(' '),
        strategy: questionTranscriptions.map(t => t.analysis?.strategy).join(', '),
        confidence_level: Math.round(questionTranscriptions.reduce((acc, t) => acc + (t.analysis?.confidence || 3), 0) / questionTranscriptions.length),
        difficulty_perception: 3,
        connections_to_prior_knowledge: questionTranscriptions.map(t => t.analysis?.key_insights).flat().join(', ')
      } : null;

      const response = await axios.post(
        `${backendUrl}/api/adaptive-assessment/submit-answer`,
        {
          session_id: sessionId,
          question_id: currentQuestion.id,
          answer: answer,
          response_time_seconds: 120, // TODO: Track actual time
          think_aloud_data: thinkAloudData,
          ai_help_used: false,
          ai_help_details: null
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      // Show analysis
      setShowAnalysis(true);
      
      // Move to next question after delay
      setTimeout(() => {
        setShowAnalysis(false);
        setCurrentQuestionIndex(prev => prev + 1);
        getNextQuestion(sessionId);
      }, 5000);

    } catch (error) {
      console.error('Error submitting answer:', error);
      setError('Failed to submit answer');
    }
  };

  const getCurrentQuestionTranscriptions = () => {
    return transcriptions.filter(t => t.questionId === currentQuestion?.id);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p className="text-lg">Initializing Think-Aloud Assessment...</p>
          </div>
        </div>
      </div>
    );
  }

  if (assessmentComplete) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-6">Assessment Complete!</h1>
            <p className="text-lg mb-4">Thank you for participating in the think-aloud assessment.</p>
            <div className="bg-gray-800 p-6 rounded-lg">
              <h2 className="text-xl font-semibold mb-4">Your Performance Summary</h2>
              <p className="text-gray-300 mb-4">
                Questions Completed: {transcriptions.length}
              </p>
              <p className="text-gray-300">
                Total Transcriptions: {transcriptions.length}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Think-Aloud Assessment</h1>
          <p className="text-gray-400">
            Speak your thoughts as you work through each problem. Your responses will be transcribed and analyzed.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900 border border-red-600 rounded-lg">
            <p className="text-red-300">{error}</p>
            <button 
              onClick={() => setError(null)}
              className="mt-2 text-sm text-red-400 hover:text-red-300"
            >
              Dismiss
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Question Panel */}
          <div className="bg-gray-800 p-6 rounded-lg">
            {currentQuestion ? (
              <>
                <div className="mb-4">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold">
                      Question {currentQuestionIndex + 1}
                    </h2>
                    <div className="text-sm text-gray-400">
                      Difficulty: {currentQuestion.complexity}
                    </div>
                  </div>
                  
                  <div className="mb-4 p-4 bg-gray-700 rounded-lg">
                    <p className="text-lg leading-relaxed">
                      {currentQuestion.question_text}
                    </p>
                  </div>

                  {/* Answer Options */}
                  {currentQuestion.options && currentQuestion.options.length > 0 ? (
                    <div className="space-y-3">
                      <h3 className="font-semibold">Select your answer:</h3>
                      {currentQuestion.options.map((option, index) => (
                        <label key={index} className="flex items-center space-x-3 p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600">
                          <input
                            type="radio"
                            name="answer"
                            value={option}
                            checked={selectedAnswer === option}
                            onChange={(e) => setSelectedAnswer(e.target.value)}
                            className="text-blue-500"
                          />
                          <span>{option}</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <h3 className="font-semibold">Enter your answer:</h3>
                      <textarea
                        value={customAnswer}
                        onChange={(e) => setCustomAnswer(e.target.value)}
                        placeholder="Type your answer here..."
                        className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                        rows="4"
                      />
                    </div>
                  )}

                  {/* Think-Aloud Prompts */}
                  <div className="mt-6 p-4 bg-blue-900 border border-blue-600 rounded-lg">
                    <h3 className="font-semibold mb-2">Think-Aloud Prompts:</h3>
                    <ul className="text-sm text-blue-200 space-y-1">
                      {currentQuestion.think_aloud_prompts?.map((prompt, index) => (
                        <li key={index}>• {prompt}</li>
                      ))}
                    </ul>
                  </div>

                  <button
                    onClick={submitAnswer}
                    disabled={!selectedAnswer && !customAnswer}
                    className="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Submit Answer
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center">
                <p className="text-gray-400">Loading question...</p>
              </div>
            )}
          </div>

          {/* Speech-to-Text Panel */}
          <div className="space-y-6">
            <SpeechToTextRecorder
              assessmentId={assessmentId}
              sessionId={sessionId}
              questionId={currentQuestion?.id}
              onTranscriptionComplete={handleTranscriptionComplete}
              onError={handleTranscriptionError}
              language="en"
            />

            {/* Transcription History */}
            <div className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Your Think-Aloud Responses</h3>
              {getCurrentQuestionTranscriptions().length > 0 ? (
                <div className="space-y-4">
                  {getCurrentQuestionTranscriptions().map((transcription, index) => (
                    <div key={index} className="p-4 bg-gray-700 rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-sm text-gray-400">
                          Recording {index + 1}
                        </span>
                        <span className="text-sm text-gray-400">
                          Confidence: {Math.round(transcription.confidence * 100)}%
                        </span>
                      </div>
                      <p className="text-gray-300 mb-2">{transcription.text}</p>
                      {transcription.analysis && (
                        <div className="mt-2 p-2 bg-gray-600 rounded text-sm">
                          <strong>Analysis:</strong> {transcription.analysis.strategy}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400">No recordings yet. Start speaking to see your transcriptions here.</p>
              )}
            </div>
          </div>
        </div>

        {/* Analysis Modal */}
        {showAnalysis && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 p-6 rounded-lg max-w-md w-full mx-4">
              <h3 className="text-xl font-semibold mb-4">Answer Analysis</h3>
              <p className="text-gray-300 mb-4">
                Your answer has been submitted and analyzed. Moving to the next question...
              </p>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ThinkAloudAssessment;