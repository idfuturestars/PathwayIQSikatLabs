import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import {
  PaperAirplaneIcon,
  SparklesIcon,
  LightBulbIcon,
  BookOpenIcon,
  ChatBubbleLeftRightIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

const StarMentor = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const quickPrompts = [
    "Explain JavaScript closures",
    "How do React hooks work?",
    "What are data structures?",
    "Explain async/await in Python",
    "How to optimize database queries?",
    "What is machine learning?"
  ];

  useEffect(() => {
    // Initialize with welcome message
    setMessages([
      {
        role: 'assistant',
        content: `Hello ${user?.username}! I'm StarMentor™, your AI-powered learning companion. I'm here to help you understand concepts, solve problems, and guide your learning journey. What would you like to learn about today?`,
        timestamp: new Date()
      }
    ]);
  }, [user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async (message = inputMessage) => {
    if (!message.trim()) return;

    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      // Use enhanced AI chat with emotional intelligence
      const response = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/ai/enhanced-chat`,
        {},
        {
          params: {
            message: message,
            emotional_context: 'focused', // Can be dynamic based on user input analysis
            learning_style: 'multimodal', // Can be detected from user patterns
            ai_personality: 'encouraging',
            session_id: sessionId
          }
        }
      );

      const aiMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        // Enhanced data from Phase 1
        emotional_state: response.data.emotional_state_detected,
        learning_style: response.data.learning_style_detected,
        ai_personality: response.data.ai_personality_used,
        adaptations: response.data.adaptations_applied,
        suggestions: response.data.next_suggestions
      };

      setMessages(prev => [...prev, aiMessage]);
      
      if (!sessionId) {
        setSessionId(response.data.session_id);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Fallback to original chat endpoint if enhanced chat fails
      try {
        const fallbackResponse = await axios.post(
          `${process.env.REACT_APP_BACKEND_URL}/api/ai/chat`,
          { 
            message: message,
            session_id: sessionId 
          }
        );

        const aiMessage = {
          role: 'assistant',
          content: fallbackResponse.data.response,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, aiMessage]);
        
        if (!sessionId) {
          setSessionId(fallbackResponse.data.session_id);
        }
      } catch (fallbackError) {
        console.error('Fallback chat also failed:', fallbackError);
        const errorMessage = {
          role: 'assistant',
          content: 'I apologize, but I\'m having trouble responding right now. Please try again.',
          timestamp: new Date(),
          isError: true
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearConversation = () => {
    setMessages([
      {
        role: 'assistant',
        content: `Hi again ${user?.username}! Ready for a fresh conversation? What would you like to explore today?`,
        timestamp: new Date()
      }
    ]);
    setSessionId(null);
  };

  const formatMessage = (content) => {
    // Basic markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-800 px-1 rounded">$1</code>')
      .replace(/\n/g, '<br>');
  };

  return (
    <div className="max-w-6xl mx-auto h-[calc(100vh-120px)] flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
              <SparklesIcon className="w-8 h-8 text-yellow-500 mr-3" />
              StarMentor™
            </h1>
            <p className="text-gray-400">Your AI-powered learning companion</p>
          </div>
          <button
            onClick={clearConversation}
            className="btn-secondary flex items-center"
          >
            <ArrowPathIcon className="w-4 h-4 mr-2" />
            New Conversation
          </button>
        </div>
      </div>

      <div className="flex flex-1 gap-6">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages Container */}
          <div className="flex-1 bg-gray-900 rounded-xl border border-gray-700 mb-4 overflow-hidden">
            <div className="h-full overflow-y-auto p-6 space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] p-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-green-600 text-white'
                        : message.isError
                        ? 'bg-red-600/20 border border-red-500 text-red-200'
                        : 'bg-gray-800 text-gray-100 border border-gray-700'
                    }`}
                  >
                    {message.role === 'assistant' && !message.isError && (
                      <div className="flex items-center mb-2">
                        <SparklesIcon className="w-4 h-4 text-yellow-500 mr-2" />
                        <span className="text-xs text-gray-400 font-medium">StarMentor™</span>
                      </div>
                    )}
                    <div 
                      className="whitespace-pre-wrap"
                      dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                    />
                    <div className="text-xs text-gray-400 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-800 border border-gray-700 p-4 rounded-lg">
                    <div className="flex items-center">
                      <SparklesIcon className="w-4 h-4 text-yellow-500 mr-2" />
                      <span className="text-xs text-gray-400 font-medium mr-3">StarMentor™</span>
                      <div className="loading-spinner w-4 h-4"></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="bg-gray-900 rounded-xl border border-gray-700 p-4">
            <div className="flex items-end space-x-3">
              <div className="flex-1">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about programming, concepts, or learning..."
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white placeholder-gray-400 resize-none focus:outline-none focus:border-green-500"
                  rows="3"
                  disabled={loading}
                />
              </div>
              <button
                onClick={() => handleSendMessage()}
                disabled={loading || !inputMessage.trim()}
                className="btn-primary p-3"
              >
                <PaperAirplaneIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="w-80 space-y-6">
          {/* Quick Prompts */}
          <div className="starguide-card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <LightBulbIcon className="w-5 h-5 text-yellow-500 mr-2" />
              Quick Questions
            </h3>
            <div className="space-y-2">
              {quickPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => handleSendMessage(prompt)}
                  className="w-full text-left p-3 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-300 hover:text-white transition-colors"
                  disabled={loading}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Learning Topics */}
          <div className="starguide-card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <BookOpenIcon className="w-5 h-5 text-blue-500 mr-2" />
              Popular Topics
            </h3>
            <div className="space-y-3">
              {[
                { topic: 'JavaScript', level: 'Beginner', color: 'bg-yellow-500' },
                { topic: 'React', level: 'Intermediate', color: 'bg-blue-500' },
                { topic: 'Python', level: 'Beginner', color: 'bg-green-500' },
                { topic: 'Algorithms', level: 'Advanced', color: 'bg-purple-500' },
                { topic: 'Databases', level: 'Intermediate', color: 'bg-red-500' },
              ].map((item, index) => (
                <button
                  key={index}
                  onClick={() => handleSendMessage(`Tell me about ${item.topic} for ${item.level} level`)}
                  className="w-full text-left p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
                  disabled={loading}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">{item.topic}</span>
                    <span className={`text-xs px-2 py-1 rounded ${item.color} text-white`}>
                      {item.level}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Tips */}
          <div className="starguide-card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <ChatBubbleLeftRightIcon className="w-5 h-5 text-green-500 mr-2" />
              Tips for Better Learning
            </h3>
            <div className="space-y-3 text-sm text-gray-300">
              <div className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <p>Ask specific questions for better answers</p>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <p>Request examples and practical applications</p>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <p>Ask for step-by-step explanations</p>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <p>Don't hesitate to ask follow-up questions</p>
              </div>
            </div>
          </div>

          {/* Session Stats */}
          <div className="starguide-card">
            <h3 className="text-lg font-semibold text-white mb-4">Session Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Messages</span>
                <span className="text-white font-medium">{messages.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Current Level</span>
                <span className="text-green-500 font-medium">Level {user?.level}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total XP</span>
                <span className="text-blue-500 font-medium">{user?.xp}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StarMentor;