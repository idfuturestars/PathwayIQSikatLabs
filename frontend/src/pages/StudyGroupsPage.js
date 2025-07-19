import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

const StudyGroupsPage = () => {
  const { user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('my-groups');
  const [userGroups, setUserGroups] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // New group creation form state
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    subject: '',
    group_type: 'study_group',
    max_members: 10,
    is_public: true,
    allow_member_invites: true,
    require_approval: false,
    enable_discussions: true,
    enable_projects: true,
    tags: [],
    learning_objectives: []
  });

  useEffect(() => {
    if (activeTab === 'my-groups') {
      fetchUserGroups();
    } else if (activeTab === 'discover') {
      searchGroups();
    }
  }, [activeTab]);

  const fetchUserGroups = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/collaboration/groups/user`,
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
        setUserGroups(data.groups || []);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch user groups');
      }
    } catch (err) {
      setError('Network error occurred while fetching groups');
      console.error('Fetch user groups error:', err);
    } finally {
      setLoading(false);
    }
  };

  const searchGroups = async (query = '') => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      let url = `${process.env.REACT_APP_BACKEND_URL}/api/collaboration/groups/search`;
      if (query) {
        url += `?name=${encodeURIComponent(query)}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.groups || []);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to search groups');
      }
    } catch (err) {
      setError('Network error occurred while searching groups');
      console.error('Search groups error:', err);
    } finally {
      setLoading(false);
    }
  };

  const createGroup = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/collaboration/groups/create`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newGroup)
        }
      );

      if (response.ok) {
        const data = await response.json();
        setShowCreateModal(false);
        setNewGroup({
          name: '', description: '', subject: '', group_type: 'study_group',
          max_members: 10, is_public: true, allow_member_invites: true,
          require_approval: false, enable_discussions: true, enable_projects: true,
          tags: [], learning_objectives: []
        });
        fetchUserGroups(); // Refresh user groups
        setError(null);
        alert('Study group created successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create group');
      }
    } catch (err) {
      setError('Network error occurred while creating group');
      console.error('Create group error:', err);
    } finally {
      setLoading(false);
    }
  };

  const joinGroup = async (groupId) => {
    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/collaboration/groups/${groupId}/join`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        alert(data.message || 'Successfully joined the group!');
        fetchUserGroups(); // Refresh user groups
        searchGroups(); // Refresh search results
      } else {
        const errorData = await response.json();
        alert(errorData.detail || 'Failed to join group');
      }
    } catch (err) {
      alert('Network error occurred while joining group');
      console.error('Join group error:', err);
    }
  };

  const GroupCard = ({ group, showJoinButton = false }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">{group.name}</h3>
          <p className="text-gray-600 mb-3">{group.description}</p>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
              </svg>
              {group.member_count || 0} members
            </span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
              </svg>
              {group.subject || 'General'}
            </span>
            {group.user_role && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                group.user_role === 'owner' ? 'bg-purple-100 text-purple-800' :
                group.user_role === 'moderator' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {group.user_role}
              </span>
            )}
          </div>
        </div>
        {showJoinButton && !group.user_is_member && (
          <button
            onClick={() => joinGroup(group.group_id)}
            className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Join Group
          </button>
        )}
      </div>
      
      {group.tags && group.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {group.tags.map((tag, index) => (
            <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-sm">
              #{tag}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="text-sm text-gray-500">
          Created {new Date(group.created_at).toLocaleDateString()}
        </div>
        <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">
          View Details →
        </button>
      </div>
    </div>
  );

  const CreateGroupModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-screen overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Create Study Group</h2>
            <button
              onClick={() => setShowCreateModal(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Group Name</label>
            <input
              type="text"
              value={newGroup.name}
              onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter group name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              value={newGroup.description}
              onChange={(e) => setNewGroup({...newGroup, description: e.target.value})}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describe the purpose and goals of your study group"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
              <input
                type="text"
                value={newGroup.subject}
                onChange={(e) => setNewGroup({...newGroup, subject: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Mathematics, Science"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Max Members</label>
              <input
                type="number"
                value={newGroup.max_members}
                onChange={(e) => setNewGroup({...newGroup, max_members: parseInt(e.target.value)})}
                min="2"
                max="50"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_public"
                checked={newGroup.is_public}
                onChange={(e) => setNewGroup({...newGroup, is_public: e.target.checked})}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="is_public" className="ml-2 text-sm text-gray-700">
                Make group publicly discoverable
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="enable_discussions"
                checked={newGroup.enable_discussions}
                onChange={(e) => setNewGroup({...newGroup, enable_discussions: e.target.checked})}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="enable_discussions" className="ml-2 text-sm text-gray-700">
                Enable group discussions
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="enable_projects"
                checked={newGroup.enable_projects}
                onChange={(e) => setNewGroup({...newGroup, enable_projects: e.target.checked})}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="enable_projects" className="ml-2 text-sm text-gray-700">
                Enable collaborative projects
              </label>
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
          <button
            onClick={() => setShowCreateModal(false)}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={createGroup}
            disabled={!newGroup.name || loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating...' : 'Create Group'}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Study Groups</h1>
              <p className="text-gray-600">
                Join collaborative learning groups or create your own study community.
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-4 sm:mt-0 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Create Group
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="flex space-x-8 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('my-groups')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'my-groups' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              My Groups ({userGroups.length})
            </button>
            <button
              onClick={() => setActiveTab('discover')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'discover' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Discover Groups
            </button>
          </div>
        </div>

        {/* Search (for Discover tab) */}
        {activeTab === 'discover' && (
          <div className="mb-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for study groups..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={() => searchGroups(searchQuery)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Search
              </button>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading groups...</p>
          </div>
        )}

        {/* Groups Grid */}
        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activeTab === 'my-groups' && userGroups.length === 0 && (
              <div className="col-span-full text-center py-12">
                <div className="text-gray-400 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Study Groups Yet</h3>
                <p className="text-gray-600 mb-4">Join your first study group or create one to get started!</p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create Your First Group
                </button>
              </div>
            )}

            {activeTab === 'my-groups' && userGroups.map(group => (
              <GroupCard key={group.group_id} group={group} />
            ))}

            {activeTab === 'discover' && searchResults.length === 0 && !loading && (
              <div className="col-span-full text-center py-12">
                <div className="text-gray-400 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Groups Found</h3>
                <p className="text-gray-600">Try searching for different topics or create your own group!</p>
              </div>
            )}

            {activeTab === 'discover' && searchResults.map(group => (
              <GroupCard key={group.group_id} group={group} showJoinButton />
            ))}
          </div>
        )}

        {/* Create Group Modal */}
        {showCreateModal && <CreateGroupModal />}
      </div>
    </div>
  );
};

export default StudyGroupsPage;