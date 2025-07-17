import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const EmotionalIntelligenceDashboard = ({ emotionalData, onPersonalityChange }) => {
  const [currentEmotion, setCurrentEmotion] = useState('focused');
  const [learningStyle, setLearningStyle] = useState('multimodal');
  const [aiPersonality, setAiPersonality] = useState('encouraging');
  const [emotionalHistory, setEmotionalHistory] = useState([]);
  const [adaptiveRecommendations, setAdaptiveRecommendations] = useState([]);
  const { user } = useAuth();

  const emotions = {
    confident: { color: 'green', icon: '😊', label: 'Confident' },
    frustrated: { color: 'red', icon: '😤', label: 'Frustrated' },
    confused: { color: 'yellow', icon: '🤔', label: 'Confused' },
    excited: { color: 'purple', icon: '🤩', label: 'Excited' },
    anxious: { color: 'orange', icon: '😰', label: 'Anxious' },
    bored: { color: 'gray', icon: '😴', label: 'Bored' },
    focused: { color: 'blue', icon: '🎯', label: 'Focused' }
  };

  const learningStyles = {
    visual: { icon: '👁️', label: 'Visual', description: 'Learns through seeing' },
    auditory: { icon: '👂', label: 'Auditory', description: 'Learns through hearing' },
    kinesthetic: { icon: '✋', label: 'Kinesthetic', description: 'Learns through doing' },
    reading_writing: { icon: '📝', label: 'Reading/Writing', description: 'Learns through text' },
    multimodal: { icon: '🌟', label: 'Multimodal', description: 'Combines multiple styles' }
  };

  const aiPersonalities = {
    encouraging: { icon: '🌟', label: 'Encouraging', description: 'Positive and supportive' },
    analytical: { icon: '🔍', label: 'Analytical', description: 'Logical and systematic' },
    creative: { icon: '🎨', label: 'Creative', description: 'Imaginative and innovative' },
    patient: { icon: '🧘', label: 'Patient', description: 'Calm and methodical' },
    energetic: { icon: '⚡', label: 'Energetic', description: 'Dynamic and enthusiastic' }
  };

  useEffect(() => {
    if (emotionalData) {
      setCurrentEmotion(emotionalData.emotional_state || 'focused');
      setLearningStyle(emotionalData.learning_style || 'multimodal');
      
      // Add to emotional history
      setEmotionalHistory(prev => [...prev, {
        emotion: emotionalData.emotional_state,
        timestamp: new Date().toISOString(),
        confidence: emotionalData.confidence_score || 0.5
      }].slice(-10)); // Keep last 10 entries
      
      // Generate adaptive recommendations
      generateAdaptiveRecommendations(emotionalData.emotional_state, emotionalData.learning_style);
    }
  }, [emotionalData]);

  const generateAdaptiveRecommendations = (emotion, style) => {
    const recommendations = [];
    
    // Emotional recommendations
    if (emotion === 'frustrated') {
      recommendations.push('Take a short break and try a different approach');
      recommendations.push('Break down the problem into smaller steps');
    } else if (emotion === 'bored') {
      recommendations.push('Try a more challenging problem');
      recommendations.push('Explore real-world applications');
    } else if (emotion === 'confused') {
      recommendations.push('Review fundamental concepts');
      recommendations.push('Ask for clarification or examples');
    } else if (emotion === 'anxious') {
      recommendations.push('Practice relaxation techniques');
      recommendations.push('Start with easier problems to build confidence');
    }
    
    // Learning style recommendations
    if (style === 'visual') {
      recommendations.push('Try creating diagrams or charts');
      recommendations.push('Use color coding and visual aids');
    } else if (style === 'auditory') {
      recommendations.push('Read explanations aloud');
      recommendations.push('Discuss concepts with others');
    } else if (style === 'kinesthetic') {
      recommendations.push('Try hands-on activities');
      recommendations.push('Use physical models or manipulatives');
    }
    
    setAdaptiveRecommendations(recommendations);
  };

  const handlePersonalityChange = (newPersonality) => {
    setAiPersonality(newPersonality);
    if (onPersonalityChange) {
      onPersonalityChange(newPersonality);
    }
  };

  const getEmotionalTrend = () => {
    if (emotionalHistory.length < 2) return 'stable';
    
    const recent = emotionalHistory.slice(-3);
    const positiveEmotions = ['confident', 'excited', 'focused'];
    const negativeEmotions = ['frustrated', 'confused', 'anxious', 'bored'];
    
    let positiveCount = 0;
    let negativeCount = 0;
    
    recent.forEach(entry => {
      if (positiveEmotions.includes(entry.emotion)) positiveCount++;
      if (negativeEmotions.includes(entry.emotion)) negativeCount++;
    });
    
    if (positiveCount > negativeCount) return 'improving';
    if (negativeCount > positiveCount) return 'declining';
    return 'stable';
  };

  const emotionalTrend = getEmotionalTrend();

  return (
    <div className="emotional-intelligence-dashboard bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Emotional Intelligence Dashboard</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            emotionalTrend === 'improving' ? 'bg-green-500' : 
            emotionalTrend === 'declining' ? 'bg-red-500' : 'bg-yellow-500'
          }`}></div>
          <span className="text-sm text-gray-300 capitalize">{emotionalTrend}</span>
        </div>
      </div>

      {/* Current Emotional State */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Current Emotional State</h4>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-4">
            <div className="text-4xl">{emotions[currentEmotion]?.icon}</div>
            <div>
              <div className="text-lg font-medium text-white">{emotions[currentEmotion]?.label}</div>
              <div className="text-sm text-gray-400">Detected from voice and text analysis</div>
            </div>
          </div>
          
          {emotionalData?.confidence_score && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                <span>Confidence</span>
                <span>{Math.round(emotionalData.confidence_score * 100)}%</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full bg-${emotions[currentEmotion]?.color}-500`}
                  style={{ width: `${emotionalData.confidence_score * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Learning Style */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Detected Learning Style</h4>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-4">
            <div className="text-2xl">{learningStyles[learningStyle]?.icon}</div>
            <div>
              <div className="text-lg font-medium text-white">{learningStyles[learningStyle]?.label}</div>
              <div className="text-sm text-gray-400">{learningStyles[learningStyle]?.description}</div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Personality Selection */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-300 mb-3">AI Personality</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {Object.entries(aiPersonalities).map(([key, personality]) => (
            <button
              key={key}
              onClick={() => handlePersonalityChange(key)}
              className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                aiPersonality === key
                  ? 'border-blue-500 bg-blue-500 bg-opacity-20 text-blue-300'
                  : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'
              }`}
            >
              <div className="text-xl mb-1">{personality.icon}</div>
              <div className="text-xs font-medium">{personality.label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Emotional History */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Emotional Pattern</h4>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-2 overflow-x-auto pb-2">
            {emotionalHistory.map((entry, index) => (
              <div key={index} className="flex-shrink-0 text-center">
                <div className="text-2xl mb-1">{emotions[entry.emotion]?.icon}</div>
                <div className="text-xs text-gray-400">
                  {new Date(entry.timestamp).toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>
            ))}
          </div>
          
          {emotionalHistory.length === 0 && (
            <div className="text-center text-gray-400 text-sm">
              No emotional data yet. Start interacting to see patterns!
            </div>
          )}
        </div>
      </div>

      {/* Adaptive Recommendations */}
      {adaptiveRecommendations.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Adaptive Recommendations</h4>
          <div className="bg-green-600 bg-opacity-20 rounded-lg p-4">
            <ul className="space-y-2">
              {adaptiveRecommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start space-x-2 text-sm text-green-300">
                  <span className="text-green-400 mt-1">•</span>
                  <span>{recommendation}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Emotional Intelligence Insights */}
      <div className="bg-gray-700 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Learning Insights</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Emotional Awareness</span>
            <span className="text-green-400">High</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Adaptation Speed</span>
            <span className="text-blue-400">Moderate</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Learning Efficiency</span>
            <span className="text-purple-400">
              {emotionalTrend === 'improving' ? 'Improving' : 
               emotionalTrend === 'declining' ? 'Needs Attention' : 'Stable'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmotionalIntelligenceDashboard;