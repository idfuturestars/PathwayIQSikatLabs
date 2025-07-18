import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const BadgesAndAchievements = () => {
  const { user } = useAuth();
  const [badges, setBadges] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedBadge, setSelectedBadge] = useState(null);
  const [showNotifications, setShowNotifications] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadBadges();
    loadNotifications();
  }, []);

  const loadBadges = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${backendUrl}/api/gamification/badges/user`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      setBadges(response.data.data);
    } catch (error) {
      console.error('Error loading badges:', error);
      setError('Failed to load badges');
    } finally {
      setLoading(false);
    }
  };

  const loadNotifications = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${backendUrl}/api/gamification/notifications`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      setNotifications(response.data.notifications);
    } catch (error) {
      console.error('Error loading notifications:', error);
    }
  };

  const markNotificationsRead = async (notificationIds = null) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${backendUrl}/api/gamification/notifications/read`,
        { notification_ids: notificationIds },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      loadNotifications(); // Refresh notifications
    } catch (error) {
      console.error('Error marking notifications as read:', error);
    }
  };

  const getBadgeColor = (tier) => {
    switch (tier) {
      case 'bronze': return 'text-amber-600 bg-amber-100';
      case 'silver': return 'text-gray-600 bg-gray-100';
      case 'gold': return 'text-yellow-600 bg-yellow-100';
      case 'platinum': return 'text-purple-600 bg-purple-100';
      case 'diamond': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 75) return 'bg-blue-500';
    if (percentage >= 50) return 'bg-yellow-500';
    if (percentage >= 25) return 'bg-orange-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p className="text-lg">Loading your achievements...</p>
          </div>
        </div>
      </div>
    );
  }

  const completedBadges = badges.badges?.filter(b => b.achievement.status === 'completed') || [];
  const inProgressBadges = badges.badges?.filter(b => b.achievement.status === 'in_progress') || [];
  const lockedBadges = badges.badges?.filter(b => b.achievement.status === 'locked') || [];
  const unreadNotifications = notifications.filter(n => !n.read);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">Badges & Achievements</h1>
            <p className="text-gray-400">Track your learning progress and unlock achievements</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
              </svg>
              <span>Notifications</span>
              {unreadNotifications.length > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {unreadNotifications.length}
                </span>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900 border border-red-600 rounded-lg">
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Total Points</h3>
            <p className="text-3xl font-bold text-blue-400">{badges.total_points || 0}</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Badges Earned</h3>
            <p className="text-3xl font-bold text-green-400">{badges.completed_badges || 0}</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">In Progress</h3>
            <p className="text-3xl font-bold text-yellow-400">{inProgressBadges.length}</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Total Badges</h3>
            <p className="text-3xl font-bold text-purple-400">{badges.total_badges || 0}</p>
          </div>
        </div>

        {/* Notifications Panel */}
        {showNotifications && (
          <div className="mb-8 bg-gray-800 p-6 rounded-lg">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">Recent Notifications</h3>
              {unreadNotifications.length > 0 && (
                <button
                  onClick={() => markNotificationsRead()}
                  className="text-blue-400 hover:text-blue-300 text-sm"
                >
                  Mark all as read
                </button>
              )}
            </div>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {notifications.slice(0, 10).map((notification) => (
                <div
                  key={notification.id}
                  className={`p-3 rounded-lg border-l-4 ${
                    notification.read 
                      ? 'bg-gray-700 border-gray-600' 
                      : 'bg-blue-900 border-blue-500'
                  }`}
                >
                  <p className="text-sm">{notification.message}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(notification.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
              {notifications.length === 0 && (
                <p className="text-gray-400 text-center py-4">No notifications yet</p>
              )}
            </div>
          </div>
        )}

        {/* Completed Badges */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <span className="text-green-400 mr-2">🏆</span>
            Earned Badges ({completedBadges.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {completedBadges.map((badgeData) => (
              <div
                key={badgeData.badge.id}
                className="bg-gray-800 p-4 rounded-lg hover:bg-gray-700 transition-colors cursor-pointer"
                onClick={() => setSelectedBadge(badgeData)}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="text-3xl">{badgeData.badge.icon}</div>
                  <span className={`px-2 py-1 text-xs rounded-full ${getBadgeColor(badgeData.badge.tier)}`}>
                    {badgeData.badge.tier}
                  </span>
                </div>
                <h3 className="font-semibold text-white">{badgeData.badge.name}</h3>
                <p className="text-sm text-gray-400 mb-2">{badgeData.badge.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-green-400">✓ Completed</span>
                  <span className="text-sm text-gray-400">{badgeData.badge.points} pts</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Earned {new Date(badgeData.achievement.completed_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* In Progress Badges */}
        {inProgressBadges.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <span className="text-yellow-400 mr-2">⚡</span>
              In Progress ({inProgressBadges.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {inProgressBadges.map((badgeData) => (
                <div
                  key={badgeData.badge.id}
                  className="bg-gray-800 p-4 rounded-lg hover:bg-gray-700 transition-colors cursor-pointer"
                  onClick={() => setSelectedBadge(badgeData)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-3xl opacity-75">{badgeData.badge.icon}</div>
                    <span className={`px-2 py-1 text-xs rounded-full ${getBadgeColor(badgeData.badge.tier)}`}>
                      {badgeData.badge.tier}
                    </span>
                  </div>
                  <h3 className="font-semibold text-white">{badgeData.badge.name}</h3>
                  <p className="text-sm text-gray-400 mb-3">{badgeData.badge.description}</p>
                  
                  {/* Progress Bar */}
                  <div className="mb-2">
                    <div className="flex justify-between text-sm text-gray-400 mb-1">
                      <span>Progress</span>
                      <span>{Math.round(badgeData.achievement.progress_percentage)}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getProgressColor(badgeData.achievement.progress_percentage)}`}
                        style={{ width: `${badgeData.achievement.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-yellow-400">In Progress</span>
                    <span className="text-sm text-gray-400">{badgeData.badge.points} pts</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Locked Badges */}
        {lockedBadges.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <span className="text-gray-400 mr-2">🔒</span>
              Locked Badges ({lockedBadges.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {lockedBadges.slice(0, 9).map((badgeData) => (
                <div
                  key={badgeData.badge.id}
                  className="bg-gray-800 p-4 rounded-lg opacity-75 hover:opacity-100 transition-opacity cursor-pointer"
                  onClick={() => setSelectedBadge(badgeData)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-3xl opacity-50">{badgeData.badge.icon}</div>
                    <span className={`px-2 py-1 text-xs rounded-full ${getBadgeColor(badgeData.badge.tier)}`}>
                      {badgeData.badge.tier}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-300">{badgeData.badge.name}</h3>
                  <p className="text-sm text-gray-500 mb-2">{badgeData.badge.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">🔒 Locked</span>
                    <span className="text-sm text-gray-500">{badgeData.badge.points} pts</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Badge Detail Modal */}
        {selectedBadge && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 p-6 rounded-lg max-w-md w-full mx-4">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-3">
                  <div className="text-4xl">{selectedBadge.badge.icon}</div>
                  <div>
                    <h3 className="text-xl font-bold text-white">{selectedBadge.badge.name}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full ${getBadgeColor(selectedBadge.badge.tier)}`}>
                      {selectedBadge.badge.tier}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedBadge(null)}
                  className="text-gray-400 hover:text-white"
                >
                  ✕
                </button>
              </div>
              
              <p className="text-gray-300 mb-4">{selectedBadge.badge.description}</p>
              
              {/* Requirements */}
              <div className="mb-4">
                <h4 className="font-semibold text-white mb-2">Requirements:</h4>
                <div className="space-y-2">
                  {Object.entries(selectedBadge.badge.requirements || {}).map(([key, value]) => {
                    const progress = selectedBadge.achievement.progress[key];
                    return (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-300 capitalize">{key.replace(/_/g, ' ')}</span>
                        <span className={`${progress?.completed ? 'text-green-400' : 'text-gray-400'}`}>
                          {progress?.current || 0} / {value}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
              
              {/* Progress */}
              {selectedBadge.achievement.status === 'in_progress' && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-400 mb-1">
                    <span>Overall Progress</span>
                    <span>{Math.round(selectedBadge.achievement.progress_percentage)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressColor(selectedBadge.achievement.progress_percentage)}`}
                      style={{ width: `${selectedBadge.achievement.progress_percentage}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <span className="text-lg font-semibold text-blue-400">
                  {selectedBadge.badge.points} points
                </span>
                <span className="text-sm text-gray-400">
                  Rarity: {Math.round(selectedBadge.badge.rarity * 100)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BadgesAndAchievements;