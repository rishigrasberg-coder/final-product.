import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import time
import random
import threading
import queue
import hashlib
import uuid

st.set_page_config(
    page_title="YANTRA - Professional Latency Arbitrage Platform", 
    page_icon="⭐", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ENHANCED SESSION STATE INITIALIZATION
if 'page' not in st.session_state: 
    st.session_state.page = "Dashboard"
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"
if 'auto_trading' not in st.session_state: 
    st.session_state.auto_trading = {'enabled': False, 'strategies': [], 'max_trades': 50, 'risk_per_trade': 1.0, 'trades_today': 0, 'profit_today': 0}
if 'arbitrage_settings' not in st.session_state: 
    st.session_state.arbitrage_settings = {'enabled': False, 'min_spread': 0.8, 'max_volume': 10.0, 'execution_speed': 'Ultra Fast', 'bridge_mode': 'Direct LP', 'slippage_tolerance': 0.2}
if 'broker_connections' not in st.session_state: 
    st.session_state.broker_connections = {}
if 'synthetic_symbols' not in st.session_state: 
    st.session_state.synthetic_symbols = []
if 'kill_switch' not in st.session_state: 
    st.session_state.kill_switch = {'active': False, 'reason': ''}
if 'risk_limits' not in st.session_state: 
    st.session_state.risk_limits = {'daily_loss': 5000, 'max_positions': 20, 'max_leverage': 100, 'correlation_limit': 0.7, 'drawdown_limit': 10.0, 'var_limit': 2.5}
if 'mt5_symbols' not in st.session_state:
    st.session_state.mt5_symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD', 'EURJPY', 'EURGBP', 'EURAUD', 'EURCHF', 'EURCAD', 'GBPJPY', 'GBPAUD', 'GBPCHF', 'GBPCAD', 'AUDJPY', 'AUDCHF', 'AUDCAD', 'CADJPY', 'CHFJPY', 'NZDJPY', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'US30', 'US500', 'NAS100', 'GER30', 'UK100', 'FRA40', 'JPN225', 'AUS200', 'BTCUSD', 'ETHUSD']
if 'lp_connections' not in st.session_state:
    st.session_state.lp_connections = {'Prime of Prime': {'status': 'Connected', 'latency': 0.8, 'spread': 0.1}, 'Tier 1 Banks': {'status': 'Connected', 'latency': 1.2, 'spread': 0.2}, 'ECN Providers': {'status': 'Connected', 'latency': 0.6, 'spread': 0.0}, 'Dark Pools': {'status': 'Connected', 'latency': 2.1, 'spread': 0.0}}
if 'trade_journal' not in st.session_state: 
    st.session_state.trade_journal = []

# NEW: ADVANCED BROKER MANAGEMENT SYSTEM
if 'advanced_brokers' not in st.session_state:
    st.session_state.advanced_brokers = {
        'Divit Capital': {
            'id': 'divit_001',
            'status': 'Connected',
            'accounts': [
                {'account_id': '12345678', 'type': 'Live', 'balance': 25750.00, 'equity': 25680.00, 'margin': 3200.00, 'free_margin': 22480.00, 'leverage': 100, 'currency': 'USD'},
                {'account_id': '87654321', 'type': 'Demo', 'balance': 10000.00, 'equity': 9850.00, 'margin': 1200.00, 'free_margin': 8650.00, 'leverage': 200, 'currency': 'USD'}
            ],
            'performance': {
                'avg_execution_time': 0.7,
                'slippage_avg': 0.2,
                'fill_rate': 99.8,
                'uptime': 99.9,
                'commission_paid': 245.50,
                'spreads_avg': {'EURUSD': 0.1, 'GBPUSD': 0.2, 'XAUUSD': 0.3},
                'daily_volume': 125000,
                'monthly_trades': 1250
            },
            'settings': {
                'max_slippage': 1.0,
                'execution_mode': 'Market',
                'partial_fills': True,
                'auto_reconnect': True,
                'trade_notifications': True
            }
        },
        'Kama Capital': {
            'id': 'kama_002',
            'status': 'Connected',
            'accounts': [
                {'account_id': '98765432', 'type': 'Live', 'balance': 15000.00, 'equity': 14850.00, 'margin': 2100.00, 'free_margin': 12750.00, 'leverage': 100, 'currency': 'USD'}
            ],
            'performance': {
                'avg_execution_time': 1.2,
                'slippage_avg': 0.3,
                'fill_rate': 99.5,
                'uptime': 99.7,
                'commission_paid': 180.25,
                'spreads_avg': {'EURUSD': 0.2, 'GBPUSD': 0.3, 'XAUUSD': 0.4},
                'daily_volume': 85000,
                'monthly_trades': 890
            },
            'settings': {
                'max_slippage': 1.5,
                'execution_mode': 'Instant',
                'partial_fills': False,
                'auto_reconnect': True,
                'trade_notifications': False
            }
        },
        'IC Markets': {
            'id': 'icm_003',
            'status': 'Disconnected',
            'accounts': [],
            'performance': {
                'avg_execution_time': 0.0,
                'slippage_avg': 0.0,
                'fill_rate': 0.0,
                'uptime': 0.0,
                'commission_paid': 0.0,
                'spreads_avg': {},
                'daily_volume': 0,
                'monthly_trades': 0
            },
            'settings': {
                'max_slippage': 1.0,
                'execution_mode': 'Market',
                'partial_fills': True,
                'auto_reconnect': True,
                'trade_notifications': True
            }
        }
    }

# NEW: PORTFOLIO MANAGEMENT SYSTEM
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        'positions': [
            {'id': 1, 'symbol': 'EURUSD', 'type': 'BUY', 'volume': 1.0, 'entry_price': 1.0850, 'current_price': 1.0865, 'pnl': 150.00, 'swap': -2.50, 'commission': 7.00, 'open_time': datetime.now() - timedelta(hours=2), 'broker': 'Divit Capital'},
            {'id': 2, 'symbol': 'GBPUSD', 'type': 'SELL', 'volume': 0.5, 'entry_price': 1.2650, 'current_price': 1.2630, 'pnl': 100.00, 'swap': -1.25, 'commission': 3.50, 'open_time': datetime.now() - timedelta(hours=1), 'broker': 'Kama Capital'},
            {'id': 3, 'symbol': 'XAUUSD', 'type': 'BUY', 'volume': 0.1, 'entry_price': 2650.00, 'current_price': 2655.00, 'pnl': 50.00, 'swap': 0.00, 'commission': 2.00, 'open_time': datetime.now() - timedelta(minutes=30), 'broker': 'Divit Capital'}
        ],
        'history': [],
        'analytics': {
            'total_pnl': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0
        },
        'allocation': {
            'forex': 70,
            'metals': 20,
            'indices': 10,
            'crypto': 0
        }
    }

# NEW: ADVANCED ORDER MANAGEMENT SYSTEM
if 'advanced_orders' not in st.session_state:
    st.session_state.advanced_orders = {
        'pending_orders': [],
        'order_templates': [
            {'name': 'Scalping Template', 'sl_pips': 10, 'tp_pips': 15, 'volume': 0.1, 'trailing_stop': True},
            {'name': 'Swing Template', 'sl_pips': 50, 'tp_pips': 100, 'volume': 0.5, 'trailing_stop': False},
            {'name': 'Arbitrage Template', 'sl_pips': 5, 'tp_pips': 8, 'volume': 1.0, 'trailing_stop': False}
        ],
        'oco_orders': [],
        'trailing_stops': []
    }

# NEW: STRATEGY BACKTESTING SYSTEM
if 'backtesting' not in st.session_state:
    st.session_state.backtesting = {
        'strategies': [
            {
                'name': 'MA Crossover',
                'description': 'Simple moving average crossover strategy',
                'parameters': {'fast_ma': 10, 'slow_ma': 20, 'sl_pips': 20, 'tp_pips': 40},
                'results': {'total_return': 15.5, 'win_rate': 65.2, 'max_drawdown': 8.3, 'sharpe': 1.45}
            },
            {
                'name': 'RSI Mean Reversion',
                'description': 'RSI oversold/overbought strategy',
                'parameters': {'rsi_period': 14, 'oversold': 30, 'overbought': 70, 'sl_pips': 15, 'tp_pips': 25},
                'results': {'total_return': 22.8, 'win_rate': 58.7, 'max_drawdown': 12.1, 'sharpe': 1.28}
            }
        ],
        'current_backtest': None,
        'historical_data': {}
    }

# NEW: COPY TRADING SYSTEM
if 'copy_trading' not in st.session_state:
    st.session_state.copy_trading = {
        'providers': [
            {
                'id': 'provider_001',
                'name': 'ProTrader_Alpha',
                'avatar': '👨‍💼',
                'followers': 1250,
                'monthly_return': 18.5,
                'win_rate': 72.3,
                'max_drawdown': 6.8,
                'risk_score': 4,
                'subscription_fee': 50,
                'min_copy_amount': 1000,
                'active': True,
                'trades_today': 5,
                'profit_today': 125.50
            },
            {
                'id': 'provider_002',
                'name': 'GoldMaster_Pro',
                'avatar': '🥇',
                'followers': 890,
                'monthly_return': 25.2,
                'win_rate': 68.9,
                'max_drawdown': 9.2,
                'risk_score': 6,
                'subscription_fee': 75,
                'min_copy_amount': 2000,
                'active': False,
                'trades_today': 3,
                'profit_today': 89.25
            }
        ],
        'my_subscriptions': [],
        'copy_settings': {
            'max_risk_per_trade': 2.0,
            'max_daily_trades': 10,
            'stop_loss_buffer': 5,
            'take_profit_buffer': 0
        }
    }

# EXISTING XAUUSD ARBITRAGE SYSTEM (UNCHANGED)
if 'xauusd_arbitrage' not in st.session_state:
    st.session_state.xauusd_arbitrage = {
        'enabled': False,
        'monitoring': False,
        'opportunities': [],
        'positions': [],
        'price_feeds': {
            'broker_a': {'name': 'Divit Capital', 'bid': 0, 'ask': 0, 'timestamp': 0, 'latency': 0.7},
            'broker_b': {'name': 'Kama Capital', 'bid': 0, 'ask': 0, 'timestamp': 0, 'latency': 1.2}
        },
        'settings': {
            'min_spread_pips': 0.3,
            'max_position_size': 1.0,
            'max_concurrent_trades': 5,
            'auto_execute': False,
            'risk_per_trade': 100,
            'stop_loss_pips': 5,
            'take_profit_pips': 2
        },
        'stats': {
            'total_opportunities': 0,
            'executed_trades': 0,
            'successful_trades': 0,
            'total_pnl': 0,
            'today_pnl': 0,
            'win_rate': 0,
            'avg_profit_per_trade': 0
        }
    }

# EXISTING XAUUSD ARBITRAGE ENGINE (UNCHANGED)
class XAUUSDArbitrageEngine:
    def __init__(self):
        self.is_running = False
        self.price_queue = queue.Queue()
        
    def start_monitoring(self):
        """Start the arbitrage monitoring system"""
        self.is_running = True
        if not hasattr(st.session_state, 'arbitrage_thread') or not st.session_state.arbitrage_thread.is_alive():
            st.session_state.arbitrage_thread = threading.Thread(target=self.price_monitor_loop)
            st.session_state.arbitrage_thread.daemon = True
            st.session_state.arbitrage_thread.start()
    
    def stop_monitoring(self):
        """Stop the arbitrage monitoring system"""
        self.is_running = False
        st.session_state.xauusd_arbitrage['monitoring'] = False
    
    def price_monitor_loop(self):
        """Main price monitoring loop"""
        base_price = 2650.00
        
        while self.is_running and st.session_state.xauusd_arbitrage['monitoring']:
            try:
                current_time = time.time()
                
                broker_a_mid = base_price + random.uniform(-2, 2)
                broker_a_spread = random.uniform(0.2, 0.5)
                broker_a_bid = round(broker_a_mid - broker_a_spread/2, 2)
                broker_a_ask = round(broker_a_mid + broker_a_spread/2, 2)
                
                broker_b_mid = base_price + random.uniform(-2, 2)
                broker_b_spread = random.uniform(0.2, 0.5)
                broker_b_bid = round(broker_b_mid - broker_b_spread/2, 2)
                broker_b_ask = round(broker_b_mid + broker_b_spread/2, 2)
                
                st.session_state.xauusd_arbitrage['price_feeds']['broker_a'].update({
                    'bid': broker_a_bid,
                    'ask': broker_a_ask,
                    'timestamp': current_time
                })
                
                st.session_state.xauusd_arbitrage['price_feeds']['broker_b'].update({
                    'bid': broker_b_bid,
                    'ask': broker_b_ask,
                    'timestamp': current_time
                })
                
                self.detect_arbitrage_opportunities()
                
                if st.session_state.xauusd_arbitrage['settings']['auto_execute']:
                    self.auto_execute_trades()
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Arbitrage monitoring error: {e}")
                break
    
    def detect_arbitrage_opportunities(self):
        """Detect arbitrage opportunities between brokers"""
        broker_a = st.session_state.xauusd_arbitrage['price_feeds']['broker_a']
        broker_b = st.session_state.xauusd_arbitrage['price_feeds']['broker_b']
        min_spread = st.session_state.xauusd_arbitrage['settings']['min_spread_pips']
        
        if not broker_a['bid'] or not broker_b['bid']:
            return
        
        spread_1 = broker_b['bid'] - broker_a['ask']
        spread_1_pips = spread_1 / 0.1
        
        spread_2 = broker_a['bid'] - broker_b['ask']
        spread_2_pips = spread_2 / 0.1
        
        opportunities = []
        
        if spread_1_pips >= min_spread:
            opportunities.append({
                'id': len(st.session_state.xauusd_arbitrage['opportunities']) + 1,
                'type': f"Buy {broker_a['name']} → Sell {broker_b['name']}",
                'buy_broker': broker_a['name'],
                'sell_broker': broker_b['name'],
                'buy_price': broker_a['ask'],
                'sell_price': broker_b['bid'],
                'spread_pips': round(spread_1_pips, 2),
                'spread_usd': round(spread_1, 2),
                'potential_profit': round(spread_1 * st.session_state.xauusd_arbitrage['settings']['max_position_size'] * 100, 2),
                'timestamp': datetime.now(),
                'status': 'ACTIVE',
                'latency_advantage': broker_b['latency'] - broker_a['latency']
            })
        
        if spread_2_pips >= min_spread:
            opportunities.append({
                'id': len(st.session_state.xauusd_arbitrage['opportunities']) + 1,
                'type': f"Buy {broker_b['name']} → Sell {broker_a['name']}",
                'buy_broker': broker_b['name'],
                'sell_broker': broker_a['name'],
                'buy_price': broker_b['ask'],
                'sell_price': broker_a['bid'],
                'spread_pips': round(spread_2_pips, 2),
                'spread_usd': round(spread_2, 2),
                'potential_profit': round(spread_2 * st.session_state.xauusd_arbitrage['settings']['max_position_size'] * 100, 2),
                'timestamp': datetime.now(),
                'status': 'ACTIVE',
                'latency_advantage': broker_a['latency'] - broker_b['latency']
            })
        
        for opp in opportunities:
            st.session_state.xauusd_arbitrage['opportunities'].append(opp)
            st.session_state.xauusd_arbitrage['stats']['total_opportunities'] += 1
        
        if len(st.session_state.xauusd_arbitrage['opportunities']) > 100:
            st.session_state.xauusd_arbitrage['opportunities'] = st.session_state.xauusd_arbitrage['opportunities'][-100:]
    
    def execute_arbitrage_trade(self, opportunity):
        """Execute an arbitrage trade"""
        position = {
            'id': len(st.session_state.xauusd_arbitrage['positions']) + 1,
            'opportunity_id': opportunity['id'],
            'type': opportunity['type'],
            'buy_broker': opportunity['buy_broker'],
            'sell_broker': opportunity['sell_broker'],
            'buy_price': opportunity['buy_price'],
            'sell_price': opportunity['sell_price'],
            'position_size': st.session_state.xauusd_arbitrage['settings']['max_position_size'],
            'spread_pips': opportunity['spread_pips'],
            'entry_time': datetime.now(),
            'status': 'OPEN',
            'unrealized_pnl': 0,
            'realized_pnl': 0
        }
        
        st.session_state.xauusd_arbitrage['positions'].append(position)
        st.session_state.xauusd_arbitrage['stats']['executed_trades'] += 1
        
        opportunity['status'] = 'EXECUTED'
        
        return position
    
    def close_position(self, position_id):
        """Close an arbitrage position"""
        for i, pos in enumerate(st.session_state.xauusd_arbitrage['positions']):
            if pos['id'] == position_id and pos['status'] == 'OPEN':
                realized_pnl = pos['spread_pips'] * pos['position_size'] * 10
                
                st.session_state.xauusd_arbitrage['positions'][i]['status'] = 'CLOSED'
                st.session_state.xauusd_arbitrage['positions'][i]['realized_pnl'] = realized_pnl
                st.session_state.xauusd_arbitrage['positions'][i]['close_time'] = datetime.now()
                
                st.session_state.xauusd_arbitrage['stats']['total_pnl'] += realized_pnl
                st.session_state.xauusd_arbitrage['stats']['today_pnl'] += realized_pnl
                
                if realized_pnl > 0:
                    st.session_state.xauusd_arbitrage['stats']['successful_trades'] += 1
                
                total_closed = len([p for p in st.session_state.xauusd_arbitrage['positions'] if p['status'] == 'CLOSED'])
                if total_closed > 0:
                    st.session_state.xauusd_arbitrage['stats']['win_rate'] = (st.session_state.xauusd_arbitrage['stats']['successful_trades'] / total_closed) * 100
                    st.session_state.xauusd_arbitrage['stats']['avg_profit_per_trade'] = st.session_state.xauusd_arbitrage['stats']['total_pnl'] / total_closed
                
                return True
        return False
    
    def auto_execute_trades(self):
        """Auto-execute profitable opportunities"""
        active_positions = len([pos for pos in st.session_state.xauusd_arbitrage['positions'] if pos['status'] == 'OPEN'])
        max_concurrent = st.session_state.xauusd_arbitrage['settings']['max_concurrent_trades']
        
        if active_positions >= max_concurrent:
            return
        
        recent_opportunities = [opp for opp in st.session_state.xauusd_arbitrage['opportunities'] 
                              if opp['status'] == 'ACTIVE' and 
                              (datetime.now() - opp['timestamp']).seconds < 5]
        
        for opp in recent_opportunities[:max_concurrent - active_positions]:
            if opp['spread_pips'] >= st.session_state.xauusd_arbitrage['settings']['min_spread_pips']:
                self.execute_arbitrage_trade(opp)

# Initialize arbitrage engine
arbitrage_engine = XAUUSDArbitrageEngine()

# ENHANCED CSS WITH NEW STYLES
theme_css = """
<style>
:root {
    --yantra-primary: #1E3A8A;
    --yantra-secondary: #3B82F6;
    --yantra-success: #10B981;
    --yantra-danger: #EF4444;
    --yantra-warning: #F59E0B;
    --yantra-gold: #F59E0B;
    --yantra-purple: #8B5CF6;
    --yantra-teal: #14B8A6;
}
.yantra-header {
    background: linear-gradient(135deg, var(--yantra-primary) 0%, var(--yantra-secondary) 100%);
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(30, 58, 138, 0.3);
}
.yantra-logo {
    font-size: 2.8rem;
    font-weight: 900;
    color: white;
    text-align: center;
    letter-spacing: 4px;
    margin: 0;
}
.yantra-tagline {
    color: #E5E7EB;
    text-align: center;
    font-size: 1.2rem;
    margin-top: 0.5rem;
}
.status-active {
    background: linear-gradient(135deg, var(--yantra-success) 0%, #059669 100%);
    color: white;
    padding: 0.6rem 1.2rem;
    border-radius: 25px;
    font-weight: 700;
    display: inline-block;
}
.status-inactive {
    background: linear-gradient(135deg, var(--yantra-danger) 0%, #DC2626 100%);
    color: white;
    padding: 0.6rem 1.2rem;
    border-radius: 25px;
    font-weight: 700;
    display: inline-block;
}
.broker-card {
    background: linear-gradient(135deg, #374151 0%, #1F2937 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}
.broker-connected {
    border-left: 4px solid var(--yantra-success);
}
.broker-disconnected {
    border-left: 4px solid var(--yantra-danger);
}
.portfolio-card {
    background: linear-gradient(135deg, var(--yantra-purple) 0%, #7C3AED 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(139, 92, 246, 0.3);
}
.copy-trader-card {
    background: linear-gradient(135deg, var(--yantra-teal) 0%, #0F766E 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(20, 184, 166, 0.3);
}
.arbitrage-opportunity {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
}
.gold-opportunity {
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    box-shadow: 0 4px 16px rgba(245, 158, 11, 0.3);
}
.price-feed {
    background: linear-gradient(135deg, #374151 0%, #1F2937 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}
.profit-positive {
    color: #10B981;
    font-weight: bold;
}
.profit-negative {
    color: #EF4444;
    font-weight: bold;
}
.strategy-card {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}
footer {visibility: hidden;}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

# ENHANCED SIDEBAR WITH ALL NEW FEATURES
with st.sidebar:
    st.markdown("### 🎯 YANTRA Control Center")
    st.markdown("---")
    
    st.markdown("**Theme:** Use browser settings or Streamlit menu (⋮)")
    
    st.markdown("---")
    st.markdown("### 📍 Navigation")
    
    pages = {
        "🏠 Dashboard": "Dashboard",
        "💹 Trading Terminal": "Trading Terminal",
        "📈 Advanced Charts": "Advanced Charts",
        "📊 Tick Charts": "Tick Charts",
        "🤖 Auto Trading": "Auto Trading",
        "⚡ Latency Arbitrage": "Latency Arbitrage",
        "🥇 XAUUSD Arbitrage": "XAUUSD Arbitrage",
        "🔗 Synthetic Symbols": "Synthetic Symbols",
        "🏦 Advanced Broker Manager": "Advanced Broker Manager",  # ENHANCED
        "📊 Portfolio Manager": "Portfolio Manager",  # NEW
        "📋 Advanced Orders": "Advanced Orders",  # NEW
        "🔄 Strategy Backtesting": "Strategy Backtesting",  # NEW
                "👥 Copy Trading": "Copy Trading",  # NEW
        "🌐 LP Bridge Manager": "LP Bridge Manager",
        "📊 Analytics": "Analytics",
        "📔 Trade Journal": "Trade Journal",
        "⚠️ Risk Manager": "Risk Manager",
        "🚨 Kill Switch": "Kill Switch",
        "🛡️ Safety Center": "Safety Center",
        "⚙️ Settings": "Settings"
    }
    
    for display_name, page_name in pages.items():
        if st.button(display_name, key=f"nav_{page_name}", use_container_width=True):
            st.session_state.page = page_name
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔥 Quick Stats")
    
    # Enhanced quick stats
    total_balance = sum([acc['balance'] for broker in st.session_state.advanced_brokers.values() for acc in broker['accounts']])
    total_equity = sum([acc['equity'] for broker in st.session_state.advanced_brokers.values() for acc in broker['accounts']])
    total_margin = sum([acc['margin'] for broker in st.session_state.advanced_brokers.values() for acc in broker['accounts']])
    
    st.metric("💰 Total Balance", f"${total_balance:,.2f}")
    st.metric("📈 Total Equity", f"${total_equity:,.2f}")
    st.metric("📊 Used Margin", f"${total_margin:,.2f}")
    
    # Portfolio summary
    open_positions = len(st.session_state.portfolio['positions'])
    total_pnl = sum([pos['pnl'] for pos in st.session_state.portfolio['positions']])
    
    st.metric("🎯 Open Positions", open_positions)
    st.metric("💹 Unrealized P&L", f"${total_pnl:,.2f}")
    
    st.markdown("---")
    st.markdown("### ⚡ System Status")
    
    connected_brokers = len([b for b in st.session_state.advanced_brokers.values() if b['status'] == 'Connected'])
    total_brokers = len(st.session_state.advanced_brokers)
    
    if connected_brokers == total_brokers:
        st.success(f"🟢 All Brokers Online ({connected_brokers}/{total_brokers})")
    else:
        st.warning(f"⚠️ {connected_brokers}/{total_brokers} Brokers Online")
    
    if st.session_state.xauusd_arbitrage['monitoring']:
        st.success("🥇 XAUUSD Arbitrage: ACTIVE")
    else:
        st.info("🥇 XAUUSD Arbitrage: IDLE")
    
    if st.session_state.auto_trading['enabled']:
        st.success("🤖 Auto Trading: ACTIVE")
    else:
        st.info("🤖 Auto Trading: IDLE")

# MAIN CONTENT AREA
st.markdown("""
<div class="yantra-header">
    <h1 class="yantra-logo">⭐ YANTRA</h1>
    <p class="yantra-tagline">Professional Latency Arbitrage & Multi-Broker Trading Platform</p>
</div>
""", unsafe_allow_html=True)

# PAGE ROUTING WITH ALL NEW FEATURES
if st.session_state.page == "Dashboard":
    st.markdown("# 🏠 Enhanced Dashboard")
    
    # Enhanced metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("💰 Total Balance", f"${total_balance:,.2f}", f"+${random.randint(50, 200)}")
    with col2:
        st.metric("📈 Total Equity", f"${total_equity:,.2f}", f"{((total_equity/total_balance - 1) * 100):+.2f}%")
    with col3:
        st.metric("🎯 Open Positions", open_positions, f"+{random.randint(1, 3)}")
    with col4:
        st.metric("💹 Today's P&L", f"${total_pnl + st.session_state.xauusd_arbitrage['stats']['today_pnl']:,.2f}")
    with col5:
        active_strategies = len([s for s in st.session_state.copy_trading['my_subscriptions']])
        st.metric("🤖 Active Strategies", active_strategies + len(st.session_state.auto_trading['strategies']))
    
    st.markdown("---")
    
    # Enhanced dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Portfolio Performance")
        
        # Generate portfolio performance chart
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        portfolio_values = []
        base_value = total_equity
        
        for i in range(30):
            daily_change = np.random.normal(0.02, 0.05) * base_value
            base_value += daily_change
            portfolio_values.append(base_value)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=portfolio_values,
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#10B981', width=3),
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))
        
        fig.update_layout(
            title="30-Day Portfolio Performance",
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🏦 Broker Status")
        
        for broker_name, broker_data in st.session_state.advanced_brokers.items():
            status_class = "broker-connected" if broker_data['status'] == 'Connected' else "broker-disconnected"
            
            st.markdown(f"""
            <div class="broker-card {status_class}">
                <h4>{broker_name}</h4>
                <p><strong>Status:</strong> {broker_data['status']}</p>
                <p><strong>Accounts:</strong> {len(broker_data['accounts'])}</p>
                <p><strong>Avg Execution:</strong> {broker_data['performance']['avg_execution_time']}ms</p>
                <p><strong>Daily Volume:</strong> ${broker_data['performance']['daily_volume']:,}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("🚀 Start All Systems", key="start_all_systems"):
            st.session_state.auto_trading['enabled'] = True
            st.session_state.arbitrage_settings['enabled'] = True
            if not st.session_state.xauusd_arbitrage['monitoring']:
                st.session_state.xauusd_arbitrage['monitoring'] = True
                arbitrage_engine.start_monitoring()
            st.success("✅ All systems activated!")
            st.rerun()
        
        if st.button("⏸️ Pause All Trading", key="pause_all_trading"):
            st.session_state.auto_trading['enabled'] = False
            st.session_state.arbitrage_settings['enabled'] = False
            arbitrage_engine.stop_monitoring()
            st.warning("⚠️ All trading paused!")
            st.rerun()

elif st.session_state.page == "Advanced Broker Manager":
    st.markdown("# 🏦 Advanced Broker Manager")
    
    # Broker overview
    st.markdown("### 📊 Broker Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        connected_count = len([b for b in st.session_state.advanced_brokers.values() if b['status'] == 'Connected'])
        st.metric("Connected Brokers", f"{connected_count}/{len(st.session_state.advanced_brokers)}")
    
    with col2:
        total_accounts = sum([len(b['accounts']) for b in st.session_state.advanced_brokers.values()])
        st.metric("Total Accounts", total_accounts)
    
    with col3:
        avg_execution = np.mean([b['performance']['avg_execution_time'] for b in st.session_state.advanced_brokers.values() if b['status'] == 'Connected'])
        st.metric("Avg Execution", f"{avg_execution:.1f}ms")
    
    with col4:
        total_volume = sum([b['performance']['daily_volume'] for b in st.session_state.advanced_brokers.values()])
        st.metric("Daily Volume", f"${total_volume:,}")
    
    st.markdown("---")
    
    # Detailed broker management
    for broker_name, broker_data in st.session_state.advanced_brokers.items():
        with st.expander(f"🏦 {broker_name} - {broker_data['status']}", expanded=broker_data['status'] == 'Connected'):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 💳 Accounts")
                
                if broker_data['accounts']:
                    accounts_df = pd.DataFrame(broker_data['accounts'])
                    st.dataframe(accounts_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No accounts configured")
                
                # Add new account
                st.markdown("**Add New Account:**")
                new_account_col1, new_account_col2, new_account_col3 = st.columns(3)
                
                with new_account_col1:
                    new_account_id = st.text_input("Account ID", key=f"new_acc_{broker_name}")
                with new_account_col2:
                    new_account_type = st.selectbox("Type", ["Live", "Demo"], key=f"new_type_{broker_name}")
                with new_account_col3:
                    new_leverage = st.number_input("Leverage", 1, 1000, 100, key=f"new_lev_{broker_name}")
                
                if st.button(f"➕ Add Account", key=f"add_acc_{broker_name}"):
                    new_account = {
                        'account_id': new_account_id,
                        'type': new_account_type,
                        'balance': 10000.00,
                        'equity': 10000.00,
                        'margin': 0.00,
                        'free_margin': 10000.00,
                        'leverage': new_leverage,
                        'currency': 'USD'
                    }
                    st.session_state.advanced_brokers[broker_name]['accounts'].append(new_account)
                    st.success(f"✅ Account {new_account_id} added!")
                    st.rerun()
            
            with col2:
                st.markdown("#### 📈 Performance Metrics")
                
                perf = broker_data['performance']
                
                st.metric("Execution Time", f"{perf['avg_execution_time']}ms")
                st.metric("Fill Rate", f"{perf['fill_rate']}%")
                st.metric("Uptime", f"{perf['uptime']}%")
                st.metric("Avg Slippage", f"{perf['slippage_avg']} pips")
                st.metric("Commission Paid", f"${perf['commission_paid']}")
                st.metric("Monthly Trades", f"{perf['monthly_trades']:,}")
                
                # Broker settings
                st.markdown("#### ⚙️ Settings")
                
                settings = broker_data['settings']
                
                settings['max_slippage'] = st.slider(
                    "Max Slippage (pips)", 0.1, 5.0, settings['max_slippage'], 0.1,
                    key=f"slippage_{broker_name}"
                )
                
                settings['execution_mode'] = st.selectbox(
                    "Execution Mode", ["Market", "Instant", "Request"],
                    index=["Market", "Instant", "Request"].index(settings['execution_mode']),
                    key=f"exec_mode_{broker_name}"
                )
                
                settings['partial_fills'] = st.checkbox(
                    "Allow Partial Fills", settings['partial_fills'],
                    key=f"partial_{broker_name}"
                )
                
                settings['auto_reconnect'] = st.checkbox(
                    "Auto Reconnect", settings['auto_reconnect'],
                    key=f"reconnect_{broker_name}"
                )
                
                # Connection controls
                st.markdown("#### 🔌 Connection")
                
                if broker_data['status'] == 'Connected':
                    if st.button(f"🔌 Disconnect", key=f"disconnect_{broker_name}"):
                        st.session_state.advanced_brokers[broker_name]['status'] = 'Disconnected'
                        st.warning(f"⚠️ {broker_name} disconnected!")
                        st.rerun()
                else:
                    if st.button(f"🔌 Connect", key=f"connect_{broker_name}"):
                        st.session_state.advanced_brokers[broker_name]['status'] = 'Connected'
                        st.success(f"✅ {broker_name} connected!")
                        st.rerun()
            
            # Spread monitoring
            st.markdown("#### 📊 Current Spreads")
            
            if broker_data['status'] == 'Connected':
                spreads_data = broker_data['performance']['spreads_avg']
                if spreads_data:
                    spread_cols = st.columns(len(spreads_data))
                    for i, (symbol, spread) in enumerate(spreads_data.items()):
                        with spread_cols[i]:
                            st.metric(symbol, f"{spread} pips")
                else:
                    st.info("No spread data available")
            else:
                st.info("Broker disconnected - no spread data")

elif st.session_state.page == "Portfolio Manager":
    st.markdown("# 📊 Portfolio Manager")
    
    # Portfolio overview
    col1, col2, col3, col4 = st.columns(4)
    
    total_positions = len(st.session_state.portfolio['positions'])
    total_unrealized_pnl = sum([pos['pnl'] for pos in st.session_state.portfolio['positions']])
    total_swap = sum([pos['swap'] for pos in st.session_state.portfolio['positions']])
    total_commission = sum([pos['commission'] for pos in st.session_state.portfolio['positions']])
    
    with col1:
        st.metric("Open Positions", total_positions)
    with col2:
        st.metric("Unrealized P&L", f"${total_unrealized_pnl:.2f}")
    with col3:
        st.metric("Total Swap", f"${total_swap:.2f}")
    with col4:
        st.metric("Total Commission", f"${total_commission:.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Open Positions")
        
        if st.session_state.portfolio['positions']:
            # Create positions dataframe
            positions_data = []
            for pos in st.session_state.portfolio['positions']:
                positions_data.append({
                    'ID': pos['id'],
                    'Symbol': pos['symbol'],
                    'Type': pos['type'],
                    'Volume': pos['volume'],
                    'Entry Price': pos['entry_price'],
                    'Current Price': pos['current_price'],
                    'P&L': f"${pos['pnl']:.2f}",
                    'Swap': f"${pos['swap']:.2f}",
                    'Commission': f"${pos['commission']:.2f}",
                    'Broker': pos['broker'],
                    'Duration': str(datetime.now() - pos['open_time']).split('.')[0]
                })
            
            positions_df = pd.DataFrame(positions_data)
            st.dataframe(positions_df, use_container_width=True, hide_index=True)
            
            # Position management
            st.markdown("#### 🎯 Position Management")
            
            selected_position = st.selectbox(
                "Select Position to Manage",
                options=[f"{pos['id']} - {pos['symbol']} {pos['type']}" for pos in st.session_state.portfolio['positions']],
                key="selected_position"
            )
            
            if selected_position:
                pos_id = int(selected_position.split(' - ')[0])
                position = next(pos for pos in st.session_state.portfolio['positions'] if pos['id'] == pos_id)
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("🔒 Close Position", key=f"close_pos_{pos_id}"):
                        # Move to history and remove from positions
                        position['close_time'] = datetime.now()
                        position['status'] = 'CLOSED'
                        st.session_state.portfolio['history'].append(position)
                        st.session_state.portfolio['positions'] = [p for p in st.session_state.portfolio['positions'] if p['id'] != pos_id]
                        st.success(f"✅ Position {pos_id} closed!")
                        st.rerun()
                
                with col_b:
                    if st.button("📈 Modify SL/TP", key=f"modify_pos_{pos_id}"):
                        st.info("SL/TP modification feature coming soon!")
                
                with col_c:
                    if st.button("📊 Position Details", key=f"details_pos_{pos_id}"):
                        st.json(position)
        
        else:
            st.info("No open positions")
    
    with col2:
        st.markdown("### 📊 Portfolio Allocation")
        
        # Portfolio allocation pie chart
        allocation = st.session_state.portfolio['allocation']
        
        fig = go.Figure(data=go.Pie(
            labels=list(allocation.keys()),
            values=list(allocation.values()),
            hole=0.4,
            marker_colors=['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
        ))
        
        fig.update_layout(
            title="Asset Allocation",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📈 Portfolio Analytics")
        
        analytics = st.session_state.portfolio['analytics']
        
        st.metric("Total P&L", f"${analytics['total_pnl']:.2f}")
        st.metric("Win Rate", f"{analytics['win_rate']:.1f}%")
        st.metric("Profit Factor", f"{analytics['profit_factor']:.2f}")
        st.metric("Max Drawdown", f"{analytics['max_drawdown']:.1f}%")
        st.metric("Sharpe Ratio", f"{analytics['sharpe_ratio']:.2f}")
        
        # Risk metrics
        st.markdown("### ⚠️ Risk Metrics")
        
        portfolio_risk = (total_unrealized_pnl / total_equity) * 100 if total_equity > 0 else 0
        
        if portfolio_risk > 5:
            st.error(f"🚨 High Risk: {portfolio_risk:.1f}%")
        elif portfolio_risk > 2:
            st.warning(f"⚠️ Medium Risk: {portfolio_risk:.1f}%")
        else:
            st.success(f"✅ Low Risk: {portfolio_risk:.1f}%")
        
        # Correlation matrix
        st.markdown("### 🔗 Position Correlation")
        
        symbols = list(set([pos['symbol'] for pos in st.session_state.portfolio['positions']]))
        if len(symbols) > 1:
            # Generate sample correlation matrix
            correlation_matrix = np.random.rand(len(symbols), len(symbols))
            correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
            np.fill_diagonal(correlation_matrix, 1)
            
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix,
                x=symbols,
                y=symbols,
                colorscale='RdYlBu',
                zmid=0
            ))
            
            fig.update_layout(
                title="Position Correlation",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need 2+ positions for correlation analysis")

elif st.session_state.page == "Advanced Orders":
    st.markdown("# 📋 Advanced Orders")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 New Order", "📋 Pending Orders", "🎯 Order Templates", "🔄 OCO Orders"])
    
    with tab1:
        st.markdown("### 📝 Create Advanced Order")
        
        col1, col2 = st.columns(2)
        
        with col1:
            order_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="order_symbol")
            order_type = st.selectbox("Order Type", ["Market", "Limit", "Stop", "Stop Limit"], key="order_type")
            order_side = st.selectbox("Side", ["BUY", "SELL"], key="order_side")
            order_volume = st.number_input("Volume", 0.01, 100.0, 1.0, 0.01, key="order_volume")
            
            if order_type in ["Limit", "Stop", "Stop Limit"]:
                order_price = st.number_input("Order Price", 0.0001, 10000.0, 1.0000, 0.0001, key="order_price")
        
        with col2:
            stop_loss = st.number_input("Stop Loss (pips)", 0, 1000, 20, key="order_sl")
            take_profit = st.number_input("Take Profit (pips)", 0, 1000, 30, key="order_tp")
            
            trailing_stop = st.checkbox("Trailing Stop", key="trailing_stop")
            if trailing_stop:
                trailing_distance = st.number_input("Trailing Distance (pips)", 1, 100, 15, key="trailing_distance")
            
            expiry_type = st.selectbox("Expiry", ["GTC", "Today", "Custom"], key="expiry_type")
            if expiry_type == "Custom":
                expiry_date = st.date_input("Expiry Date", key="expiry_date")
                expiry_time = st.time_input("Expiry Time", key="expiry_time")
        
        # Advanced options
        st.markdown("#### 🔧 Advanced Options")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            max_slippage = st.slider("Max Slippage (pips)", 0.1, 5.0, 1.0, 0.1, key="order_slippage")
        with col_b:
            partial_fills = st.checkbox("Allow Partial Fills", True, key="order_partial")
        with col_c:
            broker_preference = st.selectbox("Preferred Broker", ["Auto", "Divit Capital", "Kama Capital"], key="order_broker")
        
        if st.button("📤 Place Order", key="place_advanced_order"):
            new_order = {
                'id': len(st.session_state.advanced_orders['pending_orders']) + 1,
                'symbol': order_symbol,
                'type': order_type,
                'side': order_side,
                'volume': order_volume,
                'price': order_price if order_type in ["Limit", "Stop", "Stop Limit"] else 0,
                'sl_pips': stop_loss,
                'tp_pips': take_profit,
                'trailing_stop': trailing_stop,
                'trailing_distance': trailing_distance if trailing_stop else 0,
                'expiry': expiry_type,
                'max_slippage': max_slippage,
                'partial_fills': partial_fills,
                'broker': broker_preference,
                'status': 'PENDING',
                'created_time': datetime.now()
            }
            
            st.session_state.advanced_orders['pending_orders'].append(new_order)
            st.success(f"✅ Order placed: {order_side} {order_volume} {order_symbol}")
            st.rerun()
    
    with tab2:
        st.markdown("### 📋 Pending Orders")
        
        if st.session_state.advanced_orders['pending_orders']:
            orders_data = []
            for order in st.session_state.advanced_orders['pending_orders']:
                orders_data.append({
                    'ID': order['id'],
                    'Symbol': order['symbol'],
                    'Type': order['type'],
                    'Side': order['side'],
                    'Volume': order['volume'],
                    'Price': order['price'] if order['price'] > 0 else 'Market',
                    'SL': f"{order['sl_pips']} pips",
                    'TP': f"{order['tp_pips']} pips",
                    'Status': order['status'],
                    'Created': order['created_time'].strftime('%H:%M:%S')
                })
            
            orders_df = pd.DataFrame(orders_data)
            st.dataframe(orders_df, use_container_width=True, hide_index=True)
            
            # Order management
            selected_order = st.selectbox(
                "Select Order to Manage",
                options=[f"{order['id']} - {order['symbol']} {order['side']}" for order in st.session_state.advanced_orders['pending_orders']],
                key="selected_order"
            )
            
            if selected_order:
                order_id = int(selected_order.split(' - ')[0])
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("❌ Cancel Order", key=f"cancel_order_{order_id}"):
                        st.session_state.advanced_orders['pending_orders'] = [
                            o for o in st.session_state.advanced_orders['pending_orders'] if o['id'] != order_id
                        ]
                        st.success(f"✅ Order {order_id} cancelled!")
                        st.rerun()
                
                with col_b:
                    if st.button("✏️ Modify Order", key=f"modify_order_{order_id}"):
                        st.info("Order modification feature coming soon!")
                
                with col_c:
                    if st.button("🚀 Execute Now", key=f"execute_order_{order_id}"):
                        # Move order to positions
                        order = next(o for o in st.session_state.advanced_orders['pending_orders'] if o['id'] == order_id)
                        
                        new_position = {
                            'id': len(st.session_state.portfolio['positions']) + 1,
                            'symbol': order['symbol'],
                            'type': order['side'],
                            'volume': order['volume'],
                            'entry_price': order['price'] if order['price'] > 0 else random.uniform(1.0800, 1.0900),
                            'current_price': order['price'] if order['price'] > 0 else random.uniform(1.0800, 1.0900),
                            'pnl': 0,
                            'swap': 0,
                            'commission': order['volume'] * 7,
                            'open_time': datetime.now(),
                            'broker': order['broker'] if order['broker'] != 'Auto' else 'Divit Capital'
                        }
                        
                        st.session_state.portfolio['positions'].append(new_position)
                        st.session_state.advanced_orders['pending_orders'] = [
                            o for o in st.session_state.advanced_orders['pending_orders'] if o['id'] != order_id
                        ]
                        
                        st.success(f"✅ Order {order_id} executed!")
                        st.rerun()
        
        else:
            st.info("No pending orders")
    
    with tab3:
        st.markdown("### 🎯 Order Templates")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Create Template")
            
            template_name = st.text_input("Template Name", key="template_name")
            template_sl = st.number_input("Default SL (pips)", 1, 1000, 20, key="template_sl")
            template_tp = st.number_input("Default TP (pips)", 1, 1000, 30, key="template_tp")
            template_volume = st.number_input("Default Volume", 0.01, 100.0, 1.0, 0.01, key="template_volume")
            template_trailing = st.checkbox("Enable Trailing Stop", key="template_trailing")
            
            if st.button("💾 Save Template", key="save_template"):
                new_template = {
                    'name': template_name,
                    'sl_pips': template_sl,
                    'tp_pips': template_tp,
                    'volume': template_volume,
                    'trailing_stop': template_trailing
                }
                st.session_state.advanced_orders['order_templates'].append(new_template)
                st.success(f"✅ Template '{template_name}' saved!")
                st.rerun()
        
        with col2:
            st.markdown("#### 📋 Existing Templates")
            
            for i, template in enumerate(st.session_state.advanced_orders['order_templates']):
                with st.expander(f"📝 {template['name']}"):
                    st.write(f"**SL:** {template['sl_pips']} pips")
                    st.write(f"**TP:** {template['tp_pips']} pips")
                    st.write(f"**Volume:** {template['volume']}")
                    st.write(f"**Trailing:** {'Yes' if template['trailing_stop'] else 'No'}")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("🗑️ Delete", key=f"delete_template_{i}"):
                            st.session_state.advanced_orders['order_templates'].pop(i)
                            st.rerun()
                    
                    with col_b:
                        if st.button("📤 Use Template", key=f"use_template_{i}"):
                            st.info("Template applied to new order form!")
    
    with tab4:
        st.markdown("### 🔄 OCO (One-Cancels-Other) Orders")
        
        st.markdown("#### 📝 Create OCO Order")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Order 1:**")
            oco_symbol1 = st.selectbox("Symbol", st.session_state.mt5_symbols, key="oco_symbol1")
            oco_type1 = st.selectbox("Type", ["Limit", "Stop"], key="oco_type1")
            oco_side1 = st.selectbox("Side", ["BUY", "SELL"], key="oco_side1")
            oco_volume1 = st.number_input("Volume", 0.01, 100.0, 1.0, 0.01, key="oco_volume1")
            oco_price1 = st.number_input("Price", 0.0001, 10000.0, 1.0000, 0.0001, key="oco_price1")
        
        with col2:
            st.markdown("**Order 2:**")
            oco_symbol2 = st.selectbox("Symbol", st.session_state.mt5_symbols, key="oco_symbol2")
            oco_type2 = st.selectbox("Type", ["Limit", "Stop"], key="oco_type2")
            oco_side2 = st.selectbox("Side", ["BUY", "SELL"], key="oco_side2")
            oco_volume2 = st.number_input("Volume", 0.01, 100.0, 1.0, 0.01, key="oco_volume2")
            oco_price2 = st.number_input("Price", 0.0001, 10000.0, 1.0000, 0.0001, key="oco_price2")
        
        if st.button("🔄 Create OCO Order", key="create_oco"):
            oco_order = {
                'id': len(st.session_state.advanced_orders['oco_orders']) + 1,
                'order1': {
                    'symbol': oco_symbol1,
                    'type': oco_type1,
                    'side': oco_side1,
                    'volume': oco_volume1,
                    'price': oco_price1
                },
                'order2': {
                    'symbol': oco_symbol2,
                    'type': oco_type2,
                    'side': oco_side2,
                    'volume': oco_volume2,
                    'price': oco_price2
                },
                'status': 'ACTIVE',
                'created_time': datetime.now()
            }
            
            st.session_state.advanced_orders['oco_orders'].append(oco_order)
            st.success("✅ OCO Order created!")
            st.rerun()
        
        # Display existing OCO orders
        if st.session_state.advanced_orders['oco_orders']:
            st.markdown("#### 📋 Active OCO Orders")
            
            for oco in st.session_state.advanced_orders['oco_orders']:
                with st.expander(f"🔄 OCO #{oco['id']} - {oco['status']}"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write("**Order 1:**")
                        st.write(f"{oco['order1']['side']} {oco['order1']['volume']} {oco['order1']['symbol']}")
                        st.write(f"{oco['order1']['type']} @ {oco['order1']['price']}")
                    
                    with col_b:
                        st.write("**Order 2:**")
                        st.write(f"{oco['order2']['side']} {oco['order2']['volume']} {oco['order2']['symbol']}")
                        st.write(f"{oco['order2']['type']} @ {oco['order2']['price']}")
                    
                    if st.button(f"❌ Cancel OCO", key=f"cancel_oco_{oco['id']}"):
                        st.session_state.advanced_orders['oco_orders'] = [
                            o for o in st.session_state.advanced_orders['oco_orders'] if o['id'] != oco['id']
                        ]
                        st.success(f"✅ OCO Order #{oco['id']} cancelled!")
                        st.rerun()

elif st.session_state.page == "Strategy Backtesting":
    st.markdown("# 🔄 Strategy Backtesting")
    
    tab1, tab2, tab3 = st.tabs(["🧪 Run Backtest", "📊 Results", "📈 Strategy Builder"])
    
    with tab1:
        st.markdown("### 🧪 Backtest Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Basic Settings")
            
            backtest_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="backtest_symbol")
            backtest_timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "1H", "4H", "1D"], index=3, key="backtest_timeframe")
            
            start_date = st.date_input("Start Date", datetime(2024, 1, 1), key="backtest_start")
            end_date = st.date_input("End Date", datetime(2024, 12, 31), key="backtest_end")
            
            initial_balance = st.number_input("Initial Balance", 1000, 1000000, 10000, 1000, key="backtest_balance")
            risk_per_trade = st.slider("Risk per Trade (%)", 0.1, 10.0, 2.0, 0.1, key="backtest_risk")
        
        with col2:
            st.markdown("#### 🎯 Strategy Parameters")
            
            strategy_type = st.selectbox("Strategy Type", ["MA Crossover", "RSI Mean Reversion", "Bollinger Bands", "Custom"], key="strategy_type")
            
            if strategy_type == "MA Crossover":
                fast_ma = st.number_input("Fast MA Period", 1, 100, 10, key="fast_ma")
                slow_ma = st.number_input("Slow MA Period", 1, 200, 20, key="slow_ma")
                
            elif strategy_type == "RSI Mean Reversion":
                rsi_period = st.number_input("RSI Period", 1, 50, 14, key="rsi_period")
                oversold = st.number_input("Oversold Level", 1, 50, 30, key="oversold")
                overbought = st.number_input("Overbought Level", 50, 99, 70, key="overbought")
                
            elif strategy_type == "Bollinger Bands":
                bb_period = st.number_input("BB Period", 1, 50, 20, key="bb_period")
                bb_std = st.number_input("Standard Deviation", 1.0, 3.0, 2.0, 0.1, key="bb_std")
            
            stop_loss_pips = st.number_input("Stop Loss (pips)", 1, 1000, 50, key="backtest_sl")
            take_profit_pips = st.number_input("Take Profit (pips)", 1, 1000, 100, key="backtest_tp")
        
        if st.button("🚀 Run Backtest", key="run_backtest"):
            with st.spinner("Running backtest..."):
                # Simulate backtest results
                time.sleep(2)
                
                # Generate sample backtest results
                num_trades = random.randint(50, 200)
                win_rate = random.uniform(45, 75)
                total_return = random.uniform(-20, 50)
                max_drawdown = random.uniform(5, 25)
                profit_factor = random.uniform(0.8, 2.5)
                sharpe_ratio = random.uniform(-0.5, 2.0)
                
                backtest_result = {
                    'strategy': strategy_type,
                    'symbol': backtest_symbol,
                    'timeframe': backtest_timeframe,
                    'period': f"{start_date} to {end_date}",
                    'initial_balance': initial_balance,
                    'final_balance': initial_balance * (1 + total_return/100),
                    'total_return': total_return,
                    'num_trades': num_trades,
                    'win_rate': win_rate,
                    'profit_factor': profit_factor,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio,
                    'parameters': {
                        'risk_per_trade': risk_per_trade,
                        'stop_loss': stop_loss_pips,
                        'take_profit': take_profit_pips
                    }
                }
                
                st.session_state.backtesting['current_backtest'] = backtest_result
                
                st.success("✅ Backtest completed!")
                st.rerun()
    
    with tab2:
        st.markdown("### 📊 Backtest Results")
        
        if st.session_state.backtesting['current_backtest']:
            result = st.session_state.backtesting['current_backtest']
            
            # Results overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Return", f"{result['total_return']:.2f}%")
            with col2:
                st.metric("Win Rate", f"{result['win_rate']:.1f}%")
            with col3:
                st.metric("Profit Factor", f"{result['profit_factor']:.2f}")
            with col4:
                st.metric("Max Drawdown", f"{result['max_drawdown']:.1f}%")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Trades", result['num_trades'])
            with col2:
                st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
            with col3:
                st.metric("Initial Balance", f"${result['initial_balance']:,}")
            with col4:
                st.metric("Final Balance", f"${result['final_balance']:,.2f}")
            
            # Equity curve
            st.markdown("#### 📈 Equity Curve")
            
            # Generate sample equity curve
            dates = pd.date_range(start=result['period'].split(' to ')[0], end=result['period'].split(' to ')[1], freq='D')
            equity_values = []
            current_equity = result['initial_balance']
            
            for i in range(len(dates)):
                daily_return = np.random.normal(result['total_return']/365/100, 0.02)
                current_equity *= (1 + daily_return)
                equity_values.append(current_equity)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=equity_values,
                mode='lines',
                name='Equity',
                line=dict(color='#10B981', width=2),
                fill='tonexty',
                fillcolor='rgba(16, 185, 129, 0.1)'
            ))
            
            fig.update_layout(
                title=f"Equity Curve - {result['strategy']} on {result['symbol']}",
                xaxis_title="Date",
                yaxis_title="Equity ($)",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trade distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Trade Distribution")
                
                # Generate sample trade P&L distribution
                trade_pnls = np.random.normal(50, 100, result['num_trades'])
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=trade_pnls,
                    nbinsx=20,
                    marker_color='#3B82F6',
                    opacity=0.7,
                    name="Trade P&L"
                ))
                
                fig.update_layout(
                    title="Trade P&L Distribution",
                    xaxis_title="P&L ($)",
                    yaxis_title="Frequency",
                    template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📋 Strategy Parameters")
                
                st.json(result['parameters'])
                
                st.markdown("#### 💾 Save Results")
                
                if st.button("💾 Save to Strategy Library", key="save_backtest"):
                    strategy_data = {
                        'name': f"{result['strategy']} - {result['symbol']}",
                        'description': f"Backtested {result['strategy']} strategy",
                        'parameters': result['parameters'],
                        'results': {
                            'total_return': result['total_return'],
                            'win_rate': result['win_rate'],
                            'max_drawdown': result['max_drawdown'],
                            'sharpe': result['sharpe_ratio']
                        }
                    }
                    
                    st.session_state.backtesting['strategies'].append(strategy_data)
                    st.success("✅ Strategy saved to library!")
        
        else:
            st.info("No backtest results available. Run a backtest first.")
    
    with tab3:
        st.markdown("### 📈 Strategy Builder")
        
        st.markdown("#### 🛠️ Visual Strategy Builder")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Entry Conditions:**")
            
            entry_indicator1 = st.selectbox("Indicator 1", ["MA", "RSI", "MACD", "Bollinger Bands"], key="entry_ind1")
            entry_condition1 = st.selectbox("Condition", ["Above", "Below", "Crosses Above", "Crosses Below"], key="entry_cond1")
            entry_value1 = st.number_input("Value", 0.0, 100.0, 50.0, key="entry_val1")
            
            entry_logic = st.selectbox("Logic", ["AND", "OR"], key="entry_logic")
            
            entry_indicator2 = st.selectbox("Indicator 2", ["MA", "RSI", "MACD", "Bollinger Bands"], key="entry_ind2")
            entry_condition2 = st.selectbox("Condition", ["Above", "Below", "Crosses Above", "Crosses Below"], key="entry_cond2")
            entry_value2 = st.number_input("Value", 0.0, 100.0, 30.0, key="entry_val2")
        
        with col2:
            st.markdown("**Exit Conditions:**")
            
            exit_type = st.selectbox("Exit Type", ["Fixed SL/TP", "Indicator Based", "Time Based"], key="exit_type")
            
            if exit_type == "Fixed SL/TP":
                exit_sl = st.number_input("Stop Loss (pips)", 1, 1000, 50, key="exit_sl")
                exit_tp = st.number_input("Take Profit (pips)", 1, 1000, 100, key="exit_tp")
            
            elif exit_type == "Indicator Based":
                exit_indicator = st.selectbox("Exit Indicator", ["MA", "RSI", "MACD"], key="exit_indicator")
                exit_condition = st.selectbox("Exit Condition", ["Above", "Below", "Crosses"], key="exit_condition")
                exit_value = st.number_input("Exit Value", 0.0, 100.0, 70.0, key="exit_value")
            
            elif exit_type == "Time Based":
                max_hold_time = st.number_input("Max Hold Time (hours)", 1, 168, 24, key="max_hold_time")
        
        # Strategy code generation
        st.markdown("#### 💻 Generated Strategy Code")
        
        strategy_code = f"""
# Generated Strategy Code
def custom_strategy():
    # Entry Conditions
    if {entry_indicator1.lower()} {entry_condition1.lower().replace(' ', '_')} {entry_value1}:
        if {entry_logic.lower()} {entry_indicator2.lower()} {entry_condition2.lower().replace(' ', '_')} {entry_value2}:
            return "BUY"
    
    # Exit Conditions
    if {exit_type.lower().replace(' ', '_')}:
        return "CLOSE"
    
    return "HOLD"
"""
        
        st.code(strategy_code, language='python')
        
        if st.button("💾 Save Custom Strategy", key="save_custom_strategy"):
            custom_strategy = {
                'name': f"Custom Strategy {len(st.session_state.backtesting['strategies']) + 1}",
                'description': 'Custom built strategy',
                'code': strategy_code,
                'parameters': {
                    'entry_indicator1': entry_indicator1,
                    'entry_condition1': entry_condition1,
                    'entry_value1': entry_value1,
                    'entry_logic': entry_logic,
                    'entry_indicator2': entry_indicator2,
                    'entry_condition2': entry_condition2,
                    'entry_value2': entry_value2,
                    'exit_type': exit_type
                },
                'results': {'total_return': 0, 'win_rate': 0, 'max_drawdown': 0, 'sharpe': 0}
            }
            
            st.session_state.backtesting['strategies'].append(custom_strategy)
            st.success("✅ Custom strategy saved!")

elif st.session_state.page == "Copy Trading":
    st.markdown("# 👥 Copy Trading")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Signal Providers", "📊 My Subscriptions", "⚙️ Copy Settings"])
    
    with tab1:
        st.markdown("### 🔍 Available Signal Providers")
        
        # Search and filter
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Search Providers", key="search_providers")
        with col2:
            min_return = st.slider("Min Monthly Return (%)", 0, 50, 10, key="min_return_filter")
        with col3:
            max_risk = st.slider("Max Risk Score", 1, 10, 7, key="max_risk_filter")
        
        # Display providers
        for provider in st.session_state.copy_trading['providers']:
            if provider['monthly_return'] >= min_return and provider['risk_score'] <= max_risk:
                if not search_term or search_term.lower() in provider['name'].lower():
                    
                    st.markdown(f"""
                    <div class="copy-trader-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3>{provider['avatar']} {provider['name']}</h3>
                                <p><strong>Followers:</strong> {provider['followers']:,} | <strong>Risk Score:</strong> {provider['risk_score']}/10</p>
                            </div>
                            <div style="text-align: right;">
                                <h4>+{provider['monthly_return']:.1f}%</h4>
                                <p>Monthly Return</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.metric("Win Rate", f"{provider['win_rate']:.1f}%")
                    with col_b:
                        st.metric("Max Drawdown", f"{provider['max_drawdown']:.1f}%")
                    with col_c:
                        st.metric("Subscription Fee", f"${provider['subscription_fee']}/month")
                    with col_d:
                        st.metric("Min Copy Amount", f"${provider['min_copy_amount']:,}")
                    
                    # Today's performance
                    col_e, col_f, col_g = st.columns(3)
                    
                    with col_e:
                        st.write(f"**Today's Trades:** {provider['trades_today']}")
                    with col_f:
                        profit_color = "profit-positive" if provider['profit_today'] > 0 else "profit-negative"
                        st.markdown(f"**Today's Profit:** <span class='{profit_color}'>${provider['profit_today']:.2f}</span>", unsafe_allow_html=True)
                    with col_g:
                        if provider['active']:
                            st.success("🟢 Currently Active")
                        else:
                            st.info("⚪ Inactive")
                    
                    # Subscription controls
                    is_subscribed = provider['id'] in [sub['provider_id'] for sub in st.session_state.copy_trading['my_subscriptions']]
                    
                    if not is_subscribed:
                        col_x, col_y = st.columns(2)
                        
                        with col_x:
                            copy_amount = st.number_input(
                                f"Copy Amount ($)", 
                                provider['min_copy_amount'], 
                                100000, 
                                provider['min_copy_amount'],
                                key=f"copy_amount_{provider['id']}"
                            )
                        
                        with col_y:
                            if st.button(f"📋 Subscribe", key=f"subscribe_{provider['id']}"):
                                new_subscription = {
                                    'provider_id': provider['id'],
                                    'provider_name': provider['name'],
                                    'copy_amount': copy_amount,
                                    'start_date': datetime.now(),
                                    'status': 'ACTIVE',
                                    'total_copied_trades': 0,
                                    'total_profit': 0
                                }
                                
                                st.session_state.copy_trading['my_subscriptions'].append(new_subscription)
                                st.success(f"✅ Subscribed to {provider['name']}!")
                                st.rerun()
                    else:
                        st.info("✅ Already subscribed")
                    
                    st.markdown("---")
    
    with tab2:
        st.markdown("### 📊 My Subscriptions")
        
        if st.session_state.copy_trading['my_subscriptions']:
            for subscription in st.session_state.copy_trading['my_subscriptions']:
                provider = next(p for p in st.session_state.copy_trading['providers'] if p['id'] == subscription['provider_id'])
                
                st.markdown(f"""
                <div class="copy-trader-card">
                    <h3>{provider['avatar']} {subscription['provider_name']}</h3>
                    <p><strong>Status:</strong> {subscription['status']} | <strong>Copy Amount:</strong> ${subscription['copy_amount']:,}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Copied Trades", subscription['total_copied_trades'])
                with col2:
                    profit_color = "profit-positive" if subscription['total_profit'] > 0 else "profit-negative"
                    st.markdown(f"**Total Profit:** <span class='{profit_color}'>${subscription['total_profit']:.2f}</span>", unsafe_allow_html=True)
                with col3:
                    days_subscribed = (datetime.now() - subscription['start_date']).days
                    st.metric("Days Subscribed", days_subscribed)
                with col4:
                    if subscription['status'] == 'ACTIVE':
                        if st.button(f"⏸️ Pause", key=f"pause_sub_{subscription['provider_id']}"):
                            subscription['status'] = 'PAUSED'
                            st.warning(f"⚠️ Subscription to {subscription['provider_name']} paused!")
                            st.rerun()
                    else:
                        if st.button(f"▶️ Resume", key=f"resume_sub_{subscription['provider_id']}"):
                            subscription['status'] = 'ACTIVE'
                            st.success(f"✅ Subscription to {subscription['provider_name']} resumed!")
                            st.rerun()
                
                # Unsubscribe option
                if st.button(f"❌ Unsubscribe", key=f"unsub_{subscription['provider_id']}"):
                    st.session_state.copy_trading['my_subscriptions'] = [
                        sub for sub in st.session_state.copy_trading['my_subscriptions'] 
                        if sub['provider_id'] != subscription['provider_id']
                    ]
                    st.success(f"✅ Unsubscribed from {subscription['provider_name']}!")
                    st.rerun()
                
                st.markdown("---")
        
        else:
            st.info("No active subscriptions. Browse signal providers to start copy trading!")
    
    with tab3:
        st.markdown("### ⚙️ Copy Trading Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Risk Management")
            
            st.session_state.copy_trading['copy_settings']['max_risk_per_trade'] = st.slider(
                "Max Risk per Trade (%)", 0.1, 10.0, 
                st.session_state.copy_trading['copy_settings']['max_risk_per_trade'], 0.1,
                key="copy_max_risk"
            )
            
            st.session_state.copy_trading['copy_settings']['max_daily_trades'] = st.number_input(
                "Max Daily Trades", 1, 100, 
                st.session_state.copy_trading['copy_settings']['max_daily_trades'],
                key="copy_max_trades"
            )
            
            st.session_state.copy_trading['copy_settings']['stop_loss_buffer'] = st.slider(
                "Stop Loss Buffer (pips)", 0, 20, 
                st.session_state.copy_trading['copy_settings']['stop_loss_buffer'],
                key="copy_sl_buffer"
            )
            
            st.session_state.copy_trading['copy_settings']['take_profit_buffer'] = st.slider(
                "Take Profit Buffer (pips)", -10, 10, 
                st.session_state.copy_trading['copy_settings']['take_profit_buffer'],
                key="copy_tp_buffer"
            )
        
        with col2:
            st.markdown("#### ⚙️ Execution Settings")
            
            copy_delay = st.slider("Copy Delay (seconds)", 0, 60, 5, key="copy_delay")
            copy_slippage = st.slider("Max Slippage (pips)", 0.1, 5.0, 1.0, 0.1, key="copy_slippage")
            
            partial_copy = st.checkbox("Allow Partial Copies", True, key="partial_copy")
            copy_on_weekends = st.checkbox("Copy on Weekends", False, key="copy_weekends")
            
            st.markdown("#### 📊 Copy Ratio Settings")
            
            copy_ratio_type = st.selectbox("Copy Ratio Type", ["Fixed Amount", "Percentage", "Risk-Based"], key="copy_ratio_type")
            
            if copy_ratio_type == "Fixed Amount":
                fixed_amount = st.number_input("Fixed Amount per Trade ($)", 100, 10000, 1000, key="fixed_copy_amount")
            elif copy_ratio_type == "Percentage":
                copy_percentage = st.slider("Copy Percentage (%)", 1, 100, 10, key="copy_percentage")
            elif copy_ratio_type == "Risk-Based":
                risk_multiplier = st.slider("Risk Multiplier", 0.1, 5.0, 1.0, 0.1, key="risk_multiplier")
        
        if st.button("💾 Save Copy Settings", key="save_copy_settings"):
            st.success("✅ Copy trading settings saved!")

# CONTINUE WITH EXISTING PAGES (Trading Terminal, Charts, etc.)
elif st.session_state.page == "Trading Terminal":
    st.markdown("# 💹 Trading Terminal")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Market Watch")
        
        # Enhanced market watch with real-time simulation
        market_data = []
        for symbol in st.session_state.mt5_symbols[:10]:  # Show top 10 symbols
            base_price = 1.0850 if 'USD' in symbol else 2650.00 if 'XAU' in symbol else 149.50
            bid = base_price + random.uniform(-0.01, 0.01) * base_price
            ask = bid + random.uniform(0.0001, 0.001) * base_price
            change = random.uniform(-0.5, 0.5)
            
            market_data.append({
                'Symbol': symbol,
                'Bid': f"{bid:.4f}" if 'XAU' not in symbol else f"{bid:.2f}",
                'Ask': f"{ask:.4f}" if 'XAU' not in symbol else f"{ask:.2f}",
                'Spread': f"{(ask-bid)*10000:.1f}" if 'XAU' not in symbol else f"{(ask-bid):.1f}",
                'Change %': f"{change:+.2f}%"
            })
        
        market_df = pd.DataFrame(market_data)
                st.dataframe(market_df, use_container_width=True, hide_index=True)
        
        # Quick trade panel
        st.markdown("### ⚡ Quick Trade")
        
        trade_col1, trade_col2, trade_col3, trade_col4 = st.columns(4)
        
        with trade_col1:
            quick_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="quick_symbol")
        with trade_col2:
            quick_volume = st.number_input("Volume", 0.01, 100.0, 1.0, 0.01, key="quick_volume")
        with trade_col3:
            if st.button("🟢 BUY", key="quick_buy", use_container_width=True):
                # Execute buy order
                new_position = {
                    'id': len(st.session_state.portfolio['positions']) + 1,
                    'symbol': quick_symbol,
                    'type': 'BUY',
                    'volume': quick_volume,
                    'entry_price': random.uniform(1.0800, 1.0900),
                    'current_price': random.uniform(1.0800, 1.0900),
                    'pnl': 0,
                    'swap': 0,
                    'commission': quick_volume * 7,
                    'open_time': datetime.now(),
                    'broker': 'Divit Capital'
                }
                st.session_state.portfolio['positions'].append(new_position)
                st.success(f"✅ BUY {quick_volume} {quick_symbol} executed!")
                st.rerun()
        
        with trade_col4:
            if st.button("🔴 SELL", key="quick_sell", use_container_width=True):
                # Execute sell order
                new_position = {
                    'id': len(st.session_state.portfolio['positions']) + 1,
                    'symbol': quick_symbol,
                    'type': 'SELL',
                    'volume': quick_volume,
                    'entry_price': random.uniform(1.0800, 1.0900),
                    'current_price': random.uniform(1.0800, 1.0900),
                    'pnl': 0,
                    'swap': 0,
                    'commission': quick_volume * 7,
                    'open_time': datetime.now(),
                    'broker': 'Kama Capital'
                }
                st.session_state.portfolio['positions'].append(new_position)
                st.success(f"✅ SELL {quick_volume} {quick_symbol} executed!")
                st.rerun()
    
    with col2:
        st.markdown("### 📊 Account Summary")
        
        # Account metrics
        for broker_name, broker_data in st.session_state.advanced_brokers.items():
            if broker_data['status'] == 'Connected' and broker_data['accounts']:
                for account in broker_data['accounts']:
                    st.markdown(f"#### {broker_name} - {account['account_id']}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Balance", f"${account['balance']:,.2f}")
                        st.metric("Equity", f"${account['equity']:,.2f}")
                    with col_b:
                        st.metric("Margin", f"${account['margin']:,.2f}")
                        st.metric("Free Margin", f"${account['free_margin']:,.2f}")
                    
                    # Margin level
                    margin_level = (account['equity'] / account['margin']) * 100 if account['margin'] > 0 else 0
                    
                    if margin_level > 200:
                        st.success(f"✅ Margin Level: {margin_level:.1f}%")
                    elif margin_level > 100:
                        st.warning(f"⚠️ Margin Level: {margin_level:.1f}%")
                    else:
                        st.error(f"🚨 Margin Level: {margin_level:.1f}%")
                    
                    st.markdown("---")
        
        # Open positions summary
        st.markdown("### 🎯 Open Positions")
        
        if st.session_state.portfolio['positions']:
            for pos in st.session_state.portfolio['positions'][-5:]:  # Show last 5 positions
                profit_color = "profit-positive" if pos['pnl'] > 0 else "profit-negative"
                
                st.markdown(f"""
                <div style="background: #374151; padding: 0.5rem; border-radius: 8px; margin: 0.5rem 0;">
                    <strong>{pos['symbol']} {pos['type']}</strong><br>
                    Volume: {pos['volume']} | Entry: {pos['entry_price']}<br>
                    <span class="{profit_color}">P&L: ${pos['pnl']:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No open positions")

elif st.session_state.page == "Advanced Charts":
    st.markdown("# 📈 Advanced Charts")
    
    # Chart controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        chart_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="chart_symbol")
    with col2:
        chart_timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "1H", "4H", "1D"], index=3, key="chart_timeframe")
    with col3:
        chart_type = st.selectbox("Chart Type", ["Candlestick", "Line", "OHLC"], key="chart_type")
    with col4:
        chart_period = st.selectbox("Period", ["1 Day", "1 Week", "1 Month", "3 Months"], index=1, key="chart_period")
    
    # Generate sample OHLC data
    periods = {"1 Day": 24, "1 Week": 168, "1 Month": 720, "3 Months": 2160}
    num_points = periods[chart_period]
    
    dates = pd.date_range(start=datetime.now() - timedelta(hours=num_points), periods=num_points, freq='H')
    
    # Generate realistic price data
    base_price = 1.0850 if 'USD' in chart_symbol else 2650.00 if 'XAU' in chart_symbol else 149.50
    
    prices = []
    current_price = base_price
    
    for i in range(num_points):
        # Random walk with some trend
        change = np.random.normal(0, 0.001) * current_price
        current_price += change
        
        # Generate OHLC
        high = current_price + random.uniform(0, 0.002) * current_price
        low = current_price - random.uniform(0, 0.002) * current_price
        open_price = prices[-1]['close'] if prices else current_price
        close = current_price
        
        prices.append({
            'datetime': dates[i],
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': random.randint(100, 1000)
        })
    
    df = pd.DataFrame(prices)
    
    # Create chart based on type
    fig = go.Figure()
    
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=chart_symbol
        ))
    elif chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=df['close'],
            mode='lines',
            name=chart_symbol,
            line=dict(color='#3B82F6', width=2)
        ))
    elif chart_type == "OHLC":
        fig.add_trace(go.Ohlc(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=chart_symbol
        ))
    
    # Add technical indicators
    st.markdown("### 📊 Technical Indicators")
    
    indicator_col1, indicator_col2, indicator_col3 = st.columns(3)
    
    with indicator_col1:
        show_ma = st.checkbox("Moving Average", key="show_ma")
        if show_ma:
            ma_period = st.number_input("MA Period", 1, 200, 20, key="ma_period")
            df['ma'] = df['close'].rolling(window=ma_period).mean()
            
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df['ma'],
                mode='lines',
                name=f'MA({ma_period})',
                line=dict(color='#F59E0B', width=1)
            ))
    
    with indicator_col2:
        show_bb = st.checkbox("Bollinger Bands", key="show_bb")
        if show_bb:
            bb_period = st.number_input("BB Period", 1, 50, 20, key="bb_period")
            bb_std = st.number_input("Standard Deviation", 1.0, 3.0, 2.0, 0.1, key="bb_std")
            
            df['bb_middle'] = df['close'].rolling(window=bb_period).mean()
            df['bb_std'] = df['close'].rolling(window=bb_period).std()
            df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * bb_std)
            df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * bb_std)
            
            fig.add_trace(go.Scatter(
                x=df['datetime'], y=df['bb_upper'],
                mode='lines', name='BB Upper',
                line=dict(color='#EF4444', width=1, dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=df['datetime'], y=df['bb_lower'],
                mode='lines', name='BB Lower',
                line=dict(color='#EF4444', width=1, dash='dash'),
                fill='tonexty', fillcolor='rgba(239, 68, 68, 0.1)'
            ))
    
    with indicator_col3:
        show_volume = st.checkbox("Volume", key="show_volume")
    
    fig.update_layout(
        title=f"{chart_symbol} - {chart_timeframe} - {chart_period}",
        xaxis_title="Time",
        yaxis_title="Price",
        template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
        height=600,
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Volume chart if enabled
    if show_volume:
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(
            x=df['datetime'],
            y=df['volume'],
            name='Volume',
            marker_color='#10B981'
        ))
        
        volume_fig.update_layout(
            title="Volume",
            xaxis_title="Time",
            yaxis_title="Volume",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=200
        )
        
        st.plotly_chart(volume_fig, use_container_width=True)
    
    # Chart analysis tools
    st.markdown("### 🔧 Chart Analysis Tools")
    
    tool_col1, tool_col2, tool_col3 = st.columns(3)
    
    with tool_col1:
        if st.button("📏 Fibonacci Retracement", key="fib_tool"):
            st.info("Fibonacci tool activated - click on chart to set levels")
    
    with tool_col2:
        if st.button("📐 Trend Lines", key="trend_tool"):
            st.info("Trend line tool activated - draw on chart")
    
    with tool_col3:
        if st.button("📊 Support/Resistance", key="sr_tool"):
            st.info("S/R tool activated - levels will be auto-detected")

elif st.session_state.page == "Tick Charts":
    st.markdown("# 📊 Tick Charts")
    
    # Tick chart controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tick_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="tick_symbol")
    with col2:
        tick_size = st.selectbox("Tick Size", ["100", "500", "1000", "2000"], index=1, key="tick_size")
    with col3:
        auto_refresh = st.checkbox("Auto Refresh", True, key="tick_auto_refresh")
    
    # Generate tick data
    if 'tick_data' not in st.session_state:
        st.session_state.tick_data = {}
    
    if tick_symbol not in st.session_state.tick_data:
        st.session_state.tick_data[tick_symbol] = []
    
    # Simulate real-time tick data
    base_price = 1.0850 if 'USD' in tick_symbol else 2650.00 if 'XAU' in tick_symbol else 149.50
    
    # Add new ticks
    for _ in range(10):  # Add 10 new ticks
        tick_time = datetime.now() + timedelta(milliseconds=random.randint(0, 1000))
        bid = base_price + random.uniform(-0.01, 0.01) * base_price
        ask = bid + random.uniform(0.0001, 0.001) * base_price
        
        st.session_state.tick_data[tick_symbol].append({
            'time': tick_time,
            'bid': bid,
            'ask': ask,
            'spread': ask - bid
        })
    
    # Keep only last 1000 ticks
    if len(st.session_state.tick_data[tick_symbol]) > 1000:
        st.session_state.tick_data[tick_symbol] = st.session_state.tick_data[tick_symbol][-1000:]
    
    # Display tick chart
    if st.session_state.tick_data[tick_symbol]:
        tick_df = pd.DataFrame(st.session_state.tick_data[tick_symbol])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=tick_df['time'],
            y=tick_df['bid'],
            mode='lines',
            name='Bid',
            line=dict(color='#EF4444', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=tick_df['time'],
            y=tick_df['ask'],
            mode='lines',
            name='Ask',
            line=dict(color='#10B981', width=1)
        ))
        
        fig.update_layout(
            title=f"{tick_symbol} - Live Tick Data",
            xaxis_title="Time",
            yaxis_title="Price",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tick statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Bid", f"{tick_df['bid'].iloc[-1]:.4f}")
        with col2:
            st.metric("Current Ask", f"{tick_df['ask'].iloc[-1]:.4f}")
        with col3:
            avg_spread = tick_df['spread'].mean()
            st.metric("Avg Spread", f"{avg_spread:.4f}")
        with col4:
            tick_count = len(tick_df)
            st.metric("Tick Count", tick_count)
        
        # Spread analysis
        st.markdown("### 📊 Spread Analysis")
        
        spread_fig = go.Figure()
        spread_fig.add_trace(go.Scatter(
            x=tick_df['time'],
            y=tick_df['spread'] * 10000,  # Convert to pips
            mode='lines',
            name='Spread (pips)',
            line=dict(color='#F59E0B', width=1),
            fill='tonexty',
            fillcolor='rgba(245, 158, 11, 0.1)'
        ))
        
        spread_fig.update_layout(
            title="Spread Over Time",
            xaxis_title="Time",
            yaxis_title="Spread (pips)",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=200
        )
        
        st.plotly_chart(spread_fig, use_container_width=True)
    
    # Auto refresh
    if auto_refresh:
        time.sleep(1)
        st.rerun()

elif st.session_state.page == "Auto Trading":
    st.markdown("# 🤖 Auto Trading")
    
    # Auto trading status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.auto_trading['enabled']:
            st.markdown('<div class="status-active">🤖 AUTO TRADING ACTIVE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-inactive">🤖 AUTO TRADING INACTIVE</div>', unsafe_allow_html=True)
    
    with col2:
        st.metric("Trades Today", st.session_state.auto_trading['trades_today'])
    
    with col3:
        st.metric("Profit Today", f"${st.session_state.auto_trading['profit_today']:.2f}")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["⚙️ Settings", "📊 Strategies", "📈 Performance"])
    
    with tab1:
        st.markdown("### ⚙️ Auto Trading Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Trading Parameters")
            
            st.session_state.auto_trading['max_trades'] = st.number_input(
                "Max Trades per Day", 1, 1000, st.session_state.auto_trading['max_trades'], key="auto_max_trades"
            )
            
            st.session_state.auto_trading['risk_per_trade'] = st.slider(
                "Risk per Trade (%)", 0.1, 10.0, st.session_state.auto_trading['risk_per_trade'], 0.1, key="auto_risk"
            )
            
            auto_symbols = st.multiselect(
                "Trading Symbols", st.session_state.mt5_symbols, 
                default=['EURUSD', 'GBPUSD', 'XAUUSD'], key="auto_symbols"
            )
            
            auto_timeframes = st.multiselect(
                "Timeframes", ["1M", "5M", "15M", "1H", "4H"], 
                default=['5M', '15M'], key="auto_timeframes"
            )
        
        with col2:
            st.markdown("#### ⚠️ Risk Management")
            
            max_daily_loss = st.number_input("Max Daily Loss ($)", 100, 10000, 1000, key="auto_max_loss")
            max_drawdown = st.slider("Max Drawdown (%)", 1, 50, 10, key="auto_max_dd")
            
            correlation_limit = st.slider("Max Correlation", 0.1, 1.0, 0.7, 0.1, key="auto_correlation")
            
            auto_stop_loss = st.number_input("Default Stop Loss (pips)", 1, 1000, 50, key="auto_sl")
            auto_take_profit = st.number_input("Default Take Profit (pips)", 1, 1000, 100, key="auto_tp")
        
        # Control buttons
        st.markdown("#### 🎮 Controls")
        
        control_col1, control_col2, control_col3 = st.columns(3)
        
        with control_col1:
            if not st.session_state.auto_trading['enabled']:
                if st.button("🚀 Start Auto Trading", key="start_auto_trading"):
                    st.session_state.auto_trading['enabled'] = True
                    st.success("✅ Auto trading started!")
                    st.rerun()
            else:
                if st.button("⏸️ Stop Auto Trading", key="stop_auto_trading"):
                    st.session_state.auto_trading['enabled'] = False
                    st.warning("⚠️ Auto trading stopped!")
                    st.rerun()
        
        with control_col2:
            if st.button("🔄 Reset Daily Stats", key="reset_auto_stats"):
                st.session_state.auto_trading['trades_today'] = 0
                st.session_state.auto_trading['profit_today'] = 0
                st.info("📊 Daily stats reset!")
                st.rerun()
        
        with control_col3:
            if st.button("📊 View Logs", key="view_auto_logs"):
                st.info("Auto trading logs feature coming soon!")
    
    with tab2:
        st.markdown("### 📊 Trading Strategies")
        
        # Strategy list
        if st.session_state.auto_trading['strategies']:
            for i, strategy in enumerate(st.session_state.auto_trading['strategies']):
                with st.expander(f"📈 {strategy['name']} - {'ACTIVE' if strategy['enabled'] else 'INACTIVE'}"):
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Type:** {strategy['type']}")
                        st.write(f"**Symbols:** {', '.join(strategy['symbols'])}")
                        st.write(f"**Timeframe:** {strategy['timeframe']}")
                        st.write(f"**Risk:** {strategy['risk_per_trade']}%")
                    
                    with col_b:
                        st.write(f"**Trades Today:** {strategy.get('trades_today', 0)}")
                        st.write(f"**Profit Today:** ${strategy.get('profit_today', 0):.2f}")
                        st.write(f"**Win Rate:** {strategy.get('win_rate', 0):.1f}%")
                        st.write(f"**Total P&L:** ${strategy.get('total_pnl', 0):.2f}")
                    
                    # Strategy controls
                    control_col_a, control_col_b, control_col_c = st.columns(3)
                    
                    with control_col_a:
                        if strategy['enabled']:
                            if st.button(f"⏸️ Disable", key=f"disable_strategy_{i}"):
                                st.session_state.auto_trading['strategies'][i]['enabled'] = False
                                st.rerun()
                        else:
                            if st.button(f"▶️ Enable", key=f"enable_strategy_{i}"):
                                st.session_state.auto_trading['strategies'][i]['enabled'] = True
                                st.rerun()
                    
                    with control_col_b:
                        if st.button(f"⚙️ Edit", key=f"edit_strategy_{i}"):
                            st.info("Strategy editing feature coming soon!")
                    
                    with control_col_c:
                        if st.button(f"🗑️ Delete", key=f"delete_strategy_{i}"):
                            st.session_state.auto_trading['strategies'].pop(i)
                            st.success("✅ Strategy deleted!")
                            st.rerun()
        
        else:
            st.info("No strategies configured")
        
        # Add new strategy
        st.markdown("#### ➕ Add New Strategy")
        
        new_strategy_col1, new_strategy_col2 = st.columns(2)
        
        with new_strategy_col1:
            new_strategy_name = st.text_input("Strategy Name", key="new_strategy_name")
            new_strategy_type = st.selectbox("Strategy Type", ["MA Crossover", "RSI", "MACD", "Bollinger Bands"], key="new_strategy_type")
            new_strategy_symbols = st.multiselect("Symbols", st.session_state.mt5_symbols, key="new_strategy_symbols")
        
        with new_strategy_col2:
            new_strategy_timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "1H", "4H"], key="new_strategy_timeframe")
            new_strategy_risk = st.slider("Risk per Trade (%)", 0.1, 5.0, 1.0, 0.1, key="new_strategy_risk")
        
        if st.button("➕ Add Strategy", key="add_new_strategy"):
            if new_strategy_name and new_strategy_symbols:
                new_strategy = {
                    'name': new_strategy_name,
                    'type': new_strategy_type,
                    'symbols': new_strategy_symbols,
                    'timeframe': new_strategy_timeframe,
                    'risk_per_trade': new_strategy_risk,
                    'enabled': True,
                    'trades_today': 0,
                    'profit_today': 0,
                    'win_rate': 0,
                    'total_pnl': 0
                }
                
                st.session_state.auto_trading['strategies'].append(new_strategy)
                st.success(f"✅ Strategy '{new_strategy_name}' added!")
                st.rerun()
            else:
                st.error("❌ Please fill in all required fields!")
    
    with tab3:
        st.markdown("### 📈 Auto Trading Performance")
        
        # Performance metrics
        total_strategies = len(st.session_state.auto_trading['strategies'])
        active_strategies = len([s for s in st.session_state.auto_trading['strategies'] if s['enabled']])
        
        perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
        
        with perf_col1:
            st.metric("Total Strategies", total_strategies)
        with perf_col2:
            st.metric("Active Strategies", active_strategies)
        with perf_col3:
            total_trades = sum([s.get('trades_today', 0) for s in st.session_state.auto_trading['strategies']])
            st.metric("Total Trades Today", total_trades)
        with perf_col4:
            total_profit = sum([s.get('profit_today', 0) for s in st.session_state.auto_trading['strategies']])
            st.metric("Total Profit Today", f"${total_profit:.2f}")
        
        # Performance chart
        if st.session_state.auto_trading['strategies']:
            st.markdown("#### 📊 Strategy Performance Comparison")
            
            strategy_names = [s['name'] for s in st.session_state.auto_trading['strategies']]
            strategy_profits = [s.get('total_pnl', 0) for s in st.session_state.auto_trading['strategies']]
            strategy_win_rates = [s.get('win_rate', 0) for s in st.session_state.auto_trading['strategies']]
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Total P&L by Strategy', 'Win Rate by Strategy'),
                vertical_spacing=0.1
            )
            
            fig.add_trace(
                go.Bar(x=strategy_names, y=strategy_profits, name='Total P&L', marker_color='#10B981'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=strategy_names, y=strategy_win_rates, name='Win Rate (%)', marker_color='#3B82F6'),
                row=2, col=1
            )
            
            fig.update_layout(
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)

# CONTINUE WITH REMAINING PAGES...
elif st.session_state.page == "XAUUSD Arbitrage":
    st.markdown("# 🥇 XAUUSD Arbitrage System")
    
    # System status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.xauusd_arbitrage['monitoring']:
            st.markdown('<div class="status-active">🥇 MONITORING ACTIVE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-inactive">🥇 MONITORING INACTIVE</div>', unsafe_allow_html=True)
    
    with col2:
        st.metric("Opportunities Today", st.session_state.xauusd_arbitrage['stats']['total_opportunities'])
    
    with col3:
        st.metric("Today's P&L", f"${st.session_state.xauusd_arbitrage['stats']['today_pnl']:.2f}")
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Monitor", "⚙️ Settings", "📈 Opportunities", "💼 Positions"])
    
    with tab1:
        st.markdown("### 📊 Live Price Feeds")
        
        # Price feed display
        col1, col2 = st.columns(2)
        
        broker_a = st.session_state.xauusd_arbitrage['price_feeds']['broker_a']
        broker_b = st.session_state.xauusd_arbitrage['price_feeds']['broker_b']
        
        with col1:
            st.markdown(f"""
            <div class="price-feed">
                <h4>{broker_a['name']}</h4>
                <p><strong>Bid:</strong> {broker_a['bid']:.2f}</p>
                <p><strong>Ask:</strong> {broker_a['ask']:.2f}</p>
                <p><strong>Spread:</strong> {(broker_a['ask'] - broker_a['bid']):.2f}</p>
                                <p><strong>Latency:</strong> {broker_a['latency']}ms</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="price-feed">
                <h4>{broker_b['name']}</h4>
                <p><strong>Bid:</strong> {broker_b['bid']:.2f}</p>
                <p><strong>Ask:</strong> {broker_b['ask']:.2f}</p>
                <p><strong>Spread:</strong> {(broker_b['ask'] - broker_b['bid']):.2f}</p>
                <p><strong>Latency:</strong> {broker_b['latency']}ms</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Price difference analysis
        st.markdown("### 📊 Price Difference Analysis")
        
        price_diff = broker_a['bid'] - broker_b['ask']
        reverse_diff = broker_b['bid'] - broker_a['ask']
        
        diff_col1, diff_col2, diff_col3 = st.columns(3)
        
        with diff_col1:
            if price_diff > st.session_state.xauusd_arbitrage['settings']['min_profit_threshold']:
                st.success(f"🟢 Opportunity: ${price_diff:.2f}")
            else:
                st.metric("Price Diff A→B", f"${price_diff:.2f}")
        
        with diff_col2:
            if reverse_diff > st.session_state.xauusd_arbitrage['settings']['min_profit_threshold']:
                st.success(f"🟢 Opportunity: ${reverse_diff:.2f}")
            else:
                st.metric("Price Diff B→A", f"${reverse_diff:.2f}")
        
        with diff_col3:
            avg_spread = ((broker_a['ask'] - broker_a['bid']) + (broker_b['ask'] - broker_b['bid'])) / 2
            st.metric("Avg Spread", f"${avg_spread:.2f}")
        
        # Real-time chart
        st.markdown("### 📈 Real-time Price Chart")
        
        # Generate sample price history
        if 'xau_price_history' not in st.session_state:
            st.session_state.xau_price_history = []
        
        # Add new price points
        current_time = datetime.now()
        st.session_state.xau_price_history.append({
            'time': current_time,
            'broker_a_bid': broker_a['bid'],
            'broker_a_ask': broker_a['ask'],
            'broker_b_bid': broker_b['bid'],
            'broker_b_ask': broker_b['ask'],
            'diff': price_diff
        })
        
        # Keep only last 100 points
        if len(st.session_state.xau_price_history) > 100:
            st.session_state.xau_price_history = st.session_state.xau_price_history[-100:]
        
        if len(st.session_state.xau_price_history) > 10:
            price_df = pd.DataFrame(st.session_state.xau_price_history)
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('XAUUSD Prices', 'Price Difference'),
                vertical_spacing=0.1
            )
            
            # Price lines
            fig.add_trace(
                go.Scatter(x=price_df['time'], y=price_df['broker_a_bid'], 
                          name=f'{broker_a["name"]} Bid', line=dict(color='#EF4444')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=price_df['time'], y=price_df['broker_b_bid'], 
                          name=f'{broker_b["name"]} Bid', line=dict(color='#10B981')),
                row=1, col=1
            )
            
            # Price difference
            fig.add_trace(
                go.Scatter(x=price_df['time'], y=price_df['diff'], 
                          name='Price Difference', line=dict(color='#F59E0B')),
                row=2, col=1
            )
            
            # Add threshold line
            fig.add_hline(
                y=st.session_state.xauusd_arbitrage['settings']['min_profit_threshold'],
                line_dash="dash", line_color="red",
                row=2, col=1
            )
            
            fig.update_layout(
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Control buttons
        control_col1, control_col2 = st.columns(2)
        
        with control_col1:
            if not st.session_state.xauusd_arbitrage['monitoring']:
                if st.button("🚀 Start Monitoring", key="start_xau_monitoring"):
                    st.session_state.xauusd_arbitrage['monitoring'] = True
                    arbitrage_engine.start_monitoring()
                    st.success("✅ XAUUSD arbitrage monitoring started!")
                    st.rerun()
            else:
                if st.button("⏸️ Stop Monitoring", key="stop_xau_monitoring"):
                    st.session_state.xauusd_arbitrage['monitoring'] = False
                    arbitrage_engine.stop_monitoring()
                    st.warning("⚠️ XAUUSD arbitrage monitoring stopped!")
                    st.rerun()
        
        with control_col2:
            if st.button("🔄 Refresh Feeds", key="refresh_xau_feeds"):
                arbitrage_engine.update_prices()
                st.info("📊 Price feeds refreshed!")
                st.rerun()
    
    with tab2:
        st.markdown("### ⚙️ Arbitrage Settings")
        
        settings_col1, settings_col2 = st.columns(2)
        
        with settings_col1:
            st.markdown("#### 💰 Profit Settings")
            
            st.session_state.xauusd_arbitrage['settings']['min_profit_threshold'] = st.number_input(
                "Min Profit Threshold ($)", 0.1, 10.0, 
                st.session_state.xauusd_arbitrage['settings']['min_profit_threshold'], 0.1,
                key="xau_min_profit"
            )
            
            st.session_state.xauusd_arbitrage['settings']['max_position_size'] = st.number_input(
                "Max Position Size (lots)", 0.01, 100.0, 
                st.session_state.xauusd_arbitrage['settings']['max_position_size'], 0.01,
                key="xau_max_size"
            )
            
            st.session_state.xauusd_arbitrage['settings']['max_slippage'] = st.slider(
                "Max Slippage ($)", 0.1, 5.0, 
                st.session_state.xauusd_arbitrage['settings']['max_slippage'], 0.1,
                key="xau_max_slippage"
            )
        
        with settings_col2:
            st.markdown("#### ⚠️ Risk Management")
            
            st.session_state.xauusd_arbitrage['settings']['max_daily_trades'] = st.number_input(
                "Max Daily Trades", 1, 1000, 
                st.session_state.xauusd_arbitrage['settings']['max_daily_trades'],
                key="xau_max_trades"
            )
            
            st.session_state.xauusd_arbitrage['settings']['max_exposure'] = st.number_input(
                "Max Exposure ($)", 1000, 1000000, 
                st.session_state.xauusd_arbitrage['settings']['max_exposure'],
                key="xau_max_exposure"
            )
            
            st.session_state.xauusd_arbitrage['settings']['stop_loss'] = st.number_input(
                "Stop Loss ($)", 1, 1000, 
                st.session_state.xauusd_arbitrage['settings']['stop_loss'],
                key="xau_stop_loss"
            )
        
        # Execution settings
        st.markdown("#### ⚡ Execution Settings")
        
        exec_col1, exec_col2, exec_col3 = st.columns(3)
        
        with exec_col1:
            auto_execute = st.checkbox(
                "Auto Execute Opportunities", 
                st.session_state.xauusd_arbitrage['settings']['auto_execute'],
                key="xau_auto_execute"
            )
            st.session_state.xauusd_arbitrage['settings']['auto_execute'] = auto_execute
        
        with exec_col2:
            execution_delay = st.slider(
                "Execution Delay (ms)", 0, 1000, 100,
                key="xau_exec_delay"
            )
        
        with exec_col3:
            partial_fills = st.checkbox(
                "Allow Partial Fills", True,
                key="xau_partial_fills"
            )
        
        if st.button("💾 Save Settings", key="save_xau_settings"):
            st.success("✅ Arbitrage settings saved!")
    
    with tab3:
        st.markdown("### 📈 Arbitrage Opportunities")
        
        # Opportunity history
        if st.session_state.xauusd_arbitrage['opportunities']:
            st.markdown("#### 📋 Recent Opportunities")
            
            opportunities_data = []
            for opp in st.session_state.xauusd_arbitrage['opportunities'][-20:]:  # Last 20
                opportunities_data.append({
                    'Time': opp['timestamp'].strftime('%H:%M:%S'),
                    'Type': opp['type'],
                    'Profit Potential': f"${opp['profit_potential']:.2f}",
                    'Size': f"{opp['size']} lots",
                    'Status': opp['status'],
                    'Executed': '✅' if opp['executed'] else '❌'
                })
            
            opp_df = pd.DataFrame(opportunities_data)
            st.dataframe(opp_df, use_container_width=True, hide_index=True)
            
            # Opportunity statistics
            st.markdown("#### 📊 Opportunity Statistics")
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            total_opportunities = len(st.session_state.xauusd_arbitrage['opportunities'])
            executed_opportunities = len([o for o in st.session_state.xauusd_arbitrage['opportunities'] if o['executed']])
            avg_profit = np.mean([o['profit_potential'] for o in st.session_state.xauusd_arbitrage['opportunities']])
            execution_rate = (executed_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0
            
            with stat_col1:
                st.metric("Total Opportunities", total_opportunities)
            with stat_col2:
                st.metric("Executed", executed_opportunities)
            with stat_col3:
                st.metric("Avg Profit Potential", f"${avg_profit:.2f}")
            with stat_col4:
                st.metric("Execution Rate", f"{execution_rate:.1f}%")
        
        else:
            st.info("No opportunities detected yet. Start monitoring to see opportunities.")
        
        # Opportunity distribution chart
        if st.session_state.xauusd_arbitrage['opportunities']:
            st.markdown("#### 📊 Profit Distribution")
            
            profit_values = [o['profit_potential'] for o in st.session_state.xauusd_arbitrage['opportunities']]
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=profit_values,
                nbinsx=20,
                marker_color='#10B981',
                opacity=0.7,
                name="Profit Potential"
            ))
            
            fig.update_layout(
                title="Distribution of Arbitrage Opportunities",
                xaxis_title="Profit Potential ($)",
                yaxis_title="Frequency",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### 💼 Arbitrage Positions")
        
        # Active arbitrage positions
        arbitrage_positions = [pos for pos in st.session_state.portfolio['positions'] if 'arbitrage' in pos.get('tags', [])]
        
        if arbitrage_positions:
            st.markdown("#### 📋 Active Arbitrage Positions")
            
            arb_positions_data = []
            for pos in arbitrage_positions:
                arb_positions_data.append({
                    'ID': pos['id'],
                    'Symbol': pos['symbol'],
                    'Type': pos['type'],
                    'Volume': pos['volume'],
                    'Entry Price': pos['entry_price'],
                    'Current Price': pos['current_price'],
                    'P&L': f"${pos['pnl']:.2f}",
                    'Broker': pos['broker'],
                    'Duration': str(datetime.now() - pos['open_time']).split('.')[0]
                })
            
            arb_df = pd.DataFrame(arb_positions_data)
            st.dataframe(arb_df, use_container_width=True, hide_index=True)
            
            # Position management
            selected_arb_position = st.selectbox(
                "Select Position to Manage",
                options=[f"{pos['id']} - {pos['symbol']} {pos['type']}" for pos in arbitrage_positions],
                key="selected_arb_position"
            )
            
            if selected_arb_position:
                pos_id = int(selected_arb_position.split(' - ')[0])
                
                manage_col1, manage_col2, manage_col3 = st.columns(3)
                
                with manage_col1:
                    if st.button("🔒 Close Position", key=f"close_arb_pos_{pos_id}"):
                        # Close arbitrage position
                        st.session_state.portfolio['positions'] = [
                            p for p in st.session_state.portfolio['positions'] if p['id'] != pos_id
                        ]
                        st.success(f"✅ Arbitrage position {pos_id} closed!")
                        st.rerun()
                
                with manage_col2:
                    if st.button("📊 Position Details", key=f"details_arb_pos_{pos_id}"):
                        position = next(p for p in arbitrage_positions if p['id'] == pos_id)
                        st.json(position)
                
                with manage_col3:
                    if st.button("🔄 Hedge Position", key=f"hedge_arb_pos_{pos_id}"):
                        st.info("Position hedging feature coming soon!")
        
        else:
            st.info("No active arbitrage positions")
        
        # Arbitrage performance summary
        st.markdown("#### 📊 Arbitrage Performance Summary")
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            st.metric("Total Arbitrage P&L", f"${st.session_state.xauusd_arbitrage['stats']['total_pnl']:.2f}")
        with perf_col2:
            st.metric("Success Rate", f"{st.session_state.xauusd_arbitrage['stats']['success_rate']:.1f}%")
        with perf_col3:
            st.metric("Avg Profit per Trade", f"${st.session_state.xauusd_arbitrage['stats']['avg_profit']:.2f}")

elif st.session_state.page == "LP Bridge Manager":
    st.markdown("# 🌐 LP Bridge Manager")
    
    # LP Bridge status overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        connected_lps = len([lp for lp in st.session_state.lp_bridge['liquidity_providers'] if lp['status'] == 'Connected'])
        total_lps = len(st.session_state.lp_bridge['liquidity_providers'])
        st.metric("Connected LPs", f"{connected_lps}/{total_lps}")
    
    with col2:
        total_liquidity = sum([lp['available_liquidity'] for lp in st.session_state.lp_bridge['liquidity_providers']])
        st.metric("Total Liquidity", f"${total_liquidity:,}")
    
    with col3:
        avg_latency = np.mean([lp['latency'] for lp in st.session_state.lp_bridge['liquidity_providers'] if lp['status'] == 'Connected'])
        st.metric("Avg Latency", f"{avg_latency:.1f}ms")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🏦 LP Connections", "📊 Liquidity Monitor", "⚙️ Bridge Settings"])
    
    with tab1:
        st.markdown("### 🏦 Liquidity Provider Connections")
        
        for lp in st.session_state.lp_bridge['liquidity_providers']:
            with st.expander(f"🏦 {lp['name']} - {lp['status']}", expanded=lp['status'] == 'Connected'):
                
                lp_col1, lp_col2 = st.columns(2)
                
                with lp_col1:
                    st.markdown("#### 📊 Connection Details")
                    st.write(f"**Status:** {lp['status']}")
                    st.write(f"**Type:** {lp['type']}")
                    st.write(f"**Protocol:** {lp['protocol']}")
                    st.write(f"**Latency:** {lp['latency']}ms")
                    st.write(f"**Uptime:** {lp['uptime']}%")
                    
                    # Connection controls
                    if lp['status'] == 'Connected':
                        if st.button(f"🔌 Disconnect", key=f"disconnect_lp_{lp['id']}"):
                            lp['status'] = 'Disconnected'
                            st.warning(f"⚠️ {lp['name']} disconnected!")
                            st.rerun()
                    else:
                        if st.button(f"🔌 Connect", key=f"connect_lp_{lp['id']}"):
                            lp['status'] = 'Connected'
                            st.success(f"✅ {lp['name']} connected!")
                            st.rerun()
                
                with lp_col2:
                    st.markdown("#### 💰 Liquidity Information")
                    st.write(f"**Available Liquidity:** ${lp['available_liquidity']:,}")
                    st.write(f"**Min Trade Size:** ${lp['min_trade_size']:,}")
                    st.write(f"**Max Trade Size:** ${lp['max_trade_size']:,}")
                    st.write(f"**Commission:** {lp['commission']}%")
                    
                    # Supported symbols
                    st.markdown("**Supported Symbols:**")
                    symbol_chips = " ".join([f"`{symbol}`" for symbol in lp['supported_symbols']])
                    st.markdown(symbol_chips)
                
                # Performance metrics
                st.markdown("#### 📈 Performance Metrics")
                
                perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
                
                with perf_col1:
                    st.metric("Daily Volume", f"${lp['daily_volume']:,}")
                with perf_col2:
                    st.metric("Fill Rate", f"{lp['fill_rate']}%")
                with perf_col3:
                    st.metric("Avg Spread", f"{lp['avg_spread']} pips")
                with perf_col4:
                    st.metric("Rejections", lp['rejections_today'])
        
        # Add new LP connection
        st.markdown("### ➕ Add New LP Connection")
        
        new_lp_col1, new_lp_col2 = st.columns(2)
        
        with new_lp_col1:
            new_lp_name = st.text_input("LP Name", key="new_lp_name")
            new_lp_type = st.selectbox("LP Type", ["Prime Broker", "ECN", "Market Maker", "Aggregator"], key="new_lp_type")
            new_lp_protocol = st.selectbox("Protocol", ["FIX", "REST API", "WebSocket", "Custom"], key="new_lp_protocol")
        
        with new_lp_col2:
            new_lp_liquidity = st.number_input("Available Liquidity ($)", 100000, 100000000, 1000000, key="new_lp_liquidity")
            new_lp_commission = st.slider("Commission (%)", 0.01, 1.0, 0.1, 0.01, key="new_lp_commission")
            new_lp_symbols = st.multiselect("Supported Symbols", st.session_state.mt5_symbols, key="new_lp_symbols")
        
        if st.button("➕ Add LP Connection", key="add_new_lp"):
            if new_lp_name and new_lp_symbols:
                new_lp = {
                    'id': len(st.session_state.lp_bridge['liquidity_providers']) + 1,
                    'name': new_lp_name,
                    'type': new_lp_type,
                    'protocol': new_lp_protocol,
                    'status': 'Disconnected',
                    'available_liquidity': new_lp_liquidity,
                    'min_trade_size': 1000,
                    'max_trade_size': new_lp_liquidity // 10,
                    'commission': new_lp_commission,
                    'supported_symbols': new_lp_symbols,
                    'latency': random.uniform(5, 50),
                    'uptime': random.uniform(95, 99.9),
                    'daily_volume': 0,
                    'fill_rate': random.uniform(85, 99),
                    'avg_spread': random.uniform(0.5, 3.0),
                    'rejections_today': 0
                }
                
                st.session_state.lp_bridge['liquidity_providers'].append(new_lp)
                st.success(f"✅ LP '{new_lp_name}' added!")
                st.rerun()
            else:
                st.error("❌ Please fill in all required fields!")
    
    with tab2:
        st.markdown("### 📊 Liquidity Monitor")
        
        # Real-time liquidity overview
        st.markdown("#### 💰 Real-time Liquidity by Symbol")
        
        # Calculate liquidity by symbol
        symbol_liquidity = {}
        for symbol in st.session_state.mt5_symbols[:10]:  # Top 10 symbols
            total_liquidity = 0
            for lp in st.session_state.lp_bridge['liquidity_providers']:
                if lp['status'] == 'Connected' and symbol in lp['supported_symbols']:
                    total_liquidity += lp['available_liquidity'] // len(lp['supported_symbols'])
            symbol_liquidity[symbol] = total_liquidity
        
        # Display liquidity chart
        symbols = list(symbol_liquidity.keys())
        liquidity_values = list(symbol_liquidity.values())
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=symbols,
            y=liquidity_values,
            marker_color='#10B981',
            name='Available Liquidity'
        ))
        
        fig.update_layout(
            title="Available Liquidity by Symbol",
            xaxis_title="Symbol",
            yaxis_title="Liquidity ($)",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Liquidity depth analysis
        st.markdown("#### 📊 Liquidity Depth Analysis")
        
        selected_symbol = st.selectbox("Select Symbol for Depth Analysis", st.session_state.mt5_symbols, key="depth_symbol")
        
        # Generate sample depth data
        depth_levels = []
        base_price = 1.0850 if 'USD' in selected_symbol else 2650.00 if 'XAU' in selected_symbol else 149.50
        
        for i in range(10):
            bid_price = base_price - (i * 0.0001)
            ask_price = base_price + (i * 0.0001)
            bid_volume = random.randint(100000, 1000000)
            ask_volume = random.randint(100000, 1000000)
            
            depth_levels.append({
                'Level': i + 1,
                'Bid Price': f"{bid_price:.4f}",
                'Bid Volume': f"${bid_volume:,}",
                'Ask Price': f"{ask_price:.4f}",
                'Ask Volume': f"${ask_volume:,}"
            })
        
        depth_df = pd.DataFrame(depth_levels)
        st.dataframe(depth_df, use_container_width=True, hide_index=True)
        
        # LP performance comparison
        st.markdown("#### 📈 LP Performance Comparison")
        
        lp_names = [lp['name'] for lp in st.session_state.lp_bridge['liquidity_providers']]
        lp_latencies = [lp['latency'] for lp in st.session_state.lp_bridge['liquidity_providers']]
        lp_fill_rates = [lp['fill_rate'] for lp in st.session_state.lp_bridge['liquidity_providers']]
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Latency Comparison', 'Fill Rate Comparison')
        )
        
        fig.add_trace(
            go.Bar(x=lp_names, y=lp_latencies, name='Latency (ms)', marker_color='#EF4444'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=lp_names, y=lp_fill_rates, name='Fill Rate (%)', marker_color='#10B981'),
            row=1, col=2
        )
        
        fig.update_layout(
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### ⚙️ LP Bridge Settings")
        
        settings_col1, settings_col2 = st.columns(2)
        
        with settings_col1:
            st.markdown("#### 🎯 Routing Settings")
            
            routing_mode = st.selectbox(
                "Routing Mode", 
                ["Best Price", "Lowest Latency", "Highest Liquidity", "Round Robin"],
                key="routing_mode"
            )
            
            failover_enabled = st.checkbox("Enable Failover", True, key="failover_enabled")
            
            if failover_enabled:
                failover_timeout = st.number_input("Failover Timeout (ms)", 100, 5000, 1000, key="failover_timeout")
            
            load_balancing = st.checkbox("Enable Load Balancing", True, key="load_balancing")
            
            if load_balancing:
                max_lp_utilization = st.slider("Max LP Utilization (%)", 50, 100, 80, key="max_lp_util")
        
        with settings_col2:
            st.markdown("#### ⚠️ Risk Controls")
            
            max_order_size = st.number_input("Max Order Size ($)", 1000, 10000000, 1000000, key="max_order_size")
            
            position_limits = st.checkbox("Enable Position Limits", True, key="position_limits")
            
            if position_limits:
                max_net_position = st.number_input("Max Net Position ($)", 1000000, 100000000, 10000000, key="max_net_pos")
            
            credit_limits = st.checkbox("Enable Credit Limits", True, key="credit_limits")
            
            if credit_limits:
                max_credit_exposure = st.number_input("Max Credit Exposure ($)", 1000000, 100000000, 5000000, key="max_credit")
        
        # Advanced settings
        st.markdown("#### 🔧 Advanced Settings")
        
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        
        with adv_col1:
            price_tolerance = st.slider("Price Tolerance (pips)", 0.1, 10.0, 1.0, 0.1, key="price_tolerance")
        
        with adv_col2:
            execution_timeout = st.number_input("Execution Timeout (ms)", 100, 10000, 3000, key="exec_timeout")
        
        with adv_col3:
            retry_attempts = st.number_input("Retry Attempts", 1, 10, 3, key="retry_attempts")
        
        # Save settings
        if st.button("💾 Save Bridge Settings", key="save_bridge_settings"):
            bridge_settings = {
                'routing_mode': routing_mode,
                'failover_enabled': failover_enabled,
                'failover_timeout': failover_timeout if failover_enabled else None,
                'load_balancing': load_balancing,
                'max_lp_utilization': max_lp_utilization if load_balancing else None,
                'max_order_size': max_order_size,
                'position_limits': position_limits,
                'max_net_position': max_net_position if position_limits else None,
                'credit_limits': credit_limits,
                'max_credit_exposure': max_credit_exposure if credit_limits else None,
                'price_tolerance': price_tolerance,
                'execution_timeout': execution_timeout,
                'retry_attempts': retry_attempts
            }
            
            st.session_state.lp_bridge['settings'] = bridge_settings
                        st.success("✅ LP Bridge settings saved!")

# FOOTER AND AUTO-REFRESH
st.markdown("---")

# Footer with system info
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**🚀 Yantra Trading Platform**")
    st.markdown("*Advanced Multi-Broker Trading System*")

with footer_col2:
    st.markdown(f"**📊 System Status:** {'🟢 Online' if st.session_state.system_status else '🔴 Offline'}")
    st.markdown(f"**⏰ Last Update:** {datetime.now().strftime('%H:%M:%S')}")

with footer_col3:
    st.markdown(f"**👤 User:** {st.session_state.user_profile['name']}")
    st.markdown(f"**🌐 Theme:** {st.session_state.theme}")

# Auto-refresh for real-time data
if st.session_state.auto_refresh and st.session_state.page in ["Dashboard", "Trading Terminal", "Tick Charts", "XAUUSD Arbitrage"]:
    time.sleep(2)
    st.rerun()

# Custom CSS for enhanced styling
st.markdown("""
<style>
/* Enhanced card styling */
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.broker-card {
    background: #374151;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 4px solid #10B981;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.copy-trader-card {
    background: #1F2937;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border: 1px solid #374151;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.price-feed {
    background: #111827;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border: 2px solid #10B981;
    text-align: center;
}

.status-active {
    background: linear-gradient(135deg, #10B981, #059669);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    text-align: center;
    font-weight: bold;
    font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.status-inactive {
    background: linear-gradient(135deg, #6B7280, #4B5563);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    text-align: center;
    font-weight: bold;
    font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
}

.profit-positive {
    color: #10B981;
    font-weight: bold;
}

.profit-negative {
    color: #EF4444;
    font-weight: bold;
}

/* Enhanced button styling */
.stButton > button {
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

/* Sidebar enhancements */
.css-1d391kg {
    background: linear-gradient(180deg, #1F2937 0%, #111827 100%);
}

/* Main content area */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Metric styling */
.metric-container {
    background: #374151;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    margin: 0.5rem 0;
}

/* Table styling */
.dataframe {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* Chart container */
.plotly-graph-div {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

/* Alert styling */
.stAlert {
    border-radius: 8px;
    border: none;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* Success alert */
.stAlert[data-baseweb="notification"] {
    background: linear-gradient(135deg, #10B981, #059669);
    color: white;
}

/* Info alert */
.stAlert[data-baseweb="notification"][kind="info"] {
    background: linear-gradient(135deg, #3B82F6, #1D4ED8);
    color: white;
}

/* Warning alert */
.stAlert[data-baseweb="notification"][kind="warning"] {
    background: linear-gradient(135deg, #F59E0B, #D97706);
    color: white;
}

/* Error alert */
.stAlert[data-baseweb="notification"][kind="error"] {
    background: linear-gradient(135deg, #EF4444, #DC2626);
    color: white;
}

/* Expander styling */
.streamlit-expanderHeader {
    background: #374151;
    border-radius: 8px;
    border: 1px solid #4B5563;
}

/* Input styling */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid #4B5563;
    background: #374151;
    color: white;
}

.stSelectbox > div > div > select {
    border-radius: 8px;
    border: 1px solid #4B5563;
    background: #374151;
    color: white;
}

/* Slider styling */
.stSlider > div > div > div > div {
    background: #10B981;
}

/* Checkbox styling */
.stCheckbox > label > div {
    background: #374151;
    border: 1px solid #4B5563;
    border-radius: 4px;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #374151;
    border-radius: 8px;
    color: white;
    border: 1px solid #4B5563;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #10B981, #059669);
    color: white;
}

/* Column styling */
.element-container {
    margin-bottom: 1rem;
}

/* Loading spinner */
.stSpinner > div {
    border-top-color: #10B981 !important;
}

/* Progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(135deg, #10B981, #059669);
}

/* Code block styling */
.stCodeBlock {
    border-radius: 8px;
    border: 1px solid #4B5563;
    background: #1F2937;
}

/* JSON styling */
.stJson {
    border-radius: 8px;
    border: 1px solid #4B5563;
    background: #1F2937;
}

/* Dataframe styling */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #1F2937;
}

::-webkit-scrollbar-thumb {
    background: #10B981;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #059669;
}

/* Responsive design */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .metric-card {
        padding: 1rem;
    }
    
    .broker-card {
        padding: 1rem;
    }
}

/* Animation classes */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.pulse {
    animation: pulse 2s infinite;
}

/* Gradient backgrounds */
.gradient-bg-1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-bg-2 {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.gradient-bg-3 {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.gradient-bg-4 {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

/* Card hover effects */
.hover-card {
    transition: all 0.3s ease;
    cursor: pointer;
}

.hover-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

/* Status indicators */
.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.status-online {
    background: #10B981;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

.status-offline {
    background: #EF4444;
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

.status-warning {
    background: #F59E0B;
    box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
}

/* Typography enhancements */
h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    margin-bottom: 1rem;
}

.big-number {
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1;
}

.small-text {
    font-size: 0.875rem;
    color: #9CA3AF;
}

/* Loading states */
.loading-shimmer {
    background: linear-gradient(90deg, #374151 25%, #4B5563 50%, #374151 75%);
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* Success states */
.success-checkmark {
    color: #10B981;
    font-size: 1.5rem;
    animation: checkmark 0.5s ease-in-out;
}

@keyframes checkmark {
    0% { transform: scale(0); }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); }
}

/* Error states */
.error-x {
    color: #EF4444;
    font-size: 1.5rem;
    animation: errorShake 0.5s ease-in-out;
}

@keyframes errorShake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

/* Notification badges */
.notification-badge {
    background: #EF4444;
    color: white;
    border-radius: 50%;
    padding: 2px 6px;
    font-size: 0.75rem;
    font-weight: bold;
    position: absolute;
    top: -5px;
    right: -5px;
}

/* Progress indicators */
.progress-ring {
    width: 60px;
    height: 60px;
    border: 4px solid #374151;
    border-top: 4px solid #10B981;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Tooltip styling */
.custom-tooltip {
    background: #1F2937;
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.875rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    border: 1px solid #374151;
}

/* Modal styling */
.custom-modal {
    background: #1F2937;
    border-radius: 12px;
    border: 1px solid #374151;
    box-shadow: 0 20px 50px rgba(0,0,0,0.3);
}

/* Form styling */
.form-group {
    margin-bottom: 1.5rem;
}

.form-label {
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #F3F4F6;
}

.form-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #4B5563;
    border-radius: 8px;
    background: #374151;
    color: white;
    transition: border-color 0.3s ease;
}

.form-input:focus {
    border-color: #10B981;
    outline: none;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* Grid layouts */
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1rem;
}

.grid-4 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 1rem;
}

@media (max-width: 768px) {
    .grid-2, .grid-3, .grid-4 {
        grid-template-columns: 1fr;
    }
}

/* Utility classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 0.75rem; }
.mt-4 { margin-top: 1rem; }

.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }

.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 0.75rem; }
.p-4 { padding: 1rem; }

.rounded { border-radius: 0.375rem; }
.rounded-lg { border-radius: 0.5rem; }
.rounded-xl { border-radius: 0.75rem; }

.shadow-sm { box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.shadow { box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.shadow-lg { box-shadow: 0 10px 15px rgba(0,0,0,0.1); }

/* Dark mode specific adjustments */
.stApp {
    background: #111827;
    color: #F3F4F6;
}

/* Light mode overrides (when theme is Light) */
.light-mode {
    background: #FFFFFF;
    color: #1F2937;
}

.light-mode .broker-card {
    background: #F9FAFB;
    border-left-color: #10B981;
}

.light-mode .copy-trader-card {
    background: #FFFFFF;
    border-color: #E5E7EB;
}

.light-mode .price-feed {
    background: #F9FAFB;
    border-color: #10B981;
}
</style>
""", unsafe_allow_html=True)

# JavaScript for enhanced interactivity
st.markdown("""
<script>
// Auto-refresh functionality
function autoRefresh() {
    if (window.location.search.includes('auto_refresh=true')) {
        setTimeout(() => {
            window.location.reload();
        }, 5000);
    }
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+R for refresh
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        window.location.reload();
    }
    
    // Ctrl+D for dashboard
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        // Navigate to dashboard
    }
    
    // Ctrl+T for trading terminal
    if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        // Navigate to trading terminal
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    autoRefresh();
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('.main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.metric-card, .broker-card, .copy-trader-card');
    cards.forEach(card => {
        card.classList.add('hover-card');
    });
});

// Real-time clock
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const clockElements = document.querySelectorAll('.live-clock');
    clockElements.forEach(element => {
        element.textContent = timeString;
    });
}

setInterval(updateClock, 1000);

// Connection status monitor
function checkConnectionStatus() {
    // Simulate connection check
    const isOnline = navigator.onLine;
    const statusElements = document.querySelectorAll('.connection-status');
    
    statusElements.forEach(element => {
        if (isOnline) {
            element.textContent = '🟢 Online';
            element.className = 'connection-status status-online';
        } else {
            element.textContent = '🔴 Offline';
            element.className = 'connection-status status-offline';
        }
    });
}

setInterval(checkConnectionStatus, 5000);

// Price update animations
function animatePriceChange(element, newValue, oldValue) {
    if (newValue > oldValue) {
        element.classList.add('price-up');
        setTimeout(() => element.classList.remove('price-up'), 1000);
    } else if (newValue < oldValue) {
        element.classList.add('price-down');
        setTimeout(() => element.classList.remove('price-down'), 1000);
    }
}

// Chart resize handler
window.addEventListener('resize', function() {
    // Trigger Plotly chart resize
    const charts = document.querySelectorAll('.plotly-graph-div');
    charts.forEach(chart => {
        if (window.Plotly) {
            window.Plotly.Plots.resize(chart);
        }
    });
});

// Performance monitoring
function monitorPerformance() {
    const perfData = performance.getEntriesByType('navigation')[0];
    if (perfData) {
        console.log('Page Load Time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
    }
}

window.addEventListener('load', monitorPerformance);

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    showNotification('An error occurred. Please refresh the page.', 'error');
});

// Service worker registration for offline support
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => console.log('SW registered'))
        .catch(error => console.log('SW registration failed'));
}
</script>
""", unsafe_allow_html=True)

# End of application
print("✅ Yantra Trading Platform loaded successfully!")
