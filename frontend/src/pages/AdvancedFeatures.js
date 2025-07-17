import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

// Import all the advanced feature components
import VoiceRecorder from '../components/VoiceRecorder';
import AIContentGenerator from '../components/AIContentGenerator';
import EmotionalIntelligenceDashboard from '../components/EmotionalIntelligenceDashboard';
import BadgeSystem from '../components/BadgeSystem';
import Leaderboard from '../components/Leaderboard';
import StudyGroups from '../components/StudyGroups';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import PredictiveAnalytics from '../components/PredictiveAnalytics';
import ReportingSystem from '../components/ReportingSystem';

const AdvancedFeatures = () => {
  const [activeTab, setActiveTab] = useState('voice_ai');
  const [emotionalData, setEmotionalData] = useState(null);
  const [aiPersonality, setAiPersonality] = useState('encouraging');
  const [generatedContent, setGeneratedContent] = useState(null);
  const { user } = useAuth();

  const tabs = [
    {
      id: 'voice_ai',
      label: 'Voice & AI',
      icon: '🎤',
      description: 'Voice-to-text and AI-powered learning',
      phase: 'Phase 1'
    },
    {
      id: 'gamification',
      label: 'Gamification',
      icon: '🏆',
      description: 'Badges, leaderboards, and competitions',
      phase: 'Phase 2'
    },
    {
      id: 'social',
      label: 'Social Learning',
      icon: '👥',
      description: 'Study groups and collaboration',
      phase: 'Phase 2'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: '📊',
      description: 'Learning analytics and insights',
      phase: 'Phase 3'
    },
    {
      id: 'predictions',
      label: 'Predictions',
      icon: '🔮',
      description: 'Predictive analytics and forecasting',
      phase: 'Phase 3'
    },
    {
      id: 'reporting',
      label: 'Reporting',
      icon: '📋',
      description: 'Comprehensive reports and documentation',
      phase: 'Phase 3'
    }
  ];

  const handleVoiceTranscription = (transcription) => {
    console.log('Voice transcription:', transcription);
    // You can add logic to process the transcription
  };

  const handleEmotionalAnalysis = (emotionalData) => {
    setEmotionalData(emotionalData);
    console.log('Emotional analysis:', emotionalData);
  };

  const handleContentGenerated = (content) => {
    setGeneratedContent(content);
    console.log('Content generated:', content);
  };

  const handleBadgeEarned = (badges) => {
    console.log('Badges earned:', badges);
    // You can show notifications or update UI
  };

  const handlePersonalityChange = (personality) => {
    setAiPersonality(personality);
    console.log('AI personality changed to:', personality);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'voice_ai':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <VoiceRecorder 
                onTranscription={handleVoiceTranscription}
                onEmotionalAnalysis={handleEmotionalAnalysis}
              />
              <EmotionalIntelligenceDashboard 
                emotionalData={emotionalData}
                onPersonalityChange={handlePersonalityChange}
              />
            </div>
            <AIContentGenerator 
              subject="Mathematics"
              difficulty="intermediate"
              onContentGenerated={handleContentGenerated}
            />
          </div>
        );
      
      case 'gamification':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <BadgeSystem onBadgeEarned={handleBadgeEarned} />
              <Leaderboard type="global" />
            </div>
          </div>
        );
      
      case 'social':
        return (
          <div className="space-y-6">
            <StudyGroups onGroupActivity={(activity) => console.log('Group activity:', activity)} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Leaderboard type="global" subject="Mathematics" />
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-4">Collaborative Features</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">💬</div>
                    <div>
                      <div className="text-white font-medium">Group Chat</div>
                      <div className="text-gray-400 text-sm">Real-time communication</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">📚</div>
                    <div>
                      <div className="text-white font-medium">Shared Resources</div>
                      <div className="text-gray-400 text-sm">Collaborative study materials</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">🎯</div>
                    <div>
                      <div className="text-white font-medium">Group Challenges</div>
                      <div className="text-gray-400 text-sm">Team-based competitions</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      
      case 'analytics':
        return (
          <div className="space-y-6">
            <AnalyticsDashboard userId={user.id} />
          </div>
        );
      
      case 'predictions':
        return (
          <div className="space-y-6">
            <PredictiveAnalytics userId={user.id} />
          </div>
        );
      
      case 'reporting':
        return (
          <div className="space-y-6">
            <ReportingSystem />
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Advanced Features
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Explore the cutting-edge AI-powered features that make PathwayIQ the most advanced 
            educational platform available.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`p-4 rounded-lg border-2 transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'border-blue-500 bg-blue-500 bg-opacity-20 text-blue-300'
                    : 'border-gray-600 bg-gray-800 text-gray-300 hover:border-gray-500'
                }`}
              >
                <div className="text-2xl mb-2">{tab.icon}</div>
                <div className="text-sm font-medium">{tab.label}</div>
                <div className="text-xs text-gray-400 mt-1">{tab.phase}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Feature Description */}
        <div className="mb-6 bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white mb-1">
                {tabs.find(tab => tab.id === activeTab)?.label}
              </h2>
              <p className="text-gray-400">
                {tabs.find(tab => tab.id === activeTab)?.description}
              </p>
            </div>
            <div className="text-right">
              <span className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm">
                {tabs.find(tab => tab.id === activeTab)?.phase}
              </span>
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <div className="mb-8">
          {renderTabContent()}
        </div>

        {/* Footer Info */}
        <div className="text-center text-gray-400">
          <p className="text-sm">
            These advanced features are powered by cutting-edge AI technology and are continuously 
            being improved based on user feedback and the latest research in educational technology.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdvancedFeatures;