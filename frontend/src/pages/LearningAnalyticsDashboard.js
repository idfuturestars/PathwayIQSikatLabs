import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

const LearningAnalyticsDashboard = () => {
  const { user } = useContext(AuthContext);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timePeriod, setTimePeriod] = useState('30d');

  useEffect(() => {
    fetchAnalyticsData();
  }, [timePeriod]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/analytics/dashboard?time_period=${timePeriod}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data.data);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch analytics data');
      }
    } catch (err) {
      setError('Network error occurred while fetching analytics data');
      console.error('Analytics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const ProgressChart = ({ skillProgress }) => {
    if (!skillProgress) return null;
    
    return (
      <div className="space-y-3">
        {Object.entries(skillProgress).map(([skill, data]) => (
          <div key={skill} className="bg-gray-100 p-3 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium text-gray-700 capitalize">{skill.replace('_', ' ')}</span>
              <span className="text-sm font-semibold text-blue-600">{data.accuracy}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${data.accuracy}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>{data.total_attempts} attempts</span>
              <span>Recent: {data.recent_performance}%</span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const MetricCard = ({ title, value, subtitle, color = "blue" }) => (
    <div className={`bg-gradient-to-br from-${color}-50 to-${color}-100 p-6 rounded-xl border border-${color}-200`}>
      <h3 className="text-lg font-semibold text-gray-700 mb-2">{title}</h3>
      <div className={`text-3xl font-bold text-${color}-600 mb-1`}>{value}</div>
      {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading your learning analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Analytics</h3>
              <p className="text-red-600 mb-4">{error}</p>
              <button 
                onClick={fetchAnalyticsData}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const performance = analyticsData?.user_performance || {};
  const learningMetrics = analyticsData?.learning_metrics || {};
  const skillAnalytics = analyticsData?.skill_analytics || {};
  const recommendations = analyticsData?.recommendations || [];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Learning Analytics Dashboard
              </h1>
              <p className="text-gray-600">
                Welcome back, {user?.username}! Here's your learning progress overview.
              </p>
            </div>
            <div className="mt-4 sm:mt-0">
              <select
                value={timePeriod}
                onChange={(e) => setTimePeriod(e.target.value)}
                className="bg-white border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Average Score"
            value={`${performance.average_assessment_score?.toFixed(1) || 0}%`}
            subtitle="Overall performance"
            color="blue"
          />
          <MetricCard
            title="Learning Streak"
            value={`${performance.learning_streak || 0} days`}
            subtitle="Consecutive learning days"
            color="green"
          />
          <MetricCard
            title="Assessments Completed"
            value={performance.total_assessments || 0}
            subtitle="Total assessments taken"
            color="purple"
          />
          <MetricCard
            title="Content Generated"
            value={performance.total_content_generated || 0}
            subtitle="AI-generated materials"
            color="orange"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Skills Progress */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Skills Progress</h2>
            <ProgressChart skillProgress={performance.skill_progress} />
          </div>

          {/* Performance Trend */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Performance Analysis</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">Performance Trend</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  performance.performance_trend === 'improving' ? 'bg-green-100 text-green-800' :
                  performance.performance_trend === 'declining' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {performance.performance_trend?.charAt(0).toUpperCase() + performance.performance_trend?.slice(1) || 'Stable'}
                </span>
              </div>
              
              {performance.strengths?.length > 0 && (
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Strengths</h4>
                  <div className="flex flex-wrap gap-2">
                    {performance.strengths.map((strength, index) => (
                      <span key={index} className="px-2 py-1 bg-green-100 text-green-700 rounded-md text-sm">
                        {strength.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {performance.areas_for_improvement?.length > 0 && (
                <div className="p-4 bg-orange-50 rounded-lg">
                  <h4 className="font-medium text-orange-800 mb-2">Areas for Improvement</h4>
                  <div className="flex flex-wrap gap-2">
                    {performance.areas_for_improvement.map((area, index) => (
                      <span key={index} className="px-2 py-1 bg-orange-100 text-orange-700 rounded-md text-sm">
                        {area.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        {performance.recent_activity && performance.recent_activity.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Recent Activity</h2>
            <div className="space-y-3">
              {performance.recent_activity.slice(0, 5).map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-800">{activity.description}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(activity.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                  {activity.score && (
                    <span className="text-blue-600 font-medium">{activity.score}%</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Personalized Recommendations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.map((recommendation, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
                  <div className="flex items-start">
                    <div className={`w-3 h-3 rounded-full mt-1 mr-3 ${
                      recommendation.priority === 'high' ? 'bg-red-500' :
                      recommendation.priority === 'medium' ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}></div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">{recommendation.title}</h4>
                      <p className="text-sm text-gray-600 mb-2">{recommendation.description}</p>
                      <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                        recommendation.priority === 'high' ? 'bg-red-100 text-red-700' :
                        recommendation.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {recommendation.priority} priority
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LearningAnalyticsDashboard;