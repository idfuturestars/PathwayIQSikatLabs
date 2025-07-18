import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const AIContentGenerator = () => {
  const { user } = useAuth();
  const [contentTypes, setContentTypes] = useState([]);
  const [selectedContentType, setSelectedContentType] = useState('');
  const [subject, setSubject] = useState('');
  const [topic, setTopic] = useState('');
  const [difficultyLevel, setDifficultyLevel] = useState('intermediate');
  const [learningObjectives, setLearningObjectives] = useState('');
  const [targetAudience, setTargetAudience] = useState('8th grade students');
  const [length, setLength] = useState('medium');
  const [personalizationEnabled, setPersonalizationEnabled] = useState(true);
  const [contextPrompt, setContextPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [error, setError] = useState(null);
  const [userContent, setUserContent] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadContentTypes();
    loadUserContent();
  }, []);

  const loadContentTypes = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${backendUrl}/api/content-generation/content-types`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      setContentTypes(response.data.content_types);
    } catch (error) {
      console.error('Error loading content types:', error);
    }
  };

  const loadUserContent = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${backendUrl}/api/content-generation/user-content`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      setUserContent(response.data.contents);
    } catch (error) {
      console.error('Error loading user content:', error);
    }
  };

  const generateContent = async (e) => {
    e.preventDefault();
    
    if (!selectedContentType || !subject || !topic) {
      setError('Please fill in all required fields');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedContent(null);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${backendUrl}/api/content-generation/generate`,
        {
          content_type: selectedContentType,
          subject: subject,
          topic: topic,
          difficulty_level: difficultyLevel,
          learning_objectives: learningObjectives.split(',').map(obj => obj.trim()).filter(obj => obj),
          target_audience: targetAudience,
          length: length,
          personalization_enabled: personalizationEnabled,
          context_prompt: contextPrompt || undefined
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setGeneratedContent(response.data);
      loadUserContent(); // Refresh user content list
      
    } catch (error) {
      console.error('Error generating content:', error);
      setError(error.response?.data?.detail || 'Failed to generate content');
    } finally {
      setIsGenerating(false);
    }
  };

  const viewContent = async (contentId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${backendUrl}/api/content-generation/content/${contentId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      setGeneratedContent(response.data);
      setShowHistory(false);
    } catch (error) {
      console.error('Error viewing content:', error);
      setError('Failed to load content');
    }
  };

  const renderGeneratedContent = () => {
    if (!generatedContent) return null;

    const { content } = generatedContent;

    switch (generatedContent.content_type) {
      case 'quiz':
        return (
          <div className="space-y-6">
            <div className="bg-blue-900 p-4 rounded-lg">
              <h3 className="text-xl font-bold text-white mb-2">{content.title}</h3>
              <p className="text-blue-200 mb-4">{content.instructions}</p>
              <div className="flex flex-wrap gap-4 text-sm text-blue-200">
                <span>📝 {content.questions?.length || 0} Questions</span>
                <span>⏱️ {content.estimated_time}</span>
                <span>🎯 {content.total_points} Points</span>
              </div>
            </div>
            
            <div className="space-y-4">
              {content.questions?.map((question, index) => (
                <div key={question.id} className="bg-gray-800 p-4 rounded-lg">
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="font-semibold text-white">Question {index + 1}</h4>
                    <span className="text-sm text-gray-400">{question.points} pts</span>
                  </div>
                  <p className="text-gray-300 mb-3">{question.question}</p>
                  
                  {question.options && (
                    <div className="space-y-2 mb-3">
                      {question.options.map((option, optIndex) => (
                        <div key={optIndex} className="flex items-center space-x-2">
                          <span className="text-gray-400">{String.fromCharCode(65 + optIndex)}.</span>
                          <span className="text-gray-300">{option}</span>
                          {option === question.correct_answer && (
                            <span className="text-green-400 text-sm">✓ Correct</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="mt-3 p-3 bg-gray-700 rounded text-sm text-gray-300">
                    <strong>Explanation:</strong> {question.explanation}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'lesson':
        return (
          <div className="space-y-6">
            <div className="bg-green-900 p-4 rounded-lg">
              <h3 className="text-xl font-bold text-white mb-2">{content.title}</h3>
              <p className="text-green-200 mb-4">{content.introduction}</p>
              <div className="flex flex-wrap gap-4 text-sm text-green-200">
                <span>📚 {content.sections?.length || 0} Sections</span>
                <span>⏱️ {content.estimated_duration}</span>
              </div>
            </div>
            
            <div className="space-y-4">
              {content.sections?.map((section, index) => (
                <div key={index} className="bg-gray-800 p-4 rounded-lg">
                  <h4 className="font-semibold text-white mb-3">{section.title}</h4>
                  <p className="text-gray-300 mb-3">{section.content}</p>
                  
                  {section.examples && section.examples.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-700 rounded">
                      <strong className="text-white">Examples:</strong>
                      <ul className="list-disc list-inside text-gray-300 mt-2">
                        {section.examples.map((example, exIndex) => (
                          <li key={exIndex}>{example}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {section.key_concepts && section.key_concepts.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-700 rounded">
                      <strong className="text-white">Key Concepts:</strong>
                      <ul className="list-disc list-inside text-gray-300 mt-2">
                        {section.key_concepts.map((concept, conIndex) => (
                          <li key={conIndex}>{concept}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {content.summary && (
              <div className="bg-gray-800 p-4 rounded-lg">
                <h4 className="font-semibold text-white mb-2">Summary</h4>
                <p className="text-gray-300">{content.summary}</p>
              </div>
            )}
          </div>
        );

      case 'explanation':
        return (
          <div className="space-y-6">
            <div className="bg-purple-900 p-4 rounded-lg">
              <h3 className="text-xl font-bold text-white mb-2">{content.title}</h3>
              <p className="text-purple-200">{content.overview}</p>
            </div>
            
            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="font-semibold text-white mb-3">Explanation</h4>
              <p className="text-gray-300 leading-relaxed">{content.main_explanation}</p>
            </div>
            
            {content.examples && content.examples.length > 0 && (
              <div className="bg-gray-800 p-4 rounded-lg">
                <h4 className="font-semibold text-white mb-3">Examples</h4>
                <div className="space-y-3">
                  {content.examples.map((example, index) => (
                    <div key={index} className="p-3 bg-gray-700 rounded">
                      <h5 className="font-medium text-white">{example.title}</h5>
                      <p className="text-gray-300 mt-1">{example.description}</p>
                      {example.solution && (
                        <p className="text-gray-300 mt-2"><strong>Solution:</strong> {example.solution}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {content.key_points && content.key_points.length > 0 && (
              <div className="bg-gray-800 p-4 rounded-lg">
                <h4 className="font-semibold text-white mb-3">Key Points</h4>
                <ul className="list-disc list-inside text-gray-300 space-y-1">
                  {content.key_points.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );

      case 'flashcards':
        return (
          <div className="space-y-6">
            <div className="bg-yellow-900 p-4 rounded-lg">
              <h3 className="text-xl font-bold text-white mb-2">{content.title}</h3>
              <p className="text-yellow-200 mb-4">{content.instructions}</p>
              <div className="flex flex-wrap gap-4 text-sm text-yellow-200">
                <span>🃏 {content.cards?.length || 0} Cards</span>
                <span>⏱️ {content.estimated_study_time}</span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {content.cards?.map((card, index) => (
                <div key={card.id} className="bg-gray-800 p-4 rounded-lg">
                  <div className="text-center">
                    <div className="bg-gray-700 p-3 rounded mb-2">
                      <strong className="text-white">Front:</strong>
                      <p className="text-gray-300 mt-1">{card.front}</p>
                    </div>
                    <div className="bg-gray-700 p-3 rounded">
                      <strong className="text-white">Back:</strong>
                      <p className="text-gray-300 mt-1">{card.back}</p>
                    </div>
                    {card.category && (
                      <span className="inline-block mt-2 px-2 py-1 bg-gray-600 text-gray-300 text-xs rounded">
                        {card.category}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return (
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-xl font-bold text-white mb-2">{content.title}</h3>
            <pre className="text-gray-300 text-sm overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(content, null, 2)}
            </pre>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">AI Content Generator</h1>
          <p className="text-gray-400">
            Generate personalized educational content using artificial intelligence
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Content Generation Form */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 p-6 rounded-lg">
              <h2 className="text-xl font-semibold mb-4">Create New Content</h2>
              
              <form onSubmit={generateContent} className="space-y-4">
                {/* Content Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Content Type *
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {contentTypes.map((type) => (
                      <button
                        key={type.id}
                        type="button"
                        onClick={() => setSelectedContentType(type.id)}
                        className={`p-3 rounded-lg border text-left transition-colors ${
                          selectedContentType === type.id
                            ? 'border-blue-500 bg-blue-900'
                            : 'border-gray-600 bg-gray-700 hover:bg-gray-600'
                        }`}
                      >
                        <div className="text-lg mb-1">{type.icon}</div>
                        <div className="font-medium">{type.name}</div>
                        <div className="text-xs text-gray-400">{type.description}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Subject and Topic */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Subject *
                    </label>
                    <input
                      type="text"
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                      placeholder="e.g., Mathematics, Science, History"
                      className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Topic *
                    </label>
                    <input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="e.g., Quadratic Equations, Photosynthesis"
                      className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      required
                    />
                  </div>
                </div>

                {/* Difficulty and Length */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Difficulty Level
                    </label>
                    <select
                      value={difficultyLevel}
                      onChange={(e) => setDifficultyLevel(e.target.value)}
                      className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                      <option value="expert">Expert</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Length
                    </label>
                    <select
                      value={length}
                      onChange={(e) => setLength(e.target.value)}
                      className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="short">Short</option>
                      <option value="medium">Medium</option>
                      <option value="long">Long</option>
                    </select>
                  </div>
                </div>

                {/* Target Audience */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Target Audience
                  </label>
                  <input
                    type="text"
                    value={targetAudience}
                    onChange={(e) => setTargetAudience(e.target.value)}
                    placeholder="e.g., 8th grade students, High school biology class"
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  />
                </div>

                {/* Learning Objectives */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Learning Objectives (comma-separated)
                  </label>
                  <textarea
                    value={learningObjectives}
                    onChange={(e) => setLearningObjectives(e.target.value)}
                    placeholder="e.g., Solve quadratic equations, Understand discriminant, Apply quadratic formula"
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                    rows="3"
                  />
                </div>

                {/* Context Prompt */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Additional Context (optional)
                  </label>
                  <textarea
                    value={contextPrompt}
                    onChange={(e) => setContextPrompt(e.target.value)}
                    placeholder="Any additional context or specific requirements..."
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                    rows="3"
                  />
                </div>

                {/* Personalization Toggle */}
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="personalization"
                    checked={personalizationEnabled}
                    onChange={(e) => setPersonalizationEnabled(e.target.checked)}
                    className="text-blue-500 focus:ring-blue-500"
                  />
                  <label htmlFor="personalization" className="text-sm text-gray-300">
                    Enable personalization based on my learning history
                  </label>
                </div>

                {/* Generate Button */}
                <button
                  type="submit"
                  disabled={isGenerating || !selectedContentType || !subject || !topic}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isGenerating ? (
                    <>
                      <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Generating Content...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
                      </svg>
                      <span>Generate Content</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Content History Sidebar */}
          <div>
            <div className="bg-gray-800 p-6 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">My Content</h3>
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="text-blue-400 hover:text-blue-300 text-sm"
                >
                  {showHistory ? 'Hide' : 'Show'} History
                </button>
              </div>
              
              {showHistory && (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {userContent.map((content) => (
                    <div
                      key={content.id}
                      className="p-3 bg-gray-700 rounded cursor-pointer hover:bg-gray-600 transition-colors"
                      onClick={() => viewContent(content.id)}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-sm">{content.title}</span>
                        <span className="text-xs text-gray-400">{content.content_type}</span>
                      </div>
                      <p className="text-xs text-gray-400">
                        {content.subject} • {content.topic}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(content.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                  {userContent.length === 0 && (
                    <p className="text-gray-400 text-sm">No content generated yet</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Generated Content Display */}
        {generatedContent && (
          <div className="mt-6">
            <div className="bg-gray-800 p-6 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Generated Content</h2>
                <div className="flex items-center space-x-2 text-sm text-gray-400">
                  <span>Quality: {Math.round(generatedContent.quality_score * 100)}%</span>
                  <span>•</span>
                  <span>{new Date(generatedContent.created_at).toLocaleString()}</span>
                </div>
              </div>
              
              {renderGeneratedContent()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIContentGenerator;