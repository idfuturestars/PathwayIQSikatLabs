"""
Comprehensive Reporting System for Educators
Generates detailed reports with PDF/CSV export functionality
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import os
import json
import csv
from io import StringIO, BytesIO
import base64
from pymongo import MongoClient

# For PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

logger = logging.getLogger(__name__)

class ReportingSystem:
    def __init__(self, mongo_url: str):
        self.client = MongoClient(mongo_url)
        db_name = os.getenv('DB_NAME', 'idfs_pathwayiq_database')
        self.db = self.client[db_name]
        
        # Collections
        self.users_collection = self.db.users
        self.assessments_collection = self.db.assessments
        self.content_collection = self.db.content_generation
        self.groups_collection = self.db.study_groups
        self.reports_collection = self.db.reports
        
        # Report templates
        self.report_templates = {
            "student_progress": "Individual Student Progress Report",
            "class_performance": "Class Performance Summary",
            "subject_analytics": "Subject-wise Performance Analysis",
            "engagement_report": "Student Engagement Report",
            "learning_outcomes": "Learning Outcomes Assessment",
            "comparative_analysis": "Comparative Performance Analysis"
        }
    
    # REPORT GENERATION
    async def generate_student_progress_report(
        self,
        educator_id: str,
        student_id: str,
        days: int = 30,
        export_format: str = "json"
    ) -> Dict[str, Any]:
        """Generate comprehensive progress report for individual student"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Get student info
            student = self.users_collection.find_one({"id": student_id})
            if not student:
                return {"error": "Student not found"}
            
            # Get assessments data
            assessments = list(self.assessments_collection.find({
                "user_id": student_id,
                "created_at": {"$gte": since_date}
            }).sort("created_at", 1))
            
            # Get content generation data
            content_generated = list(self.content_collection.find({
                "user_id": student_id,
                "created_at": {"$gte": since_date}
            }))
            
            # Calculate performance metrics
            performance_metrics = self._calculate_student_performance(assessments)
            
            # Analyze learning patterns
            learning_patterns = self._analyze_student_learning_patterns(assessments, content_generated)
            
            # Generate recommendations
            recommendations = self._generate_student_recommendations(performance_metrics, learning_patterns)
            
            # Create report data
            report_data = {
                "report_id": str(uuid.uuid4()),
                "report_type": "student_progress",
                "generated_by": educator_id,
                "generated_at": datetime.utcnow().isoformat(),
                "student_info": {
                    "id": student_id,
                    "username": student.get("username"),
                    "level": student.get("level", 1),
                    "xp": student.get("xp", 0)
                },
                "period": {
                    "days": days,
                    "start_date": since_date.isoformat(),
                    "end_date": datetime.utcnow().isoformat()
                },
                "performance_summary": performance_metrics,
                "learning_patterns": learning_patterns,
                "detailed_assessments": [
                    {
                        "date": assessment["created_at"].isoformat(),
                        "subject": assessment.get("subject"),
                        "score": assessment.get("final_score", 0),
                        "ability_estimate": assessment.get("final_ability_estimate", 0),
                        "questions_answered": assessment.get("questions_answered", 0),
                        "questions_correct": assessment.get("questions_correct", 0)
                    }
                    for assessment in assessments
                ],
                "content_generation_summary": {
                    "total_content": len(content_generated),
                    "by_type": self._group_content_by_type(content_generated)
                },
                "recommendations": recommendations
            }
            
            # Store report in database
            report_doc = {
                **report_data,
                "generated_at": datetime.utcnow(),
                "period_start": since_date,
                "period_end": datetime.utcnow()
            }
            self.reports_collection.insert_one(report_doc)
            
            # Export in requested format
            if export_format == "pdf" and PDF_AVAILABLE:
                pdf_data = self._generate_pdf_report(report_data, "student_progress")
                return {
                    "success": True,
                    "report_data": report_data,
                    "pdf_base64": pdf_data,
                    "format": "pdf"
                }
            elif export_format == "csv":
                csv_data = self._generate_csv_report(report_data, "student_progress")
                return {
                    "success": True,
                    "report_data": report_data,
                    "csv_data": csv_data,
                    "format": "csv"
                }
            else:
                return {
                    "success": True,
                    "report_data": report_data,
                    "format": "json"
                }
                
        except Exception as e:
            logger.error(f"Error generating student progress report: {e}")
            return {"error": str(e)}
    
    async def generate_class_performance_report(
        self,
        educator_id: str,
        days: int = 30,
        subject: Optional[str] = None,
        export_format: str = "json"
    ) -> Dict[str, Any]:
        """Generate class performance summary report"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Build query
            query = {"created_at": {"$gte": since_date}}
            if subject:
                query["subject"] = subject
            
            # Get all assessments for the period
            assessments = list(self.assessments_collection.find(query))
            
            if not assessments:
                return {
                    "success": True,
                    "report_data": {
                        "message": "No assessment data available for the selected period",
                        "period": days,
                        "subject": subject
                    },
                    "format": export_format
                }
            
            # Group by student
            student_data = {}
            for assessment in assessments:
                student_id = assessment["user_id"]
                if student_id not in student_data:
                    student = self.users_collection.find_one({"id": student_id})
                    student_data[student_id] = {
                        "username": student.get("username", f"Student {student_id[:8]}") if student else f"Student {student_id[:8]}",
                        "assessments": []
                    }
                student_data[student_id]["assessments"].append(assessment)
            
            # Calculate class metrics
            all_scores = [assessment["final_score"] for assessment in assessments]
            class_metrics = {
                "total_students": len(student_data),
                "total_assessments": len(assessments),
                "class_average": sum(all_scores) / len(all_scores) if all_scores else 0,
                "highest_score": max(all_scores) if all_scores else 0,
                "lowest_score": min(all_scores) if all_scores else 0,
                "median_score": sorted(all_scores)[len(all_scores)//2] if all_scores else 0
            }
            
            # Calculate grade distribution
            grade_distribution = {
                "A (90-100)": len([s for s in all_scores if s >= 90]),
                "B (80-89)": len([s for s in all_scores if 80 <= s < 90]),
                "C (70-79)": len([s for s in all_scores if 70 <= s < 80]),
                "D (60-69)": len([s for s in all_scores if 60 <= s < 70]),
                "F (0-59)": len([s for s in all_scores if s < 60])
            }
            
            # Calculate individual student summaries
            student_summaries = []
            for student_id, data in student_data.items():
                student_assessments = data["assessments"]
                student_scores = [a["final_score"] for a in student_assessments]
                
                student_summaries.append({
                    "student_id": student_id,
                    "username": data["username"],
                    "assessment_count": len(student_assessments),
                    "average_score": sum(student_scores) / len(student_scores) if student_scores else 0,
                    "best_score": max(student_scores) if student_scores else 0,
                    "improvement": self._calculate_improvement_trend(student_scores),
                    "subjects": list(set(a.get("subject") for a in student_assessments if a.get("subject")))
                })
            
            # Sort by average score
            student_summaries.sort(key=lambda x: x["average_score"], reverse=True)
            
            # Create report data
            report_data = {
                "report_id": str(uuid.uuid4()),
                "report_type": "class_performance",
                "generated_by": educator_id,
                "generated_at": datetime.utcnow().isoformat(),
                "period": {
                    "days": days,
                    "start_date": since_date.isoformat(),
                    "end_date": datetime.utcnow().isoformat(),
                    "subject_filter": subject
                },
                "class_metrics": class_metrics,
                "grade_distribution": grade_distribution,
                "student_summaries": student_summaries,
                "top_performers": student_summaries[:5],  # Top 5
                "needs_attention": [s for s in student_summaries if s["average_score"] < 60]
            }
            
            # Store in database
            report_doc = {
                **report_data,
                "generated_at": datetime.utcnow(),
                "period_start": since_date,
                "period_end": datetime.utcnow()
            }
            self.reports_collection.insert_one(report_doc)
            
            # Export in requested format
            if export_format == "pdf" and PDF_AVAILABLE:
                pdf_data = self._generate_pdf_report(report_data, "class_performance")
                return {
                    "success": True,
                    "report_data": report_data,
                    "pdf_base64": pdf_data,
                    "format": "pdf"
                }
            elif export_format == "csv":
                csv_data = self._generate_csv_report(report_data, "class_performance")
                return {
                    "success": True,
                    "report_data": report_data,
                    "csv_data": csv_data,
                    "format": "csv"
                }
            else:
                return {
                    "success": True,
                    "report_data": report_data,
                    "format": "json"
                }
                
        except Exception as e:
            logger.error(f"Error generating class performance report: {e}")
            return {"error": str(e)}
    
    async def generate_subject_analytics_report(
        self,
        educator_id: str,
        days: int = 30,
        export_format: str = "json"
    ) -> Dict[str, Any]:
        """Generate subject-wise performance analysis"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Aggregate by subject
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": since_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$subject",
                        "total_assessments": {"$sum": 1},
                        "unique_students": {"$addToSet": "$user_id"},
                        "avg_score": {"$avg": "$final_score"},
                        "avg_ability": {"$avg": "$final_ability_estimate"},
                        "scores": {"$push": "$final_score"}
                    }
                },
                {
                    "$project": {
                        "subject": "$_id",
                        "total_assessments": 1,
                        "unique_students": {"$size": "$unique_students"},
                        "avg_score": 1,
                        "avg_ability": 1,
                        "scores": 1
                    }
                },
                {
                    "$sort": {"avg_score": -1}
                }
            ]
            
            subject_stats = list(self.assessments_collection.aggregate(pipeline))
            
            # Process subject data
            subject_analysis = []
            for stat in subject_stats:
                scores = stat["scores"]
                subject_analysis.append({
                    "subject": stat["subject"],
                    "total_assessments": stat["total_assessments"],
                    "unique_students": stat["unique_students"],
                    "average_score": round(stat["avg_score"], 2),
                    "average_ability": round(stat["avg_ability"], 2),
                    "highest_score": max(scores) if scores else 0,
                    "lowest_score": min(scores) if scores else 0,
                    "score_range": max(scores) - min(scores) if scores else 0,
                    "grade_distribution": {
                        "A": len([s for s in scores if s >= 90]),
                        "B": len([s for s in scores if 80 <= s < 90]),
                        "C": len([s for s in scores if 70 <= s < 80]),
                        "D": len([s for s in scores if 60 <= s < 70]),
                        "F": len([s for s in scores if s < 60])
                    }
                })
            
            # Find trends and insights
            if subject_analysis:
                best_subject = max(subject_analysis, key=lambda x: x["average_score"])
                most_challenging = min(subject_analysis, key=lambda x: x["average_score"])
                most_popular = max(subject_analysis, key=lambda x: x["total_assessments"])
                
                insights = {
                    "best_performing_subject": best_subject["subject"],
                    "most_challenging_subject": most_challenging["subject"],
                    "most_popular_subject": most_popular["subject"],
                    "overall_trends": self._analyze_subject_trends(subject_analysis)
                }
            else:
                insights = {
                    "message": "No data available for analysis"
                }
            
            report_data = {
                "report_id": str(uuid.uuid4()),
                "report_type": "subject_analytics",
                "generated_by": educator_id,
                "generated_at": datetime.utcnow().isoformat(),
                "period": {
                    "days": days,
                    "start_date": since_date.isoformat(),
                    "end_date": datetime.utcnow().isoformat()
                },
                "subject_analysis": subject_analysis,
                "insights": insights,
                "total_subjects": len(subject_analysis)
            }
            
            # Store in database
            report_doc = {
                **report_data,
                "generated_at": datetime.utcnow(),
                "period_start": since_date,
                "period_end": datetime.utcnow()
            }
            self.reports_collection.insert_one(report_doc)
            
            # Export in requested format
            if export_format == "pdf" and PDF_AVAILABLE:
                pdf_data = self._generate_pdf_report(report_data, "subject_analytics")
                return {
                    "success": True,
                    "report_data": report_data,
                    "pdf_base64": pdf_data,
                    "format": "pdf"
                }
            elif export_format == "csv":
                csv_data = self._generate_csv_report(report_data, "subject_analytics")
                return {
                    "success": True,
                    "report_data": report_data,
                    "csv_data": csv_data,
                    "format": "csv"
                }
            else:
                return {
                    "success": True,
                    "report_data": report_data,
                    "format": "json"
                }
                
        except Exception as e:
            logger.error(f"Error generating subject analytics report: {e}")
            return {"error": str(e)}
    
    async def get_available_reports(self, educator_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of previously generated reports"""
        try:
            reports = list(
                self.reports_collection
                .find({"generated_by": educator_id})
                .sort("generated_at", -1)
                .limit(limit)
            )
            
            report_list = []
            for report in reports:
                report_list.append({
                    "report_id": report["report_id"],
                    "report_type": report["report_type"],
                    "report_title": self.report_templates.get(report["report_type"], "Unknown Report"),
                    "generated_at": report["generated_at"].isoformat(),
                    "period_days": report.get("period", {}).get("days", 0),
                    "subject_filter": report.get("period", {}).get("subject_filter"),
                    "student_count": self._get_report_student_count(report)
                })
            
            return report_list
            
        except Exception as e:
            logger.error(f"Error getting available reports: {e}")
            return []
    
    async def get_report_by_id(self, report_id: str, educator_id: str) -> Dict[str, Any]:
        """Get a specific report by ID"""
        try:
            report = self.reports_collection.find_one({
                "report_id": report_id,
                "generated_by": educator_id
            })
            
            if not report:
                return {"error": "Report not found"}
            
            # Convert datetime objects to ISO strings for JSON serialization
            report_data = dict(report)
            report_data["generated_at"] = report_data["generated_at"].isoformat()
            report_data["period_start"] = report_data["period_start"].isoformat()
            report_data["period_end"] = report_data["period_end"].isoformat()
            
            # Remove MongoDB ObjectId
            report_data.pop("_id", None)
            
            return {
                "success": True,
                "report": report_data
            }
            
        except Exception as e:
            logger.error(f"Error getting report by ID: {e}")
            return {"error": str(e)}
    
    # HELPER METHODS
    def _calculate_student_performance(self, assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics for a student"""
        if not assessments:
            return {
                "total_assessments": 0,
                "average_score": 0,
                "best_score": 0,
                "improvement_trend": "no_data"
            }
        
        scores = [assessment.get("final_score", 0) for assessment in assessments]
        
        return {
            "total_assessments": len(assessments),
            "average_score": sum(scores) / len(scores),
            "best_score": max(scores),
            "worst_score": min(scores),
            "improvement_trend": self._calculate_improvement_trend(scores),
            "subjects_studied": list(set(a.get("subject") for a in assessments if a.get("subject"))),
            "total_questions": sum(a.get("questions_answered", 0) for a in assessments),
            "total_correct": sum(a.get("questions_correct", 0) for a in assessments)
        }
    
    def _analyze_student_learning_patterns(
        self, 
        assessments: List[Dict[str, Any]], 
        content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze learning patterns for a student"""
        return {
            "assessment_frequency": len(assessments),
            "content_generation_frequency": len(content),
            "preferred_subjects": self._find_preferred_subjects(assessments),
            "learning_consistency": self._calculate_learning_consistency(assessments),
            "engagement_score": min(100, (len(assessments) * 10) + (len(content) * 5))
        }
    
    def _generate_student_recommendations(
        self, 
        performance: Dict[str, Any], 
        patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for a student"""
        recommendations = []
        
        if performance.get("average_score", 0) < 60:
            recommendations.append("Focus on fundamental concepts and consider additional practice")
        
        if performance.get("improvement_trend") == "declining":
            recommendations.append("Performance is declining - consider one-on-one tutoring")
        
        if patterns.get("engagement_score", 0) < 30:
            recommendations.append("Increase engagement through interactive activities")
        
        if len(performance.get("subjects_studied", [])) < 2:
            recommendations.append("Explore assessments in different subjects for well-rounded learning")
        
        return recommendations if recommendations else ["Continue current learning approach"]
    
    def _calculate_improvement_trend(self, scores: List[float]) -> str:
        """Calculate if student is improving, declining, or stable"""
        if len(scores) < 3:
            return "insufficient_data"
        
        recent_avg = sum(scores[-3:]) / 3
        earlier_avg = sum(scores[:3]) / 3
        
        if recent_avg > earlier_avg + 5:
            return "improving"
        elif recent_avg < earlier_avg - 5:
            return "declining"
        else:
            return "stable"
    
    def _group_content_by_type(self, content: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group content generation by type"""
        type_counts = {}
        for item in content:
            content_type = item.get("content_type", "unknown")
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        return type_counts
    
    def _find_preferred_subjects(self, assessments: List[Dict[str, Any]]) -> List[str]:
        """Find student's preferred subjects based on frequency and performance"""
        subject_data = {}
        for assessment in assessments:
            subject = assessment.get("subject")
            if subject:
                if subject not in subject_data:
                    subject_data[subject] = {"count": 0, "total_score": 0}
                subject_data[subject]["count"] += 1
                subject_data[subject]["total_score"] += assessment.get("final_score", 0)
        
        # Sort by count and average score
        sorted_subjects = sorted(
            subject_data.items(),
            key=lambda x: (x[1]["count"], x[1]["total_score"] / x[1]["count"]),
            reverse=True
        )
        
        return [subject[0] for subject in sorted_subjects[:3]]
    
    def _calculate_learning_consistency(self, assessments: List[Dict[str, Any]]) -> float:
        """Calculate how consistent the learning pattern is"""
        if not assessments:
            return 0
        
        # Calculate based on time gaps between assessments
        dates = [assessment["created_at"] for assessment in assessments]
        dates.sort()
        
        if len(dates) < 2:
            return 100
        
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        avg_gap = sum(gaps) / len(gaps)
        
        # More consistent = smaller standard deviation
        if len(gaps) > 1:
            variance = sum((gap - avg_gap) ** 2 for gap in gaps) / len(gaps)
            consistency = max(0, 100 - variance)
        else:
            consistency = 100
        
        return min(100, consistency)
    
    def _analyze_subject_trends(self, subject_analysis: List[Dict[str, Any]]) -> List[str]:
        """Analyze trends across subjects"""
        trends = []
        
        if not subject_analysis:
            return ["No data available for trend analysis"]
        
        scores = [s["average_score"] for s in subject_analysis]
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 80:
            trends.append("Overall performance is excellent across subjects")
        elif avg_score > 60:
            trends.append("Overall performance is satisfactory with room for improvement")
        else:
            trends.append("Overall performance needs attention across subjects")
        
        # Check for large performance gaps
        if max(scores) - min(scores) > 30:
            trends.append("Significant performance variation between subjects")
        
        return trends
    
    def _get_report_student_count(self, report: Dict[str, Any]) -> int:
        """Get student count from a report"""
        if report["report_type"] == "student_progress":
            return 1
        elif report["report_type"] == "class_performance":
            return report.get("class_metrics", {}).get("total_students", 0)
        else:
            return 0
    
    # EXPORT METHODS
    def _generate_pdf_report(self, report_data: Dict[str, Any], report_type: str) -> str:
        """Generate PDF report and return base64 encoded data"""
        if not PDF_AVAILABLE:
            return None
        
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph(f"IDFS PathwayIQ™ - {self.report_templates.get(report_type, 'Report')}", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Report info
            info = Paragraph(f"Generated: {report_data['generated_at']}<br/>Period: {report_data.get('period', {}).get('days', 0)} days", styles['Normal'])
            story.append(info)
            story.append(Spacer(1, 12))
            
            if report_type == "student_progress":
                self._add_student_progress_to_pdf(story, report_data, styles)
            elif report_type == "class_performance":
                self._add_class_performance_to_pdf(story, report_data, styles)
            elif report_type == "subject_analytics":
                self._add_subject_analytics_to_pdf(story, report_data, styles)
            
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return base64.b64encode(pdf_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return None
    
    def _add_student_progress_to_pdf(self, story: List, report_data: Dict[str, Any], styles):
        """Add student progress content to PDF"""
        # Student info
        student_info = report_data["student_info"]
        story.append(Paragraph(f"Student: {student_info['username']}", styles['Heading2']))
        story.append(Paragraph(f"Level: {student_info['level']} | XP: {student_info['xp']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Performance summary
        perf = report_data["performance_summary"]
        story.append(Paragraph("Performance Summary", styles['Heading2']))
        
        perf_data = [
            ["Metric", "Value"],
            ["Total Assessments", str(perf.get("total_assessments", 0))],
            ["Average Score", f"{perf.get('average_score', 0):.1f}%"],
            ["Best Score", f"{perf.get('best_score', 0):.1f}%"],
            ["Improvement Trend", perf.get("improvement_trend", "N/A")]
        ]
        
        table = Table(perf_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Recommendations
        story.append(Paragraph("Recommendations", styles['Heading2']))
        for rec in report_data.get("recommendations", []):
            story.append(Paragraph(f"• {rec}", styles['Normal']))
    
    def _add_class_performance_to_pdf(self, story: List, report_data: Dict[str, Any], styles):
        """Add class performance content to PDF"""
        metrics = report_data["class_metrics"]
        
        # Class overview
        story.append(Paragraph("Class Overview", styles['Heading2']))
        
        overview_data = [
            ["Metric", "Value"],
            ["Total Students", str(metrics["total_students"])],
            ["Total Assessments", str(metrics["total_assessments"])],
            ["Class Average", f"{metrics['class_average']:.1f}%"],
            ["Highest Score", f"{metrics['highest_score']:.1f}%"],
            ["Lowest Score", f"{metrics['lowest_score']:.1f}%"]
        ]
        
        table = Table(overview_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Grade distribution
        story.append(Paragraph("Grade Distribution", styles['Heading2']))
        
        dist_data = [["Grade", "Count"]]
        for grade, count in report_data["grade_distribution"].items():
            dist_data.append([grade, str(count)])
        
        dist_table = Table(dist_data)
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(dist_table)
    
    def _add_subject_analytics_to_pdf(self, story: List, report_data: Dict[str, Any], styles):
        """Add subject analytics content to PDF"""
        story.append(Paragraph("Subject Performance Analysis", styles['Heading2']))
        
        # Create table with subject data
        subject_data = [["Subject", "Avg Score", "Total Assessments", "Students"]]
        
        for subject in report_data["subject_analysis"]:
            subject_data.append([
                subject["subject"],
                f"{subject['average_score']:.1f}%",
                str(subject["total_assessments"]),
                str(subject["unique_students"])
            ])
        
        table = Table(subject_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Insights
        insights = report_data.get("insights", {})
        if insights:
            story.append(Paragraph("Key Insights", styles['Heading2']))
            if "best_performing_subject" in insights:
                story.append(Paragraph(f"• Best performing subject: {insights['best_performing_subject']}", styles['Normal']))
            if "most_challenging_subject" in insights:
                story.append(Paragraph(f"• Most challenging subject: {insights['most_challenging_subject']}", styles['Normal']))
            if "most_popular_subject" in insights:
                story.append(Paragraph(f"• Most popular subject: {insights['most_popular_subject']}", styles['Normal']))
    
    def _generate_csv_report(self, report_data: Dict[str, Any], report_type: str) -> str:
        """Generate CSV report and return as string"""
        try:
            output = StringIO()
            
            if report_type == "student_progress":
                self._write_student_progress_csv(output, report_data)
            elif report_type == "class_performance":
                self._write_class_performance_csv(output, report_data)
            elif report_type == "subject_analytics":
                self._write_subject_analytics_csv(output, report_data)
            
            csv_content = output.getvalue()
            output.close()
            
            return csv_content
            
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            return "Error generating CSV report"
    
    def _write_student_progress_csv(self, output: StringIO, report_data: Dict[str, Any]):
        """Write student progress data to CSV"""
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["IDFS PathwayIQ™ - Student Progress Report"])
        writer.writerow([f"Generated: {report_data['generated_at']}"])
        writer.writerow([f"Student: {report_data['student_info']['username']}"])
        writer.writerow([])
        
        # Performance Summary
        writer.writerow(["Performance Summary"])
        perf = report_data["performance_summary"]
        writer.writerow(["Total Assessments", perf.get("total_assessments", 0)])
        writer.writerow(["Average Score", f"{perf.get('average_score', 0):.1f}%"])
        writer.writerow(["Best Score", f"{perf.get('best_score', 0):.1f}%"])
        writer.writerow(["Improvement Trend", perf.get("improvement_trend", "N/A")])
        writer.writerow([])
        
        # Detailed Assessments
        writer.writerow(["Detailed Assessment History"])
        writer.writerow(["Date", "Subject", "Score", "Ability Estimate", "Questions Answered", "Questions Correct"])
        
        for assessment in report_data.get("detailed_assessments", []):
            writer.writerow([
                assessment["date"],
                assessment["subject"],
                f"{assessment['score']:.1f}%",
                f"{assessment['ability_estimate']:.2f}",
                assessment["questions_answered"],
                assessment["questions_correct"]
            ])
    
    def _write_class_performance_csv(self, output: StringIO, report_data: Dict[str, Any]):
        """Write class performance data to CSV"""
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["IDFS PathwayIQ™ - Class Performance Report"])
        writer.writerow([f"Generated: {report_data['generated_at']}"])
        writer.writerow([])
        
        # Class Metrics
        writer.writerow(["Class Overview"])
        metrics = report_data["class_metrics"]
        writer.writerow(["Total Students", metrics["total_students"]])
        writer.writerow(["Total Assessments", metrics["total_assessments"]])
        writer.writerow(["Class Average", f"{metrics['class_average']:.1f}%"])
        writer.writerow(["Highest Score", f"{metrics['highest_score']:.1f}%"])
        writer.writerow(["Lowest Score", f"{metrics['lowest_score']:.1f}%"])
        writer.writerow([])
        
        # Student Details
        writer.writerow(["Student Performance Details"])
        writer.writerow(["Student ID", "Username", "Assessment Count", "Average Score", "Best Score", "Improvement"])
        
        for student in report_data.get("student_summaries", []):
            writer.writerow([
                student["student_id"],
                student["username"],
                student["assessment_count"],
                f"{student['average_score']:.1f}%",
                f"{student['best_score']:.1f}%",
                student["improvement"]
            ])
    
    def _write_subject_analytics_csv(self, output: StringIO, report_data: Dict[str, Any]):
        """Write subject analytics data to CSV"""
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["IDFS PathwayIQ™ - Subject Analytics Report"])
        writer.writerow([f"Generated: {report_data['generated_at']}"])
        writer.writerow([])
        
        # Subject Analysis
        writer.writerow(["Subject Performance Analysis"])
        writer.writerow(["Subject", "Average Score", "Total Assessments", "Unique Students", "Highest Score", "Lowest Score"])
        
        for subject in report_data.get("subject_analysis", []):
            writer.writerow([
                subject["subject"],
                f"{subject['average_score']:.1f}%",
                subject["total_assessments"],
                subject["unique_students"],
                f"{subject['highest_score']:.1f}%",
                f"{subject['lowest_score']:.1f}%"
            ])