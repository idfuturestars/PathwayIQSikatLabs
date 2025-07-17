import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const Leaderboard = ({ type = 'global', subject = null }) => {
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('weekly');
  const [userRank, setUserRank] = useState(null);
  const [competitions, setCompetitions] = useState([]);
  const { user } = useAuth();

  const periods = [
    { value: 'daily', label: 'Daily', icon: '📅' },
    { value: 'weekly', label: 'Weekly', icon: '📊' },
    { value: 'monthly', label: 'Monthly', icon: '🗓️' },
    { value: 'all_time', label: 'All Time', icon: '🏆' }
  ];

  useEffect(() => {
    fetchLeaderboard();
  }, [period, type, subject]);

  useEffect(() => {
    if (type === 'global') {
      fetchCompetitions();
    }
  }, [type]);

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      let endpoint = `/api/leaderboard/${type}`;
      if (subject) {
        endpoint = `/api/leaderboard/subject/${subject}`;
      }
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}${endpoint}?period=${period}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setLeaderboardData(data.leaderboard || []);
        
        // Find user's rank
        const userPosition = data.leaderboard?.findIndex(entry => entry.user_id === user.id);
        setUserRank(userPosition >= 0 ? userPosition + 1 : null);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCompetitions = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/competitions`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCompetitions(data || []);
      }
    } catch (error) {
      console.error('Error fetching competitions:', error);
    }
  };

  const joinCompetition = async (competitionId) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/competitions/${competitionId}/join`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        // Refresh competitions
        await fetchCompetitions();
        // Show success message
        showNotification('Successfully joined competition!', 'success');
      }
    } catch (error) {
      console.error('Error joining competition:', error);
      showNotification('Failed to join competition', 'error');
    }
  };

  const showNotification = (message, type) => {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transform transition-all duration-300 ${
      type === 'success' ? 'bg-green-600' : 'bg-red-600'
    } text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return { icon: '🥇', color: 'text-yellow-400' };
    if (rank === 2) return { icon: '🥈', color: 'text-gray-400' };
    if (rank === 3) return { icon: '🥉', color: 'text-yellow-600' };
    return { icon: `#${rank}`, color: 'text-gray-400' };
  };

  const getProgressColor = (score) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="leaderboard bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-center py-8">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="leaderboard bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">
          {type === 'global' ? 'Global Leaderboard' : `${subject} Leaderboard`}
        </h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-gold-500 rounded-full"></div>
          <span className="text-sm text-gray-300">Live Rankings</span>
        </div>
      </div>

      {/* Period Selection */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {periods.map(p => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-all duration-200 ${
                period === p.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {p.icon} {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* User's Rank */}
      {userRank && (
        <div className="mb-6 bg-blue-600 bg-opacity-20 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{getRankBadge(userRank).icon}</div>
              <div>
                <div className="text-white font-medium">Your Rank</div>
                <div className="text-blue-300 text-sm">Position {userRank} of {leaderboardData.length}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-white font-bold text-lg">
                {leaderboardData.find(entry => entry.user_id === user.id)?.score || 0}
              </div>
              <div className="text-blue-300 text-sm">points</div>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard List */}
      <div className="space-y-2 mb-6">
        {leaderboardData.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-2">🏆</div>
            <div>No rankings available yet</div>
            <div className="text-sm mt-1">Complete some assessments to see rankings!</div>
          </div>
        ) : (
          leaderboardData.slice(0, 10).map((entry, index) => {
            const rank = index + 1;
            const badge = getRankBadge(rank);
            const isCurrentUser = entry.user_id === user.id;
            
            return (
              <div
                key={entry.user_id}
                className={`flex items-center justify-between p-3 rounded-lg transition-all duration-200 ${
                  isCurrentUser 
                    ? 'bg-blue-600 bg-opacity-30 border border-blue-500' 
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className={`text-lg font-bold ${badge.color}`}>
                    {badge.icon}
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium">
                        {(entry.username || entry.full_name || 'User').charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <div className="text-white font-medium">
                        {entry.username || entry.full_name || 'Anonymous'}
                        {isCurrentUser && <span className="text-blue-300 ml-2">(You)</span>}
                      </div>
                      <div className="text-gray-400 text-sm">
                        Level {entry.level || 1} • {entry.xp || 0} XP
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-white font-bold">{entry.score || 0}</div>
                    <div className="text-gray-400 text-sm">points</div>
                  </div>
                  <div className="w-16 bg-gray-600 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${getProgressColor(entry.score || 0)}`}
                      style={{ width: `${Math.min((entry.score || 0) / 100 * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Active Competitions */}
      {type === 'global' && competitions.length > 0 && (
        <div className="border-t border-gray-700 pt-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Active Competitions</h4>
          <div className="space-y-3">
            {competitions.slice(0, 3).map(competition => (
              <div key={competition.id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-white font-medium">{competition.name}</div>
                    <div className="text-gray-400 text-sm">{competition.description}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {competition.participants?.length || 0} participants
                    </div>
                  </div>
                  <button
                    onClick={() => joinCompetition(competition.id)}
                    className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors duration-200"
                  >
                    Join
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Achievement Milestones */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-yellow-400">👑</div>
          <div className="text-xs text-gray-400 mt-1">Top 10</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-400">🚀</div>
          <div className="text-xs text-gray-400 mt-1">Rising Star</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-green-400">💎</div>
          <div className="text-xs text-gray-400 mt-1">Consistent</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-purple-400">⚡</div>
          <div className="text-xs text-gray-400 mt-1">Speed Runner</div>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;