import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  RocketLaunchIcon,
  TrophyIcon,
  UserGroupIcon,
  BookOpenIcon,
  ChartBarIcon,
  StarIcon,
  FireIcon,
  LightBulbIcon,
  PlayIcon,
  PlusIcon
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/dashboard`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Start Learning',
      description: 'Begin a new quest or continue where you left off',
      icon: PlayIcon,
      color: 'bg-green-500',
      action: () => navigate('/galaxy-quests'),
    },
    {
      title: 'Take Assessment',
      description: 'Test your knowledge with SkillScan™',
      icon: LightBulbIcon,
      color: 'bg-blue-500',
      action: () => navigate('/skillscan'),
    },
    {
      title: 'Join Study Group',
      description: 'Collaborate with fellow learners',
      icon: UserGroupIcon,
      color: 'bg-purple-500',
      action: () => navigate('/learning-pods'),
    },
    {
      title: 'Ask StarMentor™',
      description: 'Get AI-powered tutoring assistance',
      icon: StarIcon,
      color: 'bg-yellow-500',
      action: () => navigate('/starmentor'),
    },
  ];

  const achievements = [
    { name: 'First Steps', icon: '🚀', rarity: 'common', earned: true },
    { name: 'Quick Learner', icon: '⚡', rarity: 'rare', earned: true },
    { name: 'Team Player', icon: '🤝', rarity: 'epic', earned: false },
    { name: 'Master Scholar', icon: '👑', rarity: 'legendary', earned: false },
  ];

  const recentActivities = [
    { type: 'quest', title: 'Completed JavaScript Basics', time: '2 hours ago', xp: 50 },
    { type: 'badge', title: 'Earned "Code Warrior" badge', time: '1 day ago', xp: 100 },
    { type: 'group', title: 'Joined Python Study Group', time: '2 days ago', xp: 25 },
    { type: 'mentor', title: 'Asked StarMentor about algorithms', time: '3 days ago', xp: 10 },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner w-8 h-8"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded-xl p-8 border border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Welcome back, {user?.username}!
            </h1>
            <p className="text-gray-300 text-lg">
              Ready to continue your learning journey?
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-4">
              <div className="text-center">
                <p className="text-3xl font-bold text-green-500">{user?.level}</p>
                <p className="text-sm text-gray-400">Level</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-500">{user?.xp}</p>
                <p className="text-sm text-gray-400">XP</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-yellow-500">{analytics?.user_stats?.study_groups || 0}</p>
                <p className="text-sm text-gray-400">Groups</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-400">Progress to Level {user?.level + 1}</span>
            <span className="text-white">{user?.xp % 100}/100 XP</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(user?.xp % 100)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={action.action}
              className="starguide-card hover:bg-gray-800 transition-all duration-200 transform hover:scale-105 cursor-pointer group"
            >
              <div className="flex items-center mb-4">
                <div className={`p-3 rounded-lg ${action.color} group-hover:scale-110 transition-transform`}>
                  <action.icon className="w-6 h-6 text-white" />
                </div>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{action.title}</h3>
              <p className="text-gray-400 text-sm">{action.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Stats Overview */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Your Progress</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="starguide-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400">Questions Answered</p>
                <p className="text-3xl font-bold text-white">{analytics?.user_stats?.total_questions || 0}</p>
              </div>
              <BookOpenIcon className="w-12 h-12 text-blue-500" />
            </div>
            <div className="mt-4">
              <div className="flex items-center text-sm">
                <span className="text-green-500">↗ {analytics?.user_stats?.accuracy_rate || 0}%</span>
                <span className="text-gray-400 ml-2">accuracy rate</span>
              </div>
            </div>
          </div>

          <div className="starguide-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400">Study Time</p>
                <p className="text-3xl font-bold text-white">{analytics?.user_stats?.total_study_time || 0}h</p>
              </div>
              <ChartBarIcon className="w-12 h-12 text-purple-500" />
            </div>
            <div className="mt-4">
              <div className="flex items-center text-sm">
                <FireIcon className="w-4 h-4 text-orange-500 mr-1" />
                <span className="text-gray-400">{user?.streak_days || 0} day streak</span>
              </div>
            </div>
          </div>

          <div className="starguide-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400">Badges Earned</p>
                <p className="text-3xl font-bold text-white">{analytics?.user_stats?.badges_earned || 0}</p>
              </div>
              <TrophyIcon className="w-12 h-12 text-yellow-500" />
            </div>
            <div className="mt-4">
              <button 
                onClick={() => navigate('/starbadges')}
                className="text-sm text-green-500 hover:text-green-400"
              >
                View all badges →
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Achievements */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Recent Achievements</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {achievements.map((achievement, index) => (
            <div
              key={index}
              className={`starguide-card text-center ${
                achievement.earned ? 'border-green-500/30' : 'opacity-50'
              }`}
            >
              <div className="text-4xl mb-2">{achievement.icon}</div>
              <h3 className="text-sm font-semibold text-white mb-1">{achievement.name}</h3>
              <span className={`badge ${
                achievement.rarity === 'legendary' ? 'badge-warning' :
                achievement.rarity === 'epic' ? 'badge-info' :
                achievement.rarity === 'rare' ? 'badge-success' : 'text-gray-400'
              }`}>
                {achievement.rarity}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Recent Activity</h2>
        <div className="starguide-card">
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 ${
                    activity.type === 'quest' ? 'bg-green-500' :
                    activity.type === 'badge' ? 'bg-yellow-500' :
                    activity.type === 'group' ? 'bg-blue-500' : 'bg-purple-500'
                  }`}></div>
                  <div>
                    <p className="text-white font-medium">{activity.title}</p>
                    <p className="text-gray-400 text-sm">{activity.time}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-green-500 font-semibold">+{activity.xp} XP</span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center">
            <button 
              onClick={() => navigate('/trajectory')}
              className="btn-secondary"
            >
              View Full History
            </button>
          </div>
        </div>
      </div>

      {/* Recommended Actions */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Recommended for You</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="starguide-card">
            <h3 className="text-lg font-semibold text-white mb-4">Continue Learning</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                <span className="text-gray-300">JavaScript Advanced Concepts</span>
                <button className="btn-primary text-sm px-3 py-1">Continue</button>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                <span className="text-gray-300">React Hooks Deep Dive</span>
                <button className="btn-secondary text-sm px-3 py-1">Start</button>
              </div>
            </div>
          </div>

          <div className="starguide-card">
            <h3 className="text-lg font-semibold text-white mb-4">Join Study Groups</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                <div>
                  <p className="text-gray-300">Python Beginners</p>
                  <p className="text-gray-500 text-sm">24 members</p>
                </div>
                <button className="btn-primary text-sm px-3 py-1">Join</button>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                <div>
                  <p className="text-gray-300">Web Development</p>
                  <p className="text-gray-500 text-sm">156 members</p>
                </div>
                <button className="btn-secondary text-sm px-3 py-1">Join</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;