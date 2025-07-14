import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import {
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
  ArrowRightIcon,
  PlayIcon,
  PauseIcon,
  MicrophoneIcon,
  ChatBubbleLeftRightIcon,
  ExclamationTriangleIcon,
  StarIcon,
  ChartBarIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';

const AdaptiveSkillScan = () => {
  const { user } = useAuth();
  
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);
  
  // Question state
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [questionNumber, setQuestionNumber] = useState(0);
  const [loading, setLoading] = useState(false);
  
  // Assessment config
  const [assessmentConfig, setAssessmentConfig] = useState({
    subject: '',
    target_grade_level: '',
    assessment_type: 'diagnostic',
    enable_think_aloud: true,
    enable_ai_help_tracking: true,
    max_questions: 20
  });
  
  // Timer and interaction
  const [timeLeft, setTimeLeft] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [startTime, setStartTime] = useState(null);
  
  // Think Aloud Mode
  const [thinkAloudMode, setThinkAloudMode] = useState(false);
  const [thinkAloudData, setThinkAloudData] = useState({
    reasoning: '',
    strategy: '',
    confidence_level: 3,
    difficulty_perception: 3,
    connections_to_prior_knowledge: ''
  });
  
  // AI Help Tracking
  const [aiHelpUsed, setAiHelpUsed] = useState(false);
  const [aiHelpDetails, setAiHelpDetails] = useState(null);
  const [showAiHelper, setShowAiHelper] = useState(false);
  
  // Results and Analytics
  const [sessionAnalytics, setSessionAnalytics] = useState(null);
  const [abilityProgress, setAbilityProgress] = useState([]);
  
  // Available options
  const subjects = [
    'Mathematics', 'Science', 'Programming', 'Computer Science', 
    'Research Methods', 'Physics', 'English Language Arts'
  ];
  
  const gradeLevels = [
    { value: 'kindergarten', label: 'Kindergarten (Age 5-6)' },
    { value: 'grade_1', label: 'Grade 1 (Age 6-7)' },
    { value: 'grade_2', label: 'Grade 2 (Age 7-8)' },
    { value: 'grade_3', label: 'Grade 3 (Age 8-9)' },
    { value: 'grade_4', label: 'Grade 4 (Age 9-10)' },
    { value: 'grade_5', label: 'Grade 5 (Age 10-11)' },
    { value: 'grade_6', label: 'Grade 6 (Age 11-12)' },
    { value: 'grade_7', label: 'Grade 7 (Age 12-13)' },
    { value: 'grade_8', label: 'Grade 8 (Age 13-14)' },
    { value: 'grade_9', label: 'Grade 9 (Age 14-15)' },
    { value: 'grade_10', label: 'Grade 10 (Age 15-16)' },
    { value: 'grade_11', label: 'Grade 11 (Age 16-17)' },
    { value: 'grade_12', label: 'Grade 12 (Age 17-18)' },
    { value: 'undergraduate', label: 'Undergraduate (Age 18-22)' },
    { value: 'graduate', label: 'Graduate (Age 22-26)' },
    { value: 'doctoral', label: 'Doctoral (Age 24+)' },
    { value: 'postdoctoral', label: 'Post-Doctoral (Age 28+)' },
    { value: 'professional', label: 'Professional Development' }
  ];
  
  const assessmentTypes = [
    { value: 'diagnostic', label: 'Diagnostic Assessment', description: 'Discover your current skill level' },
    { value: 'practice', label: 'Practice Mode', description: 'Practice with adaptive questions' },
    { value: 'challenge', label: 'Challenge Mode', description: 'Push your limits with harder questions' }
  ];

  // Timer effect
  useEffect(() => {
    let interval = null;
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1);
      }, 1000);
    } else if (timeLeft === 0 && currentQuestion) {
      handleTimeUp();
    }
    return () => clearInterval(interval);
  }, [isActive, timeLeft, currentQuestion]);

  const startAdaptiveAssessment = async () => {
    if (!assessmentConfig.subject) {
      alert('Please select a subject');
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/adaptive-assessment/start`,
        assessmentConfig
      );
      
      setSessionId(response.data.session_id);
      setSessionStarted(true);
      setAbilityProgress([{
        question_number: 0,
        ability_estimate: response.data.initial_ability_estimate
      }]);
      
      // Get first question
      await getNextQuestion(response.data.session_id);
      
    } catch (error) {
      console.error('Failed to start assessment:', error);
      alert('Failed to start assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getNextQuestion = async (session_id = sessionId) => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_BACKEND_URL}/api/adaptive-assessment/${session_id}/next-question`
      );
      
      if (response.data.session_complete) {
        setSessionComplete(true);
        setSessionAnalytics(response.data.final_analytics);
        setIsActive(false);
      } else {
        setCurrentQuestion(response.data);
        setQuestionNumber(response.data.question_number);
        setTimeLeft(response.data.estimated_time_seconds || 60);
        setStartTime(Date.now());
        setIsActive(true);
        setSelectedAnswer('');
        setThinkAloudData({
          reasoning: '',
          strategy: '',
          confidence_level: 3,
          difficulty_perception: 3,
          connections_to_prior_knowledge: ''
        });
        setAiHelpUsed(false);
        setAiHelpDetails(null);
      }
    } catch (error) {
      console.error('Failed to get next question:', error);
    }
  };

  const submitAnswer = async () => {
    if (!selectedAnswer.trim()) {
      alert('Please select or enter an answer');
      return;
    }
    
    setIsActive(false);
    const responseTime = (Date.now() - startTime) / 1000;
    
    try {
      const answerData = {
        session_id: sessionId,
        question_id: currentQuestion.id,
        answer: selectedAnswer,
        response_time_seconds: responseTime,
        think_aloud_data: thinkAloudMode ? thinkAloudData : null,
        ai_help_used: aiHelpUsed,
        ai_help_details: aiHelpDetails
      };
      
      const response = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/adaptive-assessment/submit-answer`,
        answerData
      );
      
      // Update ability progress
      setAbilityProgress(prev => [...prev, {
        question_number: questionNumber,
        ability_estimate: response.data.new_ability_estimate,
        is_correct: response.data.correct
      }]);
      
      // Show result briefly
      setTimeout(() => {
        getNextQuestion();
      }, 2000);
      
    } catch (error) {
      console.error('Failed to submit answer:', error);
      alert('Failed to submit answer. Please try again.');
    }
  };

  const handleTimeUp = () => {
    if (selectedAnswer.trim()) {
      submitAnswer();
    } else {
      // Auto-submit empty answer
      setSelectedAnswer('No answer provided');
      setTimeout(submitAnswer, 100);
    }
  };

  const useAiHelp = async (helpType) => {
    setAiHelpUsed(true);
    setAiHelpDetails({
      type: helpType,
      content: `Student requested ${helpType} help for question ${currentQuestion.id}`,
      timestamp: new Date().toISOString()
    });
    setShowAiHelper(true);
  };

  const getGradeLevelColor = (gradeLevel) => {
    if (gradeLevel.includes('kindergarten') || gradeLevel.includes('grade_1') || gradeLevel.includes('grade_2')) {
      return 'text-green-400';
    } else if (gradeLevel.includes('grade_') && parseInt(gradeLevel.split('_')[1]) <= 5) {
      return 'text-blue-400';
    } else if (gradeLevel.includes('grade_') && parseInt(gradeLevel.split('_')[1]) <= 8) {
      return 'text-yellow-400';
    } else if (gradeLevel.includes('grade_') && parseInt(gradeLevel.split('_')[1]) <= 12) {
      return 'text-orange-400';
    } else if (gradeLevel.includes('undergraduate')) {
      return 'text-purple-400';
    } else {
      return 'text-red-400';
    }
  };

  // Configuration Screen
  if (!sessionStarted && !sessionComplete) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">Adaptive SkillScan™</h1>
          <p className="text-gray-400 text-lg">
            Personalized assessment that adapts to your skill level (K-PhD+)
          </p>
        </div>

        <div className="starguide-card">
          <h2 className="text-2xl font-semibold text-white mb-6">Configure Your Assessment</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="form-group">
              <label className="form-label">Subject</label>
              <select
                value={assessmentConfig.subject}
                onChange={(e) => setAssessmentConfig({...assessmentConfig, subject: e.target.value})}
                className="form-input"
              >
                <option value="">Select a subject</option>
                {subjects.map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Target Grade Level (Optional)</label>
              <select
                value={assessmentConfig.target_grade_level}
                onChange={(e) => setAssessmentConfig({...assessmentConfig, target_grade_level: e.target.value})}
                className="form-input"
              >
                <option value="">Auto-detect based on performance</option>
                {gradeLevels.map(level => (
                  <option key={level.value} value={level.value}>{level.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mb-8">
            <label className="form-label">Assessment Type</label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {assessmentTypes.map(type => (
                <label
                  key={type.value}
                  className={`relative flex flex-col p-4 border rounded-lg cursor-pointer transition-all ${
                    assessmentConfig.assessment_type === type.value
                      ? 'border-green-500 bg-green-500/10'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                >
                  <input
                    type="radio"
                    name="assessment_type"
                    value={type.value}
                    checked={assessmentConfig.assessment_type === type.value}
                    onChange={(e) => setAssessmentConfig({...assessmentConfig, assessment_type: e.target.value})}
                    className="sr-only"
                  />
                  <span className="text-white font-medium mb-1">{type.label}</span>
                  <span className="text-gray-400 text-sm">{type.description}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="think_aloud"
                checked={assessmentConfig.enable_think_aloud}
                onChange={(e) => setAssessmentConfig({...assessmentConfig, enable_think_aloud: e.target.checked})}
                className="mr-3"
              />
              <label htmlFor="think_aloud" className="text-gray-300">
                Enable Think-Aloud Mode (explain your reasoning)
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="ai_tracking"
                checked={assessmentConfig.enable_ai_help_tracking}
                onChange={(e) => setAssessmentConfig({...assessmentConfig, enable_ai_help_tracking: e.target.checked})}
                className="mr-3"
              />
              <label htmlFor="ai_tracking" className="text-gray-300">
                Track AI assistance usage
              </label>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-white mb-4">How Adaptive SkillScan™ Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div>
                <ChartBarIcon className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                <p className="text-white font-medium">Adaptive Questions</p>
                <p className="text-gray-400 text-sm">Questions adjust to your skill level</p>
              </div>
              <div>
                <MicrophoneIcon className="w-8 h-8 text-green-500 mx-auto mb-2" />
                <p className="text-white font-medium">Think-Aloud Analysis</p>
                <p className="text-gray-400 text-sm">AI analyzes your reasoning process</p>
              </div>
              <div>
                <AcademicCapIcon className="w-8 h-8 text-purple-500 mx-auto mb-2" />
                <p className="text-white font-medium">Grade Level Detection</p>
                <p className="text-gray-400 text-sm">Accurate K-PhD+ level assessment</p>
              </div>
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={startAdaptiveAssessment}
              disabled={loading || !assessmentConfig.subject}
              className="btn-primary text-lg px-8 py-3"
            >
              {loading ? (
                <div className="loading-spinner w-5 h-5"></div>
              ) : (
                <>
                  <PlayIcon className="w-5 h-5 mr-2" />
                  Start Adaptive Assessment
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Assessment Complete Screen
  if (sessionComplete && sessionAnalytics) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">Assessment Complete!</h1>
          <p className="text-gray-400 text-lg">Your adaptive learning profile has been generated</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="starguide-card text-center">
            <StarIcon className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-white mb-2">
              {Math.round(sessionAnalytics.accuracy * 100)}%
            </h3>
            <p className="text-gray-400">Accuracy</p>
          </div>
          
          <div className="starguide-card text-center">
            <AcademicCapIcon className="w-12 h-12 text-blue-500 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-white mb-2">
              {sessionAnalytics.estimated_grade_level?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </h3>
            <p className="text-gray-400">Estimated Level</p>
          </div>
          
          <div className="starguide-card text-center">
            <ClockIcon className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-white mb-2">
              {Math.round(sessionAnalytics.session_duration / 60)}min
            </h3>
            <p className="text-gray-400">Duration</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="starguide-card">
            <h3 className="text-xl font-semibold text-white mb-4">Learning Progress</h3>
            <div className="h-64 flex items-end space-x-2 mb-4">
              {abilityProgress.map((point, index) => (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div
                    className={`w-full rounded-t transition-all duration-500 ${
                      point.is_correct === true ? 'bg-green-500' : 
                      point.is_correct === false ? 'bg-red-500' : 'bg-blue-500'
                    }`}
                    style={{
                      height: `${point.ability_estimate * 200}px`
                    }}
                  />
                  <div className="text-xs text-gray-400 mt-1">{index}</div>
                </div>
              ))}
            </div>
            <p className="text-gray-400 text-sm">Your ability estimate progressed throughout the assessment</p>
          </div>

          <div className="starguide-card">
            <h3 className="text-xl font-semibold text-white mb-4">Detailed Analytics</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-400">Questions Completed</span>
                <span className="text-white">{sessionAnalytics.total_questions}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Final Ability Estimate</span>
                <span className="text-white">{Math.round(sessionAnalytics.final_ability_estimate * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">AI Help Usage</span>
                <span className="text-white">{Math.round(sessionAnalytics.ai_help_percentage)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Think-Aloud Quality</span>
                <span className="text-white">{Math.round(sessionAnalytics.think_aloud_quality * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Average Response Time</span>
                <span className="text-white">{Math.round(sessionAnalytics.average_response_time)}s</span>
              </div>
            </div>
          </div>
        </div>

        <div className="text-center mt-8">
          <button
            onClick={() => {
              setSessionStarted(false);
              setSessionComplete(false);
              setSessionId(null);
              setCurrentQuestion(null);
              setSessionAnalytics(null);
              setAbilityProgress([]);
            }}
            className="btn-primary mr-4"
          >
            Take Another Assessment
          </button>
          <button
            onClick={() => navigate('/trajectory')}
            className="btn-secondary"
          >
            View Full Progress
          </button>
        </div>
      </div>
    );
  }

  // Active Assessment Screen
  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Adaptive SkillScan™</h1>
          <p className="text-gray-400">Question {questionNumber} • {assessmentConfig.subject}</p>
        </div>
        
        <div className="text-right">
          <div className={`text-2xl font-bold ${timeLeft <= 10 ? 'text-red-500' : 'text-white'}`}>
            {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
          </div>
          <p className="text-gray-400 text-sm">Time Remaining</p>
        </div>
      </div>

      {/* Progress and Ability */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="starguide-card text-center">
          <p className="text-gray-400 text-sm">Current Ability</p>
          <p className="text-xl font-bold text-white">
            {Math.round(currentQuestion?.current_ability_estimate * 100)}%
          </p>
        </div>
        <div className="starguide-card text-center">
          <p className="text-gray-400 text-sm">Question Level</p>
          <p className={`text-lg font-semibold ${getGradeLevelColor(currentQuestion?.grade_level || '')}`}>
            {currentQuestion?.grade_level?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </p>
        </div>
        <div className="starguide-card text-center">
          <p className="text-gray-400 text-sm">Difficulty</p>
          <p className="text-lg font-semibold text-yellow-500">
            {Math.round((currentQuestion?.estimated_difficulty || 0) * 100)}%
          </p>
        </div>
      </div>

      {/* Question */}
      {currentQuestion && (
        <div className="starguide-card mb-6">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <span className="badge badge-info">{currentQuestion.complexity}</span>
                <span className="badge badge-warning">
                  {currentQuestion.estimated_time_seconds}s estimated
                </span>
                {aiHelpUsed && (
                  <span className="badge bg-purple-500 text-white">AI Help Used</span>
                )}
              </div>
            </div>
            
            <h2 className="text-xl font-semibold text-white mb-4">
              {currentQuestion.question_text}
            </h2>
          </div>

          {/* Answer Options */}
          <div className="space-y-3 mb-6">
            {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options ? (
              currentQuestion.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedAnswer(option)}
                  className={`w-full text-left p-4 rounded-lg border transition-all ${
                    selectedAnswer === option
                      ? 'border-green-500 bg-green-500/10'
                      : 'border-gray-600 hover:border-gray-500 bg-gray-800'
                  }`}
                >
                  <span className="text-white">{option}</span>
                </button>
              ))
            ) : (
              <div>
                <textarea
                  value={selectedAnswer}
                  onChange={(e) => setSelectedAnswer(e.target.value)}
                  placeholder="Enter your answer..."
                  className="form-input"
                  rows="3"
                />
              </div>
            )}
          </div>

          {/* Think Aloud Mode */}
          {assessmentConfig.enable_think_aloud && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Think Aloud Mode</h3>
                <button
                  onClick={() => setThinkAloudMode(!thinkAloudMode)}
                  className={`btn-secondary text-sm ${thinkAloudMode ? 'bg-green-500/20 border-green-500' : ''}`}
                >
                  <MicrophoneIcon className="w-4 h-4 mr-2" />
                  {thinkAloudMode ? 'Recording' : 'Start Recording'}
                </button>
              </div>
              
              {thinkAloudMode && (
                <div className="bg-gray-800 rounded-lg p-4 space-y-4">
                  <div>
                    <label className="form-label">Explain your reasoning</label>
                    <textarea
                      value={thinkAloudData.reasoning}
                      onChange={(e) => setThinkAloudData({...thinkAloudData, reasoning: e.target.value})}
                      placeholder="Walk through your thought process..."
                      className="form-input"
                      rows="2"
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Confidence Level</label>
                      <select
                        value={thinkAloudData.confidence_level}
                        onChange={(e) => setThinkAloudData({...thinkAloudData, confidence_level: parseInt(e.target.value)})}
                        className="form-input"
                      >
                        <option value={1}>1 - Not confident</option>
                        <option value={2}>2 - Somewhat unsure</option>
                        <option value={3}>3 - Moderately confident</option>
                        <option value={4}>4 - Very confident</option>
                        <option value={5}>5 - Completely certain</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="form-label">Difficulty Perception</label>
                      <select
                        value={thinkAloudData.difficulty_perception}
                        onChange={(e) => setThinkAloudData({...thinkAloudData, difficulty_perception: parseInt(e.target.value)})}
                        className="form-input"
                      >
                        <option value={1}>1 - Very easy</option>
                        <option value={2}>2 - Easy</option>
                        <option value={3}>3 - Moderate</option>
                        <option value={4}>4 - Hard</option>
                        <option value={5}>5 - Very hard</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* AI Help */}
          {assessmentConfig.enable_ai_help_tracking && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Need Help?</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => useAiHelp('hint')}
                    className="btn-secondary text-sm"
                    disabled={aiHelpUsed}
                  >
                    <LightBulbIcon className="w-4 h-4 mr-1" />
                    Hint
                  </button>
                  <button
                    onClick={() => useAiHelp('explanation')}
                    className="btn-secondary text-sm"
                    disabled={aiHelpUsed}
                  >
                    <ChatBubbleLeftRightIcon className="w-4 h-4 mr-1" />
                    Explain
                  </button>
                </div>
              </div>
              
              {aiHelpUsed && (
                <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
                  <p className="text-purple-300 text-sm">
                    <ExclamationTriangleIcon className="w-4 h-4 inline mr-1" />
                    AI assistance used - this will affect your score and ability estimate
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-between items-center">
            <button
              onClick={() => setIsActive(!isActive)}
              className="btn-secondary"
            >
              {isActive ? (
                <>
                  <PauseIcon className="w-4 h-4 mr-2" />
                  Pause
                </>
              ) : (
                <>
                  <PlayIcon className="w-4 h-4 mr-2" />
                  Resume
                </>
              )}
            </button>
            
            <button
              onClick={submitAnswer}
              disabled={!selectedAnswer.trim()}
              className="btn-primary"
            >
              Submit Answer
              <ArrowRightIcon className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdaptiveSkillScan;