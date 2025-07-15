"""
PathwayIQ Health Monitoring System
Comprehensive health checks and monitoring for production deployment
"""

import asyncio
import time
import psutil
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
import json
import os
from session_manager import session_manager

logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.health_checks = {}
        self.alerts = []
        self.monitoring_enabled = os.getenv('MONITORING_ENABLED', 'true').lower() == 'true'
        self.check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', 30))
        
    async def check_database_health(self) -> Dict[str, Any]:
        """Check MongoDB health"""
        try:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            client = AsyncIOMotorClient(mongo_url)
            
            # Test connection
            await client.admin.command('ping')
            
            # Get database stats
            db_name = os.environ.get('DB_NAME', 'pathwayiq_database')
            db = client[db_name]
            stats = await db.command('dbstats')
            
            client.close()
            
            return {
                'status': 'healthy',
                'response_time': time.time(),
                'database_size': stats.get('dataSize', 0),
                'collections': stats.get('collections', 0),
                'indexes': stats.get('indexes', 0),
                'storage_size': stats.get('storageSize', 0)
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': time.time()
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            if not session_manager.redis_client:
                return {
                    'status': 'disabled',
                    'message': 'Redis not configured'
                }
            
            # Test Redis connection
            response = session_manager.redis_client.ping()
            
            # Get Redis info
            info = session_manager.redis_client.info()
            
            return {
                'status': 'healthy' if response else 'unhealthy',
                'response_time': time.time(),
                'used_memory': info.get('used_memory', 0),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': time.time()
            }
    
    async def check_ai_services_health(self) -> Dict[str, Any]:
        """Check AI services health"""
        services = {
            'openai': os.environ.get('OPENAI_API_KEY'),
            'claude': os.environ.get('CLAUDE_API_KEY'),
            'gemini': os.environ.get('GEMINI_API_KEY')
        }
        
        results = {}
        
        for service, api_key in services.items():
            if not api_key:
                results[service] = {
                    'status': 'not_configured',
                    'message': 'API key not provided'
                }
                continue
            
            try:
                # Basic API availability check (simplified)
                results[service] = {
                    'status': 'configured',
                    'api_key_present': bool(api_key),
                    'last_checked': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                results[service] = {
                    'status': 'error',
                    'error': str(e),
                    'last_checked': datetime.now(timezone.utc).isoformat()
                }
        
        return results
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network stats
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_received': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_received': network.packets_recv
                }
            }
            
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
            return {'error': str(e)}
    
    async def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        try:
            # Active sessions
            active_sessions = session_manager.get_active_sessions_count()
            
            # Uptime
            uptime = time.time() - self.start_time
            
            return {
                'uptime_seconds': uptime,
                'active_sessions': active_sessions,
                'start_time': datetime.fromtimestamp(self.start_time, timezone.utc).isoformat(),
                'current_time': datetime.now(timezone.utc).isoformat(),
                'monitoring_enabled': self.monitoring_enabled
            }
            
        except Exception as e:
            logger.error(f"Application metrics collection failed: {e}")
            return {'error': str(e)}
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        start_time = time.time()
        
        # Run all health checks
        database_health = await self.check_database_health()
        redis_health = await self.check_redis_health()
        ai_services_health = await self.check_ai_services_health()
        system_metrics = self.get_system_metrics()
        app_metrics = await self.get_application_metrics()
        
        # Determine overall health
        overall_status = 'healthy'
        if database_health['status'] != 'healthy':
            overall_status = 'unhealthy'
        
        # Create alerts based on thresholds
        alerts = []
        
        if 'cpu' in system_metrics and system_metrics['cpu']['usage_percent'] > 80:
            alerts.append({
                'type': 'high_cpu',
                'message': f"High CPU usage: {system_metrics['cpu']['usage_percent']:.1f}%",
                'severity': 'warning'
            })
        
        if 'memory' in system_metrics and system_metrics['memory']['percent'] > 85:
            alerts.append({
                'type': 'high_memory',
                'message': f"High memory usage: {system_metrics['memory']['percent']:.1f}%",
                'severity': 'warning'
            })
        
        if 'disk' in system_metrics and system_metrics['disk']['percent'] > 90:
            alerts.append({
                'type': 'high_disk',
                'message': f"High disk usage: {system_metrics['disk']['percent']:.1f}%",
                'severity': 'critical'
            })
        
        check_duration = time.time() - start_time
        
        return {
            'overall_status': overall_status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'check_duration_seconds': check_duration,
            'components': {
                'database': database_health,
                'redis': redis_health,
                'ai_services': ai_services_health
            },
            'metrics': {
                'system': system_metrics,
                'application': app_metrics
            },
            'alerts': alerts
        }
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if not self.monitoring_enabled:
            logger.info("Monitoring disabled")
            return
        
        logger.info(f"Starting health monitoring (interval: {self.check_interval}s)")
        
        while True:
            try:
                health_status = await self.comprehensive_health_check()
                
                # Store latest health check
                self.health_checks[datetime.now(timezone.utc).isoformat()] = health_status
                
                # Keep only last 100 checks
                if len(self.health_checks) > 100:
                    oldest_key = min(self.health_checks.keys())
                    del self.health_checks[oldest_key]
                
                # Log critical alerts
                for alert in health_status.get('alerts', []):
                    if alert['severity'] == 'critical':
                        logger.critical(f"CRITICAL ALERT: {alert['message']}")
                    elif alert['severity'] == 'warning':
                        logger.warning(f"WARNING: {alert['message']}")
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.check_interval)
    
    def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health check history"""
        recent_checks = list(self.health_checks.items())[-limit:]
        return [{'timestamp': timestamp, 'status': status} for timestamp, status in recent_checks]
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        current_health = await self.comprehensive_health_check()
        health_history = self.get_health_history()
        
        # Calculate availability
        healthy_checks = sum(1 for _, status in self.health_checks.items() 
                           if status['overall_status'] == 'healthy')
        total_checks = len(self.health_checks)
        availability = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'report_generated': datetime.now(timezone.utc).isoformat(),
            'current_health': current_health,
            'availability_percentage': availability,
            'total_checks_performed': total_checks,
            'recent_history': health_history,
            'summary': {
                'uptime': current_health['metrics']['application']['uptime_seconds'],
                'active_sessions': current_health['metrics']['application']['active_sessions'],
                'database_status': current_health['components']['database']['status'],
                'redis_status': current_health['components']['redis']['status'],
                'system_health': {
                    'cpu_usage': current_health['metrics']['system']['cpu']['usage_percent'],
                    'memory_usage': current_health['metrics']['system']['memory']['percent'],
                    'disk_usage': current_health['metrics']['system']['disk']['percent']
                }
            }
        }

# Global health monitor instance
health_monitor = HealthMonitor()

# CLI command for health check
async def main():
    """Run health check"""
    health_status = await health_monitor.comprehensive_health_check()
    print(json.dumps(health_status, indent=2))

if __name__ == "__main__":
    asyncio.run(main())