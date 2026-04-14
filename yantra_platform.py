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

# ====
st.set_page_config(
    page_title="Yantra Trading Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====
def init_session_state():
    """Initialize only essential session state data"""
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    if 'theme' not in st.session_state:
        st.session_state.theme = "Dark"
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {
            'balance': 50000.0,
            'equity': 52500.0,
            'margin': 2500.0,
            'positions': []
        }
    
    if 'brokers' not in st.session_state:
        st.session_state.brokers = {
            'Divit Capital': {'status': 'Connected', 'balance': 25000, 'positions': 3},
            'Kama Capital': {'status': 'Connected', 'balance': 25000, 'positions': 2},
            'LP Bridge': {'status': 'Connected', 'balance': 0, 'positions': 0}
        }
    
    if 'symbols' not in st.session_state:
        st.session_state.symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'XAUUSD', 'BTCUSD']

init_session_state()

# ====
with st.sidebar:
    st.markdown("# 🚀 YANTRA")
    
    # Navigation - Compact Grid
    pages = [
        ("📊", "Dashboard"), ("💹", "Trading"), ("📈", "Charts"), 
        ("🤖", "Auto Trade"), ("👥", "Copy Trade"), ("🔄", "Backtest"),
        ("🥇", "Arbitrage"), ("🌐", "LP Bridge"), ("⚙️", "Settings")
    ]
    
    for i in range(0, len(pages), 3):
        cols = st.columns(3)
        for j, (icon, page) in enumerate(pages[i:i+3]):
            if j < len(cols):
                with cols[j]:
                    if st.button(icon, key=f"nav_{page}", help=page, use_container_width=True):
                        st.session_state.page = page
                        st.rerun()
    
    st.markdown("---")
    
    # Quick Stats - Ultra Compact
    st.markdown("**💰 PORTFOLIO**")
    st.metric("Balance", f"${st.session_state.portfolio['balance']:,.0f}", "2.5k")
    st.metric("P&L", f"${st.session_state.portfolio['equity'] - st.session_state.portfolio['balance']:,.0f}", "5.0%")
    
    st.markdown("**🔗 BROKERS**")
    for name, data in st.session_state.brokers.items():
        status_icon = "🟢" if data['status'] == 'Connected' else "🔴"
        st.markdown(f"{status_icon} {name[:8]} • {data['positions']} pos")

# ====
if st.session_state.page == "Dashboard":
    # Header Row - Compact
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Equity", f"${st.session_state.portfolio['equity']:,.0f}", "5.0%")
    with col2:
        st.metric("Free Margin", f"${st.session_state.portfolio['equity'] - st.session_state.portfolio['margin']:,.0f}", "2.1%")
    with col3:
        st.metric("Open Positions", len(st.session_state.portfolio['positions']), "2")
    with col4:
        st.metric("Daily P&L", "+$1,250", "2.5%")
    
    # Main Dashboard Grid
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Market Overview Chart
        st.markdown("### 📊 Market Overview")
        
        # Generate sample market data
        symbols = st.session_state.symbols[:5]
        prices = [random.uniform(1.0, 2.5) for _ in symbols]
        changes = [random.uniform(-2, 3) for _ in symbols]
        
        fig = go.Figure()
        colors = ['#10B981' if change > 0 else '#EF4444' for change in changes]
        
        fig.add_trace(go.Bar(
            x=symbols, y=changes, marker_color=colors,
            text=[f"{change:+.1f}%" for change in changes],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Daily Price Changes",
            yaxis_title="Change %",
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Quick Trade Panel
        st.markdown("### ⚡ Quick Trade")
        
        trade_col1, trade_col2, trade_col3, trade_col4, trade_col5 = st.columns(5)
        
        with trade_col1:
            symbol = st.selectbox("Symbol", st.session_state.symbols, key="quick_symbol")
        with trade_col2:
            volume = st.number_input("Volume", 0.01, 10.0, 1.0, 0.01, key="quick_volume")
        with trade_col3:
            if st.button("🟢 BUY", key="quick_buy", use_container_width=True):
                st.success(f"✅ BUY {volume} {symbol}")
        with trade_col4:
            if st.button("🔴 SELL", key="quick_sell", use_container_width=True):
                st.success(f"✅ SELL {volume} {symbol}")
        with trade_col5:
            if st.button("📊 Chart", key="quick_chart", use_container_width=True):
                st.session_state.page = "Charts"
                st.rerun()
    
    with col2:
        # Broker Status
        st.markdown("### 🔗 Broker Status")
        
        for broker, data in st.session_state.brokers.items():
            status_color = "#10B981" if data['status'] == 'Connected' else "#EF4444"
            st.markdown(f"""
            <div style="background: white; border-left: 4px solid {status_color}; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <strong>{broker}</strong><br>
                <span style="color: {status_color};">● {data['status']}</span><br>
                Balance: ${data['balance']:,}<br>
                Positions: {data['positions']}
            </div>
            """, unsafe_allow_html=True)
        
        # Recent Activity
        st.markdown("### 📈 Recent Activity")
        
        activities = [
            "🟢 BUY 1.0 EURUSD @ 1.0845",
            "🔴 SELL 0.5 GBPUSD @ 1.2650",
            "✅ Closed XAUUSD +$125",
            "🤖 Auto trade: USDJPY",
            "📊 Backtest completed"
        ]
        
        for activity in activities:
            st.markdown(f"• {activity}")

elif st.session_state.page == "Trading":
    # Trading Terminal Header
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Account Balance", f"${st.session_state.portfolio['balance']:,.0f}")
    with col2:
        st.metric("Used Margin", f"${st.session_state.portfolio['margin']:,.0f}")
    with col3:
        st.metric("Free Margin", f"${st.session_state.portfolio['equity'] - st.session_state.portfolio['margin']:,.0f}")
    with col4:
        margin_level = (st.session_state.portfolio['equity'] / st.session_state.portfolio['margin']) * 100 if st.session_state.portfolio['margin'] > 0 else 0
        st.metric("Margin Level", f"{margin_level:.0f}%")
    
    # Trading Interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Market Watch")
        
        # Market data table
        market_data = []
        for symbol in st.session_state.symbols:
            bid = random.uniform(1.0800, 1.0900) if 'USD' in symbol else random.uniform(2600, 2700)
            ask = bid + random.uniform(0.0001, 0.001) * bid
            change = random.uniform(-0.5, 0.5)
            
            market_data.append({
                'Symbol': symbol,
                'Bid': f"{bid:.4f}" if 'USD' in symbol else f"{bid:.2f}",
                'Ask': f"{ask:.4f}" if 'USD' in symbol else f"{ask:.2f}",
                'Spread': f"{(ask-bid)*10000:.1f}" if 'USD' in symbol else f"{ask-bid:.1f}",
                'Change': f"{change:+.2f}%"
            })
        
        df = pd.DataFrame(market_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Order Entry
        st.markdown("### 📝 Order Entry")
        
        order_col1, order_col2, order_col3, order_col4 = st.columns(4)
        
        with order_col1:
            order_symbol = st.selectbox("Symbol", st.session_state.symbols, key="order_symbol")
            order_type = st.selectbox("Type", ["Market", "Limit", "Stop"], key="order_type")
        
        with order_col2:
            order_side = st.selectbox("Side", ["BUY", "SELL"], key="order_side")
            order_volume = st.number_input("Volume", 0.01, 100.0, 1.0, 0.01, key="order_volume")
        
        with order_col3:
            if order_type != "Market":
                order_price = st.number_input("Price", 0.0001, 10000.0, 1.0000, 0.0001, key="order_price")
            order_sl = st.number_input("Stop Loss", 0.0, 1000.0, 0.0, 1.0, key="order_sl")
        
        with order_col4:
            order_tp = st.number_input("Take Profit", 0.0, 1000.0, 0.0, 1.0, key="order_tp")
            broker = st.selectbox("Broker", list(st.session_state.brokers.keys()), key="order_broker")
        
        if st.button("🚀 Place Order", key="place_order", use_container_width=True):
            st.success(f"✅ {order_side} {order_volume} {order_symbol} order placed!")
    
    with col2:
        st.markdown("### 💼 Open Positions")
        
        if st.session_state.portfolio['positions']:
            for i, pos in enumerate(st.session_state.portfolio['positions'][-5:]):
                pnl_color = "#10B981" if pos.get('pnl', 0) > 0 else "#EF4444"
                st.markdown(f"""
                <div style="background: white; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {pnl_color};">
                    <strong>{pos.get('symbol', 'N/A')} {pos.get('type', 'N/A')}</strong><br>
                    Volume: {pos.get('volume', 0)}<br>
                    Entry: {pos.get('entry_price', 0):.4f}<br>
                    P&L: <span style="color: {pnl_color};">${pos.get('pnl', 0):.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No open positions")
        
        st.markdown("### 📋 Pending Orders")
        st.info("No pending orders")

elif st.session_state.page == "Charts":
    # Chart Controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        chart_symbol = st.selectbox("Symbol", st.session_state.symbols, key="chart_symbol")
    with col2:
        timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "1H", "4H", "1D"], index=3, key="chart_tf")
    with col3:
        chart_type = st.selectbox("Type", ["Candlestick", "Line", "OHLC"], key="chart_type")
    with col4:
        period = st.selectbox("Period", ["1D", "1W", "1M", "3M"], index=1, key="chart_period")
    
    # Generate Chart Data
    periods = {"1D": 24, "1W": 168, "1M": 720, "3M": 2160}
    num_points = periods[period]
    
    dates = pd.date_range(start=datetime.now() - timedelta(hours=num_points), periods=num_points, freq='h')
    base_price = 1.0850 if 'USD' in chart_symbol else 2650.00
    
    # Generate OHLC data
    prices = []
    current_price = base_price
    
    for i, date in enumerate(dates):
        change = np.random.normal(0, 0.001) * current_price
        current_price += change
        
        high = current_price + random.uniform(0, 0.002) * current_price
        low = current_price - random.uniform(0, 0.002) * current_price
        open_price = prices[-1]['close'] if prices else current_price
        close = current_price
        
        prices.append({
            'datetime': date, 'open': open_price, 'high': high, 
            'low': low, 'close': close, 'volume': random.randint(100, 1000)
        })
    
    df = pd.DataFrame(prices)
    
    # Create Chart
    fig = go.Figure()
    
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df['datetime'], open=df['open'], high=df['high'],
            low=df['low'], close=df['close'], name=chart_symbol
        ))
    elif chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['close'], mode='lines',
            name=chart_symbol, line=dict(color='#3B82F6', width=2)
        ))
    
    # Technical Indicators
    indicator_col1, indicator_col2, indicator_col3 = st.columns(3)
    
    with indicator_col1:
        if st.checkbox("Moving Average", key="show_ma"):
            ma_period = st.number_input("MA Period", 1, 200, 20, key="ma_period")
            df['ma'] = df['close'].rolling(window=ma_period).mean()
            fig.add_trace(go.Scatter(
                x=df['datetime'], y=df['ma'], mode='lines',
                name=f'MA({ma_period})', line=dict(color='#F59E0B', width=1)
            ))
    
    with indicator_col2:
        if st.checkbox("Bollinger Bands", key="show_bb"):
            bb_period = st.number_input("BB Period", 1, 50, 20, key="bb_period")
            df['bb_middle'] = df['close'].rolling(window=bb_period).mean()
            df['bb_std'] = df['close'].rolling(window=bb_period).std()
            df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
            df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
            
            fig.add_trace(go.Scatter(x=df['datetime'], y=df['bb_upper'], mode='lines', name='BB Upper', line=dict(color='#EF4444', width=1, dash='dash')))
            fig.add_trace(go.Scatter(x=df['datetime'], y=df['bb_lower'], mode='lines', name='BB Lower', line=dict(color='#EF4444', width=1, dash='dash'), fill='tonexty'))
    
    with indicator_col3:
        show_volume = st.checkbox("Volume", key="show_volume")
    
    fig.update_layout(
        title=f"{chart_symbol} - {timeframe} - {period}",
        template='plotly_dark',
        height=500,
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Volume Chart
    if show_volume:
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(x=df['datetime'], y=df['volume'], name='Volume', marker_color='#10B981'))
        volume_fig.update_layout(title="Volume", template='plotly_dark', height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(volume_fig, use_container_width=True)

elif st.session_state.page == "Auto Trade":
    # Auto Trading Status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        auto_enabled = st.session_state.get('auto_enabled', False)
        status_text = "🟢 ACTIVE" if auto_enabled else "🔴 INACTIVE"
        st.markdown(f"**Auto Trading:** {status_text}")
    
    with col2:
        st.metric("Trades Today", st.session_state.get('auto_trades_today', 0))
    
    with col3:
        st.metric("Profit Today", f"${st.session_state.get('auto_profit_today', 0):.2f}")
    
    with col4:
        if auto_enabled:
            if st.button("⏸️ Stop", key="stop_auto"):
                st.session_state.auto_enabled = False
                st.rerun()
        else:
            if st.button("🚀 Start", key="start_auto"):
                st.session_state.auto_enabled = True
                st.rerun()
    
    # Auto Trading Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Trading Settings")
        
        max_trades = st.number_input("Max Trades/Day", 1, 1000, 50, key="auto_max_trades")
        risk_per_trade = st.slider("Risk per Trade (%)", 0.1, 10.0, 2.0, 0.1, key="auto_risk")
        symbols = st.multiselect("Trading Symbols", st.session_state.symbols, default=st.session_state.symbols[:3], key="auto_symbols")
        timeframes = st.multiselect("Timeframes", ["1M", "5M", "15M", "1H"], default=["5M", "15M"], key="auto_timeframes")
    
    with col2:
        st.markdown("### 🎯 Strategy Settings")
        
        strategy = st.selectbox("Strategy", ["MA Crossover", "RSI Mean Reversion", "Bollinger Bands"], key="auto_strategy")
        
        if strategy == "MA Crossover":
            fast_ma = st.number_input("Fast MA", 1, 100, 10, key="fast_ma")
            slow_ma = st.number_input("Slow MA", 1, 200, 20, key="slow_ma")
        elif strategy == "RSI Mean Reversion":
            rsi_period = st.number_input("RSI Period", 1, 50, 14, key="rsi_period")
            oversold = st.number_input("Oversold", 1, 50, 30, key="oversold")
            overbought = st.number_input("Overbought", 50, 99, 70, key="overbought")
        
        stop_loss = st.number_input("Stop Loss (pips)", 1, 1000, 50, key="auto_sl")
        take_profit = st.number_input("Take Profit (pips)", 1, 1000, 100, key="auto_tp")
    
    # Performance Chart
    st.markdown("### 📊 Auto Trading Performance")
    
    # Generate sample performance data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
    equity_curve = []
    current_equity = 10000
    
    for date in dates:
        daily_return = np.random.normal(0.001, 0.02)
        current_equity *= (1 + daily_return)
        equity_curve.append(current_equity)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=equity_curve, mode='lines',
        name='Equity Curve', line=dict(color='#10B981', width=2),
        fill='tonexty', fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    fig.update_layout(
        title="30-Day Auto Trading Performance",
        template='plotly_dark',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Copy Trade":
    st.markdown("### 👥 Copy Trading")
    
    # Signal Providers
    providers = [
        {"name": "🏆 ProTrader", "return": 15.2, "followers": 1250, "risk": 6, "fee": 29},
        {"name": "📈 GoldMaster", "return": 22.8, "followers": 890, "risk": 8, "fee": 39},
        {"name": "💎 ForexKing", "return": 18.5, "followers": 2100, "risk": 5, "fee": 25},
        {"name": "🚀 CryptoBot", "return": 31.2, "followers": 650, "risk": 9, "fee": 49}
    ]
    
    for provider in providers:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"**{provider['name']}**")
            st.markdown(f"Risk: {provider['risk']}/10")
        
        with col2:
            st.metric("Monthly Return", f"{provider['return']}%")
        
        with col3:
            st.metric("Followers", f"{provider['followers']:,}")
        
        with col4:
            st.metric("Fee", f"${provider['fee']}/mo")
        
        with col5:
            if st.button("📋 Subscribe", key=f"sub_{provider['name']}", use_container_width=True):
                st.success(f"✅ Subscribed to {provider['name']}!")
        
        st.markdown("---")

elif st.session_state.page == "Backtest":
    st.markdown("### 🔄 Strategy Backtesting")
    
    # Backtest Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Basic Settings")
        
        backtest_symbol = st.selectbox("Symbol", st.session_state.symbols, key="backtest_symbol")
        timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "1H", "4H", "1D"], index=3, key="backtest_tf")
        start_date = st.date_input("Start Date", datetime(2024, 1, 1), key="backtest_start")
        end_date = st.date_input("End Date", datetime(2024, 12, 31), key="backtest_end")
        initial_balance = st.number_input("Initial Balance", 1000, 1000000, 10000, key="backtest_balance")
    
    with col2:
        st.markdown("#### 🎯 Strategy Parameters")
        
        strategy_type = st.selectbox("Strategy", ["MA Crossover", "RSI Mean Reversion", "Bollinger Bands"], key="backtest_strategy")
        
        if strategy_type == "MA Crossover":
            fast_ma = st.number_input("Fast MA", 1, 100, 10, key="backtest_fast_ma")
            slow_ma = st.number_input("Slow MA", 1, 200, 20, key="backtest_slow_ma")
        
        stop_loss = st.number_input("Stop Loss (pips)", 1, 1000, 50, key="backtest_sl")
        take_profit = st.number_input("Take Profit (pips)", 1, 1000, 100, key="backtest_tp")
    
    if st.button("🚀 Run Backtest", key="run_backtest", use_container_width=True):
        with st.spinner("Running backtest..."):
            time.sleep(2)
            
            # Generate sample results
            total_return = random.uniform(-10, 40)
            win_rate = random.uniform(45, 75)
            num_trades = random.randint(50, 200)
            max_drawdown = random.uniform(5, 25)
            
            st.success("✅ Backtest completed!")
            
            # Results
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Return", f"{total_return:.1f}%")
            with col2:
                st.metric("Win Rate", f"{win_rate:.1f}%")
            with col3:
                st.metric("Total Trades", num_trades)
            with col4:
                st.metric("Max Drawdown", f"{max_drawdown:.1f}%")

elif st.session_state.page == "Arbitrage":
    st.markdown("### 🥇 XAUUSD Arbitrage")
    
    # Arbitrage Status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        arb_active = st.session_state.get('arb_active', False)
        status = "🟢 MONITORING" if arb_active else "🔴 INACTIVE"
        st.markdown(f"**Status:** {status}")
    
    with col2:
        st.metric("Opportunities", st.session_state.get('arb_opportunities', 0))
    
    with col3:
        st.metric("Today's P&L", f"${st.session_state.get('arb_pnl', 0):.2f}")
    
    with col4:
        if arb_active:
            if st.button("⏸️ Stop", key="stop_arb"):
                st.session_state.arb_active = False
                st.rerun()
        else:
            if st.button("🚀 Start", key="start_arb"):
                st.session_state.arb_active = True
                st.rerun()
    
    # Price Feeds
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏦 Broker A - Divit Capital")
        bid_a = random.uniform(2650, 2660)
        ask_a = bid_a + random.uniform(0.5, 2.0)
        
        st.metric("Bid", f"${bid_a:.2f}")
        st.metric("Ask", f"${ask_a:.2f}")
        st.metric("Spread", f"${ask_a - bid_a:.2f}")
    
    with col2:
        st.markdown("#### 🏦 Broker B - Kama Capital")
        bid_b = random.uniform(2650, 2660)
        ask_b = bid_b + random.uniform(0.5, 2.0)
        
        st.metric("Bid", f"${bid_b:.2f}")
        st.metric("Ask", f"${ask_b:.2f}")
        st.metric("Spread", f"${ask_b - bid_b:.2f}")
    
    # Arbitrage Opportunity
    price_diff = abs(bid_a - ask_b)
    if price_diff > 1.0:
        st.success(f"🚨 ARBITRAGE OPPORTUNITY: ${price_diff:.2f} profit potential!")
    else:
        st.info(f"Price difference: ${price_diff:.2f} (below threshold)")

elif st.session_state.page == "LP Bridge":
    st.markdown("### 🌐 LP Bridge Manager")
    
    # LP Status
    lps = [
        {"name": "Prime LP 1", "status": "Connected", "liquidity": 5000000, "latency": 12},
        {"name": "ECN Bridge", "status": "Connected", "liquidity": 3000000, "latency": 8},
        {"name": "Market Maker", "status": "Disconnected", "liquidity": 0, "latency": 0}
    ]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        connected = len([lp for lp in lps if lp['status'] == 'Connected'])
        st.metric("Connected LPs", f"{connected}/{len(lps)}")
    
    with col2:
        total_liquidity = sum([lp['liquidity'] for lp in lps])
        st.metric("Total Liquidity", f"${total_liquidity:,}")
    
    with col3:
        connected_lps = [lp for lp in lps if lp['status'] == 'Connected']
        avg_latency = np.mean([lp['latency'] for lp in connected_lps]) if connected_lps else 0
        st.metric("Avg Latency", f"{avg_latency:.1f}ms")
    
    # LP Details
    for lp in lps:
        status_color = "#10B981" if lp['status'] == 'Connected' else "#EF4444"
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"**{lp['name']}**")
            st.markdown(f"<span style='color: {status_color};'>● {lp['status']}</span>", unsafe_allow_html=True)
        
        with col2:
            st.metric("Liquidity", f"${lp['liquidity']:,}")
        
        with col3:
            st.metric("Latency", f"{lp['latency']}ms" if lp['latency'] > 0 else "N/A")
        
        with col4:
            if lp['status'] == 'Connected':
                if st.button("🔌 Disconnect", key=f"disc_{lp['name']}", use_container_width=True):
                    st.warning(f"⚠️ {lp['name']} disconnected!")
            else:
                if st.button("🔌 Connect", key=f"conn_{lp['name']}", use_container_width=True):
                    st.success(f"✅ {lp['name']} connected!")
        
        st.markdown("---")

elif st.session_state.page == "Settings":
    st.markdown("### ⚙️ Platform Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 Appearance")
        
        theme = st.selectbox("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1, key="theme_select")
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()
        
        auto_refresh = st.checkbox("Auto Refresh", True, key="auto_refresh_setting")
        refresh_interval = st.slider("Refresh Interval (seconds)", 1, 10, 3, key="refresh_interval")
        
        st.markdown("#### 🔔 Notifications")
        
        email_alerts = st.checkbox("Email Alerts", True, key="email_alerts")
        push_notifications = st.checkbox("Push Notifications", True, key="push_notifications")
        trade_confirmations = st.checkbox("Trade Confirmations", True, key="trade_confirmations")
    
    with col2:
        st.markdown("#### 🔐 Security")
        
        two_factor = st.checkbox("Two-Factor Authentication", False, key="two_factor")
        session_timeout = st.selectbox("Session Timeout", ["15 min", "30 min", "1 hour", "4 hours"], index=1, key="session_timeout")
        
        st.markdown("#### 💾 Data Management")
        
        if st.button("📊 Export Data", key="export_data", use_container_width=True):
            st.success("✅ Data exported successfully!")
        
        if st.button("🗑️ Clear Cache", key="clear_cache", use_container_width=True):
            st.success("✅ Cache cleared!")
        
        if st.button("🔄 Reset Settings", key="reset_settings", use_container_width=True):
            st.warning("⚠️ Settings reset to default!")

# ====
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**🚀 Yantra Trading Platform**")
    st.markdown("*Multi-Broker Trading System*")

with footer_col2:
    st.markdown(f"**📊 Status:** 🟢 Online")
    st.markdown(f"**⏰ Updated:** {datetime.now().strftime('%H:%M:%S')}")

with footer_col3:
    st.markdown("**👤 User:** Rishi Brillant")
    st.markdown(f"**🌐 Theme:** {st.session_state.theme}")

# ===== ULTRA-COMPACT CSS =====
st.markdown("""
<style>
/* IMPORT FONT */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* HIDE STREAMLIT ELEMENTS */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* GLOBAL SETTINGS */
.stApp {
    background: #f8f9fa !important;
    font-family: 'Inter', sans-serif !important;
}

/* ULTRA-COMPACT MAIN CONTAINER */
.main .block-container {
    padding: 0.5rem 1rem !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
}

/* COMPACT SIDEBAR */
section[data-testid="stSidebar"] {
    background: #1a1a1a !important;
    padding: 0.5rem !important;
    width: 200px !important;
}

section[data-testid="stSidebar"] .stMarkdown h1 {
    color: white !important;
    font-size: 1.5rem !important;
    margin: 0 0 1rem 0 !important;
    text-align: center !important;
}

section[data-testid="stSidebar"] .stButton {
    margin: 0.1rem !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: white !important;
    border: 1px solid #333 !important;
    border-radius: 6px !important;
    width: 100% !important;
    padding: 0.3rem !important;
    font-size: 0.8rem !important;
    height: 35px !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #333 !important;
}

/* ULTRA-COMPACT COLUMNS */
.stColumns {
    gap: 0.5rem !important;
    margin: 0.25rem 0 !important;
}

.stColumn {
    padding: 0 !important;
}

/* COMPACT METRICS */
[data-testid="metric-container"] {
    background: white !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    padding: 0.75rem !important;
    margin: 0.25rem 0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}

[data-testid="metric-container"] [data-testid="metric-value"] {
    color: #111827 !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    margin: 0 !important;
}

[data-testid="metric-container"] [data-testid="metric-label"] {
    color: #6b7280 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

[data-testid="metric-container"] [data-testid="metric-delta"] {
    color: #059669 !important;
    background: #ecfdf5 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

/* COMPACT CHARTS */
.plotly-graph-div {
    background: white !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    margin: 0.25rem 0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}

/* COMPACT BUTTONS */
.stButton > button {
    background: #111827 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    margin: 0.1rem 0 !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: #374151 !important;
    transform: translateY(-1px) !important;
}

/* COMPACT TABLES */
.dataframe {
    background: white !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    margin: 0.25rem 0 !important;
    font-size: 0.8rem !important;
}

.dataframe th {
    background: #f9fafb !important;
    color: #374151 !important;
    font-weight: 600 !important;
    padding: 0.5rem !important;
    border-bottom: 1px solid #e5e7eb !important;
}

.dataframe td {
    background: white !important;
    color: #111827 !important;
    padding: 0.5rem !important;
    border-bottom: 1px solid #f3f4f6 !important;
}

/* COMPACT HEADERS */
.stMarkdown h1 {
    color: #111827 !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    margin: 0.5rem 0 !important;
    line-height: 1.2 !important;
}

.stMarkdown h2 {
    color: #111827 !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    margin: 0.5rem 0 !important;
    line-height: 1.3 !important;
}

.stMarkdown h3 {
    color: #111827 !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    margin: 0.5rem 0 !important;
    line-height: 1.3 !important;
}

.stMarkdown h4 {
    color: #374151 !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin: 0.25rem 0 !important;
}

.stMarkdown p {
    color: #4b5563 !important;
    margin: 0.25rem 0 !important;
    line-height: 1.4 !important;
}

/* COMPACT FORM INPUTS */
.stSelectbox, .stNumberInput, .stTextInput {
    margin: 0.25rem 0 !important;
}

.stSelectbox > div > div > select,
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    background: white !important;
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
    color: #111827 !important;
    padding: 0.5rem !important;
    font-size: 0.85rem !important;
    height: 38px !important;
}

.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus,
.stTextInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

/* COMPACT CHECKBOXES */
.stCheckbox {
    margin: 0.25rem 0 !important;
}

.stCheckbox > label {
    color: #374151 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* COMPACT SLIDERS */
.stSlider {
    margin: 0.25rem 0 !important;
}

.stSlider > label {
    color: #374151 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* REMOVE EXCESSIVE SPACING */
.element-container {
    margin: 0.1rem 0 !important;
}

.stMarkdown {
    margin: 0.1rem 0 !important;
}

/* COMPACT DIVIDERS */
hr {
    margin: 0.5rem 0 !important;
    border: none !important;
    border-top: 1px solid #e5e7eb !important;
}

/* COMPACT TABS */
.stTabs [data-baseweb="tab-list"] {
    background: white !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    margin: 0.25rem 0 !important;
    padding: 0.25rem !important;
}

.stTabs [data-baseweb="tab"] {
    color: #6b7280 !important;
    padding: 0.5rem 1rem !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

.stTabs [aria-selected="true"] {
    background: #111827 !important;
    color: white !important;
}

/* COMPACT EXPANDERS */
.streamlit-expanderHeader {
    background: #f9fafb !important;
    color: #111827 !important;
    font-weight: 600 !important;
    padding: 0.75rem !important;
    border-radius: 8px 8px 0 0 !important;
}

.streamlit-expanderContent {
    background: white !important;
    padding: 0.75rem !important;
    border: 1px solid #e5e7eb !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

/* COMPACT ALERTS */
.stSuccess, .stInfo, .stWarning, .stError {
    padding: 0.5rem !important;
    margin: 0.25rem 0 !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
}

/* RESPONSIVE DESIGN */
@media (max-width: 768px) {
    .main .block-container {
        padding: 0.25rem 0.5rem !important;
    }
    
    .stColumns {
        gap: 0.25rem !important;
    }
    
    [data-testid="metric-container"] {
        padding: 0.5rem !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 1.25rem !important;
    }
}

/* HIDE SCROLLBARS BUT KEEP FUNCTIONALITY */
::-webkit-scrollbar {
    width: 4px;
    height: 4px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: #d1d5db;
    border-radius: 2px;
}

::-webkit-scrollbar-thumb:hover {
    background: #9ca3af;
}
</style>
""", unsafe_allow_html=True)

# ===== AUTO-REFRESH LOGIC =====
if st.session_state.get('auto_refresh', True) and st.session_state.page in ["Dashboard", "Trading", "Charts", "Auto Trade", "Arbitrage"]:
    time.sleep(3)
    st.rerun()

print("✅ Yantra Trading Platform V2.0 loaded successfully!")
