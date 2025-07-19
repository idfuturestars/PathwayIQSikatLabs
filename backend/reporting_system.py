"""
Comprehensive Reporting System for Educators - IDFS PathwayIQ™ powered by SikatLabs™

This module handles comprehensive report generation including:
- Student progress reports (PDF/CSV)
- Class performance analytics
- Individual student assessments
- Customizable report templates
- Data export functionality
- Automated report scheduling
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pymongo import MongoClient
import uuid
import json
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from analytics_engine import AnalyticsEngine
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportingSystem:
    def __init__(self):
        """Initialize the Reporting System with database connection and analytics"""
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            raise ValueError("MONGO_URL environment variable is required")
        
        self.client = MongoClient(mongo_url)
        self.db = self.client.get_database()
        
        # Collections
        self.users_collection = self.db.users
        self.assessments_collection = self.db.assessments
        self.content_collection = self.db.generated_content
        self.sessions_collection = self.db.speech_sessions
        self.reports_collection = self.db.reports
        
        # Initialize analytics engine
        self.analytics_engine = AnalyticsEngine()
        
        logger.info("Reporting System initialized successfully")

    def generate_student_progress_report(self, student_id: str, educator_id: str, 
                                       format: str = "pdf", date_range: str = "30d") -> Dict[str, Any]:
        """Generate comprehensive student progress report"""
        try:
            # Verify educator permissions (placeholder for now)
            educator = self.users_collection.find_one({"user_id": educator_id})
            if not educator or educator.get("role") not in ["teacher", "admin"]:
                return {"error": "Insufficient permissions to generate report"}

            # Get student data
            student = self.users_collection.find_one({"user_id": student_id})
            if not student:
                return {"error": "Student not found"}

            # Get comprehensive analytics
            analytics_data = self.analytics_engine.get_learning_analytics_dashboard(student_id, date_range)
            
            # Generate report based on format
            if format.lower() == "pdf":
                report_file = self._generate_pdf_report(student, analytics_data, date_range)
                report_type = "pdf"
            elif format.lower() == "csv":
                report_file = self._generate_csv_report(student, analytics_data, date_range)
                report_type = "csv"
            else:
                return {"error": "Unsupported format. Use 'pdf' or 'csv'"}

            # Store report metadata
            report_metadata = self._store_report_metadata(
                report_type="student_progress",
                generated_by=educator_id,
                subject_id=student_id,
                format=format,
                date_range=date_range,
                file_path=report_file
            )

            return {
                "success": True,
                "report_id": report_metadata["report_id"],
                "file_path": report_file,
                "format": format,
                "student_name": student.get("username", "Unknown"),
                "generated_at": datetime.now().isoformat(),
                "analytics_summary": {
                    "total_assessments": analytics_data["user_performance"]["total_assessments"],
                    "average_score": analytics_data["user_performance"]["average_assessment_score"],
                    "learning_streak": analytics_data["user_performance"]["learning_streak"],
                    "performance_trend": analytics_data["user_performance"]["performance_trend"]
                }
            }

        except Exception as e:
            logger.error(f"Error generating student progress report: {str(e)}")
            return {"error": "Failed to generate report"}

    def generate_class_performance_report(self, educator_id: str, class_id: str = None, 
                                        format: str = "pdf") -> Dict[str, Any]:
        """Generate class performance report for educators"""
        try:
            # Verify educator permissions
            educator = self.users_collection.find_one({"user_id": educator_id})
            if not educator or educator.get("role") not in ["teacher", "admin"]:
                return {"error": "Insufficient permissions to generate report"}

            # Get class analytics
            class_analytics = self.analytics_engine.get_class_analytics(educator_id, class_id)
            
            # Generate report based on format
            if format.lower() == "pdf":
                report_file = self._generate_class_pdf_report(class_analytics)
                report_type = "pdf"
            elif format.lower() == "csv":
                report_file = self._generate_class_csv_report(class_analytics)
                report_type = "csv"
            else:
                return {"error": "Unsupported format. Use 'pdf' or 'csv'"}

            # Store report metadata
            report_metadata = self._store_report_metadata(
                report_type="class_performance",
                generated_by=educator_id,
                subject_id=class_id or "all_classes",
                format=format,
                date_range="current",
                file_path=report_file
            )

            return {
                "success": True,
                "report_id": report_metadata["report_id"],
                "file_path": report_file,
                "format": format,
                "generated_at": datetime.now().isoformat(),
                "class_summary": {
                    "total_students": class_analytics["class_overview"]["total_students"],
                    "active_students_7d": class_analytics["class_overview"]["active_users_7d"],
                    "performance_distribution": class_analytics["performance_distribution"]
                }
            }

        except Exception as e:
            logger.error(f"Error generating class performance report: {str(e)}")
            return {"error": "Failed to generate class performance report"}

    def generate_assessment_report(self, assessment_id: str = None, educator_id: str = None, 
                                 date_range: str = "30d", format: str = "pdf") -> Dict[str, Any]:
        """Generate assessment-specific report"""
        try:
            # Verify educator permissions
            if educator_id:
                educator = self.users_collection.find_one({"user_id": educator_id})
                if not educator or educator.get("role") not in ["teacher", "admin"]:
                    return {"error": "Insufficient permissions to generate report"}

            # Get assessment data
            query = {}
            if assessment_id:
                query["assessment_id"] = assessment_id
            
            if date_range:
                end_date = datetime.now()
                if date_range == "7d":
                    start_date = end_date - timedelta(days=7)
                elif date_range == "30d":
                    start_date = end_date - timedelta(days=30)
                elif date_range == "90d":
                    start_date = end_date - timedelta(days=90)
                else:
                    start_date = end_date - timedelta(days=30)
                
                query["timestamp"] = {"$gte": start_date, "$lte": end_date}

            assessments = list(self.assessments_collection.find(query))
            
            if not assessments:
                return {"error": "No assessments found for the specified criteria"}

            # Analyze assessment data
            assessment_analytics = self._analyze_assessment_data(assessments)
            
            # Generate report
            if format.lower() == "pdf":
                report_file = self._generate_assessment_pdf_report(assessment_analytics, date_range)
                report_type = "pdf"
            elif format.lower() == "csv":
                report_file = self._generate_assessment_csv_report(assessment_analytics, date_range)
                report_type = "csv"
            else:
                return {"error": "Unsupported format. Use 'pdf' or 'csv'"}

            # Store report metadata
            report_metadata = self._store_report_metadata(
                report_type="assessment_analysis",
                generated_by=educator_id or "system",
                subject_id=assessment_id or "multiple",
                format=format,
                date_range=date_range,
                file_path=report_file
            )

            return {
                "success": True,
                "report_id": report_metadata["report_id"],
                "file_path": report_file,
                "format": format,
                "generated_at": datetime.now().isoformat(),
                "assessment_summary": assessment_analytics["summary"]
            }

        except Exception as e:
            logger.error(f"Error generating assessment report: {str(e)}")
            return {"error": "Failed to generate assessment report"}

    def get_report_templates(self) -> Dict[str, Any]:
        """Get available report templates"""
        templates = {
            "student_progress": {
                "name": "Student Progress Report",
                "description": "Comprehensive individual student performance analysis",
                "formats": ["pdf", "csv"],
                "parameters": {
                    "student_id": "required",
                    "date_range": "optional (7d, 30d, 90d)",
                    "format": "optional (pdf, csv)"
                }
            },
            "class_performance": {
                "name": "Class Performance Report",
                "description": "Overall class performance and engagement metrics",
                "formats": ["pdf", "csv"],
                "parameters": {
                    "class_id": "optional",
                    "format": "optional (pdf, csv)"
                }
            },
            "assessment_analysis": {
                "name": "Assessment Analysis Report",
                "description": "Detailed analysis of assessment results and patterns",
                "formats": ["pdf", "csv"],
                "parameters": {
                    "assessment_id": "optional",
                    "date_range": "optional (7d, 30d, 90d)",
                    "format": "optional (pdf, csv)"
                }
            },
            "learning_analytics": {
                "name": "Learning Analytics Dashboard",
                "description": "Comprehensive learning analytics with visualizations",
                "formats": ["pdf"],
                "parameters": {
                    "user_id": "required",
                    "date_range": "optional (7d, 30d, 90d)"
                }
            }
        }
        
        return {
            "available_templates": templates,
            "total_templates": len(templates),
            "supported_formats": ["pdf", "csv"]
        }

    def get_educator_reports(self, educator_id: str, limit: int = 20) -> Dict[str, Any]:
        """Get reports generated by an educator"""
        try:
            # Verify educator permissions
            educator = self.users_collection.find_one({"user_id": educator_id})
            if not educator or educator.get("role") not in ["teacher", "admin"]:
                return {"error": "Insufficient permissions"}

            reports = list(self.reports_collection.find(
                {"generated_by": educator_id},
                sort=[("created_at", -1)]
            ).limit(limit))

            for report in reports:
                # Convert ObjectId to string if present
                if "_id" in report:
                    report["_id"] = str(report["_id"])
                # Format dates for JSON serialization
                if "created_at" in report:
                    report["created_at"] = report["created_at"].isoformat()

            return {
                "reports": reports,
                "total_reports": len(reports),
                "educator_id": educator_id
            }

        except Exception as e:
            logger.error(f"Error getting educator reports: {str(e)}")
            return {"error": "Failed to retrieve reports"}

    def delete_report(self, report_id: str, educator_id: str) -> Dict[str, Any]:
        """Delete a report (if permissions allow)"""
        try:
            # Verify educator permissions and ownership
            report = self.reports_collection.find_one({"report_id": report_id})
            if not report:
                return {"error": "Report not found"}

            if report.get("generated_by") != educator_id:
                educator = self.users_collection.find_one({"user_id": educator_id})
                if not educator or educator.get("role") != "admin":
                    return {"error": "Insufficient permissions to delete this report"}

            # Delete report metadata
            self.reports_collection.delete_one({"report_id": report_id})
            
            # Optionally delete the actual file
            file_path = report.get("file_path")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Could not delete report file {file_path}: {str(e)}")

            return {"success": True, "message": "Report deleted successfully"}

        except Exception as e:
            logger.error(f"Error deleting report: {str(e)}")
            return {"error": "Failed to delete report"}

    def _generate_pdf_report(self, student: Dict[str, Any], analytics_data: Dict[str, Any], 
                           date_range: str) -> str:
        """Generate PDF report for student progress"""
        try:
            # Create report directory if it doesn't exist
            os.makedirs("/tmp/reports", exist_ok=True)
            filename = f"/tmp/reports/student_progress_{student['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title = Paragraph("IDFS PathwayIQ™ - Student Progress Report", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))

            # Student Information
            student_info = f"""
            <b>Student:</b> {student.get('username', 'Unknown')}<br/>
            <b>Level:</b> {student.get('level', 1)}<br/>
            <b>Experience Points:</b> {student.get('experience_points', 0)}<br/>
            <b>Report Period:</b> {date_range}<br/>
            <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            story.append(Paragraph(student_info, styles['Normal']))
            story.append(Spacer(1, 12))

            # Performance Summary
            perf_data = analytics_data.get("user_performance", {})
            summary = f"""
            <b>Performance Summary</b><br/>
            • Total Assessments: {perf_data.get('total_assessments', 0)}<br/>
            • Average Score: {perf_data.get('average_assessment_score', 0):.1f}%<br/>
            • Learning Streak: {perf_data.get('learning_streak', 0)} days<br/>
            • Performance Trend: {perf_data.get('performance_trend', 'N/A').title()}<br/>
            • Content Generated: {perf_data.get('total_content_generated', 0)} items<br/>
            • Speech Sessions: {perf_data.get('total_speech_sessions', 0)}
            """
            story.append(Paragraph(summary, styles['Normal']))
            story.append(Spacer(1, 12))

            # Skills Analysis
            skill_progress = perf_data.get('skill_progress', {})
            if skill_progress:
                story.append(Paragraph("<b>Skills Analysis</b>", styles['Heading2']))
                
                skill_data = []
                skill_data.append(['Skill', 'Accuracy', 'Attempts', 'Recent Performance'])
                
                for skill, data in skill_progress.items():
                    skill_data.append([
                        skill.title(),
                        f"{data.get('accuracy', 0):.1f}%",
                        str(data.get('total_attempts', 0)),
                        f"{data.get('recent_performance', 0):.1f}%"
                    ])
                
                skill_table = Table(skill_data)
                skill_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(skill_table)
                story.append(Spacer(1, 12))

            # Strengths and Improvement Areas
            strengths = perf_data.get('strengths', [])
            improvements = perf_data.get('areas_for_improvement', [])
            
            if strengths or improvements:
                story.append(Paragraph("<b>Analysis</b>", styles['Heading2']))
                
                if strengths:
                    story.append(Paragraph(f"<b>Strengths:</b> {', '.join(strengths)}", styles['Normal']))
                
                if improvements:
                    story.append(Paragraph(f"<b>Areas for Improvement:</b> {', '.join(improvements)}", styles['Normal']))
                
                story.append(Spacer(1, 12))

            # Recommendations
            recommendations = analytics_data.get('recommendations', [])
            if recommendations:
                story.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
                
                for i, rec in enumerate(recommendations[:5], 1):
                    rec_text = f"{i}. <b>{rec.get('title', 'N/A')}</b>: {rec.get('description', 'N/A')}"
                    story.append(Paragraph(rec_text, styles['Normal']))
                
                story.append(Spacer(1, 12))

            # Footer
            footer = Paragraph("Generated by IDFS PathwayIQ™ powered by SikatLabs™", styles['Italic'])
            story.append(footer)

            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise

    def _generate_csv_report(self, student: Dict[str, Any], analytics_data: Dict[str, Any], 
                           date_range: str) -> str:
        """Generate CSV report for student progress"""
        try:
            # Create report directory if it doesn't exist
            os.makedirs("/tmp/reports", exist_ok=True)
            filename = f"/tmp/reports/student_progress_{student['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header Information
                writer.writerow(['IDFS PathwayIQ™ - Student Progress Report'])
                writer.writerow([''])
                writer.writerow(['Student Information'])
                writer.writerow(['Field', 'Value'])
                writer.writerow(['Student Name', student.get('username', 'Unknown')])
                writer.writerow(['User ID', student.get('user_id', 'Unknown')])
                writer.writerow(['Level', student.get('level', 1)])
                writer.writerow(['Experience Points', student.get('experience_points', 0)])
                writer.writerow(['Report Period', date_range])
                writer.writerow(['Generated At', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([''])

                # Performance Summary
                perf_data = analytics_data.get("user_performance", {})
                writer.writerow(['Performance Summary'])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Assessments', perf_data.get('total_assessments', 0)])
                writer.writerow(['Average Assessment Score (%)', perf_data.get('average_assessment_score', 0)])
                writer.writerow(['Learning Streak (days)', perf_data.get('learning_streak', 0)])
                writer.writerow(['Performance Trend', perf_data.get('performance_trend', 'N/A').title()])
                writer.writerow(['Content Generated', perf_data.get('total_content_generated', 0)])
                writer.writerow(['Speech Sessions', perf_data.get('total_speech_sessions', 0)])
                writer.writerow([''])

                # Skills Analysis
                skill_progress = perf_data.get('skill_progress', {})
                if skill_progress:
                    writer.writerow(['Skills Analysis'])
                    writer.writerow(['Skill', 'Accuracy (%)', 'Total Attempts', 'Recent Performance (%)'])
                    
                    for skill, data in skill_progress.items():
                        writer.writerow([
                            skill.title(),
                            data.get('accuracy', 0),
                            data.get('total_attempts', 0),
                            data.get('recent_performance', 0)
                        ])
                    writer.writerow([''])

                # Recent Activity
                recent_activity = perf_data.get('recent_activity', [])
                if recent_activity:
                    writer.writerow(['Recent Activity'])
                    writer.writerow(['Type', 'Description', 'Timestamp', 'Score/Topic'])
                    
                    for activity in recent_activity[:10]:
                        writer.writerow([
                            activity.get('type', 'N/A'),
                            activity.get('description', 'N/A'),
                            activity.get('timestamp', 'N/A'),
                            activity.get('score', activity.get('topic', 'N/A'))
                        ])
                    writer.writerow([''])

                # Recommendations
                recommendations = analytics_data.get('recommendations', [])
                if recommendations:
                    writer.writerow(['Recommendations'])
                    writer.writerow(['Priority', 'Title', 'Description'])
                    
                    for rec in recommendations:
                        writer.writerow([
                            rec.get('priority', 'medium'),
                            rec.get('title', 'N/A'),
                            rec.get('description', 'N/A')
                        ])

            logger.info(f"CSV report generated: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error generating CSV report: {str(e)}")
            raise

    def _generate_class_pdf_report(self, class_analytics: Dict[str, Any]) -> str:
        """Generate PDF report for class performance"""
        try:
            # Create report directory if it doesn't exist
            os.makedirs("/tmp/reports", exist_ok=True)
            filename = f"/tmp/reports/class_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title = Paragraph("IDFS PathwayIQ™ - Class Performance Report", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))

            # Class Overview
            overview = class_analytics.get("class_overview", {})
            class_info = f"""
            <b>Class Overview</b><br/>
            • Total Students: {overview.get('total_students', 0)}<br/>
            • Total Teachers: {overview.get('total_teachers', 0)}<br/>
            • Active Users (7 days): {overview.get('active_users_7d', 0)}<br/>
            • Active Users (30 days): {overview.get('active_users_30d', 0)}<br/>
            <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            story.append(Paragraph(class_info, styles['Normal']))
            story.append(Spacer(1, 12))

            # Performance Distribution
            perf_dist = class_analytics.get("performance_distribution", {})
            if perf_dist:
                story.append(Paragraph("<b>Performance Distribution</b>", styles['Heading2']))
                
                dist_data = []
                dist_data.append(['Performance Level', 'Number of Students'])
                dist_data.append(['Excellent (90%+)', perf_dist.get('excellent', 0)])
                dist_data.append(['Good (75-89%)', perf_dist.get('good', 0)])
                dist_data.append(['Fair (60-74%)', perf_dist.get('fair', 0)])
                dist_data.append(['Needs Improvement (<60%)', perf_dist.get('needs_improvement', 0)])
                
                dist_table = Table(dist_data)
                dist_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(dist_table)
                story.append(Spacer(1, 12))

            # Top Performers
            top_performers = class_analytics.get("top_performers", [])
            if top_performers:
                story.append(Paragraph("<b>Top Performers</b>", styles['Heading2']))
                
                perf_data = []
                perf_data.append(['Rank', 'Student', 'Level', 'Average Score', 'Assessments'])
                
                for i, performer in enumerate(top_performers[:10], 1):
                    perf_data.append([
                        str(i),
                        performer.get('username', 'Unknown'),
                        str(performer.get('level', 1)),
                        f"{performer.get('average_score', 0):.1f}%",
                        str(performer.get('total_assessments', 0))
                    ])
                
                perf_table = Table(perf_data)
                perf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(perf_table)
                story.append(Spacer(1, 12))

            # Students Needing Support
            support_students = class_analytics.get("students_needing_support", [])
            if support_students:
                story.append(Paragraph("<b>Students Needing Support</b>", styles['Heading2']))
                
                support_data = []
                support_data.append(['Student', 'Average Score', 'Assessments', 'Areas for Improvement'])
                
                for student in support_students[:10]:
                    areas = ', '.join(student.get('areas_for_improvement', [])[:3])
                    support_data.append([
                        student.get('username', 'Unknown'),
                        f"{student.get('average_score', 0):.1f}%",
                        str(student.get('total_assessments', 0)),
                        areas or 'N/A'
                    ])
                
                support_table = Table(support_data)
                support_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(support_table)
                story.append(Spacer(1, 12))

            # Footer
            footer = Paragraph("Generated by IDFS PathwayIQ™ powered by SikatLabs™", styles['Italic'])
            story.append(footer)

            # Build PDF
            doc.build(story)
            
            logger.info(f"Class PDF report generated: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error generating class PDF report: {str(e)}")
            raise

    def _generate_class_csv_report(self, class_analytics: Dict[str, Any]) -> str:
        """Generate CSV report for class performance"""
        try:
            # Create report directory if it doesn't exist
            os.makedirs("/tmp/reports", exist_ok=True)
            filename = f"/tmp/reports/class_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header Information
                writer.writerow(['IDFS PathwayIQ™ - Class Performance Report'])
                writer.writerow(['Generated At', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([''])

                # Class Overview
                overview = class_analytics.get("class_overview", {})
                writer.writerow(['Class Overview'])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Students', overview.get('total_students', 0)])
                writer.writerow(['Total Teachers', overview.get('total_teachers', 0)])
                writer.writerow(['Active Users (7 days)', overview.get('active_users_7d', 0)])
                writer.writerow(['Active Users (30 days)', overview.get('active_users_30d', 0)])
                writer.writerow([''])

                # Performance Distribution
                perf_dist = class_analytics.get("performance_distribution", {})
                if perf_dist:
                    writer.writerow(['Performance Distribution'])
                    writer.writerow(['Performance Level', 'Number of Students'])
                    writer.writerow(['Excellent (90%+)', perf_dist.get('excellent', 0)])
                    writer.writerow(['Good (75-89%)', perf_dist.get('good', 0)])
                    writer.writerow(['Fair (60-74%)', perf_dist.get('fair', 0)])
                    writer.writerow(['Needs Improvement (<60%)', perf_dist.get('needs_improvement', 0)])
                    writer.writerow([''])

                # Top Performers
                top_performers = class_analytics.get("top_performers", [])
                if top_performers:
                    writer.writerow(['Top Performers'])
                    writer.writerow(['Rank', 'Student', 'User ID', 'Level', 'Average Score (%)', 'Total Assessments'])
                    
                    for i, performer in enumerate(top_performers[:15], 1):
                        writer.writerow([
                            i,
                            performer.get('username', 'Unknown'),
                            performer.get('user_id', 'Unknown'),
                            performer.get('level', 1),
                            performer.get('average_score', 0),
                            performer.get('total_assessments', 0)
                        ])
                    writer.writerow([''])

                # Students Needing Support
                support_students = class_analytics.get("students_needing_support", [])
                if support_students:
                    writer.writerow(['Students Needing Support'])
                    writer.writerow(['Student', 'User ID', 'Average Score (%)', 'Total Assessments', 'Areas for Improvement'])
                    
                    for student in support_students:
                        areas = ', '.join(student.get('areas_for_improvement', []))
                        writer.writerow([
                            student.get('username', 'Unknown'),
                            student.get('user_id', 'Unknown'),
                            student.get('average_score', 0),
                            student.get('total_assessments', 0),
                            areas or 'N/A'
                        ])

            logger.info(f"Class CSV report generated: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error generating class CSV report: {str(e)}")
            raise

    def _generate_assessment_pdf_report(self, assessment_analytics: Dict[str, Any], date_range: str) -> str:
        """Generate PDF report for assessment analysis"""
        filename = f"/tmp/reports/assessment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Simplified implementation for MVP
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title = Paragraph("IDFS PathwayIQ™ - Assessment Analysis Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        summary = assessment_analytics.get("summary", {})
        content = f"""
        <b>Assessment Analysis Summary</b><br/>
        • Period: {date_range}<br/>
        • Total Assessments: {summary.get('total_assessments', 0)}<br/>
        • Average Score: {summary.get('average_score', 0):.1f}%<br/>
        • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        story.append(Paragraph(content, styles['Normal']))

        footer = Paragraph("Generated by IDFS PathwayIQ™ powered by SikatLabs™", styles['Italic'])
        story.append(footer)

        doc.build(story)
        return filename

    def _generate_assessment_csv_report(self, assessment_analytics: Dict[str, Any], date_range: str) -> str:
        """Generate CSV report for assessment analysis"""
        filename = f"/tmp/reports/assessment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['IDFS PathwayIQ™ - Assessment Analysis Report'])
            writer.writerow(['Period', date_range])
            writer.writerow(['Generated At', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            
            summary = assessment_analytics.get("summary", {})
            writer.writerow([''])
            writer.writerow(['Summary'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Assessments', summary.get('total_assessments', 0)])
            writer.writerow(['Average Score', f"{summary.get('average_score', 0):.1f}%"])

        return filename

    def _analyze_assessment_data(self, assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze assessment data for reporting"""
        if not assessments:
            return {"summary": {"total_assessments": 0, "average_score": 0}}

        total_assessments = len(assessments)
        all_scores = []
        
        for assessment in assessments:
            responses = assessment.get("responses", [])
            if responses:
                correct_count = sum(1 for response in responses if response.get("correct", False))
                score = (correct_count / len(responses)) * 100
                all_scores.append(score)

        average_score = statistics.mean(all_scores) if all_scores else 0

        return {
            "summary": {
                "total_assessments": total_assessments,
                "average_score": average_score,
                "score_distribution": {
                    "90-100": len([s for s in all_scores if s >= 90]),
                    "80-89": len([s for s in all_scores if 80 <= s < 90]),
                    "70-79": len([s for s in all_scores if 70 <= s < 80]),
                    "below_70": len([s for s in all_scores if s < 70])
                }
            },
            "detailed_scores": all_scores
        }

    def _store_report_metadata(self, report_type: str, generated_by: str, subject_id: str, 
                             format: str, date_range: str, file_path: str) -> Dict[str, Any]:
        """Store report metadata in database"""
        try:
            report_metadata = {
                "report_id": str(uuid.uuid4()),
                "report_type": report_type,
                "generated_by": generated_by,
                "subject_id": subject_id,
                "format": format,
                "date_range": date_range,
                "file_path": file_path,
                "created_at": datetime.now(),
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            
            self.reports_collection.insert_one(report_metadata)
            logger.info(f"Report metadata stored: {report_metadata['report_id']}")
            
            return report_metadata
            
        except Exception as e:
            logger.error(f"Error storing report metadata: {str(e)}")
            raise

    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
        if self.analytics_engine:
            self.analytics_engine.close_connection()
        logger.info("Reporting System database connection closed")