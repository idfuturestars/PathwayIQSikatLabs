import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const AIContentGenerator = ({ subject, difficulty, onContentGenerated }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [contentType, setContentType] = useState('question');
  const [learningGoals, setLearningGoals] = useState(['']);
  const [personalizedPath, setPersonalizedPath] = useState(null);
  const { user } = useAuth();

  const contentTypes = [
    { value: 'question', label: 'Practice Questions', icon: '❓' },
    { value: 'explanation', label: 'Concept Explanation', icon: '📚' },
    { value: 'example', label: 'Worked Examples', icon: '💡' },
    { value: 'quiz', label: 'Quick Quiz', icon: '🧩' },
    { value: 'learning_path', label: 'Learning Path', icon: '🛤️' }
  ];

  const generateContent = async () => {
    setIsGenerating(true);
    
    try {
      let endpoint = '/api/ai/enhanced-chat';
      let requestBody = {
        message: `Generate ${contentType} content for ${subject} at ${difficulty} level`,
        emotional_context: 'focused',
        learning_style: 'multimodal',
        ai_personality: 'encouraging'
      };

      if (contentType === 'learning_path') {
        endpoint = '/api/ai/personalized-learning-path';
        requestBody = {
          subject: subject,
          learning_goals: learningGoals.filter(goal => goal.trim() !== ''),
          target_completion_weeks: 8,
          preferred_learning_style: 'multimodal'
        };
      }

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const result = await response.json();
        
        if (contentType === 'learning_path') {
          setPersonalizedPath(result);
        } else {
          setGeneratedContent(result);
        }
        
        if (onContentGenerated) {
          onContentGenerated(result);
        }
      } else {
        console.error('Content generation failed');
      }
    } catch (error) {
      console.error('Error generating content:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const addLearningGoal = () => {
    setLearningGoals([...learningGoals, '']);
  };

  const updateLearningGoal = (index, value) => {
    const newGoals = [...learningGoals];
    newGoals[index] = value;
    setLearningGoals(newGoals);
  };

  const removeLearningGoal = (index) => {
    if (learningGoals.length > 1) {
      setLearningGoals(learningGoals.filter((_, i) => i !== index));
    }
  };

  return (
    <div className="ai-content-generator bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">AI Content Generator</h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-300">AI Ready</span>
        </div>
      </div>

      {/* Content Type Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-3">Content Type</label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {contentTypes.map((type) => (
            <button
              key={type.value}
              onClick={() => setContentType(type.value)}
              className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                contentType === type.value
                  ? 'border-purple-500 bg-purple-500 bg-opacity-20 text-purple-300'
                  : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'
              }`}
            >
              <div className="text-2xl mb-1">{type.icon}</div>
              <div className="text-xs font-medium">{type.label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Learning Goals (for learning path) */}
      {contentType === 'learning_path' && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-3">Learning Goals</label>
          {learningGoals.map((goal, index) => (
            <div key={index} className="flex items-center space-x-2 mb-2">
              <input
                type="text"
                value={goal}
                onChange={(e) => updateLearningGoal(index, e.target.value)}
                placeholder={`Learning goal ${index + 1}`}
                className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              {learningGoals.length > 1 && (
                <button
                  onClick={() => removeLearningGoal(index)}
                  className="text-red-400 hover:text-red-300 p-1"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            onClick={addLearningGoal}
            className="text-purple-400 hover:text-purple-300 text-sm font-medium"
          >
            + Add Learning Goal
          </button>
        </div>
      )}

      {/* Generation Settings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Subject</label>
          <div className="bg-gray-700 rounded-lg px-3 py-2 text-white">
            {subject || 'Not specified'}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Difficulty</label>
          <div className="bg-gray-700 rounded-lg px-3 py-2 text-white">
            {difficulty || 'Not specified'}
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={generateContent}
        disabled={isGenerating}
        className={`w-full py-3 rounded-lg font-medium transition-all duration-200 ${
          isGenerating
            ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
            : 'bg-purple-600 hover:bg-purple-700 text-white'
        }`}
      >
        {isGenerating ? (
          <div className="flex items-center justify-center space-x-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Generating...</span>
          </div>
        ) : (
          `Generate ${contentTypes.find(t => t.value === contentType)?.label}`
        )}
      </button>

      {/* Generated Content Display */}
      {generatedContent && (
        <div className="mt-6 bg-gray-700 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Generated Content:</h4>
          <div className="text-white text-sm leading-relaxed">
            {generatedContent.response}
          </div>
          
          {generatedContent.adaptations_applied && (
            <div className="mt-4 p-3 bg-gray-600 rounded-lg">
              <h5 className="text-xs font-medium text-gray-300 mb-2">AI Adaptations:</h5>
              <ul className="text-xs text-gray-400 space-y-1">
                {generatedContent.adaptations_applied.map((adaptation, index) => (
                  <li key={index}>• {adaptation}</li>
                ))}
              </ul>
            </div>
          )}
          
          {generatedContent.next_suggestions && (
            <div className="mt-4 p-3 bg-blue-600 bg-opacity-20 rounded-lg">
              <h5 className="text-xs font-medium text-blue-300 mb-2">Next Steps:</h5>
              <ul className="text-xs text-blue-400 space-y-1">
                {generatedContent.next_suggestions.map((suggestion, index) => (
                  <li key={index}>• {suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Learning Path Display */}
      {personalizedPath && (
        <div className="mt-6 bg-gray-700 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Personalized Learning Path:</h4>
          
          {personalizedPath.personalized_curriculum && (
            <div className="space-y-4">
              {personalizedPath.personalized_curriculum.map((module, index) => (
                <div key={index} className="bg-gray-600 rounded-lg p-4">
                  <h5 className="font-medium text-white mb-2">{module.title}</h5>
                  <p className="text-sm text-gray-300 mb-3">{module.description}</p>
                  <div className="text-xs text-gray-400">
                    Estimated: {module.estimated_hours} hours
                  </div>
                  
                  {module.lessons && (
                    <div className="mt-3 space-y-2">
                      {module.lessons.map((lesson, lessonIndex) => (
                        <div key={lessonIndex} className="flex items-center justify-between text-xs">
                          <span className="text-gray-300">{lesson.title}</span>
                          <span className="text-gray-400">{lesson.duration_minutes} min</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {personalizedPath.learning_milestones && (
            <div className="mt-4 p-3 bg-green-600 bg-opacity-20 rounded-lg">
              <h5 className="text-xs font-medium text-green-300 mb-2">Learning Milestones:</h5>
              <div className="space-y-2">
                {personalizedPath.learning_milestones.map((milestone, index) => (
                  <div key={index} className="text-xs text-green-400">
                    <strong>{milestone.title}</strong> - {milestone.target_completion}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIContentGenerator;