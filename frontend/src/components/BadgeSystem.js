import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const BadgeSystem = ({ onBadgeEarned }) => {
  const [badges, setBadges] = useState([]);
  const [userBadges, setUserBadges] = useState([]);
  const [badgeProgress, setBadgeProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const { user } = useAuth();

  const categories = [
    { value: 'all', label: 'All Badges', icon: '🎯' },
    { value: 'engagement', label: 'Engagement', icon: '🔥' },
    { value: 'consistency', label: 'Consistency', icon: '⚡' },
    { value: 'excellence', label: 'Excellence', icon: '🌟' },
    { value: 'social', label: 'Social', icon: '🤝' },
    { value: 'subject_mastery', label: 'Subject Mastery', icon: '🧠' }
  ];

  const rarityColors = {
    common: 'gray',
    uncommon: 'green',
    rare: 'blue',
    epic: 'purple',
    legendary: 'yellow'
  };

  const rarityGradients = {
    common: 'from-gray-400 to-gray-600',
    uncommon: 'from-green-400 to-green-600',
    rare: 'from-blue-400 to-blue-600',
    epic: 'from-purple-400 to-purple-600',
    legendary: 'from-yellow-400 to-yellow-600'
  };

  useEffect(() => {
    fetchBadges();
    fetchUserBadges();
  }, []);

  const fetchBadges = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/badges`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBadges(data);
        
        // Fetch progress for each badge
        const progressPromises = data.map(badge => fetchBadgeProgress(badge.id));
        const progressResults = await Promise.all(progressPromises);
        
        const progressMap = {};
        progressResults.forEach((progress, index) => {
          if (progress) {
            progressMap[data[index].id] = progress;
          }
        });
        setBadgeProgress(progressMap);
      }
    } catch (error) {
      console.error('Error fetching badges:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserBadges = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/badges/user/${user.id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserBadges(data);
      }
    } catch (error) {
      console.error('Error fetching user badges:', error);
    }
  };

  const fetchBadgeProgress = async (badgeId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/badges/${badgeId}/progress`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Error fetching badge progress:', error);
    }
    return null;
  };

  const checkBadgeAwards = async (actionData) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/badges/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(actionData)
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.awarded_badges && data.awarded_badges.length > 0) {
          // Refresh user badges
          await fetchUserBadges();
          
          // Notify parent component
          if (onBadgeEarned) {
            onBadgeEarned(data.awarded_badges);
          }
          
          // Show notification
          data.awarded_badges.forEach(badge => {
            showBadgeNotification(badge);
          });
        }
      }
    } catch (error) {
      console.error('Error checking badge awards:', error);
    }
  };

  const showBadgeNotification = (badge) => {
    // Create a temporary notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-600 text-white p-4 rounded-lg shadow-lg z-50 transform transition-all duration-300';
    notification.innerHTML = `
      <div class="flex items-center space-x-3">
        <div class="text-2xl">${badge.icon || '🏆'}</div>
        <div>
          <div class="font-medium">Badge Earned!</div>
          <div class="text-sm opacity-90">${badge.name}</div>
        </div>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
      notification.remove();
    }, 5000);
  };

  const filteredBadges = badges.filter(badge => 
    selectedCategory === 'all' || badge.category === selectedCategory
  );

  const hasBadge = (badgeId) => {
    return userBadges.some(userBadge => userBadge.badge_id === badgeId);
  };

  const getBadgeProgress = (badgeId) => {
    return badgeProgress[badgeId] || { progress: 0, current_value: 0, target_value: 1 };
  };

  if (loading) {
    return (
      <div className="badge-system bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-center py-8">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="badge-system bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Badge Collection</h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-300">
            {userBadges.length} / {badges.length} earned
          </span>
          <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {categories.map(category => (
            <button
              key={category.value}
              onClick={() => setSelectedCategory(category.value)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-all duration-200 ${
                selectedCategory === category.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {category.icon} {category.label}
            </button>
          ))}
        </div>
      </div>

      {/* Badge Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredBadges.map(badge => {
          const earned = hasBadge(badge.id);
          const progress = getBadgeProgress(badge.id);
          
          return (
            <div
              key={badge.id}
              className={`relative bg-gray-700 rounded-lg p-4 border-2 transition-all duration-200 hover:scale-105 ${
                earned 
                  ? `border-${rarityColors[badge.rarity]}-500 bg-gradient-to-br ${rarityGradients[badge.rarity]} bg-opacity-20` 
                  : 'border-gray-600 hover:border-gray-500'
              }`}
            >
              {/* Badge Icon */}
              <div className="text-center mb-3">
                <div className={`text-4xl mb-2 ${earned ? '' : 'grayscale opacity-50'}`}>
                  {badge.icon}
                </div>
                <div className={`text-sm font-medium ${earned ? 'text-white' : 'text-gray-400'}`}>
                  {badge.name}
                </div>
              </div>

              {/* Badge Info */}
              <div className="text-center mb-3">
                <div className={`text-xs mb-1 ${earned ? 'text-gray-300' : 'text-gray-500'}`}>
                  {badge.description}
                </div>
                <div className={`text-xs font-medium ${earned ? 'text-yellow-400' : 'text-gray-500'}`}>
                  {badge.points} points
                </div>
              </div>

              {/* Rarity Badge */}
              <div className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-bold ${
                earned 
                  ? `bg-${rarityColors[badge.rarity]}-500 text-white` 
                  : 'bg-gray-600 text-gray-400'
              }`}>
                {badge.rarity.toUpperCase()}
              </div>

              {/* Progress Bar (for unearned badges) */}
              {!earned && progress.progress > 0 && (
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                    <span>Progress</span>
                    <span>{progress.current_value} / {progress.target_value}</span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full bg-blue-500 transition-all duration-300"
                      style={{ width: `${progress.progress * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Earned Badge Overlay */}
              {earned && (
                <div className="absolute top-2 left-2 bg-green-500 text-white rounded-full p-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Stats Summary */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-white">{userBadges.length}</div>
          <div className="text-xs text-gray-400">Total Badges</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-yellow-400">
            {userBadges.reduce((total, badge) => total + (badge.points || 0), 0)}
          </div>
          <div className="text-xs text-gray-400">Badge Points</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-purple-400">
            {userBadges.filter(b => badges.find(badge => badge.id === b.badge_id)?.rarity === 'epic').length}
          </div>
          <div className="text-xs text-gray-400">Epic Badges</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-yellow-400">
            {userBadges.filter(b => badges.find(badge => badge.id === b.badge_id)?.rarity === 'legendary').length}
          </div>
          <div className="text-xs text-gray-400">Legendary</div>
        </div>
      </div>

      {/* Expose checkBadgeAwards for parent components */}
      {React.useEffect(() => {
        window.checkBadgeAwards = checkBadgeAwards;
      }, [])}
    </div>
  );
};

export default BadgeSystem;