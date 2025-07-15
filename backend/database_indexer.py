"""
PathwayIQ Database Indexing for Production Performance
Creates optimized indexes for all collections
"""

import asyncio
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class DatabaseIndexer:
    def __init__(self):
        load_dotenv()
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'pathwayiq_database')
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ Database connected successfully")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    async def create_user_indexes(self):
        """Create indexes for users collection"""
        collection = self.db.users
        
        indexes = [
            # Primary indexes
            [("id", 1), ("email", 1)],  # Compound index for authentication
            [("email", 1)],  # Unique email lookup
            [("username", 1)],  # Unique username lookup
            
            # Query optimization indexes
            [("created_at", -1)],  # Recent users
            [("last_active", -1)],  # Active users
            [("role", 1)],  # Role-based queries
            [("level", -1)],  # Leaderboard queries
            [("xp", -1)],  # XP-based queries
            
            # Compound indexes for complex queries
            [("role", 1), ("level", -1)],  # Role + level queries
            [("is_active", 1), ("last_active", -1)],  # Active users with recent activity
        ]
        
        for index in indexes:
            try:
                await collection.create_index(index)
                logger.info(f"✅ Created user index: {index}")
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
    
    async def create_question_indexes(self):
        """Create indexes for questions collection"""
        collection = self.db.questions
        
        indexes = [
            # Primary indexes
            [("id", 1)],  # Primary key
            
            # Query optimization indexes
            [("subject", 1)],  # Subject-based queries
            [("difficulty", 1)],  # Difficulty filtering
            [("grade_level", 1)],  # Grade level filtering
            [("created_by", 1)],  # Creator queries
            [("created_at", -1)],  # Recent questions
            
            # Compound indexes for complex queries
            [("subject", 1), ("difficulty", 1)],  # Subject + difficulty
            [("subject", 1), ("grade_level", 1)],  # Subject + grade level
            [("created_by", 1), ("created_at", -1)],  # Creator's recent questions
            [("subject", 1), ("difficulty", 1), ("grade_level", 1)],  # Triple compound
            
            # Full-text search
            [("question_text", "text"), ("explanation", "text")],  # Text search
            
            # Tag-based queries
            [("tags", 1)],  # Tag filtering
        ]
        
        for index in indexes:
            try:
                await collection.create_index(index)
                logger.info(f"✅ Created question index: {index}")
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
    
    async def create_user_answer_indexes(self):
        """Create indexes for user_answers collection"""
        collection = self.db.user_answers
        
        indexes = [
            # Primary indexes
            [("id", 1)],  # Primary key
            
            # Query optimization indexes
            [("user_id", 1)],  # User-based queries
            [("question_id", 1)],  # Question-based queries
            [("answered_at", -1)],  # Recent answers
            [("session_id", 1)],  # Session-based queries
            
            # Compound indexes for analytics
            [("user_id", 1), ("answered_at", -1)],  # User's recent answers
            [("user_id", 1), ("is_correct", 1)],  # User's correct answers
            [("question_id", 1), ("is_correct", 1)],  # Question difficulty analysis
            [("session_id", 1), ("answered_at", 1)],  # Session progression
            
            # Performance analytics indexes
            [("user_id", 1), ("points_earned", -1)],  # Top performers
            [("user_id", 1), ("time_taken", 1)],  # Response time analysis
            [("ability_estimate_after", -1)],  # Ability tracking
        ]
        
        for index in indexes:
            try:
                await collection.create_index(index)
                logger.info(f"✅ Created user_answer index: {index}")
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
    
    async def create_session_indexes(self):
        """Create indexes for adaptive assessment sessions"""
        collection = self.db.adaptive_sessions
        
        indexes = [
            # Primary indexes
            [("session_id", 1)],  # Primary key
            
            # Query optimization indexes
            [("user_id", 1)],  # User sessions
            [("subject", 1)],  # Subject-based sessions
            [("start_time", -1)],  # Recent sessions
            [("session_type", 1)],  # Session type filtering
            
            # Compound indexes
            [("user_id", 1), ("start_time", -1)],  # User's recent sessions
            [("user_id", 1), ("subject", 1)],  # User's subject sessions
            [("session_type", 1), ("start_time", -1)],  # Recent sessions by type
            
            # TTL index for session cleanup (30 days)
            [("start_time", 1)],  # TTL index
        ]
        
        for index in indexes:
            try:
                if index == [("start_time", 1)]:
                    # Create TTL index for automatic cleanup
                    await collection.create_index(index, expireAfterSeconds=2592000)  # 30 days
                else:
                    await collection.create_index(index)
                logger.info(f"✅ Created session index: {index}")
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
    
    async def create_analytics_indexes(self):
        """Create indexes for analytics collections"""
        # User analytics
        collection = self.db.user_analytics
        
        indexes = [
            [("user_id", 1)],  # Primary key
            [("last_updated", -1)],  # Recent analytics
            [("total_study_time", -1)],  # Study time rankings
            [("learning_streak", -1)],  # Streak rankings
            [("accuracy_rate", -1)],  # Accuracy rankings
        ]
        
        for index in indexes:
            try:
                await collection.create_index(index)
                logger.info(f"✅ Created analytics index: {index}")
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
    
    async def create_all_indexes(self):
        """Create all database indexes"""
        logger.info("🔧 Starting database indexing...")
        
        if not await self.connect():
            return False
        
        try:
            await self.create_user_indexes()
            await self.create_question_indexes()
            await self.create_user_answer_indexes()
            await self.create_session_indexes()
            await self.create_analytics_indexes()
            
            logger.info("✅ All database indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database indexing failed: {e}")
            return False
        finally:
            if self.client:
                self.client.close()
    
    async def show_index_stats(self):
        """Show index statistics"""
        if not await self.connect():
            return
        
        collections = ['users', 'questions', 'user_answers', 'adaptive_sessions', 'user_analytics']
        
        for collection_name in collections:
            try:
                collection = self.db[collection_name]
                indexes = await collection.list_indexes().to_list(length=None)
                
                print(f"\n📊 {collection_name.upper()} INDEXES:")
                for index in indexes:
                    print(f"  - {index.get('name', 'Unknown')}: {index.get('key', {})}")
                
            except Exception as e:
                print(f"❌ Error getting indexes for {collection_name}: {e}")
        
        if self.client:
            self.client.close()

# Global indexer instance
db_indexer = DatabaseIndexer()

# CLI command for running indexing
async def main():
    """Run database indexing"""
    success = await db_indexer.create_all_indexes()
    if success:
        print("✅ Database indexing completed successfully")
        await db_indexer.show_index_stats()
    else:
        print("❌ Database indexing failed")

if __name__ == "__main__":
    asyncio.run(main())