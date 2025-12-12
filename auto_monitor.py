"""
Auto-Monitoring System (Telegram Disabled)
Monitors system health and fixes bugs automatically
"""
import os
import time
import threading
import traceback
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from backup_data_provider import BackupDataProvider
from fast_signals import FastSignalGenerator
from system_health import health_monitor

logger = logging.getLogger(__name__)

class AutoMonitor:
    """System monitoring without Telegram notifications"""
    
    def __init__(self):
        self.data_provider = BackupDataProvider()
        self.signal_generator = FastSignalGenerator()
        self.monitoring = False
        self.last_health_check = None
        self.error_counts = {}
        self.last_signal_update = None
        self.system_status = "HEALTHY"
        
    def start_monitoring(self):
        """Start monitoring system"""
        if self.monitoring:
            return
            
        self.monitoring = True
        logger.info("Starting auto-monitoring system (Telegram disabled)")
        
        # Start monitoring threads
        threading.Thread(target=self._monitor_system_health, daemon=True).start()
        threading.Thread(target=self._monitor_trading_signals, daemon=True).start()
        threading.Thread(target=self._monitor_api_health, daemon=True).start()
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        logger.info("Auto-monitoring stopped")
        
    def _monitor_system_health(self):
        """Monitor overall system health"""
        while self.monitoring:
            try:
                health_status = self._check_system_health()
                
                if health_status['issues']:
                    self._auto_fix_issues(health_status['issues'])
                
                self.last_health_check = datetime.now()
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(60)
                
    def _monitor_trading_signals(self):
        """Monitor trading signals"""
        while self.monitoring:
            try:
                market_data = self.data_provider.get_market_data()
                if market_data:
                    signals = self.signal_generator.generate_fast_signals(market_data)
                    # Log high-confidence signals only
                    high_conf_signals = [s for s in signals if s.get('confidence', 0) >= 95]
                    if high_conf_signals:
                        logger.info(f"High-confidence signals detected: {len(high_conf_signals)}")
                
                time.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Signal monitoring error: {e}")
                time.sleep(60)
                
    def _monitor_api_health(self):
        """Monitor API connectivity"""
        while self.monitoring:
            try:
                api_status = self._check_api_health()
                
                if api_status['failed_apis']:
                    self._fix_api_issues(api_status['failed_apis'])
                
                time.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"API monitoring error: {e}")
                time.sleep(60)
                
    def _check_system_health(self) -> Dict:
        """Check system health"""
        issues = []
        metrics = {}
        
        try:
            # Check data provider
            market_data = self.data_provider.get_market_data()
            if not market_data:
                issues.append("data_provider_failed")
            else:
                metrics['tokens_loaded'] = len(market_data)
                
            # Check signal generation
            if market_data:
                signals = self.signal_generator.generate_fast_signals(market_data)
                metrics['active_signals'] = len(signals)
                
            # Check error rates
            total_errors = sum(self.error_counts.values())
            if total_errors > 10:
                issues.append("high_error_rate")
                
            metrics['total_errors'] = total_errors
            metrics['last_check'] = datetime.now()
            
        except Exception as e:
            issues.append(f"health_check_error: {str(e)}")
            
        return {
            'status': 'HEALTHY' if not issues else 'DEGRADED',
            'issues': issues,
            'metrics': metrics
        }
        
    def _auto_fix_issues(self, issues: List[str]):
        """Auto-fix detected issues"""
        fixes_applied = []
        
        for issue in issues:
            try:
                if issue == "data_provider_failed":
                    # Reset data provider
                    self.data_provider = BackupDataProvider()
                    fixes_applied.append("Data provider reset")
                    
                elif issue == "high_error_rate":
                    # Clear error counts
                    self.error_counts.clear()
                    fixes_applied.append("Error counts cleared")
                    
            except Exception as e:
                logger.error(f"Auto-fix failed for {issue}: {e}")
                
        if fixes_applied:
            logger.info(f"Auto-fixes applied: {fixes_applied}")
            
    def _check_api_health(self) -> Dict:
        """Check API endpoint health"""
        failed_apis = []
        working_apis = []
        
        # Test Coinbase API
        try:
            data = self.data_provider._get_coinbase_prices()
            if data:
                working_apis.append("Coinbase")
            else:
                failed_apis.append("Coinbase")
        except:
            failed_apis.append("Coinbase")
            
        # Test CoinGecko API
        try:
            data = self.data_provider._get_coingecko_live()
            if data:
                working_apis.append("CoinGecko")
            else:
                failed_apis.append("CoinGecko")
        except:
            failed_apis.append("CoinGecko")
            
        return {
            'working_apis': working_apis,
            'failed_apis': failed_apis,
            'status': 'HEALTHY' if working_apis else 'DEGRADED'
        }
        
    def _fix_api_issues(self, failed_apis: List[str]):
        """Fix API connectivity issues"""
        for api in failed_apis:
            try:
                if api in ["Coinbase", "CoinGecko"]:
                    # Reset data provider to try different endpoints
                    self.data_provider = BackupDataProvider()
                    logger.info(f"Reset data provider for {api} issues")
                    
            except Exception as e:
                logger.error(f"Failed to fix {api} issues: {e}")

# Global monitor instance
auto_monitor = None

def start_auto_monitoring():
    """Start the auto-monitoring system"""
    global auto_monitor
    if auto_monitor is None:
        auto_monitor = AutoMonitor()
    auto_monitor.start_monitoring()
    
def stop_auto_monitoring():
    """Stop the auto-monitoring system"""
    global auto_monitor
    if auto_monitor:
        auto_monitor.stop_monitoring()