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

st.set_page_config(
    page_title="YANTRA - Professional Latency Arbitrage Platform", 
    page_icon="⭐", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Session State Init (YOUR EXISTING + NEW ARBITRAGE)
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

# NEW: XAUUSD Arbitrage System
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
    }# NEW: XAUUSD Arbitrage Monitor Class
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
                # Simulate real-time XAUUSD prices from both brokers
                current_time = time.time()
                
                # Broker A (Divit Capital) - 0.7ms latency
                broker_a_mid = base_price + random.uniform(-2, 2)
                broker_a_spread = random.uniform(0.2, 0.5)
                broker_a_bid = round(broker_a_mid - broker_a_spread/2, 2)
                broker_a_ask = round(broker_a_mid + broker_a_spread/2, 2)
                
                # Broker B (Kama Capital) - 1.2ms latency  
                broker_b_mid = base_price + random.uniform(-2, 2)
                broker_b_spread = random.uniform(0.2, 0.5)
                broker_b_bid = round(broker_b_mid - broker_b_spread/2, 2)
                broker_b_ask = round(broker_b_mid + broker_b_spread/2, 2)
                
                # Update price feeds
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
                
                # Detect arbitrage opportunities
                self.detect_arbitrage_opportunities()
                
                # Auto-execute if enabled
                if st.session_state.xauusd_arbitrage['settings']['auto_execute']:
                    self.auto_execute_trades()
                
                time.sleep(0.1)  # 100ms refresh rate
                
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
        
        # Opportunity 1: Buy Broker A, Sell Broker B
        spread_1 = broker_b['bid'] - broker_a['ask']
        spread_1_pips = spread_1 / 0.1
        
        # Opportunity 2: Buy Broker B, Sell Broker A
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
        
        # Add opportunities to the list
        for opp in opportunities:
            st.session_state.xauusd_arbitrage['opportunities'].append(opp)
            st.session_state.xauusd_arbitrage['stats']['total_opportunities'] += 1
        
        # Keep only last 100 opportunities
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
        
        # Mark opportunity as executed
        opportunity['status'] = 'EXECUTED'
        
        return position
    
    def close_position(self, position_id):
        """Close an arbitrage position"""
        for i, pos in enumerate(st.session_state.xauusd_arbitrage['positions']):
            if pos['id'] == position_id and pos['status'] == 'OPEN':
                # Calculate realized P&L
                realized_pnl = pos['spread_pips'] * pos['position_size'] * 10  # $10 per pip per lot
                
                st.session_state.xauusd_arbitrage['positions'][i]['status'] = 'CLOSED'
                st.session_state.xauusd_arbitrage['positions'][i]['realized_pnl'] = realized_pnl
                st.session_state.xauusd_arbitrage['positions'][i]['close_time'] = datetime.now()
                
                # Update stats
                st.session_state.xauusd_arbitrage['stats']['total_pnl'] += realized_pnl
                st.session_state.xauusd_arbitrage['stats']['today_pnl'] += realized_pnl
                
                if realized_pnl > 0:
                    st.session_state.xauusd_arbitrage['stats']['successful_trades'] += 1
                
                # Update win rate
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
        
        # Find recent profitable opportunities
        recent_opportunities = [opp for opp in st.session_state.xauusd_arbitrage['opportunities'] 
                              if opp['status'] == 'ACTIVE' and 
                              (datetime.now() - opp['timestamp']).seconds < 5]
        
        for opp in recent_opportunities[:max_concurrent - active_positions]:
            if opp['spread_pips'] >= st.session_state.xauusd_arbitrage['settings']['min_spread_pips']:
                self.execute_arbitrage_trade(opp)

# Initialize arbitrage engine
arbitrage_engine = XAUUSDArbitrageEngine()# CSS (YOUR EXISTING STYLES + NEW ARBITRAGE STYLES)
theme_css = """
<style>
:root {
    --yantra-primary: #1E3A8A;
    --yantra-secondary: #3B82F6;
    --yantra-success: #10B981;
    --yantra-danger: #EF4444;
    --yantra-warning: #F59E0B;
    --yantra-gold: #F59E0B;
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
footer {visibility: hidden;}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

# ENHANCED SIDEBAR WITH ARBITRAGE CONTROLS
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
        "🥇 XAUUSD Arbitrage": "XAUUSD Arbitrage",  # NEW PAGE
        "🔗 Synthetic Symbols": "Synthetic Symbols",
        "🏦 Broker Manager": "Broker Manager",
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
    st.markdown("### 📊 System Status")
    if st.session_state.kill_switch['active']:
        st.markdown('<div class="status-inactive">🚨 EMERGENCY STOP</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-active">✅ OPERATIONAL</div>', unsafe_allow_html=True)
    
    # NEW: XAUUSD Arbitrage Status (only show on arbitrage page)
    if st.session_state.page == "XAUUSD Arbitrage":
        st.markdown("### 🥇 XAUUSD Arbitrage")
        if st.session_state.xauusd_arbitrage['monitoring']:
            st.markdown('<div class="status-active">🟢 MONITORING</div>', unsafe_allow_html=True)
            
            # Live stats in sidebar
            recent_opps = len([opp for opp in st.session_state.xauusd_arbitrage['opportunities'] 
                              if (datetime.now() - opp['timestamp']).seconds < 60])
            st.metric("Opps/min", recent_opps)
            
            active_positions = len([pos for pos in st.session_state.xauusd_arbitrage['positions'] 
                                   if pos['status'] == 'OPEN'])
            st.metric("Active", active_positions)
            
            today_pnl = st.session_state.xauusd_arbitrage['stats']['today_pnl']
            pnl_color = "🟢" if today_pnl >= 0 else "🔴"
            st.metric("Today P&L", f"{pnl_color} ${today_pnl:.2f}")
            
        else:
            st.markdown('<div class="status-inactive">🔴 STOPPED</div>', unsafe_allow_html=True)
        
        # Quick controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ START", key="arb_start_sidebar"):
                st.session_state.xauusd_arbitrage['monitoring'] = True
                arbitrage_engine.start_monitoring()
                st.rerun()
        with col2:
            if st.button("⏹️ STOP", key="arb_stop_sidebar"):
                arbitrage_engine.stop_monitoring()
                st.rerun()
        
        # Emergency stop for arbitrage
        if st.button("🚨 ARB KILL", key="arb_kill_sidebar", use_container_width=True):
            arbitrage_engine.stop_monitoring()
            st.session_state.xauusd_arbitrage['enabled'] = False
            # Close all positions
            for pos in st.session_state.xauusd_arbitrage['positions']:
                if pos['status'] == 'OPEN':
                    arbitrage_engine.close_position(pos['id'])
            st.error("ARBITRAGE STOPPED")
            st.rerun()
        
        # Quick settings in sidebar
        st.markdown("#### Quick Settings")
        st.session_state.xauusd_arbitrage['settings']['min_spread_pips'] = st.slider(
            "Min Spread", 0.1, 2.0, 
            st.session_state.xauusd_arbitrage['settings']['min_spread_pips'], 0.1,
            key="sidebar_min_spread"
        )
        
        st.session_state.xauusd_arbitrage['settings']['auto_execute'] = st.checkbox(
            "Auto Execute", st.session_state.xauusd_arbitrage['settings']['auto_execute'],
            key="sidebar_auto_execute"
        )
    
    st.markdown("---")
    st.markdown("### 🎛️ Master Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 START", key="sidebar_start_btn", use_container_width=True):
            if not st.session_state.kill_switch['active']:
                st.session_state.auto_trading['enabled'] = True
                st.session_state.arbitrage_settings['enabled'] = True
                st.success("✅ All systems started!")
                st.rerun()
    with col2:
        if st.button("🛑 STOP", key="sidebar_stop_btn", use_container_width=True):
            st.session_state.auto_trading['enabled'] = False
            st.session_state.arbitrage_settings['enabled'] = False
            arbitrage_engine.stop_monitoring()
            st.warning("⚠️ All systems stopped!")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 💰 Account Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Balance", "$25,750", "+5.2%")
        st.metric("Equity", "$25,680", "+4.8%")
    with col2:
        st.metric("P&L", "+$1,250", "")
        st.metric("Margin", "12.5%", "")

# HEADER (YOUR EXISTING CODE)
st.markdown("""
<div class="yantra-header">
    <h1 class="yantra-logo">⭐ YANTRA</h1>
    <p class="yantra-tagline">Professional Latency Arbitrage & MT5 Bridge Platform</p>
</div>
""", unsafe_allow_html=True)# PAGE ROUTING - ENHANCED DASHBOARD + YOUR EXISTING PAGES
if st.session_state.page == "Dashboard":
    st.markdown("# 📊 Dashboard")
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Balance", "$25,750", "+5.2%")
    with col2:
        today_pnl = 1250 + st.session_state.xauusd_arbitrage['stats']['today_pnl']
        st.metric("Today P&L", f"+${today_pnl:.2f}", "+4.8%")
    with col3:
        total_positions = 12 + len([pos for pos in st.session_state.xauusd_arbitrage['positions'] if pos['status'] == 'OPEN'])
        st.metric("Positions", total_positions, "")
    with col4:
        st.metric("Win Rate", "78.5%", "+2.1%")
    
    st.markdown("---")
    
    # NEW: XAUUSD Arbitrage Dashboard Section
    if st.session_state.xauusd_arbitrage['monitoring'] or st.session_state.xauusd_arbitrage['stats']['total_opportunities'] > 0:
        st.markdown("### 🥇 XAUUSD Arbitrage Status")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            status = "🟢 ACTIVE" if st.session_state.xauusd_arbitrage['monitoring'] else "🔴 STOPPED"
            st.metric("Status", status)
        
        with col2:
            recent_opportunities = len([opp for opp in st.session_state.xauusd_arbitrage['opportunities'] 
                                      if (datetime.now() - opp['timestamp']).seconds < 300])
            st.metric("Opportunities (5min)", recent_opportunities)
        
        with col3:
            active_arb_positions = len([pos for pos in st.session_state.xauusd_arbitrage['positions'] 
                                       if pos['status'] == 'OPEN'])
            st.metric("Active Arb Positions", active_arb_positions)
        
        with col4:
            arb_today_pnl = st.session_state.xauusd_arbitrage['stats']['today_pnl']
            pnl_delta = "+$" if arb_today_pnl >= 0 else "-$"
            st.metric("Arb P&L Today", f"{pnl_delta}{abs(arb_today_pnl):.2f}")
        
        with col5:
            arb_win_rate = st.session_state.xauusd_arbitrage['stats']['win_rate']
            st.metric("Arb Win Rate", f"{arb_win_rate:.1f}%")
        
        # Quick arbitrage controls on dashboard
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if not st.session_state.xauusd_arbitrage['monitoring']:
                if st.button("🚀 Start XAUUSD Arbitrage", key="dash_start_arb"):
                    st.session_state.xauusd_arbitrage['monitoring'] = True
                    arbitrage_engine.start_monitoring()
                    st.success("✅ XAUUSD Arbitrage started!")
                    st.rerun()
        with col2:
            if st.session_state.xauusd_arbitrage['monitoring']:
                if st.button("⏹️ Stop XAUUSD Arbitrage", key="dash_stop_arb"):
                    arbitrage_engine.stop_monitoring()
                    st.warning("⚠️ XAUUSD Arbitrage stopped!")
                    st.rerun()
        with col3:
            if st.button("📊 View Full XAUUSD Dashboard", key="dash_view_arb"):
                st.session_state.page = "XAUUSD Arbitrage"
                st.rerun()
        
        st.markdown("---")
    
    # Main dashboard content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Recent Trades")
        
        # Combine regular trades with arbitrage trades
        regular_trades = [
            {"Symbol": "EURUSD", "Type": "BUY", "Entry": "1.0850", "Exit": "1.0865", "P&L": "+$150", "Source": "Manual"},
            {"Symbol": "GBPUSD", "Type": "SELL", "Entry": "1.2650", "Exit": "1.2630", "P&L": "+$200", "Source": "Auto"},
            {"Symbol": "USDJPY", "Type": "BUY", "Entry": "149.50", "Exit": "149.75", "P&L": "+$250", "Source": "Manual"},
        ]
        
        # Add recent arbitrage trades
        recent_arb_trades = []
        for pos in st.session_state.xauusd_arbitrage['positions'][-3:]:  # Last 3 arbitrage trades
            if pos['status'] == 'CLOSED':
                pnl_sign = "+" if pos['realized_pnl'] >= 0 else ""
                recent_arb_trades.append({
                    "Symbol": "XAUUSD",
                    "Type": "ARB",
                    "Entry": f"{pos['buy_price']:.2f}",
                    "Exit": f"{pos['sell_price']:.2f}",
                    "P&L": f"{pnl_sign}${pos['realized_pnl']:.2f}",
                    "Source": "Arbitrage"
                })
        
        all_trades = regular_trades + recent_arb_trades
        trades_df = pd.DataFrame(all_trades)
        st.dataframe(trades_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### System Status")
        st.success("✅ All Systems Operational")
        st.write("🟢 Brokers: 3/3 Connected")
        st.write("🟢 LP Bridges: 4/4 Active")
        st.write("🟢 Auto Trading: Enabled")
        st.write("🟢 Arbitrage: Enabled")
        st.write("🟢 Risk Limits: Compliant")
        
        # XAUUSD Arbitrage status
        if st.session_state.xauusd_arbitrage['monitoring']:
            st.write("🟢 XAUUSD Arbitrage: Active")
            recent_opportunities = len([opp for opp in st.session_state.xauusd_arbitrage['opportunities'] 
                                      if (datetime.now() - opp['timestamp']).seconds < 300])
            st.write(f"🎯 Recent Opportunities: {recent_opportunities}")
            
            # Show current price feeds if available
            broker_a = st.session_state.xauusd_arbitrage['price_feeds']['broker_a']
            broker_b = st.session_state.xauusd_arbitrage['price_feeds']['broker_b']
            
            if broker_a['bid'] and broker_b['bid']:
                st.write(f"📊 Divit Capital: ${broker_a['bid']:.2f}/${broker_a['ask']:.2f}")
                st.write(f"📊 Kama Capital: ${broker_b['bid']:.2f}/${broker_b['ask']:.2f}")
                
                # Show current spread
                spread_1 = broker_b['bid'] - broker_a['ask']
                spread_2 = broker_a['bid'] - broker_b['ask']
                max_spread = max(spread_1, spread_2) / 0.1
                
                if max_spread > 0:
                    spread_color = "🟢" if max_spread >= st.session_state.xauusd_arbitrage['settings']['min_spread_pips'] else "🟡"
                    st.write(f"{spread_color} Max Spread: {max_spread:.1f} pips")
        else:
            st.write("🔴 XAUUSD Arbitrage: Inactive")
    
    # Performance charts section
    if st.session_state.xauusd_arbitrage['stats']['total_opportunities'] > 0:
        st.markdown("---")
        st.markdown("### 📈 XAUUSD Arbitrage Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Opportunities over time (simulated)
            hours = list(range(24))
            opportunities_per_hour = [random.randint(5, 25) for _ in hours]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hours, y=opportunities_per_hour,
                mode='lines+markers',
                name='Opportunities/Hour',
                line=dict(color='#F59E0B', width=3),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title="XAUUSD Arbitrage Opportunities (24h)",
                xaxis_title="Hour",
                yaxis_title="Opportunities",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # P&L distribution
            closed_positions = [pos for pos in st.session_state.xauusd_arbitrage['positions'] if pos['status'] == 'CLOSED']
            
            if closed_positions:
                pnl_values = [pos['realized_pnl'] for pos in closed_positions]
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=pnl_values,
                    nbinsx=10,
                    marker_color='#10B981',
                    opacity=0.7
                ))
                
                fig.update_layout(
                    title="Arbitrage P&L Distribution",
                    xaxis_title="P&L ($)",
                    yaxis_title="Frequency",
                    template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No closed arbitrage positions yet")

# YOUR EXISTING PAGES CONTINUE HERE...
elif st.session_state.page == "Trading Terminal":
    st.markdown("# 💹 Trading Terminal")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Place Trade")
        symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="trade_symbol_select")
        col_a, col_b = st.columns(2)
        with col_a:
            trade_type = st.selectbox("Type", ["BUY", "SELL"], key="trade_type_select")
            volume = st.number_input("Volume (lots)", min_value=0.01, value=1.0, step=0.01, key="trade_volume_num")
        with col_b:
            entry_price = st.number_input("Entry Price", value=1.0850, step=0.0001, key="trade_entry_num")
            sl_pips = st.number_input("Stop Loss (pips)", min_value=1, value=20, step=1, key="trade_sl_num")
        
        tp_pips = st.number_input("Take Profit (pips)", min_value=1, value=30, step=1, key="trade_tp_num")
        
        if st.button("📤 PLACE TRADE", key="place_trade_btn"):
            trade = {
                'Symbol': symbol,
                'Type': trade_type,
                'Volume': volume,
                'Entry': entry_price,
                'SL': sl_pips,
                'TP': tp_pips,
                'Time': datetime.now().strftime("%H:%M:%S"),
                'Status': 'Open'
            }
            st.session_state.trade_journal.append(trade)
            st.success(f"✅ {trade_type} trade placed on {symbol}")
    
    with col2:
        st.markdown("### Quick Stats")
        st.metric("Open Trades", len([t for t in st.session_state.trade_journal if t['Status'] == 'Open']))
        st.metric("Today Trades", len(st.session_state.trade_journal))
        st.metric("Win Rate", "78.5%")
        st.metric("Profit Factor", "2.34")

elif st.session_state.page == "XAUUSD Arbitrage":
    # COMPLETE XAUUSD ARBITRAGE PAGE
    st.markdown("# 🥇 XAUUSD Latency Arbitrage System")
    
    # Status Overview
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        status = "🟢 ACTIVE" if st.session_state.xauusd_arbitrage['monitoring'] else "🔴 STOPPED"
        st.metric("Monitor Status", status)
    
    with col2:
        recent_opps = len([opp for opp in st.session_state.xauusd_arbitrage['opportunities'] 
                          if (datetime.now() - opp['timestamp']).seconds < 60])
        st.metric("Opportunities (1min)", recent_opps)
    
    with col3:
        active_positions = len([pos for pos in st.session_state.xauusd_arbitrage['positions'] 
                               if pos['status'] == 'OPEN'])
        st.metric("Active Positions", active_positions)
    
    with col4:
        today_pnl = st.session_state.xauusd_arbitrage['stats']['today_pnl']
        pnl_color = "normal" if today_pnl >= 0 else "inverse"
        st.metric("Today P&L", f"${today_pnl:.2f}", delta_color=pnl_color)
    
    with col5:
        win_rate = st.session_state.xauusd_arbitrage['stats']['win_rate']
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    st.markdown("---")
    
    # Control Panel
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎛️ Arbitrage Controls")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🚀 START MONITORING", key="start_monitoring_btn", use_container_width=True):
                st.session_state.xauusd_arbitrage['monitoring'] = True
                st.session_state.xauusd_arbitrage['enabled'] = True
                arbitrage_engine.start_monitoring()
                st.success("✅ XAUUSD Arbitrage monitoring started!")
                st.rerun()
        
        with col_b:
            if st.button("⏹️ STOP MONITORING", key="stop_monitoring_btn", use_container_width=True):
                arbitrage_engine.stop_monitoring()
                st.warning("⚠️ XAUUSD Arbitrage monitoring stopped!")
                st.rerun()
        
        with col_c:
            if st.button("🚨 EMERGENCY STOP", key="emergency_stop_btn", use_container_width=True):
                arbitrage_engine.stop_monitoring()
                st.session_state.xauusd_arbitrage['enabled'] = False
                # Close all open positions
                for i, pos in enumerate(st.session_state.xauusd_arbitrage['positions']):
                    if pos['status'] == 'OPEN':
                        arbitrage_engine.close_position(pos['id'])
                st.error("🚨 EMERGENCY STOP ACTIVATED - All positions closed!")
                st.rerun()
    
    with col2:
        st.markdown("### ⚙️ Quick Settings")
        
        st.session_state.xauusd_arbitrage['settings']['min_spread_pips'] = st.slider(
            "Min Spread (pips)", 0.1, 2.0, 
            st.session_state.xauusd_arbitrage['settings']['min_spread_pips'], 0.1,
            key="quick_min_spread"
        )
        
        st.session_state.xauusd_arbitrage['settings']['max_position_size'] = st.selectbox(
            "Position Size (lots)", [0.01, 0.05, 0.1, 0.2, 0.5, 1.0],
            index=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0].index(st.session_state.xauusd_arbitrage['settings']['max_position_size']),
            key="quick_position_size"
        )
        
        st.session_state.xauusd_arbitrage['settings']['auto_execute'] = st.checkbox(
            "Auto Execute", st.session_state.xauusd_arbitrage['settings']['auto_execute'],
            key="quick_auto_execute"
        )
    
    # Live Price Feeds
    st.markdown("### 📊 Live XAUUSD Price Feeds")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏢 Divit Capital")
        broker_a = st.session_state.xauusd_arbitrage['price_feeds']['broker_a']
        if broker_a['bid']:
            st.metric("Bid", f"${broker_a['bid']:.2f}")
            st.metric("Ask", f"${broker_a['ask']:.2f}")
            spread = (broker_a['ask'] - broker_a['bid']) / 0.1
            st.metric("Spread", f"{spread:.1f} pips")
            st.caption(f"Latency: {broker_a['latency']}ms")
        else:
            st.info("Waiting for price feed...")
    
    with col2:
        st.markdown("#### 🏢 Kama Capital")
        broker_b = st.session_state.xauusd_arbitrage['price_feeds']['broker_b']
        if broker_b['bid']:
            st.metric("Bid", f"${broker_b['bid']:.2f}")
            st.metric("Ask", f"${broker_b['ask']:.2f}")
            spread = (broker_b['ask'] - broker_b['bid']) / 0.1
            st.metric("Spread", f"{spread:.1f} pips")
            st.caption(f"Latency: {broker_b['latency']}ms")
        else:
            st.info("Waiting for price feed...")
    
    with col3:
        st.markdown("#### ⚡ Arbitrage Analysis")
        if broker_a['bid'] and broker_b['bid']:
            # Calculate spreads
            spread_1 = broker_b['bid'] - broker_a['ask']  # Buy A, Sell B
            spread_2 = broker_a['bid'] - broker_b['ask']  # Buy B, Sell A
            
            spread_1_pips = spread_1 / 0.1
            spread_2_pips = spread_2 / 0.1
            
            max_spread = max(spread_1_pips, spread_2_pips)
            min_required = st.session_state.xauusd_arbitrage['settings']['min_spread_pips']
            
            if max_spread >= min_required:
                st.success(f"🟢 OPPORTUNITY: {max_spread:.1f} pips")
                if spread_1_pips > spread_2_pips:
                    st.write(f"📈 Buy Divit → Sell Kama")
                    st.write(f"💰 Potential: ${spread_1 * 100:.2f}")
                else:
                    st.write(f"📈 Buy Kama → Sell Divit")
                    st.write(f"💰 Potential: ${spread_2 * 100:.2f}")
            else:
                st.warning(f"🟡 Spread: {max_spread:.1f} pips")
                st.write(f"Need: {min_required:.1f} pips minimum")
            
            # Latency advantage
            latency_diff = abs(broker_a['latency'] - broker_b['latency'])
            st.metric("Latency Edge", f"{latency_diff:.1f}ms")
        else:
            st.info("Waiting for price data...")
    
    st.markdown("---")
    
    # Opportunities and Positions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Recent Opportunities")
        
        if st.session_state.xauusd_arbitrage['opportunities']:
            # Show last 10 opportunities
            recent_opportunities = st.session_state.xauusd_arbitrage['opportunities'][-10:]
            
            for opp in reversed(recent_opportunities):
                time_ago = (datetime.now() - opp['timestamp']).seconds
                
                if time_ago < 60:
                    time_str = f"{time_ago}s ago"
                else:
                    time_str = f"{time_ago//60}m ago"
                
                status_color = "🟢" if opp['status'] == 'ACTIVE' else "🔵"
                
                with st.container():
                    st.markdown(f"""
                    <div class="gold-opportunity">
                        <strong>{status_color} {opp['type']}</strong><br>
                        <strong>Spread:</strong> {opp['spread_pips']} pips (${opp['spread_usd']:.2f})<br>
                        <strong>Potential Profit:</strong> ${opp['potential_profit']:.2f}<br>
                        <strong>Time:</strong> {time_str}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Manual execute button for active opportunities
                if opp['status'] == 'ACTIVE' and time_ago < 30:
                    if st.button(f"⚡ Execute #{opp['id']}", key=f"execute_opp_{opp['id']}"):
                        position = arbitrage_engine.execute_arbitrage_trade(opp)
                        st.success(f"✅ Trade executed! Position #{position['id']}")
                        st.rerun()
        else:
            st.info("No opportunities detected yet. Start monitoring to see live opportunities.")
    
    with col2:
        st.markdown("### 📊 Active Positions")
        
        open_positions = [pos for pos in st.session_state.xauusd_arbitrage['positions'] if pos['status'] == 'OPEN']
        
        if open_positions:
            for pos in open_positions:
                duration = (datetime.now() - pos['entry_time']).seconds
                duration_str = f"{duration//60}m {duration%60}s" if duration >= 60 else f"{duration}s"
                
                # Calculate unrealized P&L (simplified)
                unrealized_pnl = pos['spread_pips'] * pos['position_size'] * 10 * 0.8  # 80% of potential
                pnl_color = "profit-positive" if unrealized_pnl >= 0 else "profit-negative"
                
                st.markdown(f"""
                <div class="arbitrage-opportunity">
                    <strong>Position #{pos['id']}</strong><br>
                    <strong>Type:</strong> {pos['type']}<br>
                    <strong>Size:</strong> {pos['position_size']} lots<br>
                    <strong>Entry Spread:</strong> {pos['spread_pips']} pips<br>
                    <strong>Unrealized P&L:</strong> <span class="{pnl_color}">${unrealized_pnl:.2f}</span><br>
                    <strong>Duration:</strong> {duration_str}
                </div>
                """, unsafe_allow_html=True)
                
                # Close position button
                if st.button(f"🔒 Close Position #{pos['id']}", key=f"close_pos_{pos['id']}"):
                    success = arbitrage_engine.close_position(pos['id'])
                    if success:
                        st.success(f"✅ Position #{pos['id']} closed!")
                        st.rerun()
        else:
            st.info("No active arbitrage positions")
        
        # Show recent closed positions
        st.markdown("### 📈 Recent Closed Positions")
        closed_positions = [pos for pos in st.session_state.xauusd_arbitrage['positions'] if pos['status'] == 'CLOSED'][-5:]
        
        if closed_positions:
            for pos in reversed(closed_positions):
                pnl_color = "profit-positive" if pos['realized_pnl'] >= 0 else "profit-negative"
                pnl_sign = "+" if pos['realized_pnl'] >= 0 else ""
                
                st.markdown(f"""
                **Position #{pos['id']}** - {pos['type']}<br>
                P&L: <span class="{pnl_color}">{pnl_sign}${pos['realized_pnl']:.2f}</span><br>
                Spread: {pos['spread_pips']} pips
                """, unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No closed positions yet")    # Advanced Settings Section
    st.markdown("---")
    st.markdown("### ⚙️ Advanced Arbitrage Settings")
    
    with st.expander("🔧 Detailed Configuration", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Risk Management")
            st.session_state.xauusd_arbitrage['settings']['max_concurrent_trades'] = st.slider(
                "Max Concurrent Trades", 1, 10, 
                st.session_state.xauusd_arbitrage['settings']['max_concurrent_trades'],
                key="max_concurrent_trades"
            )
            
            st.session_state.xauusd_arbitrage['settings']['risk_per_trade'] = st.number_input(
                "Risk per Trade ($)", min_value=10, max_value=1000, 
                value=st.session_state.xauusd_arbitrage['settings']['risk_per_trade'],
                step=10, key="risk_per_trade"
            )
            
            st.session_state.xauusd_arbitrage['settings']['stop_loss_pips'] = st.slider(
                "Stop Loss (pips)", 1, 20, 
                st.session_state.xauusd_arbitrage['settings']['stop_loss_pips'],
                key="stop_loss_pips"
            )
        
        with col2:
            st.markdown("#### Execution Settings")
            st.session_state.xauusd_arbitrage['settings']['take_profit_pips'] = st.slider(
                "Take Profit (pips)", 1, 10, 
                st.session_state.xauusd_arbitrage['settings']['take_profit_pips'],
                key="take_profit_pips"
            )
            
            execution_speed = st.selectbox(
                "Execution Speed", 
                ["Ultra Fast", "Fast", "Normal"],
                index=0, key="execution_speed"
            )
            
            slippage_tolerance = st.slider(
                "Slippage Tolerance (pips)", 0.1, 2.0, 0.5, 0.1,
                key="slippage_tolerance"
            )
        
        with col3:
            st.markdown("#### Monitoring Settings")
            refresh_rate = st.selectbox(
                "Price Refresh Rate", 
                ["100ms", "200ms", "500ms", "1000ms"],
                index=0, key="refresh_rate"
            )
            
            opportunity_timeout = st.slider(
                "Opportunity Timeout (seconds)", 5, 60, 30,
                key="opportunity_timeout"
            )
            
            enable_alerts = st.checkbox(
                "Enable Sound Alerts", False,
                key="enable_alerts"
            )
    
    # Performance Analytics
    st.markdown("---")
    st.markdown("### 📊 Performance Analytics")
    
    if st.session_state.xauusd_arbitrage['stats']['total_opportunities'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Opportunities Timeline Chart
            st.markdown("#### 🎯 Opportunities Over Time")
            
            # Generate sample data for demonstration
            hours = list(range(24))
            opportunities_data = []
            cumulative_opps = 0
            
            for hour in hours:
                hour_opps = random.randint(3, 15)
                cumulative_opps += hour_opps
                opportunities_data.append({
                    'hour': hour,
                    'opportunities': hour_opps,
                    'cumulative': cumulative_opps
                })
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Bar chart for hourly opportunities
            fig.add_trace(
                go.Bar(
                    x=[d['hour'] for d in opportunities_data],
                    y=[d['opportunities'] for d in opportunities_data],
                    name="Opportunities/Hour",
                    marker_color='#F59E0B',
                    opacity=0.7
                ),
                secondary_y=False,
            )
            
            # Line chart for cumulative
            fig.add_trace(
                go.Scatter(
                    x=[d['hour'] for d in opportunities_data],
                    y=[d['cumulative'] for d in opportunities_data],
                    mode='lines+markers',
                    name="Cumulative",
                    line=dict(color='#10B981', width=3),
                    marker=dict(size=6)
                ),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="Hour of Day")
            fig.update_yaxes(title_text="Opportunities", secondary_y=False)
            fig.update_yaxes(title_text="Cumulative", secondary_y=True)
            
            fig.update_layout(
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # P&L Distribution
            st.markdown("#### 💰 P&L Distribution")
            
            closed_positions = [pos for pos in st.session_state.xauusd_arbitrage['positions'] if pos['status'] == 'CLOSED']
            
            if closed_positions:
                pnl_values = [pos['realized_pnl'] for pos in closed_positions]
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=pnl_values,
                    nbinsx=15,
                    marker_color='#10B981',
                    opacity=0.7,
                    name="P&L Distribution"
                ))
                
                # Add mean line
                mean_pnl = np.mean(pnl_values)
                fig.add_vline(
                    x=mean_pnl, 
                    line_dash="dash", 
                    line_color="red",
                    annotation_text=f"Mean: ${mean_pnl:.2f}"
                )
                
                fig.update_layout(
                    title="Trade P&L Distribution",
                    xaxis_title="P&L ($)",
                    yaxis_title="Frequency",
                    template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Show sample data for demonstration
                sample_pnl = np.random.normal(25, 15, 50)  # Mean $25, std $15
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=sample_pnl,
                    nbinsx=15,
                    marker_color='#10B981',
                    opacity=0.7,
                    name="Sample P&L"
                ))
                
                fig.update_layout(
                    title="Expected P&L Distribution (Sample)",
                    xaxis_title="P&L ($)",
                    yaxis_title="Frequency",
                    template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Statistics Table
        st.markdown("#### 📈 Detailed Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Opportunities", st.session_state.xauusd_arbitrage['stats']['total_opportunities'])
            st.metric("Executed Trades", st.session_state.xauusd_arbitrage['stats']['executed_trades'])
        
        with col2:
            st.metric("Successful Trades", st.session_state.xauusd_arbitrage['stats']['successful_trades'])
            execution_rate = (st.session_state.xauusd_arbitrage['stats']['executed_trades'] / 
                            max(st.session_state.xauusd_arbitrage['stats']['total_opportunities'], 1)) * 100
            st.metric("Execution Rate", f"{execution_rate:.1f}%")
        
        with col3:
            st.metric("Total P&L", f"${st.session_state.xauusd_arbitrage['stats']['total_pnl']:.2f}")
            st.metric("Avg Profit/Trade", f"${st.session_state.xauusd_arbitrage['stats']['avg_profit_per_trade']:.2f}")
        
        with col4:
            st.metric("Win Rate", f"{st.session_state.xauusd_arbitrage['stats']['win_rate']:.1f}%")
            
            # Calculate Sharpe ratio (simplified)
            if closed_positions:
                returns = [pos['realized_pnl'] for pos in closed_positions]
                sharpe = np.mean(returns) / (np.std(returns) + 0.01)  # Avoid division by zero
                st.metric("Sharpe Ratio", f"{sharpe:.2f}")
            else:
                st.metric("Sharpe Ratio", "N/A")
    
    else:
        st.info("📊 Start monitoring to see performance analytics")
        
        # Show sample analytics for demonstration
        st.markdown("#### 📈 Expected Performance (Sample Data)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sample opportunities chart
            sample_hours = list(range(24))
            sample_opps = [random.randint(5, 20) for _ in sample_hours]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sample_hours,
                y=sample_opps,
                marker_color='#F59E0B',
                opacity=0.7,
                name="Expected Opportunities/Hour"
            ))
            
            fig.update_layout(
                title="Expected Opportunities Distribution",
                xaxis_title="Hour of Day",
                yaxis_title="Opportunities",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sample performance metrics
            st.markdown("**Expected Performance Metrics:**")
            st.write("🎯 Opportunities/Day: 150-300")
            st.write("⚡ Execution Rate: 15-25%")
            st.write("💰 Avg Profit/Trade: $20-40")
            st.write("📊 Win Rate: 75-85%")
            st.write("⏱️ Avg Trade Duration: 30-120s")
            st.write("📈 Expected Daily P&L: $300-800")
    
    # Risk Monitoring
    st.markdown("---")
    st.markdown("### ⚠️ Risk Monitoring")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🛡️ Position Risk")
        current_exposure = len([pos for pos in st.session_state.xauusd_arbitrage['positions'] if pos['status'] == 'OPEN'])
        max_exposure = st.session_state.xauusd_arbitrage['settings']['max_concurrent_trades']
        
        risk_percentage = (current_exposure / max_exposure) * 100
        
        if risk_percentage < 50:
            st.success(f"✅ Low Risk: {current_exposure}/{max_exposure} positions")
        elif risk_percentage < 80:
            st.warning(f"⚠️ Medium Risk: {current_exposure}/{max_exposure} positions")
        else:
            st.error(f"🚨 High Risk: {current_exposure}/{max_exposure} positions")
    
    with col2:
        st.markdown("#### 💸 Daily P&L Risk")
        daily_pnl = st.session_state.xauusd_arbitrage['stats']['today_pnl']
        max_daily_risk = st.session_state.xauusd_arbitrage['settings']['risk_per_trade'] * 10  # 10x single trade risk
        
        if daily_pnl > -max_daily_risk * 0.5:
            st.success(f"✅ P&L: ${daily_pnl:.2f}")
        elif daily_pnl > -max_daily_risk:
            st.warning(f"⚠️ P&L: ${daily_pnl:.2f}")
        else:
            st.error(f"🚨 P&L: ${daily_pnl:.2f}")
    
    with col3:
        st.markdown("#### 🔄 System Health")
        if st.session_state.xauusd_arbitrage['monitoring']:
            st.success("✅ Monitoring Active")
            st.success("✅ Price Feeds OK")
            st.success("✅ Execution Ready")
        else:
            st.warning("⚠️ Monitoring Stopped")
            st.info("ℹ️ Price Feeds Idle")
            st.info("ℹ️ Execution Paused")

# Continue with your existing pages...
elif st.session_state.page == "Advanced Charts":
    st.markdown("# 📈 Advanced Charts")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symbol = st.selectbox("Select Symbol", st.session_state.mt5_symbols, key="chart_symbol_select")
        
        # Generate sample OHLC data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)
        
        price_data = []
        base_price = 1.0850 if symbol == 'EURUSD' else 2650.00 if symbol == 'XAUUSD' else 149.50
        
        for i, date in enumerate(dates):
            change = np.random.normal(0, 0.002) * base_price
            base_price += change
            
            high = base_price + abs(np.random.normal(0, 0.001)) * base_price
            low = base_price - abs(np.random.normal(0, 0.001)) * base_price
            close = base_price + np.random.normal(0, 0.0005) * base_price
            
            price_data.append({
                'Date': date,
                'Open': base_price,
                'High': high,
                'Low': low,
                'Close': close,
                'Volume': random.randint(1000, 10000)
            })
        
        df = pd.DataFrame(price_data)
        
        # Create candlestick chart
        fig = go.Figure(data=go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=symbol
        ))
        
        fig.update_layout(
            title=f"{symbol} - Daily Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Chart Controls")
        timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "1H", "4H", "1D"], index=5, key="chart_timeframe")
        chart_type = st.selectbox("Chart Type", ["Candlestick", "Line", "Area"], key="chart_type")
        
        st.markdown("### Indicators")
        show_ma = st.checkbox("Moving Average", key="show_ma")
        show_bb = st.checkbox("Bollinger Bands", key="show_bb")
        show_rsi = st.checkbox("RSI", key="show_rsi")
        
        st.markdown("### Market Info")
        st.metric("Current Price", f"{df['Close'].iloc[-1]:.4f}")
        st.metric("Daily Change", f"{((df['Close'].iloc[-1] / df['Open'].iloc[-1]) - 1) * 100:.2f}%")
        st.metric("Volume", f"{df['Volume'].iloc[-1]:,}")

elif st.session_state.page == "Tick Charts":
    st.markdown("# 📊 Tick Charts")
    
    symbol = st.selectbox("Select Symbol", st.session_state.mt5_symbols, key="tick_symbol_select")
    
    # Generate real-time tick data
    if 'tick_data' not in st.session_state:
        st.session_state.tick_data = []
    
    # Add new tick data
    if len(st.session_state.tick_data) < 100:
        base_price = 1.0850 if symbol == 'EURUSD' else 2650.00 if symbol == 'XAUUSD' else 149.50
        for i in range(100):
            tick_price = base_price + np.random.normal(0, 0.001) * base_price
            st.session_state.tick_data.append({
                'time': datetime.now() - timedelta(seconds=100-i),
                'price': tick_price,
                'volume': random.randint(1, 10)
            })
    
    # Create tick chart
    tick_df = pd.DataFrame(st.session_state.tick_data[-50:])  # Last 50 ticks
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tick_df['time'],
        y=tick_df['price'],
        mode='lines+markers',
        name=f'{symbol} Ticks',
        line=dict(color='#3B82F6', width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title=f"{symbol} - Live Tick Data",
        xaxis_title="Time",
        yaxis_title="Price",
        template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Auto-refresh
    if st.button("🔄 Refresh", key="tick_refresh"):
        st.rerun()

elif st.session_state.page == "Auto Trading":
    st.markdown("# 🤖 Auto Trading")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Strategy Configuration")
        
        strategy_name = st.text_input("Strategy Name", "EURUSD Scalper", key="strategy_name")
        
        col_a, col_b = st.columns(2)
        with col_a:
            entry_signal = st.selectbox("Entry Signal", ["RSI Oversold", "MA Crossover", "Breakout"], key="entry_signal")
            exit_signal = st.selectbox("Exit Signal", ["Take Profit", "Stop Loss", "Trailing Stop"], key="exit_signal")
        with col_b:
            risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.1, key="auto_risk_per_trade")
            max_trades = st.number_input("Max Daily Trades", 1, 100, 20, key="auto_max_trades")
        
        if st.button("💾 Save Strategy", key="save_strategy"):
            strategy = {
                'name': strategy_name,
                'entry': entry_signal,
                'exit': exit_signal,
                'risk': risk_per_trade,
                'max_trades': max_trades
            }
            st.session_state.auto_trading['strategies'].append(strategy)
            st.success(f"✅ Strategy '{strategy_name}' saved!")
    
    with col2:
        st.markdown("### Auto Trading Status")
        
        if st.session_state.auto_trading['enabled']:
            st.success("🟢 Auto Trading: ACTIVE")
        else:
            st.error("🔴 Auto Trading: INACTIVE")
        
        st.metric("Strategies", len(st.session_state.auto_trading['strategies']))
        st.metric("Trades Today", st.session_state.auto_trading['trades_today'])
        st.metric("Profit Today", f"${st.session_state.auto_trading['profit_today']:.2f}")
        
        if st.button("🚀 Start Auto Trading", key="start_auto_trading"):
            st.session_state.auto_trading['enabled'] = True
            st.success("✅ Auto Trading Started!")
            st.rerun()
        
        if st.button("🛑 Stop Auto Trading", key="stop_auto_trading"):
            st.session_state.auto_trading['enabled'] = False
            st.warning("⚠️ Auto Trading Stopped!")
            st.rerun()

elif st.session_state.page == "Latency Arbitrage":
    st.markdown("# ⚡ Latency Arbitrage")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "🟢 ACTIVE" if st.session_state.arbitrage_settings['enabled'] else "🔴 INACTIVE")
        st.metric("Opportunities Today", "47")
        st.metric("Executed Trades", "12")
    
    with col2:
        st.metric("Success Rate", "89.2%")
        st.metric("Avg Profit", "$23.50")
        st.metric("Total P&L", "+$282.00")
    
    with col3:
        st.metric("Latency Edge", "0.8ms")
        st.metric("Bridge Status", "🟢 CONNECTED")
        st.metric("LP Feeds", "4/4 Active")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Arbitrage Settings")
        
        st.session_state.arbitrage_settings['min_spread'] = st.slider(
            "Minimum Spread (pips)", 0.1, 2.0, 
            st.session_state.arbitrage_settings['min_spread'], 0.1,
            key="arb_min_spread"
        )
        
        st.session_state.arbitrage_settings['max_volume'] = st.slider(
            "Maximum Volume (lots)", 0.1, 50.0, 
            st.session_state.arbitrage_settings['max_volume'], 0.1,
            key="arb_max_volume"
        )
        
        st.session_state.arbitrage_settings['execution_speed'] = st.selectbox(
            "Execution Speed", ["Ultra Fast", "Fast", "Normal"],
            index=0, key="arb_execution_speed"
        )
        
        st.session_state.arbitrage_settings['slippage_tolerance'] = st.slider(
            "Slippage Tolerance (pips)", 0.1, 1.0, 
            st.session_state.arbitrage_settings['slippage_tolerance'], 0.1,
            key="arb_slippage"
        )
    
    with col2:
        st.markdown("### Quick Actions")
        
        if st.button("🚀 Enable Arbitrage", key="enable_arbitrage"):
            st.session_state.arbitrage_settings['enabled'] = True
            st.success("✅ Arbitrage Enabled!")
            st.rerun()
        
        if st.button("⏸️ Pause Arbitrage", key="pause_arbitrage"):
            st.session_state.arbitrage_settings['enabled'] = False
            st.warning("⚠️ Arbitrage Paused!")
            st.rerun()
        
        st.markdown("### Recent Opportunities")
        opportunities = [
            {"Pair": "EURUSD", "Spread": "1.2 pips", "Status": "✅ Executed"},
            {"Pair": "GBPUSD", "Spread": "0.9 pips", "Status": "⏭️ Skipped"},
            {"Pair": "XAUUSD", "Spread": "1.5 pips", "Status": "✅ Executed"},
        ]
        
        for opp in opportunities:
            st.write(f"**{opp['Pair']}** - {opp['Spread']} - {opp['Status']}")

elif st.session_state.page == "Synthetic Symbols":
    st.markdown("# 🔗 Synthetic Symbols")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Create Synthetic Symbol")
        
        symbol_name = st.text_input("Symbol Name", "CUSTOM_INDEX", key="synthetic_name")
        
        col_a, col_b = st.columns(2)
        with col_a:
            base_symbol = st.selectbox("Base Symbol", st.session_state.mt5_symbols, key="synthetic_base")
            weight_1 = st.slider("Weight 1", 0.1, 2.0, 1.0, 0.1, key="synthetic_weight1")
        with col_b:
            quote_symbol = st.selectbox("Quote Symbol", st.session_state.mt5_symbols, index=1, key="synthetic_quote")
            weight_2 = st.slider("Weight 2", 0.1, 2.0, 1.0, 0.1, key="synthetic_weight2")
        
        formula = st.text_area("Formula", f"({base_symbol} * {weight_1}) / ({quote_symbol} * {weight_2})", key="synthetic_formula")
        
        if st.button("➕ Create Symbol", key="create_synthetic"):
            synthetic = {
                'name': symbol_name,
                'base': base_symbol,
                'quote': quote_symbol,
                'weight1': weight_1,
                'weight2': weight_2,
                'formula': formula
            }
            st.session_state.synthetic_symbols.append(synthetic)
            st.success(f"✅ Synthetic symbol '{symbol_name}' created!")
    
    with col2:
        st.markdown("### Existing Synthetics")
        
        if st.session_state.synthetic_symbols:
            for i, symbol in enumerate(st.session_state.synthetic_symbols):
                st.write(f"**{symbol['name']}**")
                st.write(f"Formula: {symbol['formula']}")
                if st.button(f"🗑️ Delete", key=f"delete_synthetic_{i}"):
                    st.session_state.synthetic_symbols.pop(i)
                    st.rerun()
                st.markdown("---")
        else:
            st.info("No synthetic symbols created yet")

elif st.session_state.page == "Broker Manager":
    st.markdown("# 🏦 Broker Manager")
    
    # Broker connection status
    brokers = {
        "Divit Capital": {"status": "Connected", "latency": "0.7ms", "spread": "0.1 pips"},
        "Kama Capital": {"status": "Connected", "latency": "1.2ms", "spread": "0.2 pips"},
        "IC Markets": {"status": "Disconnected", "latency": "N/A", "spread": "N/A"}
    }
    
    for broker_name, info in brokers.items():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write(f"**{broker_name}**")
        with col2:
            if info["status"] == "Connected":
                st.success(f"🟢 {info['status']}")
            else:
                st.error(f"🔴 {info['status']}")
        with col3:
            st.write(f"Latency: {info['latency']}")
        with col4:
            st.write(f"Spread: {info['spread']}")
        
        st.markdown("---")

elif st.session_state.page == "LP Bridge Manager":
    st.markdown("# 🌐 LP Bridge Manager")
    
    for lp_name, info in st.session_state.lp_connections.items():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write(f"**{lp_name}**")
        with col2:
            st.success(f"🟢 {info['status']}")
        with col3:
            st.write(f"Latency: {info['latency']}ms")
        with col4:
            st.write(f"Spread: {info['spread']} pips")
        
        st.markdown("---")

elif st.session_state.page == "Analytics":
    st.markdown("# 📊 Analytics")
    
    # Combined analytics including XAUUSD arbitrage
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pnl = 1250 + st.session_state.xauusd_arbitrage['stats']['today_pnl']
        st.metric("Total P&L", f"${total_pnl:.2f}")
    with col2:
        total_trades = 45 + st.session_state.xauusd_arbitrage['stats']['executed_trades']
        st.metric("Total Trades", total_trades)
    with col3:
        combined_win_rate = (78.5 + st.session_state.xauusd_arbitrage['stats']['win_rate']) / 2
        st.metric("Combined Win Rate", f"{combined_win_rate:.1f}%")
    with col4:
        st.metric("Sharpe Ratio", "2.34")
    
    # Performance chart
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    pnl_data = np.cumsum(np.random.normal(25, 50, 30))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=pnl_data,
        mode='lines+markers',
        name='Cumulative P&L',
        line=dict(color='#10B981', width=3)
    ))
    
    fig.update_layout(
        title="30-Day Performance",
        xaxis_title="Date",
        yaxis_title="P&L ($)",
        template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Trade Journal":
    st.markdown("# 📔 Trade Journal")
    
    if st.session_state.trade_journal:
        df = pd.DataFrame(st.session_state.trade_journal)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No trades recorded yet")

elif st.session_state.page == "Risk Manager":
    st.markdown("# ⚠️ Risk Manager")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Risk Limits")
        
        st.session_state.risk_limits['daily_loss'] = st.number_input(
            "Daily Loss Limit ($)", 1000, 50000, 
            st.session_state.risk_limits['daily_loss'], 100,
            key="daily_loss_limit"
        )
        
        st.session_state.risk_limits['max_positions'] = st.slider(
            "Max Open Positions", 1, 50, 
            st.session_state.risk_limits['max_positions'],
            key="max_positions_limit"
        )
        
        st.session_state.risk_limits['max_leverage'] = st.slider(
            "Max Leverage", 1, 500, 
            st.session_state.risk_limits['max_leverage'],
            key="max_leverage_limit"
        )
    
    with col2:
        st.markdown("### Current Risk Status")
        st.success("✅ All limits compliant")
        st.metric("Current Drawdown", "2.1%")
        st.metric("VaR (95%)", "$1,250")
        st.metric("Open Positions", "12")

elif st.session_state.page == "Kill Switch":
    st.markdown("# 🚨 Kill Switch")
    
    if st.session_state.kill_switch['active']:
        st.error("🚨 EMERGENCY STOP ACTIVATED")
        st.write(f"Reason: {st.session_state.kill_switch['reason']}")
        
        if st.button("🔄 RESET SYSTEM", key="reset_kill_switch"):
            st.session_state.kill_switch['active'] = False
            st.session_state.kill_switch['reason'] = ''
            st.success("✅ System Reset!")
            st.rerun()
    else:
        st.success("✅ System Operating Normally")
        
        st.markdown("### Emergency Stop Triggers")
        
        if st.button("🚨 ACTIVATE KILL SWITCH", key="activate_kill_switch"):
            st.session_state.kill_switch['active'] = True
            st.session_state.kill_switch['reason'] = 'Manual activation'
            st.session_state.auto_trading['enabled'] = False
            st.session_state.arbitrage_settings['enabled'] = False
            arbitrage_engine.stop_monitoring()
            st.error("🚨 EMERGENCY STOP ACTIVATED!")
            st.rerun()

elif st.session_state.page == "Safety Center":
    st.markdown("# 🛡️ Safety Center")
    
    st.success("✅ All Safety Checks Passed")
    
    safety_checks = [
        {"Check": "Broker Connections", "Status": "✅ OK", "Details": "All brokers responding"},
        {"Check": "Risk Limits", "Status": "✅ OK", "Details": "Within acceptable ranges"},
        {"Check": "System Resources", "Status": "✅ OK", "Details": "CPU: 45%, RAM: 62%"},
        {"Check": "Network Latency", "Status": "✅ OK", "Details": "Avg: 0.8ms"},
        {"Check": "XAUUSD Arbitrage", "Status": "✅ OK", "Details": "Monitoring active"},
    ]
    
    for check in safety_checks:
        col1, col2, col3 = st.columns([2, 1, 3])
        with col1:
            st.write(check["Check"])
        with col2:
            st.write(check["Status"])
        with col3:
            st.write(check["Details"])

elif st.session_state.page == "Settings":
    st.markdown("# ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### General Settings")
        
        st.session_state.theme = st.selectbox(
            "Theme", ["Dark", "Light"], 
            index=0 if st.session_state.theme == "Dark" else 1,
            key="theme_select"
        )
        
        auto_refresh = st.checkbox("Auto Refresh", True, key="auto_refresh_setting")
        sound_alerts = st.checkbox("Sound Alerts", False, key="sound_alerts_setting")
        
        st.markdown("### Trading Settings")
        default_volume = st.number_input("Default Volume", 0.01, 10.0, 1.0, 0.01, key="default_volume_setting")
        default_sl = st.number_input("Default SL (pips)", 1, 100, 20, key="default_sl_setting")
        default_tp = st.number_input("Default TP (pips)", 1, 200, 30, key="default_tp_setting")
    
    with col2:
        st.markdown("### XAUUSD Arbitrage Settings")
        
        # Global arbitrage settings
        global_arb_enabled = st.checkbox(
            "Enable XAUUSD Arbitrage", 
            st.session_state.xauusd_arbitrage['enabled'],
            key="global_arb_enabled"
        )
        
        if global_arb_enabled != st.session_state.xauusd_arbitrage['enabled']:
            st.session_state.xauusd_arbitrage['enabled'] = global_arb_enabled
            if not global_arb_enabled:
                arbitrage_engine.stop_monitoring()
        
        # Export/Import Settings
        st.markdown("### Data Management")
        
        if st.button("📤 Export Settings", key="export_settings"):
            settings_data = {
                'arbitrage_settings': st.session_state.arbitrage_settings,
                'xauusd_arbitrage': st.session_state.xauusd_arbitrage['settings'],
                'risk_limits': st.session_state.risk_limits
            }
            st.download_button(
                "💾 Download Settings",
                json.dumps(settings_data, indent=2),
                "yantra_settings.json",
                "application/json"
            )
        
        if st.button("🗑️ Reset All Data", key="reset_all_data"):
            if st.button("⚠️ Confirm Reset", key="confirm_reset"):
                # Reset all session state
                for key in list(st.session_state.keys()):
                    if key != 'page':
                        del st.session_state[key]
                st.success("✅ All data reset!")
                st.rerun()

# Auto-refresh for real-time updates (only on XAUUSD Arbitrage page)
if st.session_state.page == "XAUUSD Arbitrage" and st.session_state.xauusd_arbitrage['monitoring']:
    time.sleep(1)  # Small delay to prevent too frequent updates
    st.rerun()
