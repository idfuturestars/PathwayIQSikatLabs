import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

const PredictiveAnalyticsPage = () => {
  const { user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('outcomes');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // State for different prediction types
  const [learningOutcomes, setLearningOutcomes] = useState(null);
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [skillMastery, setSkillMastery] = useState(null);
  const [studentSuccess, setStudentSuccess] = useState(null);
  const [learningPath, setLearningPath] = useState(null);

  // Form states
  const [predictionHorizon, setPredictionHorizon] = useState(30);
  const [selectedSkills, setSelectedSkills] = useState(['mathematics', 'reading', 'science']);
  const [learningGoals, setLearningGoals] = useState(['improve_math_skills', 'master_reading_comprehension']);
  const [timeConstraint, setTimeConstraint] = useState('');

  useEffect(() => {
    // Load initial predictions based on active tab
    if (activeTab === 'outcomes') {
      fetchLearningOutcomes();
    } else if (activeTab === 'risk') {
      fetchRiskAssessment();
    } else if (activeTab === 'success') {
      fetchStudentSuccess();
    }
  }, [activeTab]);

  const fetchLearningOutcomes = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/predictive/learning-outcomes?prediction_horizon=${predictionHorizon}`,
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
        setLearningOutcomes(data.predictions);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch learning outcomes');
      }
    } catch (err) {
      setError('Network error occurred while fetching predictions');
      console.error('Learning outcomes error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRiskAssessment = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/predictive/risk-assessment`,
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
        setRiskAssessment(data.risk_assessment);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch risk assessment');
      }
    } catch (err) {
      setError('Network error occurred while fetching risk assessment');
      console.error('Risk assessment error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSkillMastery = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/predictive/skill-mastery`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(selectedSkills)
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSkillMastery(data.skill_mastery_predictions);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch skill mastery predictions');
      }
    } catch (err) {
      setError('Network error occurred while fetching skill mastery predictions');
      console.error('Skill mastery error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudentSuccess = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/predictive/student-success`,
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
        setStudentSuccess(data.success_prediction);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch student success prediction');
      }
    } catch (err) {
      setError('Network error occurred while fetching success prediction');
      console.error('Student success error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateLearningPath = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const requestBody = {
        learning_goals: learningGoals,
        time_constraint: timeConstraint ? parseInt(timeConstraint) : null
      };
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/predictive/learning-path`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        }
      );

      if (response.ok) {
        const data = await response.json();
        setLearningPath(data.optimized_learning_path);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to generate learning path');
      }
    } catch (err) {
      setError('Network error occurred while generating learning path');
      console.error('Learning path error:', err);
    } finally {
      setLoading(false);
    }
  };

  const PredictionCard = ({ title, children }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      {children}
    </div>
  );

  const MetricDisplay = ({ label, value, color = "blue" }) => (
    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
      <span className="text-gray-700 font-medium">{label}</span>
      <span className={`text-${color}-600 font-semibold`}>{value}</span>
    </div>
  );

  const ProgressBar = ({ percentage, color = "blue" }) => (
    <div className="w-full bg-gray-200 rounded-full h-3">
      <div 
        className={`bg-${color}-500 h-3 rounded-full transition-all duration-300`}
        style={{ width: `${Math.min(Math.max(percentage, 0), 100)}%` }}
      ></div>
    </div>
  );

  const RiskIndicator = ({ level }) => {
    const colors = {
      low: "bg-green-100 text-green-800",
      medium: "bg-yellow-100 text-yellow-800", 
      high: "bg-red-100 text-red-800",
      critical: "bg-red-200 text-red-900"
    };
    
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors[level] || colors.low}`}>
        {level.charAt(0).toUpperCase() + level.slice(1)} Risk
      </span>
    );
  };

  if (loading && !learningOutcomes && !riskAssessment && !studentSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Analyzing your learning data...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Predictive Analytics
          </h1>
          <p className="text-gray-600">
            AI-powered insights into your learning journey and future performance.
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="flex space-x-8 border-b border-gray-200">
            {[
              { id: 'outcomes', label: 'Learning Outcomes' },
              { id: 'risk', label: 'Risk Assessment' },
              { id: 'skills', label: 'Skill Mastery' },
              { id: 'path', label: 'Learning Path' },
              { id: 'success', label: 'Success Prediction' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={() => {
                setError(null);
                if (activeTab === 'outcomes') fetchLearningOutcomes();
                else if (activeTab === 'risk') fetchRiskAssessment();
                else if (activeTab === 'success') fetchStudentSuccess();
              }}
              className="mt-2 text-red-600 hover:text-red-800 font-medium text-sm"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Learning Outcomes Tab */}
        {activeTab === 'outcomes' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-gray-200">
              <label className="text-sm font-medium text-gray-700">
                Prediction Horizon (days):
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="range"
                  min="7"
                  max="365"
                  value={predictionHorizon}
                  onChange={(e) => setPredictionHorizon(e.target.value)}
                  className="w-32"
                />
                <span className="text-sm text-gray-600 w-12">{predictionHorizon}d</span>
                <button
                  onClick={fetchLearningOutcomes}
                  disabled={loading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  Update
                </button>
              </div>
            </div>

            {learningOutcomes && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PredictionCard title="Performance Prediction">
                  <div className="space-y-3">
                    <MetricDisplay 
                      label="Overall Score" 
                      value={`${(learningOutcomes.predicted_performance?.overall_score * 100)?.toFixed(1) || 0}%`}
                      color="blue"
                    />
                    {learningOutcomes.predicted_performance?.skill_specific_scores && 
                      Object.entries(learningOutcomes.predicted_performance.skill_specific_scores).map(([skill, score]) => (
                        <div key={skill} className="space-y-1">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600 capitalize">{skill.replace('_', ' ')}</span>
                            <span className="text-sm font-medium">{(score * 100).toFixed(1)}%</span>
                          </div>
                          <ProgressBar percentage={score * 100} />
                        </div>
                      ))
                    }
                  </div>
                </PredictionCard>

                <PredictionCard title="Engagement Prediction">
                  <div className="space-y-3">
                    <MetricDisplay 
                      label="Activity Level" 
                      value={`${(learningOutcomes.engagement_prediction?.activity_level * 100)?.toFixed(0) || 0}%`}
                      color="green"
                    />
                    <MetricDisplay 
                      label="Session Frequency" 
                      value={`${learningOutcomes.engagement_prediction?.session_frequency || 0}/week`}
                      color="green"
                    />
                    <MetricDisplay 
                      label="Retention Probability" 
                      value={`${(learningOutcomes.engagement_prediction?.retention_probability * 100)?.toFixed(1) || 0}%`}
                      color="green"
                    />
                  </div>
                </PredictionCard>

                {learningOutcomes.learning_trajectory?.expected_level_progression && (
                  <PredictionCard title="Level Progression">
                    <div className="space-y-3">
                      {learningOutcomes.learning_trajectory.expected_level_progression.map((progression, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-gray-700">Day {progression.day}</span>
                          <div className="text-right">
                            <div className="font-semibold text-purple-600">Level {progression.predicted_level}</div>
                            <div className="text-xs text-gray-500">{(progression.confidence * 100).toFixed(0)}% confidence</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </PredictionCard>
                )}

                {learningOutcomes.recommendations && (
                  <PredictionCard title="AI Recommendations">
                    <div className="space-y-3">
                      {learningOutcomes.recommendations.map((rec, index) => (
                        <div key={index} className="p-3 border border-gray-200 rounded-lg">
                          <div className="flex items-start">
                            <div className={`w-3 h-3 rounded-full mt-1 mr-3 ${
                              rec.priority === 'high' ? 'bg-red-500' : 
                              rec.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                            }`}></div>
                            <div>
                              <h4 className="font-medium text-gray-800">{rec.title}</h4>
                              <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </PredictionCard>
                )}
              </div>
            )}
          </div>
        )}

        {/* Risk Assessment Tab */}
        {activeTab === 'risk' && (
          <div className="space-y-6">
            {riskAssessment && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PredictionCard title="Risk Overview">
                  <div className="space-y-4">
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <div className="text-3xl font-bold text-gray-800 mb-2">
                        {riskAssessment.risk_score}/100
                      </div>
                      <RiskIndicator level={riskAssessment.overall_risk_level} />
                    </div>
                    
                    {riskAssessment.early_warning_indicators && (
                      <div className="space-y-2">
                        <h4 className="font-medium text-gray-800">Warning Indicators</h4>
                        {Object.entries(riskAssessment.early_warning_indicators).map(([indicator, value]) => (
                          <div key={indicator} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span className="text-sm text-gray-600 capitalize">
                              {indicator.replace('_', ' ')}
                            </span>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              value ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                            }`}>
                              {value ? 'At Risk' : 'Stable'}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </PredictionCard>

                {riskAssessment.intervention_recommendations && (
                  <PredictionCard title="Intervention Recommendations">
                    <div className="space-y-3">
                      {riskAssessment.intervention_recommendations.map((intervention, index) => (
                        <div key={index} className="p-3 border border-gray-200 rounded-lg">
                          <div className="flex items-center mb-2">
                            <span className={`px-2 py-1 rounded text-xs font-medium mr-2 ${
                              intervention.urgency === 'high' ? 'bg-red-100 text-red-700' :
                              intervention.urgency === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              {intervention.urgency}
                            </span>
                            <h4 className="font-medium text-gray-800">{intervention.title}</h4>
                          </div>
                          <p className="text-sm text-gray-600">{intervention.description}</p>
                        </div>
                      ))}
                    </div>
                  </PredictionCard>
                )}

                {riskAssessment.protective_factors && (
                  <PredictionCard title="Protective Factors">
                    <div className="space-y-2">
                      {riskAssessment.protective_factors.map((factor, index) => (
                        <div key={index} className="flex items-center p-2 bg-green-50 rounded-lg">
                          <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          <span className="text-sm text-gray-700 capitalize">{factor.replace('_', ' ')}</span>
                        </div>
                      ))}
                    </div>
                  </PredictionCard>
                )}
              </div>
            )}
          </div>
        )}

        {/* Skills Mastery Tab */}
        {activeTab === 'skills' && (
          <div className="space-y-6">
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Select Skills to Analyze</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                {['mathematics', 'reading', 'science', 'writing', 'critical_thinking', 'problem_solving'].map(skill => (
                  <label key={skill} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedSkills.includes(skill)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedSkills([...selectedSkills, skill]);
                        } else {
                          setSelectedSkills(selectedSkills.filter(s => s !== skill));
                        }
                      }}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700 capitalize">{skill.replace('_', ' ')}</span>
                  </label>
                ))}
              </div>
              <button
                onClick={fetchSkillMastery}
                disabled={loading || selectedSkills.length === 0}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                Analyze Skill Mastery
              </button>
            </div>

            {skillMastery && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Object.entries(skillMastery).map(([skill, prediction]) => (
                  <PredictionCard key={skill} title={skill.charAt(0).toUpperCase() + skill.slice(1).replace('_', ' ')}>
                    <div className="space-y-3">
                      <MetricDisplay 
                        label="Current Mastery" 
                        value={`${(prediction.current_mastery_level * 100).toFixed(1)}%`}
                        color="blue"
                      />
                      <MetricDisplay 
                        label="Predicted Mastery Date" 
                        value={new Date(prediction.predicted_mastery_date).toLocaleDateString()}
                        color="green"
                      />
                      <MetricDisplay 
                        label="Required Practice Sessions" 
                        value={prediction.required_practice_sessions}
                        color="orange"
                      />
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-600">Confidence Level</span>
                        <ProgressBar percentage={prediction.confidence_level * 100} color="purple" />
                      </div>
                    </div>
                  </PredictionCard>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Learning Path Tab */}
        {activeTab === 'path' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Generate Optimized Learning Path</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Learning Goals</label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {['improve_math_skills', 'master_reading_comprehension', 'develop_critical_thinking', 'enhance_problem_solving', 'strengthen_science_foundation', 'advance_writing_skills'].map(goal => (
                      <label key={goal} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={learningGoals.includes(goal)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setLearningGoals([...learningGoals, goal]);
                            } else {
                              setLearningGoals(learningGoals.filter(g => g !== goal));
                            }
                          }}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700 capitalize">{goal.replace('_', ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Time Constraint (days) - Optional
                  </label>
                  <input
                    type="number"
                    value={timeConstraint}
                    onChange={(e) => setTimeConstraint(e.target.value)}
                    placeholder="e.g., 90"
                    className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <button
                  onClick={generateLearningPath}
                  disabled={loading || learningGoals.length === 0}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Generating...' : 'Generate Learning Path'}
                </button>
              </div>
            </div>

            {learningPath && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PredictionCard title="Path Overview">
                  <div className="space-y-3">
                    <MetricDisplay 
                      label="Estimated Completion Time" 
                      value={`${learningPath.estimated_completion_time} days`}
                      color="blue"
                    />
                    <MetricDisplay 
                      label="Success Probability" 
                      value={`${(learningPath.success_probability * 100).toFixed(1)}%`}
                      color="green"
                    />
                    {learningPath.optimization_factors && (
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Optimization Factors</h4>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div>Learning Style: {learningPath.optimization_factors.user_learning_style}</div>
                          <div>Optimal Session Length: {learningPath.optimization_factors.optimal_session_length} min</div>
                          <div>Learning Velocity: {learningPath.optimization_factors.learning_velocity}x</div>
                        </div>
                      </div>
                    )}
                  </div>
                </PredictionCard>

                {learningPath.personalized_sequence && learningPath.personalized_sequence.length > 0 && (
                  <PredictionCard title="Learning Sequence">
                    <div className="space-y-3">
                      {learningPath.personalized_sequence.map((step, index) => (
                        <div key={index} className="p-3 border border-gray-200 rounded-lg">
                          <div className="flex items-center mb-2">
                            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full mr-2">
                              Step {index + 1}
                            </span>
                            <h4 className="font-medium text-gray-800">{step.title || `Goal ${index + 1}`}</h4>
                          </div>
                          <p className="text-sm text-gray-600">{step.description || 'Personalized learning activities'}</p>
                          {step.estimated_time && (
                            <div className="mt-2 text-xs text-gray-500">
                              Estimated time: {step.estimated_time} days
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </PredictionCard>
                )}
              </div>
            )}
          </div>
        )}

        {/* Success Prediction Tab */}
        {activeTab === 'success' && (
          <div className="space-y-6">
            {studentSuccess && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PredictionCard title="Success Probability">
                  <div className="text-center p-6">
                    <div className="text-4xl font-bold text-green-600 mb-4">
                      {(studentSuccess.success_probability * 100).toFixed(1)}%
                    </div>
                    <div className="text-gray-600 mb-4">Probability of Academic Success</div>
                    <ProgressBar percentage={studentSuccess.success_probability * 100} color="green" />
                  </div>
                </PredictionCard>

                {studentSuccess.success_factors && (
                  <PredictionCard title="Success Factors">
                    <div className="space-y-3">
                      {Object.entries(studentSuccess.success_factors).map(([factor, score]) => (
                        <div key={factor} className="space-y-1">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600 capitalize">
                              {factor.replace('_', ' ')}
                            </span>
                            <span className="text-sm font-medium">{(score * 100).toFixed(0)}%</span>
                          </div>
                          <ProgressBar percentage={score * 100} />
                        </div>
                      ))}
                    </div>
                  </PredictionCard>
                )}

                {studentSuccess.risk_mitigation_strategies && (
                  <PredictionCard title="Success Strategies">
                    <div className="space-y-3">
                      {studentSuccess.risk_mitigation_strategies.map((strategy, index) => (
                        <div key={index} className="p-3 border border-gray-200 rounded-lg">
                          <h4 className="font-medium text-gray-800 mb-1">{strategy.title}</h4>
                          <p className="text-sm text-gray-600">{strategy.description}</p>
                        </div>
                      ))}
                    </div>
                  </PredictionCard>
                )}

                {studentSuccess.confidence_metrics && (
                  <PredictionCard title="Prediction Confidence">
                    <div className="space-y-3">
                      <MetricDisplay 
                        label="Prediction Confidence" 
                        value={`${(studentSuccess.confidence_metrics.prediction_confidence * 100).toFixed(1)}%`}
                        color="purple"
                      />
                      <MetricDisplay 
                        label="Data Completeness" 
                        value={`${(studentSuccess.confidence_metrics.data_completeness * 100).toFixed(1)}%`}
                        color="purple"
                      />
                      <MetricDisplay 
                        label="Model Reliability" 
                        value={`${(studentSuccess.confidence_metrics.model_reliability * 100).toFixed(1)}%`}
                        color="purple"
                      />
                    </div>
                  </PredictionCard>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictiveAnalyticsPage;