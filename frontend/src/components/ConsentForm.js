import React, { useState } from 'react';
import {
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  ShieldCheckIcon,
  UserIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

const ConsentForm = ({ onConsentSubmit, onClose, className = "" }) => {
  const [userAge, setUserAge] = useState('');
  const [parentalConsent, setParentalConsent] = useState(false);
  const [parentEmail, setParentEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const age = parseInt(userAge);
      
      if (isNaN(age) || age < 5 || age > 120) {
        setError('Please enter a valid age between 5 and 120');
        setIsSubmitting(false);
        return;
      }

      if (age < 18 && !parentalConsent) {
        setError('Parental consent is required for users under 18');
        setIsSubmitting(false);
        return;
      }

      if (age < 18 && parentalConsent && !parentEmail.trim()) {
        setError('Parent email is required for users under 18');
        setIsSubmitting(false);
        return;
      }

      const consentData = {
        user_age: age,
        parental_consent: parentalConsent,
        parent_email: parentEmail.trim() || null,
        consent_timestamp: new Date().toISOString()
      };

      await onConsentSubmit(consentData);
      
    } catch (err) {
      setError(err.message || 'Failed to submit consent form');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isUnder18 = userAge && parseInt(userAge) < 18;

  return (
    <div className={`consent-form-container ${className}`}>
      <div className="pathwayiq-card max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <ShieldCheckIcon className="w-6 h-6 text-blue-500" />
            <h2 className="text-xl font-semibold text-white">Privacy & Consent</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <DocumentTextIcon className="w-5 h-5 text-blue-400 mt-0.5" />
            <div>
              <h3 className="text-blue-300 font-medium mb-2">Voice Data Collection</h3>
              <p className="text-blue-200 text-sm">
                We collect voice recordings to improve your learning experience through think-aloud assessments. 
                Your voice data is processed securely and used only for educational analysis.
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4">
            <div className="flex items-center space-x-2">
              <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
              <span className="text-red-300 text-sm">{error}</span>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="form-label">
              <UserIcon className="w-4 h-4 mr-2 inline" />
              Your Age
            </label>
            <input
              type="number"
              value={userAge}
              onChange={(e) => setUserAge(e.target.value)}
              className="form-input"
              placeholder="Enter your age"
              min="5"
              max="120"
              required
            />
          </div>

          {isUnder18 && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />
                <span className="text-yellow-300 font-medium">Under 18 - Parental Consent Required</span>
              </div>
              
              <div className="space-y-3">
                <p className="text-yellow-200 text-sm">
                  In compliance with GDPR and COPPA regulations, users under 18 require parental consent 
                  for voice data collection and processing.
                </p>
                
                <div>
                  <label className="form-label">Parent/Guardian Email</label>
                  <input
                    type="email"
                    value={parentEmail}
                    onChange={(e) => setParentEmail(e.target.value)}
                    className="form-input"
                    placeholder="parent@example.com"
                    required
                  />
                </div>
                
                <label className="flex items-start space-x-2">
                  <input
                    type="checkbox"
                    checked={parentalConsent}
                    onChange={(e) => setParentalConsent(e.target.checked)}
                    className="form-checkbox mt-1"
                    required
                  />
                  <span className="text-white text-sm">
                    I confirm that I have parental/guardian consent to use voice recording features for educational purposes. 
                    I understand that voice data will be processed according to the privacy policy.
                  </span>
                </label>
              </div>
            </div>
          )}

          {!isUnder18 && userAge && (
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <CheckCircleIcon className="w-5 h-5 text-green-500" />
                <span className="text-green-300 font-medium">Age 18+ - No Additional Consent Required</span>
              </div>
              <p className="text-green-200 text-sm mt-2">
                You can use voice recording features directly. Your voice data will be processed securely 
                for educational analysis.
              </p>
            </div>
          )}

          <div className="bg-gray-800 rounded-lg p-4">
            <h4 className="text-white font-medium mb-2">Data Processing Information</h4>
            <ul className="text-gray-300 text-sm space-y-1">
              <li>• Voice recordings are processed using OpenAI Whisper for transcription</li>
              <li>• Audio data is temporarily stored and then deleted after processing</li>
              <li>• Transcripts are used for educational assessment and feedback</li>
              <li>• You can request data deletion at any time</li>
              <li>• Data is encrypted and stored securely</li>
            </ul>
          </div>

          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={isSubmitting || !userAge || (isUnder18 && (!parentalConsent || !parentEmail.trim()))}
              className="btn-primary flex-1"
            >
              {isSubmitting ? (
                <div className="loading-spinner w-4 h-4 mr-2"></div>
              ) : (
                <CheckCircleIcon className="w-4 h-4 mr-2" />
              )}
              {isSubmitting ? 'Submitting...' : 'Accept & Continue'}
            </button>
            
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
            >
              <XMarkIcon className="w-4 h-4 mr-2" />
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ConsentForm;