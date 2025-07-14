import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocation, useNavigate } from 'react-router-dom';
import StarLogo from './StarLogo';
import { 
  RocketLaunchIcon,
  UserGroupIcon,
  BookOpenIcon,
  TrophyIcon,
  ChartBarIcon,
  StarIcon,
  ExclamationTriangleIcon,
  MapIcon,
  ChatBubbleLeftRightIcon,
  InformationCircleIcon,
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
  BellIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const navigationItems = [
    { name: 'Mission Control', icon: RocketLaunchIcon, path: '/dashboard', color: '#ff6b6b' },
    { name: 'SkillScan™', icon: BookOpenIcon, path: '/skillscan', color: '#4ecdc4' },
    { name: 'StarMentor™', icon: ChatBubbleLeftRightIcon, path: '/starmentor', color: '#45b7d1' },
    { name: 'Galaxy Quests', icon: MapIcon, path: '/galaxy-quests', color: '#96ceb4' },
    { name: 'Learning Pods', icon: UserGroupIcon, path: '/learning-pods', color: '#ffd93d' },
    { name: 'Trajectory', icon: ChartBarIcon, path: '/trajectory', color: '#ff9ff3' },
    { name: 'StarRankings', icon: TrophyIcon, path: '/starrankings', color: '#f9ca24' },
    { name: 'StarBadges™', icon: StarIcon, path: '/starbadges', color: '#6c5ce7' },
    { name: 'SOS Station', icon: ExclamationTriangleIcon, path: '/sos-station', color: '#fd79a8' },
    { name: 'Mission Intel', icon: InformationCircleIcon, path: '/mission-intel', color: '#00b894' },
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="starguide-container">
      {/* Header */}
      <header className="starguide-header">
        <div className="flex items-center">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-800 transition-colors"
          >
            {sidebarOpen ? <XMarkIcon className="w-6 h-6" /> : <Bars3Icon className="w-6 h-6" />}
          </button>
          
          <StarLogo size={40} className="mr-3" />
          <div>
            <h1 className="text-xl font-bold text-white">StarGuide</h1>
            <p className="text-xs text-gray-400">powered by IDFS PathwayIQ™</p>
          </div>
        </div>

        <div className="flex-1 max-w-md mx-8 hidden md:block">
          <div className="relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search lessons, quests, or mentors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500"
            />
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button className="p-2 rounded-lg hover:bg-gray-800 transition-colors">
            <BellIcon className="w-6 h-6 text-gray-400" />
          </button>
          
          <div className="flex items-center space-x-3">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium text-white">{user?.username}</p>
              <p className="text-xs text-gray-400">Level {user?.level} • {user?.xp} XP</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg hover:bg-gray-800 transition-colors text-gray-400 hover:text-white"
            >
              <ArrowRightOnRectangleIcon className="w-6 h-6" />
            </button>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside className={`starguide-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <nav className="py-4">
          {navigationItems.map((item) => (
            <button
              key={item.name}
              onClick={() => {
                navigate(item.path);
                setSidebarOpen(false);
              }}
              className={`nav-item w-full text-left ${isActive(item.path) ? 'active' : ''}`}
            >
              <item.icon 
                className="nav-item-icon" 
                style={{ color: isActive(item.path) ? item.color : '#888' }}
              />
              <span>{item.name}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="starguide-content">
        {children}
      </main>

      {/* Right Sidebar */}
      <aside className="starguide-right-sidebar hidden lg:block">
        <div className="p-6">
          {/* User Stats */}
          <div className="starguide-card mb-6">
            <h3 className="text-lg font-semibold mb-4 text-white">Your Progress</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Level Progress</span>
                  <span className="text-white">{user?.xp % 100}/100 XP</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${(user?.xp % 100)}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-white">{user?.level}</p>
                  <p className="text-xs text-gray-400">Level</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-500">{user?.xp}</p>
                  <p className="text-xs text-gray-400">Total XP</p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="starguide-card mb-6">
            <h3 className="text-lg font-semibold mb-4 text-white">Quick Actions</h3>
            <div className="space-y-2">
              <button 
                onClick={() => navigate('/galaxy-quests')}
                className="w-full text-left p-3 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center">
                  <MapIcon className="w-5 h-5 mr-3 text-green-500" />
                  <span className="text-white">Find Battle</span>
                </div>
              </button>
              <button 
                onClick={() => navigate('/learning-pods')}
                className="w-full text-left p-3 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center">
                  <UserGroupIcon className="w-5 h-5 mr-3 text-blue-500" />
                  <span className="text-white">Create Private Quest</span>
                </div>
              </button>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="starguide-card">
            <h3 className="text-lg font-semibold mb-4 text-white">Recent Activity</h3>
            <div className="space-y-3">
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-gray-300">Completed JavaScript Quest</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                <span className="text-gray-300">Joined Python Learning Pod</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
                <span className="text-gray-300">Earned Badge: Code Warrior</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default Layout;