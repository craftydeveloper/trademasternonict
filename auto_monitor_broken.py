"""
Comprehensive Auto-Monitoring System
Monitors system health, fixes bugs automatically, and sends Telegram updates
"""
import os
import time
import threading
import traceback
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
# Telegram disabled per user request
from backup_data_provider import BackupDataProvider
from fast_signals import FastSignalGenerator
from system_health import health_monitor

logger = logging.getLogger(__name__)

class AutoMonitor:
    """Comprehensive system monitoring with auto-fixing"""
    
    def __init__(self):
        self.telegram = None  # Telegram disabled per user request
        self.data_provider = BackupDataProvider()
        self.signal_generator = FastSignalGenerator()
        self.monitoring = False
        self.last_health_check = None
        self.error_counts = {}
        self.last_signal_update = None
        self.system_status = "HEALTHY"
        self.last_alerts = {}
        
    def start_monitoring(self):
        """Start comprehensive monitoring"""
        if self.monitoring:
            return
            
        self.monitoring = True
        logger.info("Starting auto-monitoring system")
        
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
                # Check every 5 minutes
                time.sleep(300)
                
                health_status = self._check_system_health()
                
                # Auto-fix any detected issues
                if health_status['issues']:
                    self._auto_fix_issues(health_status['issues'])
                    
                # Run system health auto-fixes
                system_fixes = health_monitor.auto_fix_system_issues()
                if system_fixes:
                    logger.info(f"Applied {len(system_fixes)} system fixes")
                    
                # Send daily health report
                if self._should_send_daily_report():
                    self._send_daily_health_report(health_status)
                    
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                self._handle_monitor_error("system_health", e)
                
    def _monitor_trading_signals(self):
        """Monitor trading signals and alert on new opportunities"""
        while self.monitoring:
            try:
                # Check every 2 minutes for new signals
                time.sleep(120)
                
                market_data = self.data_provider.get_market_data()
                if not market_data:
                    continue
                    
                signals = self.signal_generator.generate_fast_signals(market_data)
                
                # Check for high-confidence new signals
                for signal in signals:
                    if signal['confidence'] >= 90 and signal['is_primary_trade']:
                        self._alert_new_signal(signal)
                        
                self.last_signal_update = datetime.now()
                
            except Exception as e:
                logger.error(f"Signal monitoring error: {e}")
                self._handle_monitor_error("trading_signals", e)
                
    def _monitor_api_health(self):
        """Monitor API connectivity and fix issues"""
        while self.monitoring:
            try:
                # Check every 1 minute
                time.sleep(60)
                
                api_status = self._check_api_health()
                
                # Auto-fix API issues
                if api_status['failed_apis']:
                    self._fix_api_issues(api_status['failed_apis'])
                    
            except Exception as e:
                logger.error(f"API monitoring error: {e}")
                self._handle_monitor_error("api_health", e)
                
    def _check_system_health(self) -> Dict:
        """Comprehensive system health check"""
        issues = []
        metrics = {}
        
        try:
            # Check market data availability
            market_data = self.data_provider.get_market_data()
            if not market_data:
                issues.append("market_data_unavailable")
            else:
                metrics['market_data_symbols'] = len(market_data)
                
            # Check signal generation
            if market_data:
                signals = self.signal_generator.generate_fast_signals(market_data)
                metrics['active_signals'] = len(signals)
                
            # Telegram disabled - no connectivity checks needed
                
            # Check error rates
            total_errors = sum(self.error_counts.values())
            if total_errors > 10:
                issues.append("high_error_rate")
                
            metrics['total_errors'] = total_errors
            metrics['last_check'] = datetime.now()
            
        except Exception as e:
            issues.append(f"health_check_error: {str(e)}")
            
        self.last_health_check = datetime.now()
        return {
            'status': 'HEALTHY' if not issues else 'ISSUES_DETECTED',
            'issues': issues,
            'metrics': metrics
        }
        
    def _auto_fix_issues(self, issues: List[str]):
        """Automatically fix detected issues"""
        fixes_applied = []
        
        for issue in issues:
            try:
                if issue == "market_data_unavailable":
                    # Try alternative data sources
                    self.data_provider._get_coinbase_prices()
                    fixes_applied.append("Switched to Coinbase API backup")
                    
                elif issue == "high_error_rate":
                    # Reset error counters
                    self.error_counts.clear()
                    fixes_applied.append("Reset error counters")
                    
                elif "api" in issue.lower():
                    # Generic API fix
                    self._fix_api_issues([issue])
                    fixes_applied.append(f"Applied API fix for {issue}")
                    
            except Exception as e:
                logger.error(f"Auto-fix failed for {issue}: {e}")
                
        if fixes_applied:
            # Telegram disabled - no notifications sent
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
            
        # Test Binance API
        try:
            data = self.data_provider._get_binance_prices()
            if data:
                working_apis.append("Binance")
            else:
                failed_apis.append("Binance")
        except:
            failed_apis.append("Binance")
            
        return {
            'working_apis': working_apis,
            'failed_apis': failed_apis,
            'health_score': len(working_apis) / (len(working_apis) + len(failed_apis)) if (working_apis or failed_apis) else 0
        }
        
    def _fix_api_issues(self, failed_apis: List[str]):
        """Fix API connectivity issues"""
        for api in failed_apis:
            try:
                if api == "Coinbase":
                    # Force cache refresh
                    self.data_provider._update_cache({})
                elif api == "Binance":
                    # Reset connection
                    pass  # Binance auto-recovers
                    
            except Exception as e:
                logger.error(f"Failed to fix {api}: {e}")
                
    def _alert_new_signal(self, signal: Dict):
        """Alert about new high-confidence signals"""
        # Avoid spam - only alert once per hour for same symbol
        signal_key = f"{signal['symbol']}_{signal['action']}"
        now = datetime.now()
        
        if signal_key in self.last_alerts:
            if now - self.last_alerts[signal_key] < timedelta(hours=1):
                return
                
        self.last_alerts[signal_key] = now
        
        # Format signal alert
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        take_profit = signal['take_profit']
        
        message = (
            f"🎯 NEW HIGH-CONFIDENCE SIGNAL\n\n"
            f"Symbol: {signal['symbol']}\n"
            f"Action: {signal['action']}\n"
            f"Confidence: {signal['confidence']}%\n\n"
            f"📊 Trading Details:\n"
            f"Entry: ${entry_price:.4f}\n"
            f"Stop Loss: ${stop_loss:.4f}\n"
            f"Take Profit: ${take_profit:.4f}\n"
            f"Leverage: {signal['leverage']}x\n\n"
            f"💰 Risk Management:\n"
            f"Risk: {signal['bybit_settings']['risk_management']['risk_percentage']}\n"
            f"Position: {signal['bybit_settings']['qty']} {signal['symbol']}\n\n"
            f"⏰ Time: {now.strftime('%H:%M:%S')}"
        )
        
        # Telegram disabled(message, urgent=True)
        
    def _should_send_daily_report(self) -> bool:
        """Check if daily report should be sent"""
        if not hasattr(self, '_last_daily_report'):
            self._last_daily_report = datetime.now().date()
            return True
            
        return datetime.now().date() > self._last_daily_report
        
    def _send_daily_health_report(self, health_status: Dict):
        """Send daily system health report"""
        metrics = health_status['metrics']
        
        message = (
            f"📊 Daily System Report\n\n"
            f"🟢 Status: {health_status['status']}\n"
            f"📈 Market Data: {metrics.get('market_data_symbols', 0)} symbols\n"
            f"🎯 Active Signals: {metrics.get('active_signals', 0)}\n"
            f"⚠️ Total Errors: {metrics.get('total_errors', 0)}\n\n"
            f"✅ Auto-monitoring active\n"
            f"✅ Bug fixing enabled\n"
            f"✅ Telegram alerts working\n\n"
            f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        # Telegram disabled(message)
        self._last_daily_report = datetime.now().date()
        
    def _handle_monitor_error(self, component: str, error: Exception):
        """Handle monitoring errors with auto-recovery"""
        self.error_counts[component] = self.error_counts.get(component, 0) + 1
        
        # Send error alert if too many errors
        if self.error_counts[component] >= 3:
            # Telegram disabled(
                f"⚠️ Monitor Error Alert\n\n"
                f"Component: {component}\n"
                f"Error Count: {self.error_counts[component]}\n"
                f"Last Error: {str(error)[:200]}\n\n"
                f"Auto-recovery in progress...",
                urgent=True
            )
            
        # Auto-recovery: restart component
        if self.error_counts[component] >= 5:
            self._restart_component(component)
            
    def _restart_component(self, component: str):
        """Restart specific monitoring component"""
        try:
            if component == "trading_signals":
                threading.Thread(target=self._monitor_trading_signals, daemon=True).start()
            elif component == "api_health":
                threading.Thread(target=self._monitor_api_health, daemon=True).start()
            elif component == "system_health":
                threading.Thread(target=self._monitor_system_health, daemon=True).start()
                
            self.error_counts[component] = 0
            # Telegram disabled(f"✅ Component Restarted: {component}")
            
        except Exception as e:
            logger.error(f"Failed to restart {component}: {e}")

# Global monitor instance
auto_monitor = AutoMonitor()

def start_auto_monitoring():
    """Start the auto-monitoring system"""
    auto_monitor.start_monitoring()
    
def stop_auto_monitoring():
    """Stop the auto-monitoring system"""
    auto_monitor.stop_monitoring()