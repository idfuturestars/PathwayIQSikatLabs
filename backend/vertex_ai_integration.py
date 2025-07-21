"""
Google Cloud Vertex AI Integration for PathwayIQ ML Pipeline
Project ID: pathwayiq-ml-pipeline-466617
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
import asyncio
import logging

# Google Cloud imports
try:
    from google.cloud import storage
    from google.cloud import aiplatform
    import vertexai
    from vertexai.generative_models import GenerativeModel
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

logger = logging.getLogger(__name__)

class PathwayIQVertexAI:
    def __init__(self, mongo_url: str, project_id: str = "pathwayiq-ml-pipeline-466617"):
        self.project_id = project_id
        self.location = "us-central1"
        self.bucket_name = f"pathwayiq-education-data-{project_id.split('-')[-1]}"
        
        # MongoDB connection
        self.client = MongoClient(mongo_url)
        db_name = os.getenv('DB_NAME', 'idfs_pathwayiq_database')
        self.db = self.client[db_name]
        
        # Initialize Google Cloud clients
        if GOOGLE_CLOUD_AVAILABLE:
            try:
                # Initialize Vertex AI
                aiplatform.init(project=project_id, location=self.location)
                vertexai.init(project=project_id, location=self.location)
                
                # Initialize storage client
                self.storage_client = storage.Client(project=project_id)
                
                logger.info(f"✅ Google Cloud initialized for project: {project_id}")
            except Exception as e:
                logger.error(f"❌ Google Cloud initialization failed: {e}")
                self.storage_client = None
        else:
            logger.error("❌ Google Cloud libraries not available")
            self.storage_client = None
    
    async def export_educational_data_to_gcs(self) -> Dict[str, Any]:
        """Export PathwayIQ educational data to Google Cloud Storage"""
        try:
            if not self.storage_client:
                return {"error": "Google Cloud Storage not available"}
            
            # Create or get bucket
            bucket = await self._ensure_bucket_exists()
            
            # Export datasets for different ML models
            export_results = {}
            
            # 1. Student Performance Dataset
            performance_data = await self._export_performance_dataset()
            if performance_data:
                performance_file = "student_performance_dataset.csv"
                performance_data.to_csv(f"/tmp/{performance_file}", index=False)
                
                blob = bucket.blob(f"datasets/{performance_file}")
                blob.upload_from_filename(f"/tmp/{performance_file}")
                
                export_results["performance_dataset"] = {
                    "gcs_path": f"gs://{self.bucket_name}/datasets/{performance_file}",
                    "records": len(performance_data),
                    "features": list(performance_data.columns)
                }
            
            # 2. At-Risk Student Dataset
            risk_data = await self._export_risk_dataset()
            if risk_data:
                risk_file = "student_risk_dataset.csv"
                risk_data.to_csv(f"/tmp/{risk_file}", index=False)
                
                blob = bucket.blob(f"datasets/{risk_file}")
                blob.upload_from_filename(f"/tmp/{risk_file}")
                
                export_results["risk_dataset"] = {
                    "gcs_path": f"gs://{self.bucket_name}/datasets/{risk_file}",
                    "records": len(risk_data),
                    "features": list(risk_data.columns)
                }
            
            # 3. Engagement Prediction Dataset
            engagement_data = await self._export_engagement_dataset()
            if engagement_data:
                engagement_file = "student_engagement_dataset.csv"
                engagement_data.to_csv(f"/tmp/{engagement_file}", index=False)
                
                blob = bucket.blob(f"datasets/{engagement_file}")
                blob.upload_from_filename(f"/tmp/{engagement_file}")
                
                export_results["engagement_dataset"] = {
                    "gcs_path": f"gs://{self.bucket_name}/datasets/{engagement_file}",
                    "records": len(engagement_data),
                    "features": list(engagement_data.columns)
                }
            
            logger.info(f"✅ Educational data exported to GCS: {export_results}")
            return {
                "success": True,
                "bucket": self.bucket_name,
                "datasets": export_results,
                "project_id": self.project_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error exporting data to GCS: {e}")
            return {"error": str(e)}
    
    async def _ensure_bucket_exists(self):
        """Create or get the GCS bucket"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket = self.storage_client.create_bucket(
                    self.bucket_name, 
                    location=self.location
                )
                logger.info(f"✅ Created bucket: {self.bucket_name}")
            else:
                logger.info(f"✅ Using existing bucket: {self.bucket_name}")
            
            return bucket
            
        except Exception as e:
            logger.error(f"❌ Error with bucket: {e}")
            raise
    
    async def _export_performance_dataset(self) -> Optional[pd.DataFrame]:
        """Export student performance prediction dataset"""
        try:
            # Get assessments with user context
            pipeline = [
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "user_id",
                        "foreignField": "id",
                        "as": "user_info"
                    }
                },
                {
                    "$unwind": "$user_info"
                },
                {
                    "$project": {
                        "user_id": 1,
                        "final_score": 1,
                        "final_ability_estimate": 1,
                        "questions_answered": 1,
                        "questions_correct": 1,
                        "subject": 1,
                        "assessment_type": 1,
                        "created_at": 1,
                        "user_level": "$user_info.level",
                        "user_xp": "$user_info.xp",
                        "user_role": "$user_info.role"
                    }
                }
            ]
            
            assessments = list(self.db.assessments.aggregate(pipeline))
            
            if not assessments:
                logger.warning("No assessment data found for performance dataset")
                return None
            
            df = pd.DataFrame(assessments)
            
            # Feature engineering for ML
            df['accuracy_rate'] = df['questions_correct'] / df['questions_answered'].replace(0, 1)
            df['efficiency'] = df['final_score'] / df['questions_answered'].replace(0, 1)
            df['day_of_week'] = pd.to_datetime(df['created_at']).dt.dayofweek
            df['hour_of_day'] = pd.to_datetime(df['created_at']).dt.hour
            
            # Create target variable (high performance: score >= 80)
            df['high_performance'] = (df['final_score'] >= 80).astype(int)
            
            # Select features for ML model
            feature_columns = [
                'user_level', 'user_xp', 'questions_answered',
                'accuracy_rate', 'efficiency', 'day_of_week', 'hour_of_day',
                'final_ability_estimate', 'high_performance'
            ]
            
            # Filter and clean data
            df_ml = df[feature_columns].dropna()
            
            logger.info(f"✅ Performance dataset prepared: {len(df_ml)} records")
            return df_ml
            
        except Exception as e:
            logger.error(f"❌ Error preparing performance dataset: {e}")
            return None
    
    async def _export_risk_dataset(self) -> Optional[pd.DataFrame]:
        """Export at-risk student identification dataset"""
        try:
            # Aggregate user performance data
            pipeline = [
                {
                    "$group": {
                        "_id": "$user_id",
                        "avg_score": {"$avg": "$final_score"},
                        "assessment_count": {"$sum": 1},
                        "total_questions": {"$sum": "$questions_answered"},
                        "total_correct": {"$sum": "$questions_correct"},
                        "latest_assessment": {"$max": "$created_at"},
                        "subjects": {"$addToSet": "$subject"}
                    }
                },
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "_id",
                        "foreignField": "id",
                        "as": "user_info"
                    }
                },
                {
                    "$unwind": "$user_info"
                }
            ]
            
            user_stats = list(self.db.assessments.aggregate(pipeline))
            
            if not user_stats:
                logger.warning("No user statistics found for risk dataset")
                return None
            
            # Create risk dataset
            risk_data = []
            for user_stat in user_stats:
                overall_accuracy = user_stat['total_correct'] / max(user_stat['total_questions'], 1)
                days_since_last = (datetime.utcnow() - user_stat['latest_assessment']).days
                
                # Risk criteria: avg_score < 60 OR low engagement (< 5 assessments and > 30 days inactive)
                is_at_risk = (
                    user_stat['avg_score'] < 60 or 
                    (user_stat['assessment_count'] < 5 and days_since_last > 30)
                )
                
                risk_data.append({
                    'user_level': user_stat['user_info']['level'],
                    'user_xp': user_stat['user_info']['xp'],
                    'avg_score': user_stat['avg_score'],
                    'assessment_count': user_stat['assessment_count'],
                    'overall_accuracy': overall_accuracy,
                    'subject_diversity': len(user_stat['subjects']),
                    'days_since_last': days_since_last,
                    'at_risk': int(is_at_risk)
                })
            
            df_risk = pd.DataFrame(risk_data)
            
            logger.info(f"✅ Risk dataset prepared: {len(df_risk)} records")
            logger.info(f"At-risk distribution: {df_risk['at_risk'].value_counts().to_dict()}")
            
            return df_risk
            
        except Exception as e:
            logger.error(f"❌ Error preparing risk dataset: {e}")
            return None
    
    async def _export_engagement_dataset(self) -> Optional[pd.DataFrame]:
        """Export student engagement prediction dataset"""
        try:
            # Get content generation and assessment activity
            content_activity = list(self.db.content_generation.aggregate([
                {
                    "$group": {
                        "_id": "$user_id",
                        "content_count": {"$sum": 1},
                        "avg_quality": {"$avg": "$quality_score"},
                        "total_usage": {"$sum": "$usage_count"}
                    }
                }
            ]))
            
            assessment_activity = list(self.db.assessments.aggregate([
                {
                    "$group": {
                        "_id": "$user_id",
                        "assessment_count": {"$sum": 1},
                        "avg_score": {"$avg": "$final_score"}
                    }
                }
            ]))
            
            # Merge activity data
            user_engagement = {}
            
            for content in content_activity:
                user_id = content['_id']
                user_engagement[user_id] = {
                    'user_id': user_id,
                    'content_count': content['content_count'],
                    'avg_content_quality': content['avg_quality'],
                    'total_content_usage': content['total_usage'],
                    'assessment_count': 0,
                    'avg_assessment_score': 0
                }
            
            for assessment in assessment_activity:
                user_id = assessment['_id']
                if user_id in user_engagement:
                    user_engagement[user_id]['assessment_count'] = assessment['assessment_count']
                    user_engagement[user_id]['avg_assessment_score'] = assessment['avg_score']
                else:
                    user_engagement[user_id] = {
                        'user_id': user_id,
                        'content_count': 0,
                        'avg_content_quality': 0,
                        'total_content_usage': 0,
                        'assessment_count': assessment['assessment_count'],
                        'avg_assessment_score': assessment['avg_score']
                    }
            
            if not user_engagement:
                logger.warning("No engagement data found")
                return None
            
            # Create engagement score and dataset
            engagement_data = []
            for user_data in user_engagement.values():
                # Calculate engagement score (0-100)
                engagement_score = min(100, 
                    (user_data['assessment_count'] * 10) + 
                    (user_data['content_count'] * 5) + 
                    (user_data['total_content_usage'] * 2)
                )
                
                engagement_data.append({
                    'assessment_frequency': user_data['assessment_count'],
                    'content_creation': user_data['content_count'],
                    'avg_assessment_score': user_data['avg_assessment_score'],
                    'avg_content_quality': user_data['avg_content_quality'],
                    'content_usage': user_data['total_content_usage'],
                    'engagement_score': engagement_score
                })
            
            df_engagement = pd.DataFrame(engagement_data)
            
            logger.info(f"✅ Engagement dataset prepared: {len(df_engagement)} records")
            return df_engagement
            
        except Exception as e:
            logger.error(f"❌ Error preparing engagement dataset: {e}")
            return None
    
    async def create_vertex_ai_models(self, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create and train Vertex AI AutoML models"""
        try:
            if not GOOGLE_CLOUD_AVAILABLE:
                return {"error": "Google Cloud libraries not available"}
            
            training_results = {}
            
            # 1. Performance Prediction Model
            if "performance_dataset" in dataset_info:
                performance_result = await self._train_performance_model(
                    dataset_info["performance_dataset"]["gcs_path"]
                )
                training_results["performance_model"] = performance_result
            
            # 2. Risk Assessment Model
            if "risk_dataset" in dataset_info:
                risk_result = await self._train_risk_model(
                    dataset_info["risk_dataset"]["gcs_path"]
                )
                training_results["risk_model"] = risk_result
            
            # 3. Engagement Prediction Model
            if "engagement_dataset" in dataset_info:
                engagement_result = await self._train_engagement_model(
                    dataset_info["engagement_dataset"]["gcs_path"]
                )
                training_results["engagement_model"] = engagement_result
            
            return {
                "success": True,
                "training_jobs": training_results,
                "project_id": self.project_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating Vertex AI models: {e}")
            return {"error": str(e)}
    
    async def _train_performance_model(self, gcs_path: str) -> Dict[str, Any]:
        """Train student performance prediction model"""
        try:
            # Create dataset
            dataset = aiplatform.TabularDataset.create(
                display_name="pathwayiq_performance_dataset",
                gcs_source=gcs_path
            )
            
            # Create AutoML training job
            training_job = aiplatform.AutoMLTabularTrainingJob(
                display_name="pathwayiq_performance_prediction",
                optimization_prediction_type="classification",
                optimization_objective="maximize-au-prc"
            )
            
            # Start training (this will run asynchronously)
            model = training_job.run(
                dataset=dataset,
                target_column="high_performance",
                training_fraction_split=0.8,
                validation_fraction_split=0.1,
                test_fraction_split=0.1,
                model_display_name="pathwayiq_performance_model"
            )
            
            return {
                "model_resource_name": model.resource_name,
                "training_job": training_job.resource_name,
                "dataset": dataset.resource_name,
                "status": "training_started"
            }
            
        except Exception as e:
            logger.error(f"❌ Error training performance model: {e}")
            return {"error": str(e)}
    
    async def _train_risk_model(self, gcs_path: str) -> Dict[str, Any]:
        """Train at-risk student identification model"""
        try:
            # Create dataset
            dataset = aiplatform.TabularDataset.create(
                display_name="pathwayiq_risk_dataset",
                gcs_source=gcs_path
            )
            
            # Create AutoML training job
            training_job = aiplatform.AutoMLTabularTrainingJob(
                display_name="pathwayiq_risk_assessment",
                optimization_prediction_type="classification",
                optimization_objective="maximize-au-prc"
            )
            
            # Start training
            model = training_job.run(
                dataset=dataset,
                target_column="at_risk",
                training_fraction_split=0.8,
                validation_fraction_split=0.1,
                test_fraction_split=0.1,
                model_display_name="pathwayiq_risk_model"
            )
            
            return {
                "model_resource_name": model.resource_name,
                "training_job": training_job.resource_name,
                "dataset": dataset.resource_name,
                "status": "training_started"
            }
            
        except Exception as e:
            logger.error(f"❌ Error training risk model: {e}")
            return {"error": str(e)}
    
    async def _train_engagement_model(self, gcs_path: str) -> Dict[str, Any]:
        """Train student engagement prediction model"""
        try:
            # Create dataset
            dataset = aiplatform.TabularDataset.create(
                display_name="pathwayiq_engagement_dataset",
                gcs_source=gcs_path
            )
            
            # Create AutoML training job
            training_job = aiplatform.AutoMLTabularTrainingJob(
                display_name="pathwayiq_engagement_prediction",
                optimization_prediction_type="regression",
                optimization_objective="minimize-rmse"
            )
            
            # Start training
            model = training_job.run(
                dataset=dataset,
                target_column="engagement_score",
                training_fraction_split=0.8,
                validation_fraction_split=0.1,
                test_fraction_split=0.1,
                model_display_name="pathwayiq_engagement_model"
            )
            
            return {
                "model_resource_name": model.resource_name,
                "training_job": training_job.resource_name,
                "dataset": dataset.resource_name,
                "status": "training_started"
            }
            
        except Exception as e:
            logger.error(f"❌ Error training engagement model: {e}")
            return {"error": str(e)}

# Initialize PathwayIQ Vertex AI integration
def get_vertex_ai_integration(mongo_url: str, project_id: str = "pathwayiq-ml-pipeline-466617") -> PathwayIQVertexAI:
    """Get or create PathwayIQ Vertex AI integration instance"""
    return PathwayIQVertexAI(mongo_url, project_id)