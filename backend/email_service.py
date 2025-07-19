"""
Email service for sending reports and notifications using SendGrid
"""
import os
import logging
from typing import List, Dict, Any, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'hello@idfuturestars.com')
        self.from_name = os.getenv('SENDGRID_FROM_NAME', 'IDFS PathwayIQ Reports')
        
        if not self.api_key:
            logger.error("SENDGRID_API_KEY not found in environment variables")
            raise ValueError("SendGrid API key is required")
        
        self.client = SendGridAPIClient(api_key=self.api_key)
    
    async def send_learning_analytics_report(
        self,
        recipient_email: str,
        recipient_name: str,
        report_data: Dict[str, Any],
        report_period: str = "Weekly"
    ) -> bool:
        """Send learning analytics report to educator"""
        try:
            # Generate report content
            subject = f"IDFS PathwayIQ™ {report_period} Learning Analytics Report"
            
            html_content = self._generate_analytics_report_html(
                recipient_name, report_data, report_period
            )
            
            plain_content = self._generate_analytics_report_text(
                recipient_name, report_data, report_period
            )
            
            # Create message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(recipient_email, recipient_name),
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", plain_content)
            )
            
            # Send email
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Analytics report sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send analytics report: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending analytics report: {str(e)}")
            return False
    
    async def send_student_progress_alert(
        self,
        recipient_email: str,
        recipient_name: str,
        student_name: str,
        alert_type: str,
        alert_details: Dict[str, Any]
    ) -> bool:
        """Send alert about student progress or performance"""
        try:
            subject = f"IDFS PathwayIQ™ Student Alert: {student_name} - {alert_type}"
            
            html_content = self._generate_progress_alert_html(
                recipient_name, student_name, alert_type, alert_details
            )
            
            plain_content = self._generate_progress_alert_text(
                recipient_name, student_name, alert_type, alert_details
            )
            
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(recipient_email, recipient_name),
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", plain_content)
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Progress alert sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send progress alert: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending progress alert: {str(e)}")
            return False
    
    async def send_bulk_report(
        self,
        recipients: List[Dict[str, str]],
        report_data: Dict[str, Any],
        report_type: str = "Learning Analytics"
    ) -> Dict[str, Any]:
        """Send bulk reports to multiple recipients"""
        results = {
            "sent": [],
            "failed": [],
            "total": len(recipients)
        }
        
        for recipient in recipients:
            email = recipient.get('email')
            name = recipient.get('name', 'Educator')
            
            success = await self.send_learning_analytics_report(
                email, name, report_data
            )
            
            if success:
                results["sent"].append(email)
            else:
                results["failed"].append(email)
        
        return results
    
    def _generate_analytics_report_html(
        self, 
        recipient_name: str, 
        report_data: Dict[str, Any], 
        report_period: str
    ) -> str:
        """Generate HTML content for analytics report"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>IDFS PathwayIQ™ Learning Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #1a1a1a; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metric {{ margin-bottom: 20px; padding: 15px; border-left: 4px solid #3b82f6; background-color: #f8f9fa; }}
                .metric-title {{ font-weight: bold; color: #1a1a1a; }}
                .metric-value {{ font-size: 24px; color: #3b82f6; margin: 5px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>IDFS PathwayIQ™</h1>
                <p>powered by SikatLabs™</p>
                <h2>{report_period} Learning Analytics Report</h2>
            </div>
            
            <div class="content">
                <p>Dear {recipient_name},</p>
                
                <p>Here's your {report_period.lower()} learning analytics report from IDFS PathwayIQ™:</p>
                
                <div class="metric">
                    <div class="metric-title">Total Students</div>
                    <div class="metric-value">{report_data.get('total_students', 0)}</div>
                </div>
                
                <div class="metric">
                    <div class="metric-title">Active Learners</div>
                    <div class="metric-value">{report_data.get('active_students', 0)}</div>
                </div>
                
                <div class="metric">
                    <div class="metric-title">Assessments Completed</div>
                    <div class="metric-value">{report_data.get('assessments_completed', 0)}</div>
                </div>
                
                <div class="metric">
                    <div class="metric-title">Average Performance Score</div>
                    <div class="metric-value">{report_data.get('avg_performance', 0):.1f}%</div>
                </div>
                
                <div class="metric">
                    <div class="metric-title">Study Groups Created</div>
                    <div class="metric-value">{report_data.get('study_groups', 0)}</div>
                </div>
                
                <p><strong>Key Insights:</strong></p>
                <ul>
                    {self._generate_insights_html(report_data)}
                </ul>
                
                <p>For detailed analytics, please log in to your IDFS PathwayIQ™ dashboard.</p>
                
                <p>Best regards,<br>
                The IDFS PathwayIQ™ Team</p>
            </div>
            
            <div class="footer">
                <p>© 2025 IDFS PathwayIQ™ powered by SikatLabs™</p>
                <p>This report was generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
        </body>
        </html>
        """
    
    def _generate_analytics_report_text(
        self, 
        recipient_name: str, 
        report_data: Dict[str, Any], 
        report_period: str
    ) -> str:
        """Generate plain text content for analytics report"""
        insights = self._generate_insights_text(report_data)
        
        return f"""
IDFS PathwayIQ™ {report_period} Learning Analytics Report
=======================================================

Dear {recipient_name},

Here's your {report_period.lower()} learning analytics report from IDFS PathwayIQ™:

METRICS:
--------
Total Students: {report_data.get('total_students', 0)}
Active Learners: {report_data.get('active_students', 0)}
Assessments Completed: {report_data.get('assessments_completed', 0)}
Average Performance Score: {report_data.get('avg_performance', 0):.1f}%
Study Groups Created: {report_data.get('study_groups', 0)}

KEY INSIGHTS:
------------
{insights}

For detailed analytics, please log in to your IDFS PathwayIQ™ dashboard.

Best regards,
The IDFS PathwayIQ™ Team

---
© 2025 IDFS PathwayIQ™ powered by SikatLabs™
Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
    
    def _generate_progress_alert_html(
        self,
        recipient_name: str,
        student_name: str,
        alert_type: str,
        alert_details: Dict[str, Any]
    ) -> str:
        """Generate HTML content for progress alert"""
        alert_color = "#dc2626" if alert_type == "At Risk" else "#059669"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>IDFS PathwayIQ™ Student Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #1a1a1a; color: white; padding: 20px; text-align: center; }}
                .alert {{ padding: 20px; border-left: 4px solid {alert_color}; background-color: #f8f9fa; margin: 20px 0; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>IDFS PathwayIQ™</h1>
                <p>powered by SikatLabs™</p>
                <h2>Student Progress Alert</h2>
            </div>
            
            <div class="content">
                <p>Dear {recipient_name},</p>
                
                <div class="alert">
                    <h3>Alert: {alert_type}</h3>
                    <p><strong>Student:</strong> {student_name}</p>
                    <p><strong>Details:</strong> {alert_details.get('message', 'Performance alert triggered')}</p>
                    <p><strong>Recommendation:</strong> {alert_details.get('recommendation', 'Please review student progress')}</p>
                </div>
                
                <p>Please log in to your IDFS PathwayIQ™ dashboard to view detailed analytics and take appropriate action.</p>
                
                <p>Best regards,<br>
                The IDFS PathwayIQ™ Team</p>
            </div>
            
            <div class="footer">
                <p>© 2025 IDFS PathwayIQ™ powered by SikatLabs™</p>
                <p>Alert generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
        </body>
        </html>
        """
    
    def _generate_progress_alert_text(
        self,
        recipient_name: str,
        student_name: str,
        alert_type: str,
        alert_details: Dict[str, Any]
    ) -> str:
        """Generate plain text content for progress alert"""
        return f"""
IDFS PathwayIQ™ Student Progress Alert
====================================

Dear {recipient_name},

ALERT: {alert_type}
Student: {student_name}

Details: {alert_details.get('message', 'Performance alert triggered')}
Recommendation: {alert_details.get('recommendation', 'Please review student progress')}

Please log in to your IDFS PathwayIQ™ dashboard to view detailed analytics and take appropriate action.

Best regards,
The IDFS PathwayIQ™ Team

---
© 2025 IDFS PathwayIQ™ powered by SikatLabs™
Alert generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
    
    def _generate_insights_html(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML insights list"""
        insights = []
        
        if report_data.get('avg_performance', 0) > 80:
            insights.append("<li>Excellent overall performance with 80%+ average scores</li>")
        elif report_data.get('avg_performance', 0) < 60:
            insights.append("<li>Performance below 60% - consider additional support</li>")
        
        if report_data.get('active_students', 0) < report_data.get('total_students', 1) * 0.7:
            insights.append("<li>Student engagement could be improved - less than 70% active</li>")
        
        if report_data.get('study_groups', 0) > 0:
            insights.append(f"<li>{report_data.get('study_groups')} collaborative study groups are active</li>")
        
        return '\n'.join(insights) if insights else "<li>Continue monitoring student progress</li>"
    
    def _generate_insights_text(self, report_data: Dict[str, Any]) -> str:
        """Generate plain text insights"""
        insights = []
        
        if report_data.get('avg_performance', 0) > 80:
            insights.append("- Excellent overall performance with 80%+ average scores")
        elif report_data.get('avg_performance', 0) < 60:
            insights.append("- Performance below 60% - consider additional support")
        
        if report_data.get('active_students', 0) < report_data.get('total_students', 1) * 0.7:
            insights.append("- Student engagement could be improved - less than 70% active")
        
        if report_data.get('study_groups', 0) > 0:
            insights.append(f"- {report_data.get('study_groups')} collaborative study groups are active")
        
        return '\n'.join(insights) if insights else "- Continue monitoring student progress"

# Initialize email service
email_service = EmailService()