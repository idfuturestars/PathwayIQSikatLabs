import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const PredictiveAnalytics = ({ userId = null }) => {
  const [predictions, setPredictions] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedPrediction, setSelectedPrediction] = useState('success_probability');
  const [batchPredictions, setBatchPredictions] = useState([]);
  const { user } = useAuth();

  const targetUserId = userId || user.id;

  const predictionTypes = [
    { 
      value: 'success_probability', 
      label: 'Success Probability', 
      icon: '🎯',
      description: 'Likelihood of achieving learning goals'
    },
    { 
      value: 'completion_time', 
      label: 'Completion Time', 
      icon: '⏱️',
      description: 'Predicted time to complete objectives'
    },
    { 
      value: 'dropout_risk', 
      label: 'Dropout Risk', 
      icon: '⚠️',
      description: 'Risk of discontinuing learning'
    },
    { 
      value: 'performance_forecast', 
      label: 'Performance Forecast', 
      icon: '📈',
      description: 'Future performance predictions'
    }
  ];

  useEffect(() => {
    fetchPredictions();
  }, [targetUserId]);

  const fetchPredictions = async () => {
    setLoading(true);
    try {
      const predictionPromises = predictionTypes.map(type => 
        fetchSinglePrediction(type.value)
      );
      
      const results = await Promise.all(predictionPromises);
      
      const predictionsMap = {};
      results.forEach((result, index) => {
        if (result) {
          predictionsMap[predictionTypes[index].value] = result;
        }
      });
      
      setPredictions(predictionsMap);
    } catch (error) {
      console.error('Error fetching predictions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSinglePrediction = async (predictionType) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/analytics/predictions/${targetUserId}?prediction_type=${predictionType}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error(`Error fetching ${predictionType} prediction:`, error);
    }
    return null;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const getRiskColor = (risk) => {
    if (risk >= 0.7) return 'text-red-400';
    if (risk >= 0.4) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getRiskLabel = (risk) => {
    if (risk >= 0.7) return 'High Risk';
    if (risk >= 0.4) return 'Medium Risk';
    return 'Low Risk';
  };

  const renderSuccessProbability = () => {
    const prediction = predictions.success_probability;
    if (!prediction) return null;

    const probability = prediction.prediction?.success_probability || 0;
    const confidence = prediction.confidence || 0;

    return (
      <div className="space-y-6">
        <div className="bg-gray-700 rounded-lg p-6">
          <div className="text-center mb-6">
            <div className="text-6xl mb-2">🎯</div>
            <div className="text-3xl font-bold text-white mb-2">
              {Math.round(probability * 100)}%
            </div>
            <div className="text-gray-400">Success Probability</div>
          </div>
          
          <div className="w-full bg-gray-600 rounded-full h-4 mb-4">
            <div 
              className="bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 h-4 rounded-full transition-all duration-500"
              style={{ width: `${probability * 100}%` }}
            />
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-red-400">Low</span>
            <span className={`font-medium ${getConfidenceColor(confidence)}`}>
              {getConfidenceLabel(confidence)} Confidence
            </span>
            <span className="text-green-400">High</span>
          </div>
        </div>

        {prediction.prediction?.factors && (
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-medium mb-4">Contributing Factors</h4>
            <div className="space-y-3">
              {Object.entries(prediction.prediction.factors).map(([factor, value]) => (
                <div key={factor} className="flex items-center justify-between">
                  <span className="text-gray-300 capitalize">
                    {factor.replace('_', ' ')}
                  </span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-600 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${value * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-400">
                      {Math.round(value * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderCompletionTime = () => {
    const prediction = predictions.completion_time;
    if (!prediction) return null;

    const time = prediction.prediction?.predicted_completion_time || 0;
    const confidence = prediction.confidence || 0;

    return (
      <div className="space-y-6">
        <div className="bg-gray-700 rounded-lg p-6">
          <div className="text-center mb-6">
            <div className="text-6xl mb-2">⏱️</div>
            <div className="text-3xl font-bold text-white mb-2">
              {Math.round(time)} min
            </div>
            <div className="text-gray-400">Predicted Completion Time</div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-lg font-bold text-blue-400">
                {Math.round(time * 0.8)} min
              </div>
              <div className="text-sm text-gray-400">Optimistic</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-red-400">
                {Math.round(time * 1.2)} min
              </div>
              <div className="text-sm text-gray-400">Conservative</div>
            </div>
          </div>
          
          <div className="mt-4 text-center">
            <span className={`text-sm font-medium ${getConfidenceColor(confidence)}`}>
              {getConfidenceLabel(confidence)} Confidence
            </span>
          </div>
        </div>

        {prediction.prediction?.factors && (
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-medium mb-4">Time Factors</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Base Time</span>
                <span className="text-white">
                  {Math.round(prediction.prediction.factors.base_time)} min
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Efficiency Factor</span>
                <span className="text-white">
                  {prediction.prediction.factors.efficiency_factor?.toFixed(2)}x
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderDropoutRisk = () => {
    const prediction = predictions.dropout_risk;
    if (!prediction) return null;

    const risk = prediction.prediction?.dropout_risk || 0;
    const riskLevel = prediction.prediction?.risk_level || 'low';
    const confidence = prediction.confidence || 0;

    return (
      <div className="space-y-6">
        <div className="bg-gray-700 rounded-lg p-6">
          <div className="text-center mb-6">
            <div className="text-6xl mb-2">⚠️</div>
            <div className="text-3xl font-bold text-white mb-2">
              {Math.round(risk * 100)}%
            </div>
            <div className={`text-lg font-medium ${getRiskColor(risk)}`}>
              {getRiskLabel(risk)}
            </div>
          </div>
          
          <div className="w-full bg-gray-600 rounded-full h-4 mb-4">
            <div 
              className="bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 h-4 rounded-full transition-all duration-500"
              style={{ width: `${risk * 100}%` }}
            />
          </div>
          
          <div className="text-center">
            <span className={`text-sm font-medium ${getConfidenceColor(confidence)}`}>
              {getConfidenceLabel(confidence)} Confidence
            </span>
          </div>
        </div>

        {prediction.prediction?.risk_factors && (
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-medium mb-4">Risk Factors</h4>
            <div className="space-y-2">
              {prediction.prediction.risk_factors.map((factor, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span className="text-gray-300">{factor}</span>
                </div>
              ))}
            </div>
            
            {prediction.prediction.risk_factors.length === 0 && (
              <div className="text-center text-green-400">
                <div className="text-2xl mb-2">✅</div>
                <div>No significant risk factors detected</div>
              </div>
            )}
          </div>
        )}

        <div className="bg-green-600 bg-opacity-20 rounded-lg p-4">
          <h4 className="text-green-300 font-medium mb-2">Recommendations</h4>
          <div className="space-y-2 text-sm text-green-200">
            <div>• Maintain consistent study schedule</div>
            <div>• Engage with study groups</div>
            <div>• Use AI help when needed</div>
            <div>• Set achievable daily goals</div>
          </div>
        </div>
      </div>
    );
  };

  const renderPerformanceForecast = () => {
    const prediction = predictions.performance_forecast;
    if (!prediction) return null;

    const forecast = prediction.prediction?.performance_forecast || [];
    const trend = prediction.prediction?.trend_direction || 'stable';
    const confidence = prediction.confidence || 0;

    return (
      <div className="space-y-6">
        <div className="bg-gray-700 rounded-lg p-6">
          <div className="text-center mb-6">
            <div className="text-6xl mb-2">📈</div>
            <div className="text-xl font-bold text-white mb-2">
              Performance Forecast
            </div>
            <div className={`text-lg font-medium ${
              trend === 'improving' ? 'text-green-400' :
              trend === 'declining' ? 'text-red-400' :
              'text-yellow-400'
            }`}>
              {trend === 'improving' ? '📈 Improving' :
               trend === 'declining' ? '📉 Declining' :
               '➡️ Stable'} Trend
            </div>
          </div>
          
          <div className="text-center">
            <span className={`text-sm font-medium ${getConfidenceColor(confidence)}`}>
              {getConfidenceLabel(confidence)} Confidence
            </span>
          </div>
        </div>

        {forecast.length > 0 && (
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-medium mb-4">4-Week Forecast</h4>
            <div className="space-y-3">
              {forecast.map((week, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-gray-300">Week {week.week}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-600 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${week.predicted_performance * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-white">
                      {Math.round(week.predicted_performance * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Performance Chart</h4>
          <div className="h-32 bg-gray-600 rounded-lg flex items-center justify-center">
            <div className="text-center text-gray-400">
              <div className="text-2xl mb-1">📊</div>
              <div className="text-sm">Performance trend visualization</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderPredictionContent = () => {
    switch (selectedPrediction) {
      case 'success_probability': return renderSuccessProbability();
      case 'completion_time': return renderCompletionTime();
      case 'dropout_risk': return renderDropoutRisk();
      case 'performance_forecast': return renderPerformanceForecast();
      default: return renderSuccessProbability();
    }
  };

  if (loading) {
    return (
      <div className="predictive-analytics bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-center py-8">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="predictive-analytics bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Predictive Analytics</h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-300">AI Powered</span>
        </div>
      </div>

      {/* Prediction Type Selection */}
      <div className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {predictionTypes.map(type => (
            <button
              key={type.value}
              onClick={() => setSelectedPrediction(type.value)}
              className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
                selectedPrediction === type.value
                  ? 'border-purple-500 bg-purple-500 bg-opacity-20'
                  : 'border-gray-600 bg-gray-700 hover:border-gray-500'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{type.icon}</div>
                <div>
                  <div className="text-white font-medium">{type.label}</div>
                  <div className="text-gray-400 text-sm">{type.description}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Prediction Content */}
      {renderPredictionContent()}

      {/* AI Disclaimer */}
      <div className="mt-6 bg-blue-600 bg-opacity-20 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <div className="text-blue-400 text-lg">ℹ️</div>
          <div>
            <div className="text-blue-300 font-medium">AI Predictions</div>
            <div className="text-blue-200 text-sm">
              These predictions are based on your learning patterns and historical data. 
              They should be used as guidance and may change based on your continued progress.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictiveAnalytics;