import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const ReportingSystem = () => {
  const [reports, setReports] = useState([]);
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [reportHistory, setReportHistory] = useState([]);
  const { user } = useAuth();

  const [reportForm, setReportForm] = useState({
    report_type: 'individual_student',
    target_id: '',
    title: '',
    description: '',
    format: 'json'
  });

  const reportTypes = [
    { 
      value: 'individual_student', 
      label: 'Individual Student Report', 
      icon: '👤',
      description: 'Detailed analysis of a single student\'s performance'
    },
    { 
      value: 'class_summary', 
      label: 'Class Summary Report', 
      icon: '👥',
      description: 'Overview of entire class performance'
    },
    { 
      value: 'subject_performance', 
      label: 'Subject Performance Report', 
      icon: '📚',
      description: 'Analysis of performance in specific subjects'
    },
    { 
      value: 'engagement_report', 
      label: 'Engagement Report', 
      icon: '🎯',
      description: 'Student engagement and participation analysis'
    },
    { 
      value: 'predictive_report', 
      label: 'Predictive Analytics Report', 
      icon: '🔮',
      description: 'Future performance predictions and recommendations'
    },
    { 
      value: 'intervention_report', 
      label: 'Intervention Report', 
      icon: '🚨',
      description: 'Identification of students needing support'
    }
  ];

  const formats = [
    { value: 'json', label: 'JSON Data', icon: '📊' },
    { value: 'pdf', label: 'PDF Document', icon: '📄' },
    { value: 'csv', label: 'CSV Spreadsheet', icon: '📈' }
  ];

  useEffect(() => {
    fetchReportTemplates();
    fetchReportHistory();
  }, []);

  const fetchReportTemplates = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reports/templates`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || {});
      }
    } catch (error) {
      console.error('Error fetching report templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchReportHistory = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reports/history`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setReportHistory(data.reports || []);
      }
    } catch (error) {
      console.error('Error fetching report history:', error);
    }
  };

  const generateReport = async (e) => {
    e.preventDefault();
    setGeneratingReport(true);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(reportForm)
      });
      
      if (response.ok) {
        const report = await response.json();
        setReports([report, ...reports]);
        setShowCreateForm(false);
        setReportForm({
          report_type: 'individual_student',
          target_id: '',
          title: '',
          description: '',
          format: 'json'
        });
        showNotification('Report generated successfully!', 'success');
        await fetchReportHistory();
      } else {
        showNotification('Failed to generate report', 'error');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      showNotification('Error generating report', 'error');
    } finally {
      setGeneratingReport(false);
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

  const downloadReport = (report) => {
    const dataStr = JSON.stringify(report.data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${report.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getReportIcon = (reportType) => {
    return reportTypes.find(type => type.value === reportType)?.icon || '📊';
  };

  const getReportTypeLabel = (reportType) => {
    return reportTypes.find(type => type.value === reportType)?.label || reportType;
  };

  if (loading) {
    return (
      <div className="reporting-system bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-center py-8">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="reporting-system bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Reporting System</h3>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200"
        >
          {showCreateForm ? 'Cancel' : 'Generate Report'}
        </button>
      </div>

      {/* Create Report Form */}
      {showCreateForm && (
        <div className="mb-6 bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-medium mb-4">Generate New Report</h4>
          <form onSubmit={generateReport} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Report Type</label>
              <select
                value={reportForm.report_type}
                onChange={(e) => setReportForm({...reportForm, report_type: e.target.value})}
                className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {reportTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              <div className="text-xs text-gray-400 mt-1">
                {reportTypes.find(type => type.value === reportForm.report_type)?.description}
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Target ID</label>
              <input
                type="text"
                value={reportForm.target_id}
                onChange={(e) => setReportForm({...reportForm, target_id: e.target.value})}
                placeholder={
                  reportForm.report_type === 'individual_student' ? 'Student ID' :
                  reportForm.report_type === 'class_summary' ? 'Class ID' :
                  reportForm.report_type === 'subject_performance' ? 'Subject name' :
                  'Target ID'
                }
                className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Title</label>
                <input
                  type="text"
                  value={reportForm.title}
                  onChange={(e) => setReportForm({...reportForm, title: e.target.value})}
                  className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Format</label>
                <select
                  value={reportForm.format}
                  onChange={(e) => setReportForm({...reportForm, format: e.target.value})}
                  className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {formats.map(format => (
                    <option key={format.value} value={format.value}>
                      {format.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
              <textarea
                value={reportForm.description}
                onChange={(e) => setReportForm({...reportForm, description: e.target.value})}
                className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={generatingReport}
              className={`w-full py-2 rounded-lg font-medium transition-colors duration-200 ${
                generatingReport
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {generatingReport ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Generating Report...</span>
                </div>
              ) : (
                'Generate Report'
              )}
            </button>
          </form>
        </div>
      )}

      {/* Recent Reports */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Recent Reports</h4>
        <div className="space-y-3">
          {reports.length === 0 && reportHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <div className="text-6xl mb-4">📊</div>
              <div className="text-lg font-medium mb-2">No Reports Generated</div>
              <div className="text-sm">Generate your first report to see detailed analytics!</div>
            </div>
          ) : (
            [...reports, ...reportHistory].slice(0, 10).map((report, index) => (
              <div key={index} className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{getReportIcon(report.report_type)}</div>
                    <div>
                      <div className="text-white font-medium">{report.title}</div>
                      <div className="text-gray-400 text-sm">{report.description}</div>
                      <div className="text-gray-500 text-xs mt-1">
                        {getReportTypeLabel(report.report_type)} • Generated {formatDate(report.generated_at)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => downloadReport(report)}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors duration-200"
                    >
                      Download
                    </button>
                    <button
                      className="px-3 py-1 bg-gray-600 hover:bg-gray-500 text-white rounded-lg text-sm font-medium transition-colors duration-200"
                    >
                      View
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Report Templates */}
      {Object.keys(templates).length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Available Report Templates</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(templates).map(([templateName, template]) => (
              <div key={templateName} className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h5 className="text-white font-medium capitalize">
                    {templateName.replace('_', ' ')}
                  </h5>
                  <button
                    onClick={() => setReportForm({
                      ...reportForm,
                      report_type: templateName,
                      title: `${templateName.replace('_', ' ')} Report`
                    })}
                    className="text-blue-400 hover:text-blue-300 text-sm"
                  >
                    Use Template
                  </button>
                </div>
                
                <div className="text-xs text-gray-400 mb-2">Sections:</div>
                <div className="flex flex-wrap gap-1 mb-3">
                  {template.sections?.map((section, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-600 text-gray-300 rounded text-xs">
                      {section.replace('_', ' ')}
                    </span>
                  ))}
                </div>
                
                <div className="text-xs text-gray-400 mb-2">Visualizations:</div>
                <div className="flex flex-wrap gap-1">
                  {template.visualizations?.map((viz, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-600 bg-opacity-20 text-blue-300 rounded text-xs">
                      {viz.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Report Statistics */}
      <div className="bg-gray-700 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Report Statistics</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {reports.length + reportHistory.length}
            </div>
            <div className="text-xs text-gray-400">Total Reports</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {reports.filter(r => r.report_type === 'individual_student').length}
            </div>
            <div className="text-xs text-gray-400">Student Reports</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">
              {reports.filter(r => r.report_type === 'class_summary').length}
            </div>
            <div className="text-xs text-gray-400">Class Reports</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">
              {reports.filter(r => r.report_type === 'predictive_report').length}
            </div>
            <div className="text-xs text-gray-400">Predictive Reports</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportingSystem;