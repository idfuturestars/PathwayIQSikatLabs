import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const StudyGroups = ({ onGroupActivity }) => {
  const [studyGroups, setStudyGroups] = useState([]);
  const [userGroups, setUserGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [groupActivity, setGroupActivity] = useState({});
  const { user } = useAuth();

  const [createGroupForm, setCreateGroupForm] = useState({
    name: '',
    description: '',
    subject: '',
    max_members: 20,
    is_private: false
  });

  const subjects = [
    'Mathematics', 'Science', 'English', 'History', 'Geography', 
    'Physics', 'Chemistry', 'Biology', 'Computer Science', 'Art'
  ];

  useEffect(() => {
    fetchUserStudyGroups();
  }, []);

  const fetchUserStudyGroups = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/study-groups/user`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserGroups(data.study_groups || []);
      }
    } catch (error) {
      console.error('Error fetching user study groups:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGroupActivity = async (groupId) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/study-groups/${groupId}/activity`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setGroupActivity(prev => ({
          ...prev,
          [groupId]: data
        }));
      }
    } catch (error) {
      console.error('Error fetching group activity:', error);
    }
  };

  const createStudyGroup = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/study-groups`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(createGroupForm)
      });
      
      if (response.ok) {
        await fetchUserStudyGroups();
        setShowCreateForm(false);
        setCreateGroupForm({
          name: '',
          description: '',
          subject: '',
          max_members: 20,
          is_private: false
        });
        showNotification('Study group created successfully!', 'success');
      }
    } catch (error) {
      console.error('Error creating study group:', error);
      showNotification('Failed to create study group', 'error');
    }
  };

  const joinStudyGroup = async (groupId) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/study-groups/${groupId}/join`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        await fetchUserStudyGroups();
        showNotification('Successfully joined study group!', 'success');
      }
    } catch (error) {
      console.error('Error joining study group:', error);
      showNotification('Failed to join study group', 'error');
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

  const getRoleIcon = (role) => {
    switch (role) {
      case 'leader': return '👑';
      case 'moderator': return '🛡️';
      case 'member': return '👤';
      default: return '👥';
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'leader': return 'text-yellow-400';
      case 'moderator': return 'text-blue-400';
      case 'member': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="study-groups bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-center py-8">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="study-groups bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Study Groups</h3>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200"
        >
          {showCreateForm ? 'Cancel' : 'Create Group'}
        </button>
      </div>

      {/* Create Group Form */}
      {showCreateForm && (
        <div className="mb-6 bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Create New Study Group</h4>
          <form onSubmit={createStudyGroup} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Group Name</label>
              <input
                type="text"
                value={createGroupForm.name}
                onChange={(e) => setCreateGroupForm({...createGroupForm, name: e.target.value})}
                className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
              <textarea
                value={createGroupForm.description}
                onChange={(e) => setCreateGroupForm({...createGroupForm, description: e.target.value})}
                className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
                required
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Subject</label>
                <select
                  value={createGroupForm.subject}
                  onChange={(e) => setCreateGroupForm({...createGroupForm, subject: e.target.value})}
                  className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select a subject</option>
                  {subjects.map(subject => (
                    <option key={subject} value={subject}>{subject}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Max Members</label>
                <input
                  type="number"
                  value={createGroupForm.max_members}
                  onChange={(e) => setCreateGroupForm({...createGroupForm, max_members: parseInt(e.target.value)})}
                  className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="2"
                  max="50"
                />
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="private"
                checked={createGroupForm.is_private}
                onChange={(e) => setCreateGroupForm({...createGroupForm, is_private: e.target.checked})}
                className="w-4 h-4 text-blue-600 bg-gray-600 border-gray-500 rounded focus:ring-blue-500"
              />
              <label htmlFor="private" className="text-sm text-gray-300">Private Group</label>
            </div>
            
            <button
              type="submit"
              className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors duration-200"
            >
              Create Study Group
            </button>
          </form>
        </div>
      )}

      {/* User's Study Groups */}
      {userGroups.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Your Study Groups</h4>
          <div className="space-y-3">
            {userGroups.map(group => (
              <div key={group.group_id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <h5 className="text-white font-medium">{group.name}</h5>
                      <span className={`text-sm ${getRoleColor(group.role)}`}>
                        {getRoleIcon(group.role)} {group.role}
                      </span>
                    </div>
                    <div className="text-gray-400 text-sm">{group.member_count} members</div>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedGroup(selectedGroup === group.group_id ? null : group.group_id);
                      if (selectedGroup !== group.group_id) {
                        fetchGroupActivity(group.group_id);
                      }
                    }}
                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors duration-200"
                  >
                    {selectedGroup === group.group_id ? 'Hide' : 'View'}
                  </button>
                </div>
                
                {/* Group Activity */}
                {selectedGroup === group.group_id && groupActivity[group.group_id] && (
                  <div className="mt-4 pt-4 border-t border-gray-600">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400">
                          {groupActivity[group.group_id].member_count || 0}
                        </div>
                        <div className="text-xs text-gray-400">Members</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">85%</div>
                        <div className="text-xs text-gray-400">Avg Score</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400">42</div>
                        <div className="text-xs text-gray-400">Sessions</div>
                      </div>
                    </div>
                    
                    <div className="mt-4">
                      <h6 className="text-sm font-medium text-gray-300 mb-2">Recent Activity</h6>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-sm">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="text-gray-400">Math study session completed</span>
                          <span className="text-gray-500">2 hours ago</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <span className="text-gray-400">New member joined</span>
                          <span className="text-gray-500">1 day ago</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                          <span className="text-gray-400">Group challenge started</span>
                          <span className="text-gray-500">3 days ago</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Suggested Study Groups */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Suggested Study Groups</h4>
        <div className="space-y-3">
          {/* Mock suggested groups */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <h5 className="text-white font-medium">Advanced Mathematics</h5>
                  <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">Mathematics</span>
                </div>
                <div className="text-gray-400 text-sm">For students tackling calculus and beyond</div>
                <div className="text-gray-500 text-xs mt-1">15/20 members • Public</div>
              </div>
              <button
                onClick={() => joinStudyGroup('mock-group-1')}
                className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors duration-200"
              >
                Join
              </button>
            </div>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <h5 className="text-white font-medium">Science Explorers</h5>
                  <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Science</span>
                </div>
                <div className="text-gray-400 text-sm">Collaborative learning for all science subjects</div>
                <div className="text-gray-500 text-xs mt-1">8/15 members • Public</div>
              </div>
              <button
                onClick={() => joinStudyGroup('mock-group-2')}
                className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors duration-200"
              >
                Join
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Study Group Features */}
      <div className="bg-gray-700 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Study Group Features</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">📚</div>
            <div>
              <div className="text-white text-sm font-medium">Shared Resources</div>
              <div className="text-gray-400 text-xs">Access study materials together</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-2xl">💬</div>
            <div>
              <div className="text-white text-sm font-medium">Group Chat</div>
              <div className="text-gray-400 text-xs">Real-time collaboration</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-2xl">📊</div>
            <div>
              <div className="text-white text-sm font-medium">Progress Tracking</div>
              <div className="text-gray-400 text-xs">Monitor group performance</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-2xl">🎯</div>
            <div>
              <div className="text-white text-sm font-medium">Group Challenges</div>
              <div className="text-gray-400 text-xs">Competitive learning games</div>
            </div>
          </div>
        </div>
      </div>

      {/* Empty State */}
      {userGroups.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          <div className="text-6xl mb-4">👥</div>
          <div className="text-lg font-medium mb-2">No Study Groups Yet</div>
          <div className="text-sm">Create or join a study group to collaborate with peers!</div>
        </div>
      )}
    </div>
  );
};

export default StudyGroups;