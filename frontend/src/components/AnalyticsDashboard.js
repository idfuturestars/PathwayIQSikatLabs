import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const AnalyticsDashboard = ({ userId = null }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('overview');
  const { user } = useAuth();

  const targetUserId = userId || user.id;

  const timeRanges = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' }
  ];

  const metrics = [
    { value: 'overview', label: 'Overview', icon: '📊' },
    { value: 'progress', label: 'Progress', icon: '📈' },
    { value: 'engagement', label: 'Engagement', icon: '🎯' },
    { value: 'skills', label: 'Skills', icon: '🧠' },
    { value: 'insights', label: 'Insights', icon: '💡' }
  ];

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange, targetUserId]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/analytics/learning/${targetUserId}?time_range=${timeRange}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMetricColor = (value, max) => {
    const percentage = (value / max) * 100;
    if (percentage >= 90) return 'text-green-400';
    if (percentage >= 70) return 'text-blue-400';
    if (percentage >= 50) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getProgressBarColor = (value, max) => {
    const percentage = (value / max) * 100;
    if (percentage >= 90) return 'bg-green-500';
    if (percentage >= 70) return 'bg-blue-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const renderOverview = () => {
    if (!analyticsData?.core_metrics) return null;

    const metrics = analyticsData.core_metrics;
    
    return (
      <div className="space-y-6">
        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-white">
                  {metrics.total_sessions || 0}
                </div>
                <div className="text-sm text-gray-400">Total Sessions</div>
              </div>
              <div className="text-2xl">📚</div>
            </div>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-blue-400">
                  {Math.round(metrics.overall_accuracy || 0)}%
                </div>
                <div className="text-sm text-gray-400">Accuracy</div>
              </div>
              <div className="text-2xl">🎯</div>
            </div>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-green-400">
                  {Math.round(metrics.total_study_time || 0)}
                </div>
                <div className="text-sm text-gray-400">Minutes Studied</div>
              </div>
              <div className="text-2xl">⏱️</div>
            </div>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-purple-400">
                  {Math.round(metrics.engagement_score || 0)}
                </div>
                <div className="text-sm text-gray-400">Engagement</div>
              </div>
              <div className="text-2xl">🔥</div>
            </div>
          </div>
        </div>

        {/* Performance Chart */}
        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Performance Trends</h4>
          <div className="h-48 bg-gray-600 rounded-lg flex items-center justify-center">
            <div className="text-center text-gray-400">
              <div className="text-4xl mb-2">📈</div>
              <div>Performance chart visualization</div>
              <div className="text-sm mt-1">Chart implementation needed</div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-white font-medium mb-2">Learning Velocity</div>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-gray-600 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.abs(metrics.learning_velocity || 0) * 100}%` }}
                />
              </div>
              <span className={`text-sm ${metrics.learning_velocity >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {metrics.learning_velocity >= 0 ? '↗️' : '↘️'} {Math.abs(metrics.learning_velocity || 0).toFixed(1)}%
              </span>
            </div>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-white font-medium mb-2">Session Quality</div>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-gray-600 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${(metrics.average_session_time || 0) / 60 * 100}%` }}
                />
              </div>
              <span className="text-sm text-green-400">
                {Math.round(metrics.average_session_time || 0)} min
              </span>
            </div>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-white font-medium mb-2">Assessment Score</div>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-gray-600 rounded-full h-2">
                <div 
                  className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${metrics.average_assessment_score || 0}%` }}
                />
              </div>
              <span className="text-sm text-purple-400">
                {Math.round(metrics.average_assessment_score || 0)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderProgress = () => {
    if (!analyticsData?.learning_progress) return null;

    const progress = analyticsData.learning_progress;
    
    return (
      <div className="space-y-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Subject Progress</h4>
          <div className="space-y-4">
            {Object.entries(progress).map(([subject, data]) => (
              <div key={subject} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium capitalize">{subject}</span>
                  <span className={`text-sm font-medium ${getMetricColor(data.current_level * 100, 100)}`}>
                    {Math.round(data.current_level * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-500 ${getProgressBarColor(data.current_level * 100, 100)}`}
                    style={{ width: `${data.current_level * 100}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>Improvement: {(data.improvement * 100).toFixed(1)}%</span>
                  <span className="capitalize">{data.trend}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Learning Milestones</h4>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div>
                <div className="text-white text-sm">Completed 50 Questions</div>
                <div className="text-gray-400 text-xs">Achievement unlocked</div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <div>
                <div className="text-white text-sm">7-Day Streak</div>
                <div className="text-gray-400 text-xs">Consistency milestone</div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div>
                <div className="text-white text-sm">Perfect Score</div>
                <div className="text-gray-400 text-xs">Excellence achieved</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderEngagement = () => {
    if (!analyticsData?.engagement_metrics) return null;

    const engagement = analyticsData.engagement_metrics;
    
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-medium mb-4">Activity Pattern</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Active Days</span>
                <span className="text-white font-medium">{engagement.active_days || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Session Frequency</span>
                <span className="text-white font-medium">{(engagement.session_frequency || 0).toFixed(1)}/day</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Help Requests</span>
                <span className="text-white font-medium">{(engagement.help_seeking_behavior || 0).toFixed(1)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Consistency</span>
                <span className="text-white font-medium">{Math.round(engagement.consistency_score || 0)}%</span>
              </div>
            </div>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-medium mb-4">Engagement Trends</h4>
            <div className="h-32 bg-gray-600 rounded-lg flex items-center justify-center">
              <div className="text-center text-gray-400">
                <div className="text-2xl mb-1">📊</div>
                <div className="text-sm">Engagement trend chart</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Learning Preferences</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-400 mb-2">Preferred Session Length</div>
              <div className="text-lg text-white font-medium">
                {Math.round(engagement.preferred_session_length || 30)} minutes
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-2">Best Time to Study</div>
              <div className="text-lg text-white font-medium">Evening</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderSkills = () => {
    if (!analyticsData?.skill_analysis) return null;

    const skills = analyticsData.skill_analysis;
    
    return (
      <div className="space-y-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Skill Mastery</h4>
          <div className="space-y-4">
            {Object.entries(skills).map(([skill, data]) => (
              <div key={skill} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium capitalize">{skill}</span>
                  <span className={`text-sm font-medium ${getMetricColor(data.mastery_level * 100, 100)}`}>
                    {Math.round(data.mastery_level * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-500 ${getProgressBarColor(data.mastery_level * 100, 100)}`}
                    style={{ width: `${data.mastery_level * 100}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>Questions: {data.attempts}</span>
                  <span>Correct: {data.correct}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Skill Recommendations</h4>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <div className="text-white text-sm">Focus on weak areas</div>
                <div className="text-gray-400 text-xs">Prioritize subjects with lower mastery</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <div className="text-white text-sm">Practice consistently</div>
                <div className="text-gray-400 text-xs">Regular practice improves retention</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div>
                <div className="text-white text-sm">Challenge yourself</div>
                <div className="text-gray-400 text-xs">Try harder problems in strong subjects</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderInsights = () => {
    if (!analyticsData?.insights) return null;

    const insights = analyticsData.insights;
    
    return (
      <div className="space-y-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">AI Insights</h4>
          <div className="space-y-4">
            {insights.map((insight, index) => (
              <div key={index} className={`border-l-4 pl-4 ${
                insight.severity === 'critical' ? 'border-red-500' :
                insight.severity === 'warning' ? 'border-yellow-500' :
                'border-blue-500'
              }`}>
                <div className="flex items-start space-x-2">
                  <div className={`text-lg ${
                    insight.severity === 'critical' ? 'text-red-500' :
                    insight.severity === 'warning' ? 'text-yellow-500' :
                    'text-blue-500'
                  }`}>
                    {insight.type === 'performance' ? '📊' :
                     insight.type === 'engagement' ? '🎯' :
                     insight.type === 'progress' ? '📈' : '💡'}
                  </div>
                  <div className="flex-1">
                    <div className="text-white font-medium">{insight.message}</div>
                    <div className="text-gray-400 text-sm mt-1">{insight.recommendation}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Personalized Recommendations</h4>
          <div className="space-y-3">
            <div className="bg-green-600 bg-opacity-20 rounded-lg p-3">
              <div className="text-green-300 font-medium">Study Schedule</div>
              <div className="text-green-200 text-sm">Continue with your current 45-minute sessions</div>
            </div>
            <div className="bg-blue-600 bg-opacity-20 rounded-lg p-3">
              <div className="text-blue-300 font-medium">Focus Areas</div>
              <div className="text-blue-200 text-sm">Spend more time on challenging topics</div>
            </div>
            <div className="bg-purple-600 bg-opacity-20 rounded-lg p-3">
              <div className="text-purple-300 font-medium">Learning Style</div>
              <div className="text-purple-200 text-sm">Try visual learning aids for better retention</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (selectedMetric) {
      case 'overview': return renderOverview();
      case 'progress': return renderProgress();
      case 'engagement': return renderEngagement();
      case 'skills': return renderSkills();
      case 'insights': return renderInsights();
      default: return renderOverview();
    }
  };

  if (loading) {
    return (
      <div className="analytics-dashboard bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-center py-8">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Learning Analytics</h3>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-1 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {timeRanges.map(range => (
              <option key={range.value} value={range.value}>{range.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Metric Navigation */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {metrics.map(metric => (
            <button
              key={metric.value}
              onClick={() => setSelectedMetric(metric.value)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-all duration-200 ${
                selectedMetric === metric.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {metric.icon} {metric.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      {renderContent()}

      {/* Empty State */}
      {!analyticsData && (
        <div className="text-center py-8 text-gray-400">
          <div className="text-6xl mb-4">📊</div>
          <div className="text-lg font-medium mb-2">No Analytics Data</div>
          <div className="text-sm">Start learning to see your progress analytics!</div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;