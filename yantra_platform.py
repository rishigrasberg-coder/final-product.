import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random
import json

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Yantra Trading Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== COMPLETE SESSION STATE INITIALIZATION =====
def init_session_state():
    """Initialize ALL session state data - keeping every feature"""
    
    # Core navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    if 'theme' not in st.session_state:
        st.session_state.theme = "Dark"
    
    # Portfolio data
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {
            'balance': 50000.0,
            'equity': 52500.0,
            'margin': 2500.0,
            'free_margin': 50000.0,
            'margin_level': 2100.0,
            'positions': [
                {'id': 1, 'symbol': 'EURUSD', 'type': 'BUY', 'volume': 1.0, 'entry_price': 1.0845, 'current_price': 1.0865, 'pnl': 200.0, 'broker': 'Divit Capital', 'open_time': datetime.now() - timedelta(hours=2)},
                {'id': 2, 'symbol': 'GBPUSD', 'type': 'SELL', 'volume': 0.5, 'entry_price': 1.2650, 'current_price': 1.2635, 'pnl': 75.0, 'broker': 'Kama Capital', 'open_time': datetime.now() - timedelta(hours=1)},
                {'id': 3, 'symbol': 'XAUUSD', 'type': 'BUY', 'volume': 0.1, 'entry_price': 2650.0, 'current_price': 2665.0, 'pnl': 150.0, 'broker': 'Divit Capital', 'open_time': datetime.now() - timedelta(minutes=30), 'tags': ['arbitrage']}
            ],
            'pending_orders': [
                {'id': 101, 'symbol': 'USDJPY', 'type': 'BUY LIMIT', 'volume': 1.0, 'price': 149.50, 'sl': 149.00, 'tp': 150.00, 'broker': 'Kama Capital'},
                {'id': 102, 'symbol': 'AUDUSD', 'type': 'SELL STOP', 'volume': 0.5, 'price': 0.6500, 'sl': 0.6550, 'tp': 0.6450, 'broker': 'Divit Capital'}
            ]
        }
    
    # Broker connections
    if 'brokers' not in st.session_state:
        st.session_state.brokers = {
            'Divit Capital': {
                'status': 'Connected',
                'balance': 25000,
                'equity': 26250,
                'margin': 1250,
                'positions': 2,
                'server': 'DivitCapital-Live',
                'ping': 12,
                'last_update': datetime.now()
            },
            'Kama Capital': {
                'status': 'Connected',
                'balance': 25000,
                'equity': 26250,
                'margin': 1250,
                'positions': 1,
                'server': 'KamaCapital-Live',
                'ping': 8,
                'last_update': datetime.now()
            },
            'LP Bridge': {
                'status': 'Connected',
                'balance': 0,
                'equity': 0,
                'margin': 0,
                'positions': 0,
                'server': 'LP-Aggregator',
                'ping': 5,
                'last_update': datetime.now()
            }
        }
    
    # Trading symbols
    if 'mt5_symbols' not in st.session_state:
        st.session_state.mt5_symbols = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF', 'EURGBP',
            'EURJPY', 'GBPJPY', 'AUDJPY', 'CADJPY', 'CHFJPY', 'EURCHF', 'AUDCAD', 'GBPCAD',
            'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'US30', 'US500', 'NAS100', 'GER40',
            'UK100', 'FRA40', 'JPN225', 'AUS200', 'BTCUSD', 'ETHUSD', 'LTCUSD', 'ADAUSD'
        ]
    
    # Auto trading system
    if 'auto_trading' not in st.session_state:
        st.session_state.auto_trading = {
            'enabled': False,
            'trades_today': 12,
            'profit_today': 450.75,
            'max_trades': 50,
            'risk_per_trade': 2.0,
            'strategies': [
                {
                    'name': 'MA Crossover EURUSD',
                    'type': 'MA Crossover',
                    'symbols': ['EURUSD', 'GBPUSD'],
                    'timeframe': '15M',
                    'risk_per_trade': 1.5,
                    'enabled': True,
                    'trades_today': 5,
                    'profit_today': 125.50,
                    'win_rate': 68.5,
                    'total_pnl': 1250.75
                },
                {
                    'name': 'RSI Gold Strategy',
                    'type': 'RSI',
                    'symbols': ['XAUUSD'],
                    'timeframe': '5M',
                    'risk_per_trade': 3.0,
                    'enabled': True,
                    'trades_today': 7,
                    'profit_today': 325.25,
                    'win_rate': 71.2,
                    'total_pnl': 2150.25
                }
            ]
        }
    
    # XAUUSD Arbitrage system
    if 'xauusd_arbitrage' not in st.session_state:
        st.session_state.xauusd_arbitrage = {
            'monitoring': False,
            'price_feeds': {
                'broker_a': {
                    'name': 'Divit Capital',
                    'bid': 2655.25,
                    'ask': 2656.75,
                    'latency': 12
                },
                'broker_b': {
                    'name': 'Kama Capital',
                    'bid': 2654.80,
                    'ask': 2656.30,
                    'latency': 8
                }
            },
            'settings': {
                'min_profit_threshold': 1.0,
                'max_position_size': 1.0,
                'max_slippage': 0.5,
                'max_daily_trades': 20,
                'max_exposure': 50000,
                'stop_loss': 10.0,
                'auto_execute': False
            },
            'opportunities': [
                {
                    'timestamp': datetime.now() - timedelta(minutes=5),
                    'type': 'A→B',
                    'profit_potential': 1.45,
                    'size': 0.5,
                    'status': 'Executed',
                    'executed': True
                },
                {
                    'timestamp': datetime.now() - timedelta(minutes=15),
                    'type': 'B→A',
                    'profit_potential': 1.20,
                    'size': 0.3,
                    'status': 'Missed',
                    'executed': False
                }
            ],
            'stats': {
                'total_opportunities': 25,
                'today_pnl': 125.75,
                'total_pnl': 1250.50,
                'success_rate': 72.5,
                'avg_profit': 1.85
            }
        }
    
    # LP Bridge system
    if 'lp_bridge' not in st.session_state:
        st.session_state.lp_bridge = {
            'liquidity_providers': [
                {
                    'id': 1,
                    'name': 'Prime Broker 1',
                    'type': 'Prime Broker',
                    'protocol': 'FIX',
                    'status': 'Connected',
                    'available_liquidity': 5000000,
                    'total_liquidity': 10000000,
                    'utilization': 50.0,
                    'min_trade_size': 10000,
                    'max_trade_size': 500000,
                    'commission': 0.15,
                    'supported_symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],
                    'latency': 12.5,
                    'uptime': 99.2,
                    'daily_volume': 2500000,
                    'fill_rate': 98.5,
                    'avg_spread': 0.8,
                    'rejections_today': 2
                },
                {
                    'id': 2,
                    'name': 'ECN Bridge',
                    'type': 'ECN',
                    'protocol': 'REST API',
                    'status': 'Connected',
                    'available_liquidity': 3000000,
                    'total_liquidity': 5000000,
                    'utilization': 60.0,
                    'min_trade_size': 1000,
                    'max_trade_size': 300000,
                    'commission': 0.08,
                    'supported_symbols': ['EURUSD', 'GBPUSD', 'AUDUSD', 'USDCAD'],
                    'latency': 8.2,
                    'uptime': 99.8,
                    'daily_volume': 1800000,
                    'fill_rate': 99.2,
                    'avg_spread': 0.6,
                    'rejections_today': 0
                },
                {
                    'id': 3,
                    'name': 'Market Maker',
                    'type': 'Market Maker',
                    'protocol': 'WebSocket',
                    'status': 'Disconnected',
                    'available_liquidity': 0,
                    'total_liquidity': 8000000,
                    'utilization': 0.0,
                    'min_trade_size': 5000,
                    'max_trade_size': 800000,
                    'commission': 0.12,
                    'supported_symbols': ['XAUUSD', 'XAGUSD', 'USOIL'],
                    'latency': 0,
                    'uptime': 0,
                    'daily_volume': 0,
                    'fill_rate': 0,
                    'avg_spread': 0,
                    'rejections_today': 0
                }
            ],
            'settings': {
                'routing_mode': 'Best Price',
                'failover_enabled': True,
                'failover_timeout': 1000,
                'load_balancing': True,
                'max_lp_utilization': 80,
                'max_order_size': 1000000,
                'position_limits': True,
                'max_net_position': 10000000,
                'credit_limits': True,
                'max_credit_exposure': 5000000,
                'price_tolerance': 1.0,
                'execution_timeout': 3000,
                'retry_attempts': 3
            }
        }
    
    # Copy trading system
    if 'copy_trading' not in st.session_state:
        st.session_state.copy_trading = {
            'subscriptions': [
                {
                    'provider': 'ProTrader Elite',
                    'status': 'Active',
                    'monthly_return': 15.2,
                    'followers': 1250,
                    'risk_score': 6,
                    'monthly_fee': 29,
                    'copy_ratio': 0.1,
                    'trades_copied': 45,
                    'profit_this_month': 125.50
                }
            ],
            'available_providers': [
                {'name': '🏆 ProTrader Elite', 'return': 15.2, 'followers': 1250, 'risk': 6, 'fee': 29},
                {'name': '📈 GoldMaster Pro', 'return': 22.8, 'followers': 890, 'risk': 8, 'fee': 39},
                {'name': '💎 ForexKing', 'return': 18.5, 'followers': 2100, 'risk': 5, 'fee': 25},
                {'name': '🚀 CryptoBot AI', 'return': 31.2, 'followers': 650, 'risk': 9, 'fee': 49},
                {'name': '⚡ ScalpMaster', 'return': 12.8, 'followers': 1850, 'risk': 4, 'fee': 19},
                {'name': '🎯 TrendFollower', 'return': 19.5, 'followers': 1420, 'risk': 7, 'fee': 35}
            ]
        }
    
    # Backtesting system
    if 'backtesting' not in st.session_state:
        st.session_state.backtesting = {
            'results': [],
            'saved_strategies': [
                {
                    'name': 'MA Cross EURUSD',
                    'symbol': 'EURUSD',
                    'timeframe': '1H',
                    'strategy': 'MA Crossover',
                    'parameters': {'fast_ma': 10, 'slow_ma': 20},
                    'total_return': 15.5,
                    'win_rate': 65.2,
                    'max_drawdown': 8.5,
                    'sharpe_ratio': 1.25
                },
                {
                    'name': 'RSI Gold Strategy',
                    'symbol': 'XAUUSD',
                    'timeframe': '15M',
                    'strategy': 'RSI Mean Reversion',
                    'parameters': {'rsi_period': 14, 'oversold': 30, 'overbought': 70},
                    'total_return': 22.8,
                    'win_rate': 58.9,
                    'max_drawdown': 12.3,
                    'sharpe_ratio': 1.45
                }
            ]
        }
    
    # Settings
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'auto_refresh': True,
            'refresh_interval': 3,
            'notifications': {
                'email_alerts': True,
                'push_notifications': True,
                'trade_confirmations': True,
                'price_alerts': True
            },
            'security': {
                'two_factor': False,
                'session_timeout': '30 min',
                'auto_logout': True
            },
            'display': {
                'decimal_places': 4,
                'currency_symbol': '$',
                'date_format': 'DD/MM/YYYY',
                'time_format': '24h'
            }
        }

init_session_state()

# ===== HELPER CLASSES =====
class ArbitrageEngine:
    @staticmethod
    def start_monitoring():
        st.session_state.xauusd_arbitrage['monitoring'] = True
    
    @staticmethod
    def stop_monitoring():
        st.session_state.xauusd_arbitrage['monitoring'] = False
    
    @staticmethod
    def update_prices():
        # Simulate price updates
        base_price = 2655.0
        st.session_state.xauusd_arbitrage['price_feeds']['broker_a']['bid'] = base_price + random.uniform(-2, 2)
        st.session_state.xauusd_arbitrage['price_feeds']['broker_a']['ask'] = st.session_state.xauusd_arbitrage['price_feeds']['broker_a']['bid'] + random.uniform(0.5, 2.0)
        st.session_state.xauusd_arbitrage['price_feeds']['broker_b']['bid'] = base_price + random.uniform(-2, 2)
        st.session_state.xauusd_arbitrage['price_feeds']['broker_b']['ask'] = st.session_state.xauusd_arbitrage['price_feeds']['broker_b']['bid'] + random.uniform(0.5, 2.0)

arbitrage_engine = ArbitrageEngine()

# ===== COMPACT SIDEBAR WITH ALL NAVIGATION =====
with st.sidebar:
    st.markdown("# 🚀 YANTRA")
    
    # Main navigation pages
    main_pages = [
        ("📊", "Dashboard"), ("💹", "Trading Terminal"), ("📈", "Advanced Charts"),
        ("📊", "Tick Charts"), ("🤖", "Auto Trading"), ("👥", "Copy Trading"),
        ("🔄", "Backtesting"), ("🥇", "XAUUSD Arbitrage"), ("🌐", "LP Bridge Manager")
    ]
    
    # Create navigation grid (3 columns)
    for i in range(0, len(main_pages), 3):
        cols = st.columns(3)
        for j, (icon, page) in enumerate(main_pages[i:i+3]):
            if j < len(cols):
                with cols[j]:
                    if st.button(icon, key=f"nav_{page}", help=page, use_container_width=True):
                        st.session_state.page = page
                        st.rerun()
    
    st.markdown("---")
    
    # Quick portfolio stats
    st.markdown("**💰 PORTFOLIO**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Balance", f"${st.session_state.portfolio['balance']:,.0f}")
    with col2:
        pnl = st.session_state.portfolio['equity'] - st.session_state.portfolio['balance']
        st.metric("P&L", f"${pnl:,.0f}")
    
    # Broker status
    st.markdown("**🔗 BROKERS**")
    for name, data in st.session_state.brokers.items():
        status_icon = "🟢" if data['status'] == 'Connected' else "🔴"
        short_name = name.split()[0][:8]  # First word, max 8 chars
        st.markdown(f"{status_icon} {short_name} • {data['positions']} pos")
    
    st.markdown("---")
    
    # Quick settings
    st.markdown("**⚙️ SETTINGS**")
    
    # Theme toggle
    if st.button("🌓 Theme", key="theme_toggle", use_container_width=True):
        st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
        st.rerun()
    
    # Auto refresh toggle
    auto_refresh = st.checkbox("🔄 Auto Refresh", st.session_state.settings['auto_refresh'], key="sidebar_auto_refresh")
    if auto_refresh != st.session_state.settings['auto_refresh']:
        st.session_state.settings['auto_refresh'] = auto_refresh

# ===== MAIN CONTENT AREA - ALL PAGES WITH FULL FEATURES =====

if st.session_state.page == "Dashboard":
    # Portfolio overview header
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Equity", f"${st.session_state.portfolio['equity']:,.0f}", 
                 f"{((st.session_state.portfolio['equity'] / st.session_state.portfolio['balance'] - 1) * 100):+.1f}%")
    
    with col2:
        st.metric("Free Margin", f"${st.session_state.portfolio['equity'] - st.session_state.portfolio['margin']:,.0f}",
                 f"{st.session_state.portfolio['margin_level']:.0f}%")
    
    with col3:
        st.metric("Open Positions", len(st.session_state.portfolio['positions']), 
                 f"+{len([p for p in st.session_state.portfolio['positions'] if p['pnl'] > 0])}")
    
    with col4:
        daily_pnl = sum([p['pnl'] for p in st.session_state.portfolio['positions']])
        st.metric("Daily P&L", f"${daily_pnl:+.2f}", 
                 f"{(daily_pnl / st.session_state.portfolio['balance'] * 100):+.2f}%")
    
    with col5:
        margin_level = (st.session_state.portfolio['equity'] / st.session_state.portfolio['margin']) * 100 if st.session_state.portfolio['margin'] > 0 else 0
        st.metric("Margin Level", f"{margin_level:.0f}%", "Healthy" if margin_level > 200 else "Warning")
    
    # Main dashboard content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Market overview with real-time data
        st.markdown("### 📊 Market Overview")
        
        # Generate market data for major pairs
        market_data = []
        for symbol in st.session_state.mt5_symbols[:8]:  # Top 8 symbols
            if 'USD' in symbol:
                base_price = random.uniform(0.8, 1.5) if symbol != 'USDJPY' else random.uniform(140, 155)
            elif 'XAU' in symbol:
                base_price = random.uniform(2600, 2700)
            else:
                base_price = random.uniform(0.6, 2.0)
            
            change = random.uniform(-1.5, 2.0)
            volume = random.randint(1000, 10000)
            
            market_data.append({
                'Symbol': symbol,
                'Price': base_price,
                'Change': change,
                'Volume': volume
            })
        
        # Create market overview chart
        df_market = pd.DataFrame(market_data)
        
        fig = go.Figure()
        
        # Color bars based on positive/negative change
        colors = ['#10B981' if change > 0 else '#EF4444' for change in df_market['Change']]
        
        fig.add_trace(go.Bar(
            x=df_market['Symbol'],
            y=df_market['Change'],
            marker_color=colors,
            text=[f"{change:+.2f}%" for change in df_market['Change']],
            textposition='outside',
            name='Daily Change %'
        ))
        
        fig.update_layout(
            title="Daily Price Changes - Major Pairs",
            xaxis_title="Symbol",
            yaxis_title="Change %",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Quick trade panel
        st.markdown("### ⚡ Quick Trade")
        
        trade_col1, trade_col2, trade_col3, trade_col4, trade_col5, trade_col6 = st.columns(6)
        
        with trade_col1:
            quick_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols[:10], key="quick_symbol")
        
        with trade_col2:
            quick_volume = st.number_input("Volume", 0.01, 10.0, 1.0, 0.01, key="quick_volume")
        
        with trade_col3:
            quick_broker = st.selectbox("Broker", list(st.session_state.brokers.keys()), key="quick_broker")
        
        with trade_col4:
            if st.button("🟢 BUY", key="quick_buy", use_container_width=True):
                # Add position to portfolio
                new_position = {
                    'id': len(st.session_state.portfolio['positions']) + 1,
                    'symbol': quick_symbol,
                    'type': 'BUY',
                    'volume': quick_volume,
                    'entry_price': random.uniform(1.0, 2.0),
                    'current_price': random.uniform(1.0, 2.0),
                    'pnl': random.uniform(-50, 100),
                    'broker': quick_broker,
                    'open_time': datetime.now()
                }
                st.session_state.portfolio['positions'].append(new_position)
                st.success(f"✅ BUY {quick_volume} {quick_symbol} @ {quick_broker}")
                st.rerun()
        
        with trade_col5:
            if st.button("🔴 SELL", key="quick_sell", use_container_width=True):
                # Add position to portfolio
                new_position = {
                    'id': len(st.session_state.portfolio['positions']) + 1,
                    'symbol': quick_symbol,
                    'type': 'SELL',
                    'volume': quick_volume,
                    'entry_price': random.uniform(1.0, 2.0),
                    'current_price': random.uniform(1.0, 2.0),
                    'pnl': random.uniform(-50, 100),
                    'broker': quick_broker,
                    'open_time': datetime.now()
                }
                st.session_state.portfolio['positions'].append(new_position)
                st.success(f"✅ SELL {quick_volume} {quick_symbol} @ {quick_broker}")
                st.rerun()
        
        with trade_col6:
            if st.button("📊 Chart", key="quick_chart", use_container_width=True):
                st.session_state.page = "Advanced Charts"
                st.rerun()
        
        # Economic calendar
        st.markdown("### 📅 Economic Calendar")
        
        economic_events = [
            {'Time': '09:30', 'Currency': 'USD', 'Event': 'Non-Farm Payrolls', 'Impact': 'High', 'Forecast': '200K', 'Previous': '195K'},
            {'Time': '14:00', 'Currency': 'EUR', 'Event': 'ECB Interest Rate', 'Impact': 'High', 'Forecast': '4.50%', 'Previous': '4.50%'},
            {'Time': '15:30', 'Currency': 'GBP', 'Event': 'GDP Growth Rate', 'Impact': 'Medium', 'Forecast': '0.2%', 'Previous': '0.1%'},
            {'Time': '21:00', 'Currency': 'JPY', 'Event': 'BoJ Policy Meeting', 'Impact': 'High', 'Forecast': '-0.10%', 'Previous': '-0.10%'}
        ]
        
        econ_df = pd.DataFrame(economic_events)
        st.dataframe(econ_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Broker status detailed
        st.markdown("### 🔗 Broker Connections")
        
        for broker_name, broker_data in st.session_state.brokers.items():
            status_color = "#10B981" if broker_data['status'] == 'Connected' else "#EF4444"
            
            st.markdown(f"""
            <div style="background: white; border-left: 4px solid {status_color}; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <strong>{broker_name}</strong><br>
                <span style="color: {status_color};">● {broker_data['status']}</span><br>
                <small>Server: {broker_data.get('server', 'N/A')}</small><br>
                Balance: ${broker_data['balance']:,}<br>
                Equity: ${broker_data.get('equity', broker_data['balance']):,}<br>
                Positions: {broker_data['positions']}<br>
                Ping: {broker_data.get('ping', 0)}ms
            </div>
            """, unsafe_allow_html=True)
        
        # Open positions summary
        st.markdown("### 💼 Open Positions")
        
        if st.session_state.portfolio['positions']:
            for pos in st.session_state.portfolio['positions'][-5:]:  # Show last 5 positions
                pnl_color = "#10B981" if pos['pnl'] > 0 else "#EF4444"
                duration = datetime.now() - pos['open_time']
                duration_str = str(duration).split('.')[0]  # Remove microseconds
                
                st.markdown(f"""
                <div style="background: white; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {pnl_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <strong>{pos['symbol']} {pos['type']}</strong><br>
                    Volume: {pos['volume']}<br>
                    Entry: {pos['entry_price']:.4f}<br>
                    Current: {pos['current_price']:.4f}<br>
                    P&L: <span style="color: {pnl_color}; font-weight: bold;">${pos['pnl']:+.2f}</span><br>
                    <small>Duration: {duration_str}</small><br>
                    <small>Broker: {pos['broker']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No open positions")
        
                # Pending orders
        st.markdown("### 📋 Pending Orders")
        
        if st.session_state.portfolio['pending_orders']:
            for order in st.session_state.portfolio['pending_orders']:
                order_color = "#3B82F6" if 'BUY' in order['type'] else "#F59E0B"
                
                st.markdown(f"""
                <div style="background: white; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {order_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <strong>{order['symbol']} {order['type']}</strong><br>
                    Volume: {order['volume']}<br>
                    Price: {order['price']:.4f}<br>
                    SL: {order.get('sl', 'None')}<br>
                    TP: {order.get('tp', 'None')}<br>
                    <small>Broker: {order['broker']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No pending orders")
        
        # Recent activity feed
        st.markdown("### 📈 Recent Activity")
        
        recent_activities = [
            "🟢 BUY 1.0 EURUSD @ 1.0845 - Divit Capital",
            "🔴 SELL 0.5 GBPUSD @ 1.2650 - Kama Capital", 
            "✅ Closed XAUUSD +$125.50 profit",
            "🤖 Auto trade: RSI signal on USDJPY",
            "📊 Backtest completed: MA Cross strategy",
            "🔄 Arbitrage opportunity detected",
            "👥 Copy trade executed from ProTrader",
            "⚠️ Margin level warning: 150%"
        ]
        
        for activity in recent_activities:
            st.markdown(f"• {activity}")

elif st.session_state.page == "Trading Terminal":
    # Trading terminal header with account info
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Account Balance", f"${st.session_state.portfolio['balance']:,.0f}")
    
    with col2:
        st.metric("Used Margin", f"${st.session_state.portfolio['margin']:,.0f}")
    
    with col3:
        free_margin = st.session_state.portfolio['equity'] - st.session_state.portfolio['margin']
        st.metric("Free Margin", f"${free_margin:,.0f}")
    
    with col4:
        margin_level = (st.session_state.portfolio['equity'] / st.session_state.portfolio['margin']) * 100 if st.session_state.portfolio['margin'] > 0 else 0
        st.metric("Margin Level", f"{margin_level:.0f}%")
    
    with col5:
        total_pnl = sum([pos['pnl'] for pos in st.session_state.portfolio['positions']])
        st.metric("Total P&L", f"${total_pnl:+.2f}")
    
    # Main trading interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Market watch with real-time prices
        st.markdown("### 📊 Market Watch")
        
        # Generate real-time market data
        market_data = []
        for symbol in st.session_state.mt5_symbols[:15]:  # Show top 15 symbols
            if 'USD' in symbol and symbol != 'USDJPY':
                bid = random.uniform(0.8000, 1.5000)
                ask = bid + random.uniform(0.0001, 0.0020)
                spread = (ask - bid) * 10000  # in pips
            elif symbol == 'USDJPY':
                bid = random.uniform(140.00, 155.00)
                ask = bid + random.uniform(0.001, 0.020)
                spread = (ask - bid) * 100  # in pips
            elif 'XAU' in symbol:
                bid = random.uniform(2600.00, 2700.00)
                ask = bid + random.uniform(0.50, 3.00)
                spread = ask - bid
            elif 'BTC' in symbol:
                bid = random.uniform(40000, 50000)
                ask = bid + random.uniform(10, 100)
                spread = ask - bid
            else:
                bid = random.uniform(0.5000, 2.0000)
                ask = bid + random.uniform(0.0001, 0.0020)
                spread = (ask - bid) * 10000
            
            change = random.uniform(-1.0, 1.0)
            
            market_data.append({
                'Symbol': symbol,
                'Bid': f"{bid:.4f}" if 'XAU' not in symbol and 'BTC' not in symbol else f"{bid:.2f}",
                'Ask': f"{ask:.4f}" if 'XAU' not in symbol and 'BTC' not in symbol else f"{ask:.2f}",
                'Spread': f"{spread:.1f}",
                'Change': f"{change:+.2f}%"
            })
        
        market_df = pd.DataFrame(market_data)
        st.dataframe(market_df, use_container_width=True, hide_index=True)
        
        # Advanced order entry panel
        st.markdown("### 📝 Advanced Order Entry")
        
        # Order entry form
        order_col1, order_col2, order_col3, order_col4 = st.columns(4)
        
        with order_col1:
            order_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="order_symbol")
            order_type = st.selectbox("Order Type", ["Market", "Limit", "Stop", "Stop Limit"], key="order_type")
            order_side = st.selectbox("Side", ["BUY", "SELL"], key="order_side")
        
        with order_col2:
            order_volume = st.number_input("Volume", 0.01, 100.0, 1.0, 0.01, key="order_volume")
            
            if order_type != "Market":
                order_price = st.number_input("Price", 0.0001, 10000.0, 1.0000, 0.0001, key="order_price")
            else:
                order_price = None
            
            if order_type == "Stop Limit":
                stop_price = st.number_input("Stop Price", 0.0001, 10000.0, 1.0000, 0.0001, key="stop_price")
        
        with order_col3:
            order_sl = st.number_input("Stop Loss", 0.0, 1000.0, 0.0, 1.0, key="order_sl")
            order_tp = st.number_input("Take Profit", 0.0, 1000.0, 0.0, 1.0, key="order_tp")
            order_comment = st.text_input("Comment", key="order_comment")
        
        with order_col4:
            order_broker = st.selectbox("Broker", list(st.session_state.brokers.keys()), key="order_broker")
            order_expiry = st.selectbox("Expiry", ["GTC", "Today", "1 Hour", "4 Hours"], key="order_expiry")
            
            # Risk calculation
            if order_volume and order_sl:
                risk_amount = order_volume * order_sl * 100000  # Simplified risk calculation
                st.metric("Risk Amount", f"${risk_amount:.2f}")
        
        # Order placement buttons
        place_col1, place_col2, place_col3 = st.columns(3)
        
        with place_col1:
            if st.button("🚀 Place Order", key="place_order", use_container_width=True):
                # Create new order
                new_order = {
                    'id': len(st.session_state.portfolio['pending_orders']) + 100,
                    'symbol': order_symbol,
                    'type': f"{order_side} {order_type}",
                    'volume': order_volume,
                    'price': order_price if order_price else "Market",
                    'sl': order_sl if order_sl > 0 else None,
                    'tp': order_tp if order_tp > 0 else None,
                    'broker': order_broker,
                    'comment': order_comment,
                    'expiry': order_expiry,
                    'timestamp': datetime.now()
                }
                
                if order_type == "Market":
                    # Execute immediately as position
                    new_position = {
                        'id': len(st.session_state.portfolio['positions']) + 1,
                        'symbol': order_symbol,
                        'type': order_side,
                        'volume': order_volume,
                        'entry_price': random.uniform(1.0, 2.0),
                        'current_price': random.uniform(1.0, 2.0),
                        'pnl': random.uniform(-50, 100),
                        'broker': order_broker,
                        'open_time': datetime.now(),
                        'sl': order_sl if order_sl > 0 else None,
                        'tp': order_tp if order_tp > 0 else None
                    }
                    st.session_state.portfolio['positions'].append(new_position)
                    st.success(f"✅ Market {order_side} {order_volume} {order_symbol} executed!")
                else:
                    # Add to pending orders
                    st.session_state.portfolio['pending_orders'].append(new_order)
                    st.success(f"✅ {order_side} {order_type} order placed for {order_volume} {order_symbol}")
                
                st.rerun()
        
        with place_col2:
            if st.button("📊 Chart Analysis", key="chart_analysis", use_container_width=True):
                st.session_state.page = "Advanced Charts"
                st.rerun()
        
        with place_col3:
            if st.button("🔄 Reset Form", key="reset_form", use_container_width=True):
                st.rerun()
        
        # Position management
        st.markdown("### 💼 Position Management")
        
        if st.session_state.portfolio['positions']:
            # Position management table
            positions_data = []
            for pos in st.session_state.portfolio['positions']:
                positions_data.append({
                    'ID': pos['id'],
                    'Symbol': pos['symbol'],
                    'Type': pos['type'],
                    'Volume': pos['volume'],
                    'Entry Price': f"{pos['entry_price']:.4f}",
                    'Current Price': f"{pos['current_price']:.4f}",
                    'P&L': f"${pos['pnl']:+.2f}",
                    'Broker': pos['broker'],
                    'Duration': str(datetime.now() - pos['open_time']).split('.')[0]
                })
            
            positions_df = pd.DataFrame(positions_data)
            st.dataframe(positions_df, use_container_width=True, hide_index=True)
            
            # Position actions
            pos_action_col1, pos_action_col2, pos_action_col3 = st.columns(3)
            
            with pos_action_col1:
                selected_position = st.selectbox(
                    "Select Position",
                    options=[f"{pos['id']} - {pos['symbol']} {pos['type']}" for pos in st.session_state.portfolio['positions']],
                    key="selected_position"
                )
            
            with pos_action_col2:
                if st.button("🔒 Close Position", key="close_position", use_container_width=True):
                    if selected_position:
                        pos_id = int(selected_position.split(' - ')[0])
                        st.session_state.portfolio['positions'] = [
                            p for p in st.session_state.portfolio['positions'] if p['id'] != pos_id
                        ]
                        st.success(f"✅ Position {pos_id} closed!")
                        st.rerun()
            
            with pos_action_col3:
                if st.button("🔄 Close All", key="close_all_positions", use_container_width=True):
                    total_pnl = sum([pos['pnl'] for pos in st.session_state.portfolio['positions']])
                    st.session_state.portfolio['positions'] = []
                    st.success(f"✅ All positions closed! Total P&L: ${total_pnl:+.2f}")
                    st.rerun()
        else:
            st.info("No open positions")
    
    with col2:
        # Order book / Level II data
        st.markdown("### 📊 Order Book")
        
        selected_symbol_ob = st.selectbox("Symbol", st.session_state.mt5_symbols[:5], key="orderbook_symbol")
        
        # Generate sample order book data
        base_price = 1.0850 if 'USD' in selected_symbol_ob else 2650.00
        
        orderbook_data = []
        for i in range(10):
            bid_price = base_price - (i * 0.0001)
            ask_price = base_price + (i * 0.0001)
            bid_volume = random.randint(100, 1000) / 100
            ask_volume = random.randint(100, 1000) / 100
            
            orderbook_data.append({
                'Bid Vol': f"{bid_volume:.2f}",
                'Bid': f"{bid_price:.4f}",
                'Ask': f"{ask_price:.4f}",
                'Ask Vol': f"{ask_volume:.2f}"
            })
        
        orderbook_df = pd.DataFrame(orderbook_data)
        st.dataframe(orderbook_df, use_container_width=True, hide_index=True)
        
        # Trade history
        st.markdown("### 📈 Trade History")
        
        # Generate sample trade history
        trade_history = []
        for i in range(5):
            trade_history.append({
                'Time': (datetime.now() - timedelta(minutes=i*15)).strftime('%H:%M'),
                'Symbol': random.choice(st.session_state.mt5_symbols[:5]),
                'Side': random.choice(['BUY', 'SELL']),
                'Volume': f"{random.uniform(0.1, 2.0):.2f}",
                'Price': f"{random.uniform(1.0800, 1.0900):.4f}",
                'P&L': f"${random.uniform(-50, 150):+.2f}"
            })
        
        trade_df = pd.DataFrame(trade_history)
        st.dataframe(trade_df, use_container_width=True, hide_index=True)
        
        # Account summary
        st.markdown("### 💰 Account Summary")
        
        # Calculate account metrics
        total_volume = sum([pos['volume'] for pos in st.session_state.portfolio['positions']])
        avg_pnl = np.mean([pos['pnl'] for pos in st.session_state.portfolio['positions']]) if st.session_state.portfolio['positions'] else 0
        
        st.metric("Total Volume", f"{total_volume:.2f} lots")
        st.metric("Avg P&L per Position", f"${avg_pnl:.2f}")
        st.metric("Win Rate", "68.5%")  # Sample data
        
        # Risk metrics
        st.markdown("### ⚠️ Risk Metrics")
        
        risk_percentage = (st.session_state.portfolio['margin'] / st.session_state.portfolio['equity']) * 100
        st.metric("Risk Exposure", f"{risk_percentage:.1f}%")
        
        max_drawdown = random.uniform(5, 15)  # Sample data
        st.metric("Max Drawdown", f"{max_drawdown:.1f}%")
        
        var_95 = random.uniform(100, 500)  # Sample data
        st.metric("VaR (95%)", f"${var_95:.0f}")

elif st.session_state.page == "Advanced Charts":
    # Chart controls header
    chart_col1, chart_col2, chart_col3, chart_col4, chart_col5 = st.columns(5)
    
    with chart_col1:
        chart_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="chart_symbol")
    
    with chart_col2:
        timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "30M", "1H", "4H", "1D", "1W"], index=4, key="chart_timeframe")
    
    with chart_col3:
        chart_type = st.selectbox("Chart Type", ["Candlestick", "Line", "OHLC", "Heikin Ashi"], key="chart_type")
    
    with chart_col4:
        period = st.selectbox("Period", ["1D", "1W", "1M", "3M", "6M", "1Y"], index=2, key="chart_period")
    
    with chart_col5:
        if st.button("🔄 Refresh", key="refresh_chart", use_container_width=True):
            st.rerun()
    
    # Generate comprehensive chart data
    periods_map = {"1D": 24, "1W": 168, "1M": 720, "3M": 2160, "6M": 4320, "1Y": 8760}
    num_points = periods_map[period]
    
    # Create date range based on timeframe
    if timeframe in ["1M", "5M", "15M", "30M"]:
        freq = f"{timeframe[:-1]}T"
    elif timeframe in ["1H", "4H"]:
        freq = f"{timeframe[:-1]}H"
    elif timeframe == "1D":
        freq = "D"
    elif timeframe == "1W":
        freq = "W"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=num_points)
    dates = pd.date_range(start=start_date, end=end_date, freq=freq)
    
    # Generate realistic OHLC data
    if 'XAU' in chart_symbol:
        base_price = 2650.0
        volatility = 0.02
    elif 'BTC' in chart_symbol:
        base_price = 45000.0
        volatility = 0.03
    elif chart_symbol == 'USDJPY':
        base_price = 149.50
        volatility = 0.01
    else:
        base_price = 1.0850
        volatility = 0.015
    
    prices = []
    current_price = base_price
    
    for i, date in enumerate(dates):
        # Generate price movement with trend and volatility
        trend = np.sin(i / 50) * 0.001  # Long-term trend
        noise = np.random.normal(0, volatility) * current_price
        
        current_price += (trend * current_price) + noise
        
        # Generate OHLC from current price
        high = current_price + random.uniform(0, 0.005) * current_price
        low = current_price - random.uniform(0, 0.005) * current_price
        open_price = prices[-1]['close'] if prices else current_price
        close = current_price
        
        # Ensure OHLC logic is correct
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        volume = random.randint(100, 2000)
        
        prices.append({
            'datetime': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df_chart = pd.DataFrame(prices)
    
    # Main chart area
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Create main price chart
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.15, 0.15],
            subplot_titles=(f'{chart_symbol} - {timeframe}', 'Volume', 'Indicators')
        )
        
        # Price chart
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=df_chart['datetime'],
                open=df_chart['open'],
                high=df_chart['high'],
                low=df_chart['low'],
                close=df_chart['close'],
                name=chart_symbol,
                increasing_line_color='#10B981',
                decreasing_line_color='#EF4444'
            ), row=1, col=1)
        
        elif chart_type == "Line":
            fig.add_trace(go.Scatter(
                x=df_chart['datetime'],
                y=df_chart['close'],
                mode='lines',
                name=chart_symbol,
                line=dict(color='#3B82F6', width=2)
            ), row=1, col=1)
        
        elif chart_type == "OHLC":
            fig.add_trace(go.Ohlc(
                x=df_chart['datetime'],
                open=df_chart['open'],
                high=df_chart['high'],
                low=df_chart['low'],
                close=df_chart['close'],
                name=chart_symbol
            ), row=1, col=1)
        
        # Volume chart
        colors = ['#10B981' if close >= open else '#EF4444' 
                 for close, open in zip(df_chart['close'], df_chart['open'])]
        
        fig.add_trace(go.Bar(
            x=df_chart['datetime'],
            y=df_chart['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ), row=2, col=1)
        
        # Technical indicators will be added based on user selection
        
        fig.update_layout(
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=700,
            xaxis_rangeslider_visible=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Technical indicators panel
        st.markdown("### 📊 Technical Indicators")
        
        # Moving Averages
        st.markdown("#### Moving Averages")
        show_ma = st.checkbox("Show MA", key="show_ma")
        if show_ma:
            ma_period = st.number_input("MA Period", 1, 200, 20, key="ma_period")
            ma_type = st.selectbox("MA Type", ["SMA", "EMA"], key="ma_type")
            
            if ma_type == "SMA":
                df_chart['ma'] = df_chart['close'].rolling(window=ma_period).mean()
            else:  # EMA
                df_chart['ma'] = df_chart['close'].ewm(span=ma_period).mean()
            
            fig.add_trace(go.Scatter(
                x=df_chart['datetime'],
                y=df_chart['ma'],
                mode='lines',
                name=f'{ma_type}({ma_period})',
                line=dict(color='#F59E0B', width=2)
            ), row=1, col=1)
        
        # Bollinger Bands
        show_bb = st.checkbox("Bollinger Bands", key="show_bb")
        if show_bb:
            bb_period = st.number_input("BB Period", 1, 50, 20, key="bb_period")
            bb_std = st.number_input("Standard Deviation", 1.0, 3.0, 2.0, 0.1, key="bb_std")
            
            df_chart['bb_middle'] = df_chart['close'].rolling(window=bb_period).mean()
            df_chart['bb_std'] = df_chart['close'].rolling(window=bb_period).std()
            df_chart['bb_upper'] = df_chart['bb_middle'] + (df_chart['bb_std'] * bb_std)
            df_chart['bb_lower'] = df_chart['bb_middle'] - (df_chart['bb_std'] * bb_std)
            
            fig.add_trace(go.Scatter(
                x=df_chart['datetime'], y=df_chart['bb_upper'],
                mode='lines', name='BB Upper',
                line=dict(color='#EF4444', width=1, dash='dash')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df_chart['datetime'], y=df_chart['bb_lower'],
                mode='lines', name='BB Lower',
                line=dict(color='#EF4444', width=1, dash='dash'),
                fill='tonexty', fillcolor='rgba(239, 68, 68, 0.1)'
            ), row=1, col=1)
        
        # RSI
        show_rsi = st.checkbox("RSI", key="show_rsi")
        if show_rsi:
            rsi_period = st.number_input("RSI Period", 1, 50, 14, key="rsi_period")
            
            # Calculate RSI
            delta = df_chart['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
            rs = gain / loss
            df_chart['rsi'] = 100 - (100 / (1 + rs))
            
            fig.add_trace(go.Scatter(
                x=df_chart['datetime'],
                y=df_chart['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='#8B5CF6', width=2)
            ), row=3, col=1)
            
            # RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        # MACD
        show_macd = st.checkbox("MACD", key="show_macd")
        if show_macd:
            fast_period = st.number_input("Fast Period", 1, 50, 12, key="macd_fast")
            slow_period = st.number_input("Slow Period", 1, 100, 26, key="macd_slow")
            signal_period = st.number_input("Signal Period", 1, 20, 9, key="macd_signal")
            
            # Calculate MACD
            ema_fast = df_chart['close'].ewm(span=fast_period).mean()
            ema_slow = df_chart['close'].ewm(span=slow_period).mean()
            df_chart['macd'] = ema_fast - ema_slow
            df_chart['macd_signal'] = df_chart['macd'].ewm(span=signal_period).mean()
            df_chart['macd_histogram'] = df_chart['macd'] - df_chart['macd_signal']
            
            fig.add_trace(go.Scatter(
                x=df_chart['datetime'], y=df_chart['macd'],
                mode='lines', name='MACD', line=dict(color='#3B82F6', width=2)
            ), row=3, col=1)
            
            fig.add_trace(go.Scatter(
                x=df_chart['datetime'], y=df_chart['macd_signal'],
                mode='lines', name='Signal', line=dict(color='#F59E0B', width=2)
            ), row=3, col=1)
        
        # Drawing tools
        st.markdown("#### 🎨 Drawing Tools")
        
        drawing_tool = st.selectbox("Tool", ["None", "Trend Line", "Support/Resistance", "Fibonacci"], key="drawing_tool")
        
        if drawing_tool != "None":
            st.info(f"Selected: {drawing_tool}")
            st.markdown("*Click on chart to draw*")
        
        # Chart settings
        st.markdown("#### ⚙️ Chart Settings")
        
        show_grid = st.checkbox("Show Grid", True, key="show_grid")
        show_crosshair = st.checkbox("Crosshair", True, key="show_crosshair")
        
        # Update chart with new indicators
        st.plotly_chart(fig, use_container_width=True, key="updated_chart")

elif st.session_state.page == "Tick Charts":
    st.markdown("### 📊 Real-Time Tick Charts")
    
    # Tick chart controls
    tick_col1, tick_col2, tick_col3, tick_col4 = st.columns(4)
    
    with tick_col1:
        tick_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols[:10], key="tick_symbol")
    
    with tick_col2:
        tick_count = st.selectbox("Tick Count", [100, 500, 1000, 2000], index=1, key="tick_count")
    
    with tick_col3:
        auto_scroll = st.checkbox("Auto Scroll", True, key="auto_scroll")
    
    with tick_col4:
        if st.button("🔄 Reset", key="reset_ticks", use_container_width=True):
            st.rerun()
    
    # Generate tick data
    tick_data = []
    base_price = 1.0850 if 'USD' in tick_symbol else 2650.0
    current_price = base_price
    
    for i in range(tick_count):
        # Simulate tick movement
        change = random.uniform(-0.0005, 0.0005) * current_price
        current_price += change
        
        tick_data.append({
            'time': datetime.now() - timedelta(seconds=tick_count-i),
            'bid': current_price - random.uniform(0.0001, 0.0003) * current_price,
            'ask': current_price + random.uniform(0.0001, 0.0003) * current_price,
            'volume': random.randint(1, 10)
        })
    
    tick_df = pd.DataFrame(tick_data)
    
    # Create tick chart
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.8, 0.2],
            subplot_titles=(f'{tick_symbol} - Tick Chart', 'Volume')
    )
    
    # Tick price chart
    fig.add_trace(go.Scatter(
        x=tick_df['time'],
        y=tick_df['bid'],
        mode='lines',
        name='Bid',
        line=dict(color='#EF4444', width=1)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=tick_df['time'],
        y=tick_df['ask'],
        mode='lines',
        name='Ask',
        line=dict(color='#10B981', width=1)
    ), row=1, col=1)
    
    # Volume bars
    fig.add_trace(go.Bar(
        x=tick_df['time'],
        y=tick_df['volume'],
        name='Volume',
        marker_color='#3B82F6',
        opacity=0.7
    ), row=2, col=1)
    
    fig.update_layout(
        template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tick statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_spread = (tick_df['ask'] - tick_df['bid']).mean()
        st.metric("Avg Spread", f"{avg_spread:.5f}")
    
    with col2:
        total_volume = tick_df['volume'].sum()
        st.metric("Total Volume", f"{total_volume}")
    
    with col3:
        price_range = tick_df['ask'].max() - tick_df['bid'].min()
        st.metric("Price Range", f"{price_range:.5f}")
    
    with col4:
        tick_frequency = len(tick_df) / (tick_df['time'].max() - tick_df['time'].min()).total_seconds()
        st.metric("Tick Frequency", f"{tick_frequency:.1f}/sec")

elif st.session_state.page == "Auto Trading":
    # Auto trading header
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        auto_enabled = st.session_state.auto_trading['enabled']
        status_text = "🟢 ACTIVE" if auto_enabled else "🔴 INACTIVE"
        st.markdown(f"**Auto Trading:** {status_text}")
    
    with col2:
        st.metric("Trades Today", st.session_state.auto_trading['trades_today'])
    
    with col3:
        st.metric("Profit Today", f"${st.session_state.auto_trading['profit_today']:.2f}")
    
    with col4:
        total_strategies = len(st.session_state.auto_trading['strategies'])
        active_strategies = len([s for s in st.session_state.auto_trading['strategies'] if s['enabled']])
        st.metric("Active Strategies", f"{active_strategies}/{total_strategies}")
    
    with col5:
        if auto_enabled:
            if st.button("⏸️ Stop All", key="stop_auto", use_container_width=True):
                st.session_state.auto_trading['enabled'] = False
                st.rerun()
        else:
            if st.button("🚀 Start All", key="start_auto", use_container_width=True):
                st.session_state.auto_trading['enabled'] = True
                st.rerun()
    
    # Strategy management
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🤖 Strategy Management")
        
        # Strategy list
        for i, strategy in enumerate(st.session_state.auto_trading['strategies']):
            with st.expander(f"📊 {strategy['name']} - {'🟢 Active' if strategy['enabled'] else '🔴 Inactive'}"):
                strat_col1, strat_col2, strat_col3 = st.columns(3)
                
                with strat_col1:
                    st.markdown(f"**Type:** {strategy['type']}")
                    st.markdown(f"**Symbols:** {', '.join(strategy['symbols'])}")
                    st.markdown(f"**Timeframe:** {strategy['timeframe']}")
                    st.markdown(f"**Risk per Trade:** {strategy['risk_per_trade']}%")
                
                with strat_col2:
                    st.metric("Trades Today", strategy['trades_today'])
                    st.metric("Profit Today", f"${strategy['profit_today']:.2f}")
                    st.metric("Win Rate", f"{strategy['win_rate']:.1f}%")
                
                with strat_col3:
                    st.metric("Total P&L", f"${strategy['total_pnl']:.2f}")
                    
                    # Strategy controls
                    if strategy['enabled']:
                        if st.button("⏸️ Stop", key=f"stop_strategy_{i}", use_container_width=True):
                            st.session_state.auto_trading['strategies'][i]['enabled'] = False
                            st.rerun()
                    else:
                        if st.button("🚀 Start", key=f"start_strategy_{i}", use_container_width=True):
                            st.session_state.auto_trading['strategies'][i]['enabled'] = True
                            st.rerun()
                    
                    if st.button("⚙️ Edit", key=f"edit_strategy_{i}", use_container_width=True):
                        st.info("Strategy editor would open here")
                    
                    if st.button("🗑️ Delete", key=f"delete_strategy_{i}", use_container_width=True):
                        st.session_state.auto_trading['strategies'].pop(i)
                        st.rerun()
        
        # Add new strategy
        st.markdown("### ➕ Create New Strategy")
        
        new_strat_col1, new_strat_col2, new_strat_col3 = st.columns(3)
        
        with new_strat_col1:
            new_strategy_name = st.text_input("Strategy Name", key="new_strategy_name")
            new_strategy_type = st.selectbox("Strategy Type", 
                ["MA Crossover", "RSI Mean Reversion", "Bollinger Bands", "MACD", "Custom"], 
                key="new_strategy_type")
            new_symbols = st.multiselect("Symbols", st.session_state.mt5_symbols, 
                default=['EURUSD'], key="new_symbols")
        
        with new_strat_col2:
            new_timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "30M", "1H", "4H"], 
                index=2, key="new_timeframe")
            new_risk = st.slider("Risk per Trade (%)", 0.1, 10.0, 2.0, 0.1, key="new_risk")
            new_max_trades = st.number_input("Max Trades/Day", 1, 100, 10, key="new_max_trades")
        
        with new_strat_col3:
            # Strategy-specific parameters
            if new_strategy_type == "MA Crossover":
                fast_ma = st.number_input("Fast MA", 1, 100, 10, key="new_fast_ma")
                slow_ma = st.number_input("Slow MA", 1, 200, 20, key="new_slow_ma")
            elif new_strategy_type == "RSI Mean Reversion":
                rsi_period = st.number_input("RSI Period", 1, 50, 14, key="new_rsi_period")
                oversold = st.number_input("Oversold", 1, 50, 30, key="new_oversold")
                overbought = st.number_input("Overbought", 50, 99, 70, key="new_overbought")
            
            stop_loss = st.number_input("Stop Loss (pips)", 1, 1000, 50, key="new_sl")
            take_profit = st.number_input("Take Profit (pips)", 1, 1000, 100, key="new_tp")
        
        if st.button("🚀 Create Strategy", key="create_strategy", use_container_width=True):
            if new_strategy_name and new_symbols:
                new_strategy = {
                    'name': new_strategy_name,
                    'type': new_strategy_type,
                    'symbols': new_symbols,
                    'timeframe': new_timeframe,
                    'risk_per_trade': new_risk,
                    'enabled': False,
                    'trades_today': 0,
                    'profit_today': 0.0,
                    'win_rate': 0.0,
                    'total_pnl': 0.0
                }
                st.session_state.auto_trading['strategies'].append(new_strategy)
                st.success(f"✅ Strategy '{new_strategy_name}' created!")
                st.rerun()
            else:
                st.error("Please fill in strategy name and select symbols")
    
    with col2:
        # Performance monitoring
        st.markdown("### 📊 Performance Monitor")
        
        # Equity curve
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
        equity_values = []
        current_equity = 10000
        
        for date in dates:
            daily_return = np.random.normal(0.002, 0.015)  # 0.2% daily return with 1.5% volatility
            current_equity *= (1 + daily_return)
            equity_values.append(current_equity)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity_values,
            mode='lines',
            name='Auto Trading Equity',
            line=dict(color='#10B981', width=3),
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))
        
        fig.update_layout(
            title="30-Day Auto Trading Performance",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics
        st.markdown("### 📈 Key Metrics")
        
        total_return = ((equity_values[-1] / equity_values[0]) - 1) * 100
        st.metric("30-Day Return", f"{total_return:+.2f}%")
        
        max_equity = max(equity_values)
        current_equity = equity_values[-1]
        drawdown = ((current_equity / max_equity) - 1) * 100
        st.metric("Current Drawdown", f"{drawdown:.2f}%")
        
        # Calculate Sharpe ratio (simplified)
        returns = np.diff(equity_values) / equity_values[:-1]
        sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
        st.metric("Sharpe Ratio", f"{sharpe:.2f}")
        
        # Risk metrics
        st.markdown("### ⚠️ Risk Management")
        
        st.metric("Max Daily Loss", f"${st.session_state.auto_trading.get('max_daily_loss', 500):.0f}")
        st.metric("Max Positions", st.session_state.auto_trading.get('max_positions', 10))
        st.metric("Max Risk per Trade", f"{st.session_state.auto_trading['risk_per_trade']:.1f}%")
        
        # Global settings
        st.markdown("### ⚙️ Global Settings")
        
        max_daily_trades = st.number_input("Max Daily Trades", 1, 1000, 
            st.session_state.auto_trading['max_trades'], key="global_max_trades")
        
        global_risk = st.slider("Global Risk per Trade (%)", 0.1, 10.0, 
            st.session_state.auto_trading['risk_per_trade'], 0.1, key="global_risk")
        
        emergency_stop = st.checkbox("Emergency Stop at -5%", True, key="emergency_stop")
        
        if st.button("💾 Save Settings", key="save_auto_settings", use_container_width=True):
            st.session_state.auto_trading['max_trades'] = max_daily_trades
            st.session_state.auto_trading['risk_per_trade'] = global_risk
            st.success("✅ Settings saved!")

elif st.session_state.page == "Copy Trading":
    st.markdown("### 👥 Copy Trading Platform")
    
    # Copy trading overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_subs = len(st.session_state.copy_trading['subscriptions'])
        st.metric("Active Subscriptions", active_subs)
    
    with col2:
        total_monthly_fees = sum([sub['monthly_fee'] for sub in st.session_state.copy_trading['subscriptions']])
        st.metric("Monthly Fees", f"${total_monthly_fees}")
    
    with col3:
        total_profit = sum([sub['profit_this_month'] for sub in st.session_state.copy_trading['subscriptions']])
        st.metric("This Month Profit", f"${total_profit:.2f}")
    
    with col4:
        total_trades = sum([sub['trades_copied'] for sub in st.session_state.copy_trading['subscriptions']])
        st.metric("Trades Copied", total_trades)
    
    # Main copy trading interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🏆 Signal Providers")
        
        # Available providers
        for provider in st.session_state.copy_trading['available_providers']:
            with st.container():
                prov_col1, prov_col2, prov_col3, prov_col4, prov_col5 = st.columns(5)
                
                with prov_col1:
                    st.markdown(f"**{provider['name']}**")
                    risk_color = "#10B981" if provider['risk'] <= 5 else "#F59E0B" if provider['risk'] <= 7 else "#EF4444"
                    st.markdown(f"<span style='color: {risk_color};'>Risk: {provider['risk']}/10</span>", unsafe_allow_html=True)
                
                with prov_col2:
                    return_color = "#10B981" if provider['return'] > 0 else "#EF4444"
                    st.metric("Monthly Return", f"{provider['return']:+.1f}%")
                
                with prov_col3:
                    st.metric("Followers", f"{provider['followers']:,}")
                
                with prov_col4:
                    st.metric("Monthly Fee", f"${provider['fee']}")
                
                with prov_col5:
                    # Check if already subscribed
                    is_subscribed = any(sub['provider'] == provider['name'] for sub in st.session_state.copy_trading['subscriptions'])
                    
                    if is_subscribed:
                        if st.button("✅ Subscribed", key=f"unsub_{provider['name']}", use_container_width=True):
                            # Unsubscribe
                            st.session_state.copy_trading['subscriptions'] = [
                                sub for sub in st.session_state.copy_trading['subscriptions'] 
                                if sub['provider'] != provider['name']
                            ]
                            st.success(f"Unsubscribed from {provider['name']}")
                            st.rerun()
                    else:
                        if st.button("📋 Subscribe", key=f"sub_{provider['name']}", use_container_width=True):
                            # Subscribe
                            new_subscription = {
                                'provider': provider['name'],
                                'status': 'Active',
                                'monthly_return': provider['return'],
                                'followers': provider['followers'],
                                'risk_score': provider['risk'],
                                'monthly_fee': provider['fee'],
                                'copy_ratio': 0.1,
                                'trades_copied': 0,
                                'profit_this_month': 0.0
                            }
                            st.session_state.copy_trading['subscriptions'].append(new_subscription)
                            st.success(f"✅ Subscribed to {provider['name']}!")
                            st.rerun()
                
                st.markdown("---")
        
        # Subscription management
        st.markdown("### ⚙️ Manage Subscriptions")
        
        if st.session_state.copy_trading['subscriptions']:
            for i, subscription in enumerate(st.session_state.copy_trading['subscriptions']):
                with st.expander(f"📊 {subscription['provider']} - {subscription['status']}"):
                    sub_col1, sub_col2, sub_col3 = st.columns(3)
                    
                    with sub_col1:
                        st.markdown(f"**Provider:** {subscription['provider']}")
                        st.markdown(f"**Status:** {subscription['status']}")
                        st.markdown(f"**Risk Score:** {subscription['risk_score']}/10")
                        st.markdown(f"**Monthly Fee:** ${subscription['monthly_fee']}")
                    
                    with sub_col2:
                        st.metric("Monthly Return", f"{subscription['monthly_return']:+.1f}%")
                        st.metric("Trades Copied", subscription['trades_copied'])
                        st.metric("Profit This Month", f"${subscription['profit_this_month']:+.2f}")
                    
                    with sub_col3:
                        # Copy settings
                        new_copy_ratio = st.slider(
                            "Copy Ratio", 0.01, 1.0, subscription['copy_ratio'], 0.01,
                            key=f"copy_ratio_{i}"
                        )
                        
                        max_copy_amount = st.number_input(
                            "Max Copy Amount", 100, 10000, 1000,
                            key=f"max_copy_{i}"
                        )
                        
                        copy_sl = st.checkbox("Copy Stop Loss", True, key=f"copy_sl_{i}")
                        copy_tp = st.checkbox("Copy Take Profit", True, key=f"copy_tp_{i}")
                        
                        if st.button("💾 Update Settings", key=f"update_sub_{i}", use_container_width=True):
                            st.session_state.copy_trading['subscriptions'][i]['copy_ratio'] = new_copy_ratio
                            st.success("Settings updated!")
                        
                        if st.button("🗑️ Unsubscribe", key=f"delete_sub_{i}", use_container_width=True):
                            st.session_state.copy_trading['subscriptions'].pop(i)
                            st.success("Unsubscribed!")
                            st.rerun()
        else:
            st.info("No active subscriptions")
    
    with col2:
        # Copy trading performance
        st.markdown("### 📊 Copy Trading Performance")
        
        if st.session_state.copy_trading['subscriptions']:
            # Performance chart
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
            
            fig = go.Figure()
            
            for subscription in st.session_state.copy_trading['subscriptions']:
                # Generate sample performance data
                performance = []
                current_value = 1000
                
                for date in dates:
                    daily_return = np.random.normal(subscription['monthly_return']/30/100, 0.02)
                    current_value *= (1 + daily_return)
                    performance.append(current_value)
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=performance,
                    mode='lines',
                    name=subscription['provider'].split()[0],  # Short name
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="Copy Trading Performance (30 Days)",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent copy trades
        st.markdown("### 📈 Recent Copy Trades")
        
        recent_copy_trades = [
            {'Time': '14:30', 'Provider': 'ProTrader', 'Symbol': 'EURUSD', 'Type': 'BUY', 'Volume': '0.10', 'P&L': '+$12.50'},
            {'Time': '13:45', 'Provider': 'GoldMaster', 'Symbol': 'XAUUSD', 'Type': 'SELL', 'Volume': '0.05', 'P&L': '+$25.00'},
            {'Time': '12:15', 'Provider': 'ForexKing', 'Symbol': 'GBPUSD', 'Type': 'BUY', 'Volume': '0.15', 'P&L': '-$8.75'},
            {'Time': '11:30', 'Provider': 'ProTrader', 'Symbol': 'USDJPY', 'Type': 'SELL', 'Volume': '0.20', 'P&L': '+$18.25'}
        ]
        
        copy_trades_df = pd.DataFrame(recent_copy_trades)
        st.dataframe(copy_trades_df, use_container_width=True, hide_index=True)
        
        # Copy trading settings
        st.markdown("### ⚙️ Global Copy Settings")
        
        max_copy_exposure = st.number_input("Max Copy Exposure", 1000, 50000, 10000, key="max_copy_exposure")
        copy_delay = st.selectbox("Copy Delay", ["Instant", "1 second", "5 seconds"], key="copy_delay")
        auto_close = st.checkbox("Auto Close on Provider Close", True, key="auto_close")
        
        if st.button("💾 Save Copy Settings", key="save_copy_settings", use_container_width=True):
            st.success("✅ Copy settings saved!")

elif st.session_state.page == "Backtesting":
    st.markdown("### 🔄 Strategy Backtesting Engine")
    
    # Backtest configuration
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📋 Backtest Configuration")
        
        config_col1, config_col2, config_col3 = st.columns(3)
        
        with config_col1:
            backtest_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="backtest_symbol")
            timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "30M", "1H", "4H", "1D"], index=4, key="backtest_timeframe")
            initial_balance = st.number_input("Initial Balance", 1000, 1000000, 10000, key="backtest_balance")
        
        with config_col2:
            start_date = st.date_input("Start Date", datetime(2023, 1, 1), key="backtest_start")
            end_date = st.date_input("End Date", datetime(2024, 12, 31), key="backtest_end")
            commission = st.number_input("Commission per Trade", 0.0, 100.0, 7.0, 0.1, key="backtest_commission")
        
        with config_col3:
            strategy_type = st.selectbox("Strategy", ["MA Crossover", "RSI Mean Reversion", "Bollinger Bands", "MACD", "Custom"], key="backtest_strategy")
            position_size = st.selectbox("Position Sizing", ["Fixed", "% of Balance", "Kelly Criterion"], key="position_sizing")
            max_positions = st.number_input("Max Concurrent Positions", 1, 20, 5, key="max_positions")
        
        # Strategy parameters
        st.markdown("#### 🎯 Strategy Parameters")
        
        param_col1, param_col2, param_col3 = st.columns(3)
        
        with param_col1:
            if strategy_type == "MA Crossover":
                fast_ma = st.number_input("Fast MA Period", 1, 100, 10, key="backtest_fast_ma")
                slow_ma = st.number_input("Slow MA Period", 1, 200, 20, key="backtest_slow_ma")
                ma_type = st.selectbox("MA Type", ["SMA", "EMA"], key="backtest_ma_type")
            
            elif strategy_type == "RSI Mean Reversion":
                rsi_period = st.number_input("RSI Period", 1, 50, 14, key="backtest_rsi_period")
                oversold = st.number_input("Oversold Level", 1, 50, 30, key="backtest_oversold")
                overbought = st.number_input("Overbought Level", 50, 99, 70, key="backtest_overbought")
            
            elif strategy_type == "Bollinger Bands":
                bb_period = st.number_input("BB Period", 1, 50, 20, key="backtest_bb_period")
                bb_std = st.number_input("Standard Deviation", 1.0, 3.0, 2.0, 0.1, key="backtest_bb_std")
        
        with param_col2:
            stop_loss = st.number_input("Stop Loss (pips)", 0, 1000, 50, key="backtest_sl")
            take_profit = st.number_input("Take Profit (pips)", 0, 1000, 100, key="backtest_tp")
            trailing_stop = st.checkbox("Trailing Stop", key="backtest_trailing")
            
            if trailing_stop:
                trailing_distance = st.number_input("Trailing Distance (pips)", 1, 100, 20, key="trailing_distance")
        
        with param_col3:
            risk_per_trade = st.slider("Risk per Trade (%)", 0.1, 10.0, 2.0, 0.1, key="backtest_risk")
            slippage = st.number_input("Slippage (pips)", 0.0, 10.0, 1.0, 0.1, key="backtest_slippage")
            
            # Advanced options
            use_spread = st.checkbox("Include Spread", True, key="use_spread")
            use_swap = st.checkbox("Include Swap", False, key="use_swap")
        
        # Run backtest button
        if st.button("🚀 Run Backtest", key="run_backtest", use_container_width=True):
            with st.spinner("Running backtest... This may take a few moments."):
                # Simulate backtest processing
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)  # Simulate processing time
                    progress_bar.progress(i + 1)
                
                # Generate realistic backtest results
                num_trades = random.randint(50, 300)
                win_rate = random.uniform(45, 75)
                total_return = random.uniform(-20, 60)
                max_drawdown = random.uniform(5, 30)
                profit_factor = random.uniform(0.8, 2.5)
                sharpe_ratio = random.uniform(-0.5, 2.0)
                
                # Store results
                backtest_results = {
                    'symbol': backtest_symbol,
                    'timeframe': timeframe,
                    'strategy': strategy_type,
                    'start_date': start_date,
                    'end_date': end_date,
                    'initial_balance': initial_balance,
                    'final_balance': initial_balance * (1 + total_return/100),
                    'total_return': total_return,
                    'num_trades': num_trades,
                    'win_rate': win_rate,
                    'max_drawdown': max_drawdown,
                    'profit_factor': profit_factor,
                    'sharpe_ratio': sharpe_ratio,
                    'avg_trade': (initial_balance * total_return/100) / num_trades if num_trades > 0 else 0,
                    'best_trade': random.uniform(50, 500),
                    'worst_trade': random.uniform(-200, -50),
                    'avg_trade_duration': random.uniform(2, 48),  # hours
                    'commission_paid': num_trades * commission
                }
                
                st.session_state.backtesting['results'].append(backtest_results)
                
                st.success("✅ Backtest completed successfully!")
                st.rerun()
    
    with col2:
        # Saved strategies
        st.markdown("#### 💾 Saved Strategies")
        
        if st.session_state.backtesting['saved_strategies']:
            for i, strategy in enumerate(st.session_state.backtesting['saved_strategies']):
                with st.expander(f"📊 {strategy['name']}"):
                    st.markdown(f"**Symbol:** {strategy['symbol']}")
                    st.markdown(f"**Timeframe:** {strategy['timeframe']}")
                    st.markdown(f"**Strategy:** {strategy['strategy']}")
                    
                    st.metric("Total Return", f"{strategy['total_return']:+.1f}%")
                    st.metric("Win Rate", f"{strategy['win_rate']:.1f}%")
                    st.metric("Max Drawdown", f"{strategy['max_drawdown']:.1f}%")
                    
                    if st.button("🔄 Re-run", key=f"rerun_strategy_{i}", use_container_width=True):
                        st.info("Re-running strategy...")
                    
                    if st.button("🗑️ Delete", key=f"delete_strategy_{i}", use_container_width=True):
                        st.session_state.backtesting['saved_strategies'].pop(i)
                        st.rerun()
        else:
            st.info("No saved strategies")
        
       # Quick strategy templates
st.markdown("#### 🎯 Quick Templates")

templates = [
    "Golden Cross (50/200 MA)",
    "RSI Divergence", 
    "Bollinger Squeeze",
    "MACD Signal",
    "Support/Resistance"
]

for template in templates:
    if st.button(f"📋 {template}", key=f"template_{template}", use_container_width=True):
        st.info(f"Loading {template} template...")
    
    # Backtest results display
    if st.session_state.backtesting['results']:
        st.markdown("### 📊 Backtest Results")
        
        # Get latest results
        latest_result = st.session_state.backtesting['results'][-1]
        
        # Results overview
        result_col1, result_col2, result_col3, result_col4, result_col5 = st.columns(5)
        
        with result_col1:
            st.metric("Total Return", f"{latest_result['total_return']:+.2f}%")
        
        with result_col2:
            st.metric("Win Rate", f"{latest_result['win_rate']:.1f}%")
        
        with result_col3:
            st.metric("Total Trades", latest_result['num_trades'])
        
        with result_col4:
            st.metric("Profit Factor", f"{latest_result['profit_factor']:.2f}")
        
        with result_col5:
            st.metric("Sharpe Ratio", f"{latest_result['sharpe_ratio']:.2f}")
        
        # Detailed results
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown("#### 💰 Performance Metrics")
            
            st.metric("Initial Balance", f"${latest_result['initial_balance']:,.0f}")
            st.metric("Final Balance", f"${latest_result['final_balance']:,.0f}")
            st.metric("Net Profit", f"${latest_result['final_balance'] - latest_result['initial_balance']:+,.0f}")
            st.metric("Max Drawdown", f"{latest_result['max_drawdown']:.2f}%")
            st.metric("Average Trade", f"${latest_result['avg_trade']:+.2f}")
            st.metric("Best Trade", f"${latest_result['best_trade']:+.2f}")
            st.metric("Worst Trade", f"${latest_result['worst_trade']:+.2f}")
        
        with detail_col2:
            st.markdown("#### 📈 Trade Statistics")
            
            winning_trades = int(latest_result['num_trades'] * latest_result['win_rate'] / 100)
            losing_trades = latest_result['num_trades'] - winning_trades
            
            st.metric("Winning Trades", winning_trades)
            st.metric("Losing Trades", losing_trades)
            st.metric("Avg Trade Duration", f"{latest_result['avg_trade_duration']:.1f} hours")
            st.metric("Commission Paid", f"${latest_result['commission_paid']:.2f}")
            
            # Calculate additional metrics
            expectancy = (latest_result['win_rate']/100 * latest_result['best_trade']) + ((100-latest_result['win_rate'])/100 * latest_result['worst_trade'])
            st.metric("Expectancy", f"${expectancy:.2f}")
        
        # Equity curve
        st.markdown("#### 📊 Equity Curve")
        
        # Generate equity curve data
        dates = pd.date_range(start=latest_result['start_date'], end=latest_result['end_date'], periods=latest_result['num_trades'])
        equity_values = [latest_result['initial_balance']]
        
        for i in range(latest_result['num_trades']):
            # Simulate trade result
            if random.random() < latest_result['win_rate']/100:
                # Winning trade
                profit = random.uniform(10, latest_result['best_trade'])
            else:
                # Losing trade
                profit = random.uniform(latest_result['worst_trade'], -10)
            
            equity_values.append(equity_values[-1] + profit)
        
        # Add final date
        dates = list(dates) + [latest_result['end_date']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity_values,
            mode='lines',
            name='Equity',
            line=dict(color='#10B981', width=3),
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))
        
        # Add drawdown
        peak = equity_values[0]
        drawdown = []
        for value in equity_values:
            if value > peak:
                peak = value
            dd = ((value - peak) / peak) * 100
            drawdown.append(dd)
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=drawdown,
            mode='lines',
            name='Drawdown %',
            line=dict(color='#EF4444', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=f"Backtest Results: {latest_result['symbol']} - {latest_result['strategy']}",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=400,
            yaxis=dict(title="Equity ($)"),
            yaxis2=dict(title="Drawdown (%)", overlaying='y', side='right'),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Save strategy option
save_col1, save_col2 = st.columns(2)

with save_col1:
    strategy_name = st.text_input("Strategy Name", f"{latest_result['strategy']} {latest_result['symbol']}", key="save_strategy_name")

with save_col2:
    if st.button("💾 Save Strategy", key="save_strategy", use_container_width=True):
        if strategy_name:
            saved_strategy = {
                'name': strategy_name,
                'symbol': latest_result['symbol'],
                'timeframe': latest_result['timeframe'],
                'strategy': latest_result['strategy'],
                'parameters': {},  # Would store actual parameters
                'total_return': latest_result['total_return'],
                'win_rate': latest_result['win_rate'],
                'max_drawdown': latest_result['max_drawdown'],
                'sharpe_ratio': latest_result['sharpe_ratio']
            }
            st.session_state.backtesting['saved_strategies'].append(saved_strategy)
            st.success(f"✅ Strategy '{strategy_name}' saved!")
        else:
            st.error("Please enter a strategy name")

# This should be an if statement, not elif
if st.session_state.page == "XAUUSD Arbitrage":
    st.markdown("### 🥇 XAUUSD Arbitrage Engine")
    
    # Arbitrage status header
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        monitoring = st.session_state.xauusd_arbitrage['monitoring']
        status_text = "🟢 MONITORING" if monitoring else "🔴 STOPPED"
        st.markdown(f"**Status:** {status_text}")
    
    with col2:
        st.metric("Today P&L", f"${st.session_state.xauusd_arbitrage['stats']['today_pnl']:+.2f}")
    
    with col3:
        st.metric("Total P&L", f"${st.session_state.xauusd_arbitrage['stats']['total_pnl']:+.2f}")
    
    with col4:
        st.metric("Success Rate", f"{st.session_state.xauusd_arbitrage['stats']['success_rate']:.1f}%")
    
    with col5:
        if monitoring:
            if st.button("⏸️ Stop Monitoring", key="stop_arbitrage", use_container_width=True):
                arbitrage_engine.stop_monitoring()
                st.rerun()
        else:
            if st.button("🚀 Start Monitoring", key="start_arbitrage", use_container_width=True):
                arbitrage_engine.start_monitoring()
                st.rerun()
    
    # Main arbitrage interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Price feeds comparison
        st.markdown("### 📊 Real-Time Price Feeds")
        
        # Update prices if monitoring
        if monitoring:
            arbitrage_engine.update_prices()
        
        price_feeds = st.session_state.xauusd_arbitrage['price_feeds']
        
        # Price comparison table
        price_data = []
        for broker_key, feed in price_feeds.items():
            spread = feed['ask'] - feed['bid']
            price_data.append({
                'Broker': feed['name'],
                'Bid': f"{feed['bid']:.2f}",
                'Ask': f"{feed['ask']:.2f}",
                'Spread': f"{spread:.2f}",
                'Latency': f"{feed['latency']}ms"
            })
        
        price_df = pd.DataFrame(price_data)
        st.dataframe(price_df, use_container_width=True, hide_index=True)
        
        # Price difference analysis
        broker_a = price_feeds['broker_a']
        broker_b = price_feeds['broker_b']
        
        bid_diff = broker_a['bid'] - broker_b['bid']
        ask_diff = broker_a['ask'] - broker_b['ask']
        
        diff_col1, diff_col2, diff_col3 = st.columns(3)
        
        with diff_col1:
            st.metric("Bid Difference", f"{bid_diff:+.2f}")
        
        with diff_col2:
            st.metric("Ask Difference", f"{ask_diff:+.2f}")
        
        with diff_col3:
            # Calculate potential arbitrage profit
            if bid_diff > 0:
                arb_profit = bid_diff - 0.5  # Minus estimated costs
                arb_direction = f"{broker_a['name']} → {broker_b['name']}"
            else:
                arb_profit = abs(bid_diff) - 0.5
                arb_direction = f"{broker_b['name']} → {broker_a['name']}"
            
            profit_color = "#10B981" if arb_profit > 0 else "#EF4444"
            st.markdown(f"**Arbitrage Opportunity**")
            st.markdown(f"<span style='color: {profit_color}; font-weight: bold;'>${arb_profit:+.2f}</span>", unsafe_allow_html=True)
            st.markdown(f"<small>{arb_direction}</small>", unsafe_allow_html=True)
        
        # Real-time price chart
        st.markdown("### 📈 Price Movement Chart")
        
        # Generate price history for chart
        times = pd.date_range(start=datetime.now() - timedelta(hours=1), periods=60, freq='1T')
        
        broker_a_prices = []
        broker_b_prices = []
        current_a = broker_a['bid']
        current_b = broker_b['bid']
        
        for _ in times:
            current_a += random.uniform(-1, 1)
            current_b += random.uniform(-1, 1)
            broker_a_prices.append(current_a)
            broker_b_prices.append(current_b)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=times,
            y=broker_a_prices,
            mode='lines',
            name=broker_a['name'],
            line=dict(color='#3B82F6', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=times,
            y=broker_b_prices,
            mode='lines',
            name=broker_b['name'],
            line=dict(color='#F59E0B', width=2)
        ))
        
        # Add difference as area
        differences = [a - b for a, b in zip(broker_a_prices, broker_b_prices)]
        
        fig.add_trace(go.Scatter(
            x=times,
            y=differences,
            mode='lines',
            name='Price Difference',
            line=dict(color='#10B981', width=1),
            yaxis='y2',
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))
        
        fig.update_layout(
            title="XAUUSD Price Comparison - Last Hour",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=400,
            yaxis=dict(title="Price ($)"),
            yaxis2=dict(title="Difference ($)", overlaying='y', side='right'),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Arbitrage opportunities log
        st.markdown("### 🎯 Arbitrage Opportunities")
        
        opportunities = st.session_state.xauusd_arbitrage['opportunities']
        
        if opportunities:
            opp_data = []
            for opp in opportunities[-10:]:  # Show last 10 opportunities
                status_icon = "✅" if opp['executed'] else "❌"
                opp_data.append({
                    'Time': opp['timestamp'].strftime('%H:%M:%S'),
                    'Type': opp['type'],
                    'Profit Potential': f"${opp['profit_potential']:.2f}",
                    'Size': opp['size'],
                    'Status': f"{status_icon} {opp['status']}"
                })
            
            opp_df = pd.DataFrame(opp_data)
            st.dataframe(opp_df, use_container_width=True, hide_index=True)
        else:
            st.info("No arbitrage opportunities detected yet")
    
    with col2:
        # Arbitrage settings
        st.markdown("### ⚙️ Arbitrage Settings")
        
        settings = st.session_state.xauusd_arbitrage['settings']
        
        # Execution settings
        st.markdown("#### 🎯 Execution")
        
        min_profit = st.number_input("Min Profit Threshold ($)", 0.1, 10.0, settings['min_profit_threshold'], 0.1, key="arb_min_profit")
        max_position = st.number_input("Max Position Size", 0.1, 10.0, settings['max_position_size'], 0.1, key="arb_max_position")
        max_slippage = st.number_input("Max Slippage ($)", 0.1, 5.0, settings['max_slippage'], 0.1, key="arb_max_slippage")
        
        auto_execute = st.checkbox("Auto Execute", settings['auto_execute'], key="arb_auto_execute")
        
        # Risk management
        st.markdown("#### ⚠️ Risk Management")
        
        max_daily_trades = st.number_input("Max Daily Trades", 1, 100, settings['max_daily_trades'], key="arb_max_daily")
        max_exposure = st.number_input("Max Exposure ($)", 1000, 100000, settings['max_exposure'], key="arb_max_exposure")
        stop_loss = st.number_input("Stop Loss ($)", 1.0, 100.0, settings['stop_loss'], 1.0, key="arb_stop_loss")
        
        # Update settings
        if st.button("💾 Save Settings", key="save_arb_settings", use_container_width=True):
            st.session_state.xauusd_arbitrage['settings'].update({
                'min_profit_threshold': min_profit,
                'max_position_size': max_position,
                'max_slippage': max_slippage,
                'auto_execute': auto_execute,
                'max_daily_trades': max_daily_trades,
                'max_exposure': max_exposure,
                'stop_loss': stop_loss
            })
            st.success("✅ Settings saved!")
        
        # Performance statistics
        st.markdown("### 📊 Performance Stats")
        
        stats = st.session_state.xauusd_arbitrage['stats']
        
        st.metric("Total Opportunities", stats['total_opportunities'])
        st.metric("Average Profit", f"${stats['avg_profit']:.2f}")
        st.metric("Best Opportunity", "$3.25")  # Sample data
        st.metric("Worst Loss", "-$1.50")  # Sample data
        
        # Daily performance chart
        st.markdown("### 📈 Daily Performance")
        
        # Generate daily performance data
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), periods=7, freq='D')
        daily_pnl = [random.uniform(-50, 200) for _ in dates]
        
        fig = go.Figure()
        
        colors = ['#10B981' if pnl > 0 else '#EF4444' for pnl in daily_pnl]
        
        fig.add_trace(go.Bar(
            x=dates,
            y=daily_pnl,
            marker_color=colors,
            name='Daily P&L'
        ))
        
        fig.update_layout(
            title="7-Day Arbitrage Performance",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=250,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Manual execution
        st.markdown("### 🎮 Manual Execution")
        
        manual_size = st.number_input("Position Size", 0.01, 5.0, 0.1, 0.01, key="manual_arb_size")
        manual_direction = st.selectbox("Direction", ["A→B", "B→A"], key="manual_direction")
        
        if st.button("⚡ Execute Arbitrage", key="manual_execute", use_container_width=True):
            # Simulate manual execution
            profit = random.uniform(0.5, 3.0)
            st.success(f"✅ Arbitrage executed! Profit: ${profit:.2f}")
            
            # Add to opportunities log
            new_opportunity = {
                'timestamp': datetime.now(),
                'type': manual_direction,
                'profit_potential': profit,
                'size': manual_size,
                'status': 'Executed',
                'executed': True
            }
            st.session_state.xauusd_arbitrage['opportunities'].append(new_opportunity)
            st.rerun()

elif st.session_state.page == "LP Bridge Manager":
    st.markdown("### 🌐 Liquidity Provider Bridge Manager")
    
    # LP Bridge overview
    lps = st.session_state.lp_bridge['liquidity_providers']
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        connected_lps = len([lp for lp in lps if lp['status'] == 'Connected'])
        total_lps = len(lps)
        st.metric("Connected LPs", f"{connected_lps}/{total_lps}")
    
    with col2:
        total_liquidity = sum([lp['available_liquidity'] for lp in lps if lp['status'] == 'Connected'])
        st.metric("Available Liquidity", f"${total_liquidity:,}")
    
    with col3:
        avg_latency = np.mean([lp['latency'] for lp in lps if lp['status'] == 'Connected' and lp['latency'] > 0])
        st.metric("Avg Latency", f"{avg_latency:.1f}ms")
    
    with col4:
        total_volume = sum([lp['daily_volume'] for lp in lps])
        st.metric("Daily Volume", f"${total_volume:,}")
    
    # Main LP management interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔗 Liquidity Provider Status")
        
        # LP status table with detailed information
        for i, lp in enumerate(lps):
            status_color = "#10B981" if lp['status'] == 'Connected' else "#EF4444"
            utilization_color = "#10B981" if lp['utilization'] < 70 else "#F59E0B" if lp['utilization'] < 90 else "#EF4444"
            
            with st.expander(f"🏦 {lp['name']} - {'🟢 Connected' if lp['status'] == 'Connected' else '🔴 Disconnected'}"):
                lp_col1, lp_col2, lp_col3 = st.columns(3)
                
                with lp_col1:
                    st.markdown(f"**Type:** {lp['type']}")
                    st.markdown(f"**Protocol:** {lp['protocol']}")
                    st.markdown(f"**Status:** <span style='color: {status_color};'>● {lp['status']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Uptime:** {lp['uptime']:.1f}%")
                
                with lp_col2:
                    st.metric("Available Liquidity", f"${lp['available_liquidity']:,}")
                    st.metric("Total Liquidity", f"${lp['total_liquidity']:,}")
                    st.markdown(f"**Utilization:** <span style='color: {utilization_color};'>{lp['utilization']:.1f}%</span>", unsafe_allow_html=True)
                    st.metric("Commission", f"{lp['commission']:.2f}%")
                
                with lp_col3:
                    st.metric("Latency", f"{lp['latency']:.1f}ms" if lp['latency'] > 0 else "N/A")
                    st.metric("Fill Rate", f"{lp['fill_rate']:.1f}%")
                    st.metric("Avg Spread", f"{lp['avg_spread']:.1f} pips")
                    st.metric("Rejections Today", lp['rejections_today'])
                
                # LP controls
                control_col1, control_col2, control_col3 = st.columns(3)
                
                with control_col1:
                    if lp['status'] == 'Connected':
                        if st.button("🔌 Disconnect", key=f"disconnect_lp_{i}", use_container_width=True):
                            st.session_state.lp_bridge['liquidity_providers'][i]['status'] = 'Disconnected'
                            st.session_state.lp_bridge['liquidity_providers'][i]['available_liquidity'] = 0
                            st.session_state.lp_bridge['liquidity_providers'][i]['latency'] = 0
                            st.success(f"✅ {lp['name']} disconnected!")
                            st.rerun()
                    else:
                        if st.button("🔌 Connect", key=f"connect_lp_{i}", use_container_width=True):
                            st.session_state.lp_bridge['liquidity_providers'][i]['status'] = 'Connected'
                            st.session_state.lp_bridge['liquidity_providers'][i]['available_liquidity'] = lp['total_liquidity'] // 2
                            st.session_state.lp_bridge['liquidity_providers'][i]['latency'] = random.uniform(5, 20)
                            st.success(f"✅ {lp['name']} connected!")
                            st.rerun()
                
                with control_col2:
                    if st.button("⚙️ Configure", key=f"config_lp_{i}", use_container_width=True):
                        st.info("LP configuration panel would open here")
                
                with control_col3:
                    if st.button("📊 Statistics", key=f"stats_lp_{i}", use_container_width=True):
                        st.info("Detailed LP statistics would open here")
                
                # Supported symbols
                st.markdown("**Supported Symbols:**")
                symbols_text = ", ".join(lp['supported_symbols'])
                st.markdown(f"<small>{symbols_text}</small>", unsafe_allow_html=True)
        
        # LP routing and load balancing
        st.markdown("### 🔄 Order Routing & Load Balancing")
        
        routing_col1, routing_col2, routing_col3 = st.columns(3)
        
        with routing_col1:
            st.markdown("#### 🎯 Routing Rules")
            
            routing_mode = st.selectbox("Routing Mode", 
                ["Best Price", "Lowest Latency", "Load Balanced", "Round Robin"], 
                index=0, key="routing_mode")
            
            price_tolerance = st.number_input("Price Tolerance ($)", 0.1, 10.0, 1.0, 0.1, key="price_tolerance")
            execution_timeout = st.number_input("Execution Timeout (ms)", 100, 10000, 3000, 100, key="execution_timeout")
        
        with routing_col2:
            st.markdown("#### ⚖️ Load Balancing")
            
            load_balancing = st.checkbox("Enable Load Balancing", True, key="load_balancing")
            max_utilization = st.slider("Max LP Utilization (%)", 50, 100, 80, 5, key="max_utilization")
            
            # Show current load distribution
            if connected_lps > 0:
                st.markdown("**Current Load:**")
                for lp in lps:
                    if lp['status'] == 'Connected':
                        st.progress(lp['utilization']/100, text=f"{lp['name']}: {lp['utilization']:.1f}%")
        
        with routing_col3:
            st.markdown("#### 🛡️ Risk Controls")
            
            position_limits = st.checkbox("Position Limits", True, key="position_limits")
            max_position = st.number_input("Max Net Position", 1000000, 100000000, 10000000, key="max_net_position")
            
            credit_limits = st.checkbox("Credit Limits", True, key="credit_limits")
            max_credit = st.number_input("Max Credit Exposure", 1000000, 50000000, 5000000, key="max_credit")
        
        # Save routing settings
        if st.button("💾 Save Routing Settings", key="save_routing", use_container_width=True):
            st.session_state.lp_bridge['settings'].update({
                'routing_mode': routing_mode,
                'price_tolerance': price_tolerance,
                'execution_timeout': execution_timeout,
                'load_balancing': load_balancing,
                'max_lp_utilization': max_utilization,
                'position_limits': position_limits,
                'max_net_position': max_position,
                'credit_limits': credit_limits,
                'max_credit_exposure': max_credit
            })
            st.success("✅ Routing settings saved!")
    
    with col2:
        # Real-time monitoring
        st.markdown("### 📊 Real-Time Monitoring")
        
        # LP performance chart
        st.markdown("#### 📈 LP Performance")
        
        # Generate performance data for connected LPs
        connected_lp_names = [lp['name'] for lp in lps if lp['status'] == 'Connected']
        
        if connected_lp_names:
            fig = go.Figure()
            
            for lp_name in connected_lp_names:
                # Generate sample latency data
                times = pd.date_range(start=datetime.now() - timedelta(minutes=30), periods=30, freq='1T')
                latencies = [random.uniform(5, 25) for _ in times]
                
                fig.add_trace(go.Scatter(
                    x=times,
                    y=latencies,
                    mode='lines',
                    name=lp_name.split()[0],  # Short name
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="LP Latency - Last 30 Minutes",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=250,
                yaxis_title="Latency (ms)",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Order flow statistics
        st.markdown("#### 📊 Order Flow")
        
        # Generate sample order flow data
        order_flow_data = []
        for lp in lps:
            if lp['status'] == 'Connected':
                orders_today = random.randint(50, 500)
                fills_today = int(orders_today * lp['fill_rate'] / 100)
                
                order_flow_data.append({
                    'LP': lp['name'].split()[0],
                    'Orders': orders_today,
                    'Fills': fills_today,
                    'Fill Rate': f"{lp['fill_rate']:.1f}%",
                    'Rejections': lp['rejections_today']
                })
        
        if order_flow_data:
            flow_df = pd.DataFrame(order_flow_data)
            st.dataframe(flow_df, use_container_width=True, hide_index=True)
        
        # Liquidity depth
        st.markdown("#### 💧 Liquidity Depth")
        
        total_available = sum([lp['available_liquidity'] for lp in lps if lp['status'] == 'Connected'])
        total_capacity = sum([lp['total_liquidity'] for lp in lps if lp['status'] == 'Connected'])
        
        if total_capacity > 0:
            utilization_pct = (total_capacity - total_available) / total_capacity * 100
            
            st.metric("Total Available", f"${total_available:,}")
            st.metric("Total Capacity", f"${total_capacity:,}")
            st.metric("Global Utilization", f"{utilization_pct:.1f}%")
            
            # Liquidity distribution pie chart
            lp_liquidity = []
            lp_names = []
            
                        for lp in lps:
                if lp['status'] == 'Connected' and lp['available_liquidity'] > 0:
                    lp_liquidity.append(lp['available_liquidity'])
                    lp_names.append(lp['name'].split()[0])
            
            if lp_liquidity:
                fig = go.Figure(data=[go.Pie(
                    labels=lp_names,
                    values=lp_liquidity,
                    hole=0.4
                )])
                
                fig.update_layout(
                    title="Liquidity Distribution",
                    template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # System alerts
        st.markdown("#### 🚨 System Alerts")
        
        alerts = [
            {"level": "warning", "message": "High latency detected on LP-3", "time": "2 min ago"},
            {"level": "info", "message": "LP-1 utilization at 85%", "time": "5 min ago"},
            {"level": "error", "message": "LP-4 connection timeout", "time": "8 min ago"},
            {"level": "success", "message": "LP-2 reconnected successfully", "time": "12 min ago"}
        ]
        
        for alert in alerts:
            if alert['level'] == 'error':
                st.error(f"🔴 {alert['message']} ({alert['time']})")
            elif alert['level'] == 'warning':
                st.warning(f"🟡 {alert['message']} ({alert['time']})")
            elif alert['level'] == 'success':
                st.success(f"🟢 {alert['message']} ({alert['time']})")
            else:
                st.info(f"🔵 {alert['message']} ({alert['time']})")

elif st.session_state.page == "Risk Management":
    st.markdown("### ⚠️ Advanced Risk Management")
    
    # Risk overview dashboard
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        current_exposure = sum([abs(pos['volume'] * pos['current_price']) for pos in st.session_state.portfolio['positions']])
        st.metric("Current Exposure", f"${current_exposure:,.0f}")
    
    with col2:
        var_95 = current_exposure * 0.05  # Simplified VaR calculation
        st.metric("VaR (95%)", f"${var_95:,.0f}")
    
    with col3:
        margin_level = (st.session_state.portfolio['equity'] / st.session_state.portfolio['margin']) * 100 if st.session_state.portfolio['margin'] > 0 else 0
        margin_color = "#10B981" if margin_level > 200 else "#F59E0B" if margin_level > 100 else "#EF4444"
        st.markdown(f"**Margin Level**")
        st.markdown(f"<span style='color: {margin_color}; font-size: 1.5em; font-weight: bold;'>{margin_level:.0f}%</span>", unsafe_allow_html=True)
    
    with col4:
        max_drawdown = random.uniform(5, 15)  # Sample data
        dd_color = "#10B981" if max_drawdown < 10 else "#F59E0B" if max_drawdown < 20 else "#EF4444"
        st.markdown(f"**Max Drawdown**")
        st.markdown(f"<span style='color: {dd_color}; font-size: 1.5em; font-weight: bold;'>{max_drawdown:.1f}%</span>", unsafe_allow_html=True)
    
    with col5:
        risk_score = random.randint(3, 8)  # Sample risk score
        score_color = "#10B981" if risk_score <= 5 else "#F59E0B" if risk_score <= 7 else "#EF4444"
        st.markdown(f"**Risk Score**")
        st.markdown(f"<span style='color: {score_color}; font-size: 1.5em; font-weight: bold;'>{risk_score}/10</span>", unsafe_allow_html=True)
    
    # Main risk management interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Position risk analysis
        st.markdown("### 📊 Position Risk Analysis")
        
        if st.session_state.portfolio['positions']:
            # Risk breakdown by position
            risk_data = []
            for pos in st.session_state.portfolio['positions']:
                position_value = abs(pos['volume'] * pos['current_price'])
                risk_amount = position_value * 0.02  # 2% risk assumption
                
                risk_data.append({
                    'Symbol': pos['symbol'],
                    'Type': pos['type'],
                    'Volume': pos['volume'],
                    'Value': f"${position_value:,.0f}",
                    'Risk': f"${risk_amount:,.0f}",
                    'P&L': f"${pos['pnl']:+.2f}",
                    'Risk %': f"{(risk_amount / st.session_state.portfolio['equity']) * 100:.1f}%"
                })
            
            risk_df = pd.DataFrame(risk_data)
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
            
            # Risk concentration chart
            st.markdown("#### 🎯 Risk Concentration")
            
            symbols = [pos['symbol'] for pos in st.session_state.portfolio['positions']]
            exposures = [abs(pos['volume'] * pos['current_price']) for pos in st.session_state.portfolio['positions']]
            
            fig = go.Figure(data=[go.Pie(
                labels=symbols,
                values=exposures,
                hole=0.4
            )])
            
            fig.update_layout(
                title="Exposure by Symbol",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No open positions to analyze")
        
        # Correlation matrix
        st.markdown("### 🔗 Correlation Matrix")
        
        # Generate sample correlation data
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD']
        correlation_matrix = np.random.rand(5, 5)
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2  # Make symmetric
        np.fill_diagonal(correlation_matrix, 1)  # Diagonal should be 1
        
        # Convert to range [-1, 1]
        correlation_matrix = correlation_matrix * 2 - 1
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=symbols,
            y=symbols,
            colorscale='RdBu',
            zmid=0,
            text=np.round(correlation_matrix, 2),
            texttemplate="%{text}",
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title="Asset Correlation Matrix",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stress testing
        st.markdown("### 🧪 Stress Testing")
        
        stress_col1, stress_col2, stress_col3 = st.columns(3)
        
        with stress_col1:
            st.markdown("#### 📉 Market Crash Scenario")
            crash_impact = current_exposure * 0.15  # 15% loss
            st.metric("Potential Loss", f"-${crash_impact:,.0f}")
            st.metric("Remaining Equity", f"${st.session_state.portfolio['equity'] - crash_impact:,.0f}")
        
        with stress_col2:
            st.markdown("#### 📈 Black Swan Event")
            swan_impact = current_exposure * 0.25  # 25% loss
            st.metric("Potential Loss", f"-${swan_impact:,.0f}")
            st.metric("Remaining Equity", f"${st.session_state.portfolio['equity'] - swan_impact:,.0f}")
        
        with stress_col3:
            st.markdown("#### 🌊 Liquidity Crisis")
            liquidity_impact = current_exposure * 0.10  # 10% loss
            st.metric("Potential Loss", f"-${liquidity_impact:,.0f}")
            st.metric("Remaining Equity", f"${st.session_state.portfolio['equity'] - liquidity_impact:,.0f}")
        
        if st.button("🧪 Run Full Stress Test", key="run_stress_test", use_container_width=True):
            with st.spinner("Running comprehensive stress test..."):
                time.sleep(2)  # Simulate processing
                st.success("✅ Stress test completed! Portfolio shows resilience under tested scenarios.")
    
    with col2:
        # Risk limits and controls
        st.markdown("### 🛡️ Risk Limits & Controls")
        
        # Position limits
        st.markdown("#### 📏 Position Limits")
        
        max_position_size = st.number_input("Max Position Size", 0.1, 100.0, 10.0, 0.1, key="max_position_size")
        max_symbol_exposure = st.number_input("Max Symbol Exposure (%)", 1, 50, 20, key="max_symbol_exposure")
        max_total_exposure = st.number_input("Max Total Exposure (%)", 10, 200, 100, key="max_total_exposure")
        
        # Risk per trade
        st.markdown("#### 💰 Risk per Trade")
        
        risk_per_trade = st.slider("Risk per Trade (%)", 0.1, 10.0, 2.0, 0.1, key="risk_per_trade")
        max_daily_loss = st.number_input("Max Daily Loss ($)", 100, 10000, 1000, key="max_daily_loss")
        max_consecutive_losses = st.number_input("Max Consecutive Losses", 1, 20, 5, key="max_consecutive_losses")
        
        # Margin requirements
        st.markdown("#### 📊 Margin Requirements")
        
        margin_call_level = st.number_input("Margin Call Level (%)", 50, 150, 100, key="margin_call_level")
        stop_out_level = st.number_input("Stop Out Level (%)", 20, 100, 50, key="stop_out_level")
        
        # Auto risk management
        st.markdown("#### 🤖 Auto Risk Management")
        
        auto_sl = st.checkbox("Auto Stop Loss", True, key="auto_sl")
        auto_tp = st.checkbox("Auto Take Profit", True, key="auto_tp")
        auto_hedge = st.checkbox("Auto Hedging", False, key="auto_hedge")
        emergency_close = st.checkbox("Emergency Close All", True, key="emergency_close")
        
        # Save risk settings
        if st.button("💾 Save Risk Settings", key="save_risk_settings", use_container_width=True):
            st.session_state.risk_management.update({
                'max_position_size': max_position_size,
                'max_symbol_exposure': max_symbol_exposure,
                'max_total_exposure': max_total_exposure,
                'risk_per_trade': risk_per_trade,
                'max_daily_loss': max_daily_loss,
                'max_consecutive_losses': max_consecutive_losses,
                'margin_call_level': margin_call_level,
                'stop_out_level': stop_out_level,
                'auto_sl': auto_sl,
                'auto_tp': auto_tp,
                'auto_hedge': auto_hedge,
                'emergency_close': emergency_close
            })
            st.success("✅ Risk settings saved!")
        
        # Risk alerts
        st.markdown("### 🚨 Risk Alerts")
        
        # Current risk status
        if margin_level < 100:
            st.error("🔴 MARGIN CALL - Add funds or close positions")
        elif margin_level < 150:
            st.warning("🟡 LOW MARGIN - Monitor closely")
        else:
            st.success("🟢 MARGIN OK")
        
        # Risk notifications
        risk_alerts = [
            {"level": "warning", "message": "EURUSD position approaching max size", "time": "1 min ago"},
            {"level": "info", "message": "Daily loss limit at 60%", "time": "15 min ago"},
            {"level": "success", "message": "All positions within risk limits", "time": "30 min ago"}
        ]
        
        for alert in risk_alerts:
            if alert['level'] == 'warning':
                st.warning(f"⚠️ {alert['message']}")
            elif alert['level'] == 'success':
                st.success(f"✅ {alert['message']}")
            else:
                st.info(f"ℹ️ {alert['message']}")
        
        # Emergency controls
        st.markdown("### 🆘 Emergency Controls")
        
        if st.button("🛑 CLOSE ALL POSITIONS", key="emergency_close_all", use_container_width=True):
            if st.session_state.portfolio['positions']:
                total_pnl = sum([pos['pnl'] for pos in st.session_state.portfolio['positions']])
                st.session_state.portfolio['positions'] = []
                st.error(f"🛑 ALL POSITIONS CLOSED! Total P&L: ${total_pnl:+.2f}")
                st.rerun()
            else:
                st.info("No positions to close")
        
        if st.button("⏸️ PAUSE ALL TRADING", key="pause_trading", use_container_width=True):
            st.session_state.trading_paused = True
            st.warning("⏸️ All trading activities paused!")
        
        if st.button("🔄 RESUME TRADING", key="resume_trading", use_container_width=True):
            st.session_state.trading_paused = False
            st.success("🔄 Trading activities resumed!")

elif st.session_state.page == "Analytics":
    st.markdown("### 📊 Advanced Trading Analytics")
    
    # Analytics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_trades = random.randint(150, 500)  # Sample data
        st.metric("Total Trades", total_trades)
    
    with col2:
        win_rate = random.uniform(55, 75)
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    with col3:
        profit_factor = random.uniform(1.2, 2.5)
        st.metric("Profit Factor", f"{profit_factor:.2f}")
    
    with col4:
        sharpe_ratio = random.uniform(0.8, 2.2)
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
    
    # Main analytics interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Performance analysis
        st.markdown("### 📈 Performance Analysis")
        
        # Time period selector
        period_col1, period_col2, period_col3 = st.columns(3)
        
        with period_col1:
            analysis_period = st.selectbox("Analysis Period", ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year"], index=2, key="analysis_period")
        
        with period_col2:
            analysis_symbol = st.selectbox("Symbol Filter", ["All"] + st.session_state.mt5_symbols[:10], key="analysis_symbol")
        
        with period_col3:
            analysis_strategy = st.selectbox("Strategy Filter", ["All", "Manual", "Auto", "Copy Trading"], key="analysis_strategy")
        
        # Equity curve with detailed analysis
        periods_map = {"1 Week": 7, "1 Month": 30, "3 Months": 90, "6 Months": 180, "1 Year": 365}
        days = periods_map[analysis_period]
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days, freq='D')
        
        # Generate realistic equity curve
        initial_balance = 10000
        equity_values = [initial_balance]
        daily_returns = []
        
        for i in range(days - 1):
            # Generate correlated returns with some trend
            base_return = 0.001  # 0.1% daily base return
            volatility = 0.02    # 2% daily volatility
            trend = np.sin(i / 30) * 0.002  # Cyclical trend
            
            daily_return = base_return + trend + np.random.normal(0, volatility)
            daily_returns.append(daily_return)
            
            new_equity = equity_values[-1] * (1 + daily_return)
            equity_values.append(new_equity)
        
        # Calculate drawdown
        peak = equity_values[0]
        drawdown = []
        for value in equity_values:
            if value > peak:
                peak = value
            dd = ((value - peak) / peak) * 100
            drawdown.append(dd)
        
        # Create comprehensive performance chart
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=('Equity Curve', 'Daily Returns', 'Drawdown')
        )
        
        # Equity curve
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity_values,
            mode='lines',
            name='Equity',
            line=dict(color='#10B981', width=3),
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ), row=1, col=1)
        
        # Daily returns
        fig.add_trace(go.Bar(
            x=dates[1:],
            y=[r * 100 for r in daily_returns],
            name='Daily Returns (%)',
            marker_color=['#10B981' if r > 0 else '#EF4444' for r in daily_returns]
        ), row=2, col=1)
        
        # Drawdown
        fig.add_trace(go.Scatter(
            x=dates,
            y=drawdown,
            mode='lines',
            name='Drawdown (%)',
            line=dict(color='#EF4444', width=2),
            fill='tonexty',
            fillcolor='rgba(239, 68, 68, 0.1)'
        ), row=3, col=1)
        
        fig.update_layout(
            title=f"Performance Analysis - {analysis_period}",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=600,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Trade analysis
        st.markdown("### 📊 Trade Analysis")
        
        # Generate sample trade data
        trade_data = []
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD']
        
        for i in range(50):  # Generate 50 sample trades
            symbol = random.choice(symbols)
            side = random.choice(['BUY', 'SELL'])
            entry_price = random.uniform(1.0, 2.0)
            exit_price = entry_price + random.uniform(-0.05, 0.05)
            volume = random.uniform(0.1, 2.0)
            
            pnl = (exit_price - entry_price) * volume * 100000 if side == 'BUY' else (entry_price - exit_price) * volume * 100000
            duration = random.uniform(0.5, 48)  # Hours
            
            trade_data.append({
                'Date': (datetime.now() - timedelta(days=random.randint(1, days))).strftime('%Y-%m-%d'),
                'Symbol': symbol,
                'Side': side,
                'Volume': f"{volume:.2f}",
                'Entry': f"{entry_price:.4f}",
                'Exit': f"{exit_price:.4f}",
                'P&L': f"${pnl:+.2f}",
                'Duration': f"{duration:.1f}h",
                'Strategy': random.choice(['Manual', 'Auto', 'Copy'])
            })
        
        trades_df = pd.DataFrame(trade_data)
        
        # Trade statistics
        trade_stats_col1, trade_stats_col2, trade_stats_col3 = st.columns(3)
        
        with trade_stats_col1:
            st.markdown("#### 🎯 Win/Loss Analysis")
            
            # Calculate win/loss stats
            pnl_values = [float(trade['P&L'].replace('$', '').replace('+', '')) for trade in trade_data]
            winning_trades = len([pnl for pnl in pnl_values if pnl > 0])
            losing_trades = len([pnl for pnl in pnl_values if pnl < 0])
            
            st.metric("Winning Trades", winning_trades)
            st.metric("Losing Trades", losing_trades)
            st.metric("Win Rate", f"{(winning_trades / len(trade_data)) * 100:.1f}%")
            
            avg_win = np.mean([pnl for pnl in pnl_values if pnl > 0]) if winning_trades > 0 else 0
            avg_loss = np.mean([pnl for pnl in pnl_values if pnl < 0]) if losing_trades > 0 else 0
            
            st.metric("Avg Win", f"${avg_win:.2f}")
            st.metric("Avg Loss", f"${avg_loss:.2f}")
        
        with trade_stats_col2:
            st.markdown("#### 📊 Symbol Performance")
            
            # Group by symbol
            symbol_pnl = {}
            for trade in trade_data:
                symbol = trade['Symbol']
                pnl = float(trade['P&L'].replace('$', '').replace('+', ''))
                if symbol not in symbol_pnl:
                    symbol_pnl[symbol] = []
                symbol_pnl[symbol].append(pnl)
            
            for symbol, pnls in symbol_pnl.items():
                total_pnl = sum(pnls)
                trade_count = len(pnls)
                st.metric(f"{symbol}", f"${total_pnl:+.0f} ({trade_count} trades)")
        
        with trade_stats_col3:
            st.markdown("#### ⏰ Time Analysis")
            
            # Duration analysis
            durations = [float(trade['Duration'].replace('h', '')) for trade in trade_data]
            avg_duration = np.mean(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            st.metric("Avg Duration", f"{avg_duration:.1f}h")
            st.metric("Max Duration", f"{max_duration:.1f}h")
            st.metric("Min Duration", f"{min_duration:.1f}h")
            
            # Best performing time periods
            st.metric("Best Hour", "14:00-15:00")  # Sample data
            st.metric("Best Day", "Tuesday")       # Sample data
        
        # Detailed trade table
        st.markdown("#### 📋 Trade History")
        st.dataframe(trades_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Advanced metrics
        st.markdown("### 📊 Advanced Metrics")
        
        # Risk-adjusted returns
        st.markdown("#### 📈 Risk-Adjusted Returns")
        
        total_return = ((equity_values[-1] / equity_values[0]) - 1) * 100
        annualized_return = ((equity_values[-1] / equity_values[0]) ** (365 / days) - 1) * 100
        volatility = np.std(daily_returns) * np.sqrt(252) * 100  # Annualized volatility
        
        st.metric("Total Return", f"{total_return:+.2f}%")
        st.metric("Annualized Return", f"{annualized_return:+.2f}%")
        st.metric("Volatility", f"{volatility:.2f}%")
        
        # Risk metrics
        max_dd = min(drawdown)
        st.metric("Max Drawdown", f"{max_dd:.2f}%")
        
        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_dd) if max_dd != 0 else 0
        st.metric("Calmar Ratio", f"{calmar_ratio:.2f}")
        
        # Sortino ratio (simplified)
        downside_returns = [r for r in daily_returns if r < 0]
        downside_deviation = np.std(downside_returns) * np.sqrt(252) if downside_returns else 0
        sortino_ratio = annualized_return / (downside_deviation * 100) if downside_deviation > 0 else 0
        st.metric("Sortino Ratio", f"{sortino_ratio:.2f}")
        
        # Monthly returns heatmap
        st.markdown("#### 🗓️ Monthly Returns")
        
        # Generate monthly returns data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        years = ['2023', '2024']
        
        monthly_returns = np.random.normal(1.5, 3.0, (len(years), len(months)))  # Sample data
        
        fig = go.Figure(data=go.Heatmap(
            z=monthly_returns,
            x=months,
            y=years,
            colorscale='RdYlGn',
            zmid=0,
            text=np.round(monthly_returns, 1),
            texttemplate="%{text}%",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Monthly Returns (%)",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=200,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance attribution
        st.markdown("#### 🎯 Performance Attribution")
        
        # Strategy performance breakdown
        strategy_performance = {
            'Manual Trading': random.uniform(-5, 15),
            'Auto Trading': random.uniform(0, 20),
            'Copy Trading': random.uniform(-2, 12),
            'Arbitrage': random.uniform(2, 8)
        }
        
        for strategy, performance in strategy_performance.items():
            color = "#10B981" if performance > 0 else "#EF4444"
            st.markdown(f"**{strategy}:** <span style='color: {color};'>{performance:+.1f}%</span>", unsafe_allow_html=True)
        
        # Asset allocation
        st.markdown("#### 🥧 Asset Allocation")
        
        allocation = {
            'Forex': 60,
            'Commodities': 25,
            'Crypto': 10,
            'Indices': 5
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(allocation.keys()),
            values=list(allocation.values()),
            hole=0.4
        )])
        
        fig.update_layout(
            title="Current Allocation",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Export options
        st.markdown("#### 📤 Export Reports")
        
        if st.button("📊 Generate PDF Report", key="generate_pdf", use_container_width=True):
            st.info("📊 Generating comprehensive PDF report...")
        
        if st.button("📈 Export to Excel", key="export_excel", use_container_width=True):
            st.info("📈 Exporting data to Excel format...")
        
        if st.button("📧 Email Report", key="email_report", use_container_width=True):
            st.info("📧 Sending report via email...")

elif st.session_state.page == "Settings":
    st.markdown("### ⚙️ Platform Settings")
    
    # Settings categories
    settings_tab1, settings_tab2, settings_tab3, settings_tab4 = st.tabs(["🎨 Appearance", "🔔 Notifications", "🔐 Security", "🔧 Advanced"])
    
    with settings_tab1:
        st.markdown("#### 🎨 Appearance Settings")
        
        # Theme settings
        theme_col1, theme_col2 = st.columns(2)
        
        with theme_col1:
            new_theme = st.selectbox("Theme", ["Light", "Dark"], 
                index=0 if st.session_state.theme == "Light" else 1, key="theme_selector")
            
            if new_theme != st.session_state.theme:
                st.session_state.theme = new_theme
                st.rerun()
            
            chart_style = st.selectbox("Chart Style", ["Modern", "Classic", "Minimal"], key="chart_style")
            color_scheme = st.selectbox("Color Scheme", ["Default", "Blue", "Green", "Purple"], key="color_scheme")
        
                with theme_col2:
            font_size = st.selectbox("Font Size", ["Small", "Medium", "Large"], index=1, key="font_size")
            layout_density = st.selectbox("Layout Density", ["Compact", "Normal", "Spacious"], index=1, key="layout_density")
            sidebar_position = st.selectbox("Sidebar Position", ["Left", "Right"], key="sidebar_position")
        
        # Dashboard customization
        st.markdown("#### 📊 Dashboard Customization")
        
        dashboard_col1, dashboard_col2 = st.columns(2)
        
        with dashboard_col1:
            show_portfolio_summary = st.checkbox("Show Portfolio Summary", True, key="show_portfolio")
            show_market_overview = st.checkbox("Show Market Overview", True, key="show_market")
            show_recent_trades = st.checkbox("Show Recent Trades", True, key="show_trades")
            show_news_feed = st.checkbox("Show News Feed", False, key="show_news")
        
        with dashboard_col2:
            default_timeframe = st.selectbox("Default Chart Timeframe", ["1M", "5M", "15M", "30M", "1H", "4H", "1D"], index=4, key="default_timeframe")
            auto_refresh = st.selectbox("Auto Refresh", ["Off", "5s", "10s", "30s", "1m"], index=2, key="auto_refresh")
            decimal_places = st.number_input("Price Decimal Places", 2, 8, 5, key="decimal_places")
    
    with settings_tab2:
        st.markdown("#### 🔔 Notification Settings")
        
        # Notification preferences
        notif_col1, notif_col2 = st.columns(2)
        
        with notif_col1:
            st.markdown("**Trade Notifications**")
            notify_trade_open = st.checkbox("Trade Opened", True, key="notify_trade_open")
            notify_trade_close = st.checkbox("Trade Closed", True, key="notify_trade_close")
            notify_sl_hit = st.checkbox("Stop Loss Hit", True, key="notify_sl")
            notify_tp_hit = st.checkbox("Take Profit Hit", True, key="notify_tp")
            
            st.markdown("**Market Notifications**")
            notify_price_alerts = st.checkbox("Price Alerts", True, key="notify_price_alerts")
            notify_news = st.checkbox("Economic News", False, key="notify_news")
            notify_volatility = st.checkbox("High Volatility", True, key="notify_volatility")
        
        with notif_col2:
            st.markdown("**System Notifications**")
            notify_connection = st.checkbox("Connection Status", True, key="notify_connection")
            notify_margin = st.checkbox("Margin Calls", True, key="notify_margin")
            notify_updates = st.checkbox("Platform Updates", True, key="notify_updates")
            
            st.markdown("**Delivery Methods**")
            email_notifications = st.checkbox("Email", True, key="email_notif")
            push_notifications = st.checkbox("Push Notifications", True, key="push_notif")
            sms_notifications = st.checkbox("SMS (Premium)", False, key="sms_notif")
            
            # Email settings
            if email_notifications:
                notification_email = st.text_input("Notification Email", "rishibrillant@gmail.com", key="notif_email")
        
        # Notification schedule
        st.markdown("#### ⏰ Notification Schedule")
        
        schedule_col1, schedule_col2 = st.columns(2)
        
        with schedule_col1:
            quiet_hours = st.checkbox("Enable Quiet Hours", False, key="quiet_hours")
            if quiet_hours:
                quiet_start = st.time_input("Quiet Start", datetime.strptime("22:00", "%H:%M").time(), key="quiet_start")
                quiet_end = st.time_input("Quiet End", datetime.strptime("08:00", "%H:%M").time(), key="quiet_end")
        
        with schedule_col2:
            weekend_notifications = st.checkbox("Weekend Notifications", False, key="weekend_notif")
            max_notifications_hour = st.number_input("Max Notifications/Hour", 1, 100, 10, key="max_notif_hour")
    
    with settings_tab3:
        st.markdown("#### 🔐 Security Settings")
        
        # Account security
        security_col1, security_col2 = st.columns(2)
        
        with security_col1:
            st.markdown("**Account Security**")
            
            two_factor_auth = st.checkbox("Two-Factor Authentication", True, key="2fa")
            if two_factor_auth:
                st.success("✅ 2FA is enabled")
                if st.button("🔄 Reset 2FA", key="reset_2fa"):
                    st.info("2FA reset instructions sent to your email")
            
            session_timeout = st.selectbox("Session Timeout", ["15 minutes", "30 minutes", "1 hour", "4 hours", "Never"], index=2, key="session_timeout")
            
            login_notifications = st.checkbox("Login Notifications", True, key="login_notif")
            
            # Password change
            st.markdown("**Change Password**")
            current_password = st.text_input("Current Password", type="password", key="current_pass")
            new_password = st.text_input("New Password", type="password", key="new_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pass")
            
            if st.button("🔒 Change Password", key="change_password"):
                if new_password == confirm_password and len(new_password) >= 8:
                    st.success("✅ Password changed successfully!")
                else:
                    st.error("❌ Passwords don't match or too short")
        
        with security_col2:
            st.markdown("**Trading Security**")
            
            require_password_trades = st.checkbox("Require Password for Large Trades", False, key="password_trades")
            if require_password_trades:
                large_trade_threshold = st.number_input("Large Trade Threshold ($)", 1000, 100000, 10000, key="large_trade_threshold")
            
            ip_whitelist = st.checkbox("IP Address Whitelist", False, key="ip_whitelist")
            if ip_whitelist:
                allowed_ips = st.text_area("Allowed IP Addresses (one per line)", "192.168.1.100\n203.0.113.1", key="allowed_ips")
            
            api_access = st.checkbox("API Access Enabled", True, key="api_access")
            if api_access:
                if st.button("🔑 Generate New API Key", key="new_api_key"):
                    new_key = "YT_" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=32))
                    st.code(new_key)
                    st.warning("⚠️ Save this key securely - it won't be shown again!")
            
            # Active sessions
            st.markdown("**Active Sessions**")
            sessions = [
                {"Device": "Windows PC", "Location": "Mumbai, India", "Last Active": "Now", "IP": "203.0.113.1"},
                {"Device": "iPhone", "Location": "Mumbai, India", "Last Active": "2 hours ago", "IP": "203.0.113.2"}
            ]
            
            for i, session in enumerate(sessions):
                with st.container():
                    sess_col1, sess_col2 = st.columns([3, 1])
                    with sess_col1:
                        st.markdown(f"**{session['Device']}** - {session['Location']}")
                        st.markdown(f"<small>Last active: {session['Last Active']} | IP: {session['IP']}</small>", unsafe_allow_html=True)
                    with sess_col2:
                        if session['Last Active'] != "Now":
                            if st.button("🚫 Revoke", key=f"revoke_session_{i}"):
                                st.success("Session revoked!")
    
    with settings_tab4:
        st.markdown("#### 🔧 Advanced Settings")
        
        # Trading settings
        advanced_col1, advanced_col2 = st.columns(2)
        
        with advanced_col1:
            st.markdown("**Trading Configuration**")
            
            default_lot_size = st.number_input("Default Lot Size", 0.01, 10.0, 0.1, 0.01, key="default_lot")
            slippage_tolerance = st.number_input("Slippage Tolerance (pips)", 0.1, 10.0, 2.0, 0.1, key="slippage_tolerance")
            execution_mode = st.selectbox("Execution Mode", ["Market", "Instant", "Request"], key="execution_mode")
            
            auto_sl_tp = st.checkbox("Auto Set SL/TP", True, key="auto_sl_tp")
            if auto_sl_tp:
                default_sl = st.number_input("Default SL (pips)", 5, 500, 50, key="default_sl")
                default_tp = st.number_input("Default TP (pips)", 5, 500, 100, key="default_tp")
            
            one_click_trading = st.checkbox("One-Click Trading", False, key="one_click")
            if one_click_trading:
                st.warning("⚠️ One-click trading bypasses confirmation dialogs")
        
        with advanced_col2:
            st.markdown("**Data & Performance**")
            
            data_compression = st.checkbox("Enable Data Compression", True, key="data_compression")
            cache_size = st.selectbox("Cache Size", ["Small (100MB)", "Medium (500MB)", "Large (1GB)"], index=1, key="cache_size")
            
            max_chart_bars = st.number_input("Max Chart Bars", 1000, 100000, 10000, key="max_chart_bars")
            tick_data_retention = st.selectbox("Tick Data Retention", ["1 Day", "1 Week", "1 Month"], index=1, key="tick_retention")
            
            hardware_acceleration = st.checkbox("Hardware Acceleration", True, key="hardware_accel")
            multi_threading = st.checkbox("Multi-Threading", True, key="multi_threading")
            
            # Debug settings
            st.markdown("**Debug & Logging**")
            debug_mode = st.checkbox("Debug Mode", False, key="debug_mode")
            log_level = st.selectbox("Log Level", ["Error", "Warning", "Info", "Debug"], index=2, key="log_level")
            
            if st.button("📋 Export Logs", key="export_logs"):
                st.info("Logs exported to Downloads folder")
            
            if st.button("🧹 Clear Cache", key="clear_cache"):
                st.success("✅ Cache cleared successfully!")
        
        # Backup and restore
        st.markdown("#### 💾 Backup & Restore")
        
        backup_col1, backup_col2 = st.columns(2)
        
        with backup_col1:
            st.markdown("**Backup Settings**")
            
            auto_backup = st.checkbox("Auto Backup", True, key="auto_backup")
            if auto_backup:
                backup_frequency = st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"], key="backup_frequency")
                backup_location = st.selectbox("Backup Location", ["Local", "Cloud", "Both"], index=2, key="backup_location")
            
            if st.button("💾 Create Backup Now", key="create_backup"):
                with st.spinner("Creating backup..."):
                    time.sleep(2)
                st.success("✅ Backup created successfully!")
        
        with backup_col2:
            st.markdown("**Restore Settings**")
            
            st.file_uploader("Upload Backup File", type=['bak', 'zip'], key="restore_file")
            
            if st.button("🔄 Restore from Backup", key="restore_backup"):
                st.warning("⚠️ This will overwrite current settings. Continue?")
                if st.button("✅ Confirm Restore", key="confirm_restore"):
                    st.success("✅ Settings restored successfully!")
        
        # Reset options
        st.markdown("#### 🔄 Reset Options")
        
        reset_col1, reset_col2, reset_col3 = st.columns(3)
        
        with reset_col1:
            if st.button("🔄 Reset UI Settings", key="reset_ui"):
                st.info("UI settings reset to default")
        
        with reset_col2:
            if st.button("🔄 Reset Trading Settings", key="reset_trading"):
                st.info("Trading settings reset to default")
        
        with reset_col3:
            if st.button("🔄 Factory Reset", key="factory_reset"):
                st.error("⚠️ This will reset ALL settings!")
    
    # Save all settings
    st.markdown("---")
    save_col1, save_col2 = st.columns(2)
    
    with save_col1:
        if st.button("💾 Save All Settings", key="save_all_settings", use_container_width=True):
            st.success("✅ All settings saved successfully!")
    
    with save_col2:
        if st.button("🔄 Reset to Defaults", key="reset_all_settings", use_container_width=True):
            st.warning("⚠️ All settings reset to default values!")

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**Yantra Trading Platform v2.0**")
    st.markdown("Professional Trading Suite")

with footer_col2:
    st.markdown("**Status:** 🟢 All Systems Operational")
    st.markdown(f"**Server Time:** {datetime.now().strftime('%H:%M:%S UTC')}")

with footer_col3:
    st.markdown("**Support:** support@yantra.trading")
    st.markdown("**Docs:** [docs.yantra.trading](https://docs.yantra.trading)")

# Auto-refresh mechanism (if enabled)
if st.session_state.get('auto_refresh', 'Off') != 'Off':
    refresh_intervals = {'5s': 5, '10s': 10, '30s': 30, '1m': 60}
    interval = refresh_intervals.get(st.session_state.get('auto_refresh', '10s'), 10)
    
    # Use JavaScript to auto-refresh
    st.markdown(f"""
    <script>
    setTimeout(function(){{
        window.location.reload();
    }}, {interval * 1000});
    </script>
    """, unsafe_allow_html=True)

# Performance monitoring (hidden)
if st.session_state.get('debug_mode', False):
    with st.expander("🔧 Debug Info"):
        st.json({
            "session_state_size": len(str(st.session_state)),
            "current_page": st.session_state.page,
            "theme": st.session_state.theme,
            "positions_count": len(st.session_state.portfolio['positions']),
            "mt5_connected": st.session_state.mt5_connected,
            "auto_trading_enabled": st.session_state.auto_trading['enabled']
        })
