"""
Predictive Analytics Engine for Learning Outcomes
Uses ML models to predict student success, performance, and learning outcomes
"""
import os
import uuid
import logging
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import xgboost as xgb
import joblib
from pymongo import MongoClient
from collections import defaultdict

logger = logging.getLogger(__name__)

class PredictiveAnalytics:
    def __init__(self, mongo_url: str):
        self.client = MongoClient(mongo_url)
        db_name = os.getenv('DB_NAME', 'idfs_pathwayiq_database')
        self.db = self.client[db_name]
        
        # Collections
        self.users_collection = self.db.users
        self.assessments_collection = self.db.assessments
        self.content_collection = self.db.content_generation
        self.groups_collection = self.db.study_groups
        self.messages_collection = self.db.group_messages
        self.predictions_collection = self.db.predictions
        
        # Model storage
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
        # Model paths
        self.model_dir = "/tmp/ml_models"
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initialize models
        self.model_configs = {
            "performance_predictor": {
                "model_type": "regression",
                "algorithm": "random_forest",
                "target": "final_score"
            },
            "success_classifier": {
                "model_type": "classification", 
                "algorithm": "gradient_boosting",
                "target": "success_category"
            },
            "risk_assessor": {
                "model_type": "classification",
                "algorithm": "xgboost",
                "target": "at_risk"
            },
            "engagement_predictor": {
                "model_type": "regression",
                "algorithm": "linear_regression",
                "target": "engagement_score"
            }
        }
    
    # DATA PREPARATION
    async def prepare_training_data(self) -> Dict[str, pd.DataFrame]:
        """Prepare training datasets for ML models"""
        try:
            logger.info("Preparing training data for ML models...")
            
            # Get all historical data
            users = list(self.users_collection.find())
            assessments = list(self.assessments_collection.find())
            content = list(self.content_collection.find())
            
            # Create user features dataset
            user_features = self._create_user_features(users, assessments, content)
            
            # Create assessment features dataset  
            assessment_features = self._create_assessment_features(assessments, users)
            
            # Create engagement features dataset
            engagement_features = self._create_engagement_features(users, assessments, content)
            
            return {
                "user_features": user_features,
                "assessment_features": assessment_features,
                "engagement_features": engagement_features
            }
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return {}
    
    def _create_user_features(
        self, 
        users: List[Dict], 
        assessments: List[Dict], 
        content: List[Dict]
    ) -> pd.DataFrame:
        """Create user-level features for prediction"""
        user_data = []
        
        for user in users:
            user_id = user["id"]
            
            # Get user assessments
            user_assessments = [a for a in assessments if a["user_id"] == user_id]
            user_content = [c for c in content if c["user_id"] == user_id]
            
            if not user_assessments:
                continue
            
            # Basic user features
            features = {
                "user_id": user_id,
                "level": user.get("level", 1),
                "xp": user.get("xp", 0),
                "role": user.get("role", "student"),
                
                # Assessment history features
                "total_assessments": len(user_assessments),
                "avg_score": np.mean([a.get("final_score", 0) for a in user_assessments]),
                "score_std": np.std([a.get("final_score", 0) for a in user_assessments]),
                "best_score": max([a.get("final_score", 0) for a in user_assessments]),
                "worst_score": min([a.get("final_score", 0) for a in user_assessments]),
                
                # Learning patterns
                "subjects_studied": len(set(a.get("subject") for a in user_assessments if a.get("subject"))),
                "avg_questions_answered": np.mean([a.get("questions_answered", 0) for a in user_assessments]),
                "avg_questions_correct": np.mean([a.get("questions_correct", 0) for a in user_assessments]),
                
                # Content generation features
                "total_content": len(user_content),
                "content_diversity": len(set(c.get("content_type") for c in user_content if c.get("content_type"))),
                
                # Time-based features
                "days_active": self._calculate_active_days(user_assessments),
                "avg_session_gap": self._calculate_avg_session_gap(user_assessments),
                
                # Performance trends
                "improvement_trend": self._calculate_improvement_trend([a.get("final_score", 0) for a in user_assessments]),
                "consistency_score": self._calculate_consistency_score([a.get("final_score", 0) for a in user_assessments]),
                
                # Target variables
                "success_category": self._classify_success_level(np.mean([a.get("final_score", 0) for a in user_assessments])),
                "at_risk": 1 if np.mean([a.get("final_score", 0) for a in user_assessments]) < 60 else 0,
                "engagement_score": min(100, len(user_assessments) * 10 + len(user_content) * 5)
            }
            
            user_data.append(features)
        
        return pd.DataFrame(user_data)
    
    def _create_assessment_features(
        self, 
        assessments: List[Dict], 
        users: List[Dict]
    ) -> pd.DataFrame:
        """Create assessment-level features for prediction"""
        assessment_data = []
        user_map = {u["id"]: u for u in users}
        
        for assessment in assessments:
            user = user_map.get(assessment["user_id"])
            if not user:
                continue
            
            features = {
                "assessment_id": assessment.get("id", str(uuid.uuid4())),
                "user_id": assessment["user_id"],
                "subject": assessment.get("subject", "unknown"),
                "assessment_type": assessment.get("assessment_type", "standard"),
                
                # User context features
                "user_level": user.get("level", 1),
                "user_xp": user.get("xp", 0),
                
                # Assessment features
                "questions_answered": assessment.get("questions_answered", 0),
                "questions_correct": assessment.get("questions_correct", 0),
                "final_ability_estimate": assessment.get("final_ability_estimate", 0),
                
                # Time features
                "day_of_week": assessment.get("created_at", datetime.now()).weekday(),
                "hour_of_day": assessment.get("created_at", datetime.now()).hour,
                
                # Target
                "final_score": assessment.get("final_score", 0)
            }
            
            assessment_data.append(features)
        
        return pd.DataFrame(assessment_data)
    
    def _create_engagement_features(
        self, 
        users: List[Dict], 
        assessments: List[Dict], 
        content: List[Dict]
    ) -> pd.DataFrame:
        """Create engagement prediction features"""
        engagement_data = []
        
        for user in users:
            user_id = user["id"]
            user_assessments = [a for a in assessments if a["user_id"] == user_id]
            user_content = [c for c in content if c["user_id"] == user_id]
            
            features = {
                "user_id": user_id,
                "level": user.get("level", 1),
                "xp": user.get("xp", 0),
                
                # Activity features
                "assessments_last_7_days": len([a for a in user_assessments 
                    if (datetime.now() - a.get("created_at", datetime.now())).days <= 7]),
                "assessments_last_30_days": len([a for a in user_assessments 
                    if (datetime.now() - a.get("created_at", datetime.now())).days <= 30]),
                "content_last_7_days": len([c for c in user_content 
                    if (datetime.now() - c.get("created_at", datetime.now())).days <= 7]),
                
                # Performance features
                "recent_avg_score": np.mean([a.get("final_score", 0) for a in user_assessments[-5:]]) if user_assessments else 0,
                "score_trend": self._calculate_recent_trend(user_assessments),
                
                # Target - engagement score
                "engagement_score": min(100, len(user_assessments) * 10 + len(user_content) * 5)
            }
            
            engagement_data.append(features)
        
        return pd.DataFrame(engagement_data)
    
    # HELPER METHODS FOR FEATURE ENGINEERING
    def _calculate_active_days(self, assessments: List[Dict]) -> int:
        """Calculate number of unique days user was active"""
        if not assessments:
            return 0
        
        dates = set()
        for assessment in assessments:
            date = assessment.get("created_at", datetime.now()).date()
            dates.add(date)
        
        return len(dates)
    
    def _calculate_avg_session_gap(self, assessments: List[Dict]) -> float:
        """Calculate average gap between learning sessions"""
        if len(assessments) < 2:
            return 0
        
        dates = sorted([a.get("created_at", datetime.now()) for a in assessments])
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        
        return np.mean(gaps) if gaps else 0
    
    def _calculate_improvement_trend(self, scores: List[float]) -> float:
        """Calculate improvement trend from scores"""
        if len(scores) < 3:
            return 0
        
        # Simple linear regression slope
        x = np.arange(len(scores))
        y = np.array(scores)
        
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            return slope
        else:
            return 0
    
    def _calculate_consistency_score(self, scores: List[float]) -> float:
        """Calculate how consistent the performance is"""
        if len(scores) < 2:
            return 100
        
        # Lower std deviation = higher consistency
        std = np.std(scores)
        consistency = max(0, 100 - std)
        return consistency
    
    def _classify_success_level(self, avg_score: float) -> str:
        """Classify student success level"""
        if avg_score >= 90:
            return "excellent"
        elif avg_score >= 80:
            return "good"
        elif avg_score >= 70:
            return "satisfactory"
        elif avg_score >= 60:
            return "needs_improvement"
        else:
            return "at_risk"
    
    def _calculate_recent_trend(self, assessments: List[Dict]) -> float:
        """Calculate recent performance trend"""
        if len(assessments) < 3:
            return 0
        
        recent_scores = [a.get("final_score", 0) for a in assessments[-5:]]
        if len(recent_scores) >= 2:
            return recent_scores[-1] - recent_scores[0]
        else:
            return 0
    
    # MODEL TRAINING
    async def train_models(self) -> Dict[str, Any]:
        """Train all ML models"""
        try:
            logger.info("Starting ML model training...")
            
            # Prepare training data
            datasets = await self.prepare_training_data()
            
            if not datasets:
                return {"error": "No training data available"}
            
            training_results = {}
            
            # Train performance predictor
            perf_result = await self._train_performance_predictor(datasets["assessment_features"])
            training_results["performance_predictor"] = perf_result
            
            # Train success classifier
            success_result = await self._train_success_classifier(datasets["user_features"])
            training_results["success_classifier"] = success_result
            
            # Train risk assessor
            risk_result = await self._train_risk_assessor(datasets["user_features"])
            training_results["risk_assessor"] = risk_result
            
            # Train engagement predictor
            engagement_result = await self._train_engagement_predictor(datasets["engagement_features"])
            training_results["engagement_predictor"] = engagement_result
            
            logger.info("ML model training completed")
            return {
                "success": True,
                "results": training_results,
                "models_trained": len([r for r in training_results.values() if r.get("success")])
            }
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {"error": str(e)}
    
    async def _train_performance_predictor(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train model to predict assessment performance"""
        try:
            if df.empty or len(df) < 10:
                return {"success": False, "error": "Insufficient data"}
            
            # Prepare features and target
            feature_cols = ["user_level", "user_xp", "questions_answered", 
                          "day_of_week", "hour_of_day", "final_ability_estimate"]
            
            # Check if all feature columns exist
            available_cols = [col for col in feature_cols if col in df.columns]
            if len(available_cols) < 3:
                return {"success": False, "error": "Insufficient feature columns"}
            
            X = df[available_cols].fillna(0)
            y = df["final_score"].fillna(0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # Save model
            model_path = f"{self.model_dir}/performance_predictor.pkl"
            scaler_path = f"{self.model_dir}/performance_predictor_scaler.pkl"
            
            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)
            
            # Store in memory
            self.models["performance_predictor"] = model
            self.scalers["performance_predictor"] = scaler
            
            return {
                "success": True,
                "rmse": rmse,
                "features_used": available_cols,
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error training performance predictor: {e}")
            return {"success": False, "error": str(e)}
    
    async def _train_success_classifier(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train model to classify student success level"""
        try:
            if df.empty or len(df) < 10:
                return {"success": False, "error": "Insufficient data"}
            
            # Prepare features and target
            feature_cols = ["level", "xp", "total_assessments", "avg_score", 
                          "subjects_studied", "total_content", "days_active"]
            
            available_cols = [col for col in feature_cols if col in df.columns]
            if len(available_cols) < 3:
                return {"success": False, "error": "Insufficient feature columns"}
            
            X = df[available_cols].fillna(0)
            y = df["success_category"].fillna("at_risk")
            
            # Encode target labels
            encoder = LabelEncoder()
            y_encoded = encoder.fit_transform(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = GradientBoostingClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=6
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save model and encoder
            model_path = f"{self.model_dir}/success_classifier.pkl"
            scaler_path = f"{self.model_dir}/success_classifier_scaler.pkl"
            encoder_path = f"{self.model_dir}/success_classifier_encoder.pkl"
            
            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)
            joblib.dump(encoder, encoder_path)
            
            # Store in memory
            self.models["success_classifier"] = model
            self.scalers["success_classifier"] = scaler
            self.encoders["success_classifier"] = encoder
            
            return {
                "success": True,
                "accuracy": accuracy,
                "classes": encoder.classes_.tolist(),
                "features_used": available_cols,
                "training_samples": len(X_train)
            }
            
        except Exception as e:
            logger.error(f"Error training success classifier: {e}")
            return {"success": False, "error": str(e)}
    
    async def _train_risk_assessor(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train model to assess student at-risk status"""
        try:
            if df.empty or len(df) < 10:
                return {"success": False, "error": "Insufficient data"}
            
            # Prepare features and target
            feature_cols = ["level", "avg_score", "score_std", "total_assessments",
                          "improvement_trend", "consistency_score", "days_active"]
            
            available_cols = [col for col in feature_cols if col in df.columns]
            if len(available_cols) < 3:
                return {"success": False, "error": "Insufficient feature columns"}
            
            X = df[available_cols].fillna(0)
            y = df["at_risk"].fillna(0)
            
            # Check class distribution
            if len(y.unique()) < 2:
                return {"success": False, "error": "Insufficient class variation"}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train XGBoost model
            model = xgb.XGBClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=6,
                learning_rate=0.1
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save model
            model_path = f"{self.model_dir}/risk_assessor.pkl"
            scaler_path = f"{self.model_dir}/risk_assessor_scaler.pkl"
            
            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)
            
            # Store in memory
            self.models["risk_assessor"] = model
            self.scalers["risk_assessor"] = scaler
            
            return {
                "success": True,
                "accuracy": accuracy,
                "features_used": available_cols,
                "training_samples": len(X_train),
                "at_risk_ratio": y.mean()
            }
            
        except Exception as e:
            logger.error(f"Error training risk assessor: {e}")
            return {"success": False, "error": str(e)}
    
    async def _train_engagement_predictor(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train model to predict student engagement"""
        try:
            if df.empty or len(df) < 10:
                return {"success": False, "error": "Insufficient data"}
            
            # Prepare features and target
            feature_cols = ["level", "xp", "assessments_last_7_days", 
                          "assessments_last_30_days", "recent_avg_score", "score_trend"]
            
            available_cols = [col for col in feature_cols if col in df.columns]
            if len(available_cols) < 3:
                return {"success": False, "error": "Insufficient feature columns"}
            
            X = df[available_cols].fillna(0)
            y = df["engagement_score"].fillna(0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = LinearRegression()
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # Save model
            model_path = f"{self.model_dir}/engagement_predictor.pkl"
            scaler_path = f"{self.model_dir}/engagement_predictor_scaler.pkl"
            
            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)
            
            # Store in memory
            self.models["engagement_predictor"] = model
            self.scalers["engagement_predictor"] = scaler
            
            return {
                "success": True,
                "rmse": rmse,
                "features_used": available_cols,
                "training_samples": len(X_train)
            }
            
        except Exception as e:
            logger.error(f"Error training engagement predictor: {e}")
            return {"success": False, "error": str(e)}
    
    # PREDICTION METHODS
    async def predict_student_performance(
        self, 
        user_id: str, 
        subject: str = "mathematics",
        questions_count: int = 10
    ) -> Dict[str, Any]:
        """Predict student performance on upcoming assessment"""
        try:
            # Get user data
            user = self.users_collection.find_one({"id": user_id})
            if not user:
                return {"error": "User not found"}
            
            # Get user's assessment history
            assessments = list(self.assessments_collection.find({
                "user_id": user_id
            }).sort("created_at", -1).limit(10))
            
            if not assessments:
                return {
                    "predicted_score": 75.0,  # Default prediction
                    "confidence": "low",
                    "reasoning": "No assessment history available"
                }
            
            # Load model
            model = await self._load_model("performance_predictor")
            if not model:
                return {"error": "Prediction model not available"}
            
            # Prepare features
            recent_ability = np.mean([a.get("final_ability_estimate", 0) for a in assessments[:3]])
            
            features = np.array([[
                user.get("level", 1),
                user.get("xp", 0),
                questions_count,
                datetime.now().weekday(),  # day of week
                datetime.now().hour,       # hour of day
                recent_ability
            ]])
            
            # Scale features
            scaler = self.scalers.get("performance_predictor")
            if scaler:
                features = scaler.transform(features)
            
            # Make prediction
            predicted_score = float(model.predict(features)[0])
            predicted_score = max(0, min(100, predicted_score))  # Clip to valid range
            
            # Calculate confidence based on model certainty and user history
            confidence = self._calculate_prediction_confidence(assessments, predicted_score)
            
            # Generate reasoning
            reasoning = self._generate_performance_reasoning(user, assessments, predicted_score)
            
            # Store prediction
            prediction_doc = {
                "prediction_id": str(uuid.uuid4()),
                "user_id": user_id,
                "prediction_type": "performance",
                "predicted_score": predicted_score,
                "confidence": confidence,
                "subject": subject,
                "features_used": {
                    "level": user.get("level", 1),
                    "xp": user.get("xp", 0),
                    "questions_count": questions_count,
                    "recent_ability": recent_ability
                },
                "created_at": datetime.utcnow()
            }
            self.predictions_collection.insert_one(prediction_doc)
            
            return {
                "predicted_score": round(predicted_score, 1),
                "confidence": confidence,
                "reasoning": reasoning,
                "subject": subject,
                "prediction_id": prediction_doc["prediction_id"]
            }
            
        except Exception as e:
            logger.error(f"Error predicting student performance: {e}")
            return {"error": str(e)}
    
    async def assess_student_risk(self, user_id: str) -> Dict[str, Any]:
        """Assess if student is at risk of poor performance"""
        try:
            # Get user data
            user = self.users_collection.find_one({"id": user_id})
            if not user:
                return {"error": "User not found"}
            
            # Get user's assessment history
            assessments = list(self.assessments_collection.find({
                "user_id": user_id
            }).sort("created_at", -1))
            
            if len(assessments) < 3:
                return {
                    "risk_level": "unknown",
                    "risk_probability": 0.5,
                    "reasoning": "Insufficient assessment history for accurate risk assessment"
                }
            
            # Load model
            model = await self._load_model("risk_assessor")
            if not model:
                return {"error": "Risk assessment model not available"}
            
            # Calculate features
            scores = [a.get("final_score", 0) for a in assessments]
            avg_score = np.mean(scores)
            score_std = np.std(scores)
            improvement_trend = self._calculate_improvement_trend(scores)
            consistency_score = self._calculate_consistency_score(scores)
            days_active = self._calculate_active_days(assessments)
            
            features = np.array([[
                user.get("level", 1),
                avg_score,
                score_std,
                len(assessments),
                improvement_trend,
                consistency_score,
                days_active
            ]])
            
            # Scale features
            scaler = self.scalers.get("risk_assessor")
            if scaler:
                features = scaler.transform(features)
            
            # Make prediction
            risk_probability = float(model.predict_proba(features)[0][1])  # Probability of being at-risk
            
            # Classify risk level
            if risk_probability > 0.7:
                risk_level = "high"
            elif risk_probability > 0.4:
                risk_level = "medium" 
            else:
                risk_level = "low"
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(user, assessments, risk_level, risk_probability)
            
            # Store assessment
            assessment_doc = {
                "assessment_id": str(uuid.uuid4()),
                "user_id": user_id,
                "assessment_type": "risk",
                "risk_level": risk_level,
                "risk_probability": risk_probability,
                "features_used": {
                    "avg_score": avg_score,
                    "score_std": score_std,
                    "improvement_trend": improvement_trend,
                    "consistency_score": consistency_score
                },
                "recommendations": recommendations,
                "created_at": datetime.utcnow()
            }
            self.predictions_collection.insert_one(assessment_doc)
            
            return {
                "risk_level": risk_level,
                "risk_probability": round(risk_probability, 3),
                "recommendations": recommendations,
                "assessment_id": assessment_doc["assessment_id"]
            }
            
        except Exception as e:
            logger.error(f"Error assessing student risk: {e}")
            return {"error": str(e)}
    
    async def predict_learning_outcomes(
        self, 
        user_id: str, 
        target_days: int = 30
    ) -> Dict[str, Any]:
        """Predict learning outcomes over specified time period"""
        try:
            # Get user data
            user = self.users_collection.find_one({"id": user_id})
            if not user:
                return {"error": "User not found"}
            
            # Get historical data
            assessments = list(self.assessments_collection.find({
                "user_id": user_id
            }).sort("created_at", -1))
            
            content_generated = list(self.content_collection.find({
                "user_id": user_id
            }))
            
            if not assessments:
                return {
                    "predicted_outcomes": {
                        "expected_assessments": 2,
                        "expected_avg_score": 70.0,
                        "skill_improvement": "moderate",
                        "engagement_level": "medium"
                    },
                    "confidence": "low",
                    "reasoning": "No historical data available"
                }
            
            # Load models
            performance_model = await self._load_model("performance_predictor")
            engagement_model = await self._load_model("engagement_predictor")
            
            # Calculate current patterns
            recent_assessments = [a for a in assessments 
                                if (datetime.now() - a.get("created_at", datetime.now())).days <= 30]
            
            current_frequency = len(recent_assessments) / 30 * target_days  # Scale to target period
            avg_recent_score = np.mean([a.get("final_score", 0) for a in recent_assessments]) if recent_assessments else 70
            
            # Predict future engagement
            if engagement_model:
                engagement_features = np.array([[
                    user.get("level", 1),
                    user.get("xp", 0),
                    len([a for a in recent_assessments if (datetime.now() - a.get("created_at", datetime.now())).days <= 7]),
                    len(recent_assessments),
                    avg_recent_score,
                    self._calculate_recent_trend(assessments)
                ]])
                
                scaler = self.scalers.get("engagement_predictor")
                if scaler:
                    engagement_features = scaler.transform(engagement_features)
                
                predicted_engagement = float(engagement_model.predict(engagement_features)[0])
            else:
                predicted_engagement = 50.0
            
            # Generate predictions
            predictions = {
                "expected_assessments": max(1, int(current_frequency)),
                "expected_avg_score": round(avg_recent_score + np.random.normal(0, 3), 1),
                "predicted_engagement": round(predicted_engagement, 1),
                "skill_improvement": self._classify_improvement_level(avg_recent_score, len(recent_assessments)),
                "learning_velocity": self._calculate_learning_velocity(assessments),
                "subject_recommendations": self._recommend_subjects(assessments)
            }
            
            # Calculate confidence
            confidence = "high" if len(recent_assessments) > 5 else "medium" if len(assessments) > 3 else "low"
            
            # Generate reasoning
            reasoning = f"Based on {len(assessments)} historical assessments and recent activity patterns. " \
                       f"Current performance trend shows {self._get_trend_description(assessments)}."
            
            return {
                "predicted_outcomes": predictions,
                "confidence": confidence,
                "reasoning": reasoning,
                "target_period_days": target_days
            }
            
        except Exception as e:
            logger.error(f"Error predicting learning outcomes: {e}")
            return {"error": str(e)}
    
    # HELPER METHODS FOR PREDICTIONS
    async def _load_model(self, model_name: str):
        """Load ML model from memory or disk"""
        if model_name in self.models:
            return self.models[model_name]
        
        try:
            model_path = f"{self.model_dir}/{model_name}.pkl"
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                self.models[model_name] = model
                
                # Load associated scaler
                scaler_path = f"{self.model_dir}/{model_name}_scaler.pkl"
                if os.path.exists(scaler_path):
                    scaler = joblib.load(scaler_path)
                    self.scalers[model_name] = scaler
                
                # Load associated encoder
                encoder_path = f"{self.model_dir}/{model_name}_encoder.pkl"
                if os.path.exists(encoder_path):
                    encoder = joblib.load(encoder_path)
                    self.encoders[model_name] = encoder
                
                return model
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
        
        return None
    
    def _calculate_prediction_confidence(
        self, 
        assessments: List[Dict], 
        predicted_score: float
    ) -> str:
        """Calculate confidence level for prediction"""
        if len(assessments) < 3:
            return "low"
        
        recent_scores = [a.get("final_score", 0) for a in assessments[:5]]
        score_variance = np.var(recent_scores)
        
        # Lower variance = higher confidence
        if score_variance < 50:
            return "high"
        elif score_variance < 150:
            return "medium"
        else:
            return "low"
    
    def _generate_performance_reasoning(
        self, 
        user: Dict, 
        assessments: List[Dict], 
        predicted_score: float
    ) -> str:
        """Generate human-readable reasoning for performance prediction"""
        recent_avg = np.mean([a.get("final_score", 0) for a in assessments[:3]])
        trend = "improving" if len(assessments) > 1 and assessments[0].get("final_score", 0) > assessments[1].get("final_score", 0) else "stable"
        
        return f"Prediction based on recent average of {recent_avg:.1f}% with {trend} trend. " \
               f"User level {user.get('level', 1)} with {len(assessments)} assessment history."
    
    def _generate_risk_recommendations(
        self, 
        user: Dict, 
        assessments: List[Dict], 
        risk_level: str, 
        risk_probability: float
    ) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == "high":
            recommendations.extend([
                "Schedule immediate one-on-one tutoring session",
                "Review fundamental concepts in struggling subjects",
                "Implement daily practice routine with shorter sessions",
                "Consider peer mentoring or study group participation"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Increase assessment frequency to monitor progress",
                "Focus on areas showing declining performance",
                "Encourage regular study schedule",
                "Provide additional practice materials"
            ])
        else:
            recommendations.extend([
                "Continue current learning approach",
                "Challenge with advanced topics",
                "Consider leadership roles in study groups"
            ])
        
        # Add specific recommendations based on performance patterns
        if assessments:
            recent_scores = [a.get("final_score", 0) for a in assessments[:3]]
            if all(score < 60 for score in recent_scores):
                recommendations.append("Focus on mastering basic concepts before advancing")
        
        return recommendations[:4]  # Return top 4 recommendations
    
    def _classify_improvement_level(self, avg_score: float, recent_activity: int) -> str:
        """Classify expected improvement level"""
        if avg_score > 85 and recent_activity > 5:
            return "excellent"
        elif avg_score > 70 and recent_activity > 3:
            return "good"
        elif avg_score > 60:
            return "moderate"
        else:
            return "needs_attention"
    
    def _calculate_learning_velocity(self, assessments: List[Dict]) -> str:
        """Calculate how fast the student is learning"""
        if len(assessments) < 5:
            return "insufficient_data"
        
        scores = [a.get("final_score", 0) for a in assessments[-10:]]  # Last 10 assessments
        improvement = scores[-1] - scores[0] if len(scores) > 1 else 0
        
        if improvement > 20:
            return "fast"
        elif improvement > 5:
            return "moderate"
        elif improvement > -5:
            return "stable"
        else:
            return "slow"
    
    def _recommend_subjects(self, assessments: List[Dict]) -> List[str]:
        """Recommend subjects based on performance patterns"""
        subject_performance = defaultdict(list)
        
        for assessment in assessments:
            subject = assessment.get("subject")
            if subject:
                subject_performance[subject].append(assessment.get("final_score", 0))
        
        # Find subjects with room for improvement
        recommendations = []
        for subject, scores in subject_performance.items():
            avg_score = np.mean(scores)
            if avg_score < 75:  # Below satisfactory
                recommendations.append(subject)
        
        return recommendations[:3]  # Top 3 subjects needing attention
    
    def _get_trend_description(self, assessments: List[Dict]) -> str:
        """Get human-readable trend description"""
        if len(assessments) < 3:
            return "limited data"
        
        scores = [a.get("final_score", 0) for a in assessments[:5]]
        trend = self._calculate_improvement_trend(scores)
        
        if trend > 2:
            return "steady improvement"
        elif trend > 0:
            return "slight improvement"
        elif trend > -2:
            return "stable performance"
        else:
            return "declining performance"