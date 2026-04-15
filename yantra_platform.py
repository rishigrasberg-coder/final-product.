import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import threading
from datetime import datetime
from typing import Dict, List
from enum import Enum
from dataclasses import dataclass
import random
import json
import asyncio
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import socket
import struct

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Yantra Trading Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ENUMS AND DATA CLASSES =====

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class ConnectionStatus(Enum):
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting"
    ERROR = "Error"

class RoutingMode(Enum):
    BEST_PRICE = "Best Price"
    LOWEST_LATENCY = "Lowest Latency"
    LOAD_BALANCED = "Load Balanced"
    ROUND_ROBIN = "Round Robin"

@dataclass
class PriceTick:
    symbol: str
    bid: float
    ask: float
    timestamp: datetime
    source: str
    latency_ms: float

@dataclass
class Position:
    id: int
    symbol: str
    side: OrderSide
    volume: float
    entry_price: float
    current_price: float
    pnl: float
    broker: str
    open_time: datetime
    sl: Optional[float] = None
    tp: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    magic_number: int = 0

@dataclass
class Order:
    id: int
    symbol: str
    order_type: OrderType
    side: OrderSide
    volume: float
    price: Optional[float]
    sl: Optional[float]
    tp: Optional[float]
    broker: str
    status: str
    timestamp: datetime
    comment: str = ""
    magic_number: int = 0

@dataclass
class LiquidityProvider:
    id: int
    name: str
    lp_type: str
    protocol: str
    status: ConnectionStatus
    available_liquidity: float
    total_liquidity: float
    utilization: float
    min_trade_size: float
    max_trade_size: float
    commission: float
    supported_symbols: List[str]
    latency_ms: float
    uptime: float
    daily_volume: float
    fill_rate: float
    avg_spread: float
    rejections_today: int
    session_id: Optional[str] = None
    fix_session: Optional[Any] = None

@dataclass
class ArbitrageOpportunity:
    timestamp: datetime
    buy_broker: str
    sell_broker: str
    symbol: str
    buy_price: float
    sell_price: float
    spread: float
    profit_potential: float
    volume: float
    status: str
    executed: bool
    execution_time_ms: float = 0

@dataclass
class MT5Account:
    login: int
    name: str
    server: str
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    leverage: int
    currency: str
    positions_count: int
    orders_count: int
    status: ConnectionStatus
    ping_ms: float
    last_update: datetime

# ===== MT5 MANAGER API INTEGRATION =====

class MT5ManagerAPI:
    """
    MT5 Manager API wrapper for broker connectivity
    This connects to the MT5 Manager API for full broker access
    """
    
    def __init__(self):
        self.connected = False
        self.server: str = ""
        self.login: int = 0
        self.password: str = ""
        self.accounts: Dict[int, MT5Account] = {}
        self.positions: Dict[int, List[Position]] = {}
        self.orders: Dict[int, List[Order]] = {}
        self.price_feeds: Dict[str, PriceTick] = {}
        self._lock = threading.Lock()
        
    def connect(self, server: str, login: int, password: str) -> bool:
        """
        Connect to MT5 Manager API
        In production, this would use the actual MT5 Manager API DLL
        """
        try:
            self.server = server
            self.login = login
            self.password = password
            
            # In production, you would call:
            # self.manager = MT5Manager()
            # result = self.manager.Connect(server, login, password)
            
            # For now, simulate connection
            self.connected = True
            
            # Initialize account data
            self._initialize_account_data()
            
            return True
            
        except Exception as e:
            print(f"MT5 Manager connection error: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from MT5 Manager"""
        self.connected = False
        self.accounts.clear()
        self.positions.clear()
        
    def _initialize_account_data(self):
        """Initialize account data after connection"""
        # In production, this would fetch real data
        pass
    
    def get_symbols(self) -> List[str]:
        """Get available trading symbols"""
        return [
            'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF', 'EURGBP',
            'EURJPY', 'GBPJPY', 'AUDJPY', 'CADJPY', 'CHFJPY', 'EURCHF', 'AUDCAD', 'GBPCAD',
            'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'US30', 'US500', 'NAS100', 'GER40',
            'UK100', 'FRA40', 'JPN225', 'AUS200', 'BTCUSD', 'ETHUSD', 'LTCUSD', 'ADAUSD'
        ]
    
    def get_price(self, symbol: str) -> Optional[PriceTick]:
        """Get current price for a symbol"""
        with self._lock:
            return self.price_feeds.get(symbol)
    
    def update_price(self, symbol: str, bid: float, ask: float, source: str = "MT5"):
        """Update price feed"""
        with self._lock:
            self.price_feeds[symbol] = PriceTick(
                symbol=symbol,
                bid=bid,
                ask=ask,
                timestamp=datetime.now(),
                source=source,
                latency_ms=random.uniform(1, 20)
            )
    
    def place_order(self, account_login: int, symbol: str, side: OrderSide, 
                   volume: float, order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None, sl: Optional[float] = None,
                   tp: Optional[float] = None, magic: int = 0, comment: str = "") -> Optional[int]:
        """
        Place an order through MT5 Manager API
        Returns order ticket or None if failed
        """
        try:
            # In production:
            # trade_request = {
            #     "action": MT5_TRADE_ACTION_DEAL,
            #     "symbol": symbol,
            #     "volume": volume,
            #     "type": MT5_ORDER_TYPE_BUY if side == OrderSide.BUY else MT5_ORDER_TYPE_SELL,
            #     "price": price,
            #     "sl": sl,
            #     "tp": tp,
            #     "magic": magic,
            #     "comment": comment
            # }
            # result = self.manager.OrderSend(trade_request)
            
            # Simulate order placement
            order_ticket = random.randint(100000, 999999)
            return order_ticket
            
        except Exception as e:
            print(f"Order placement error: {e}")
            return None
    
    def close_position(self, position_id: int) -> bool:
        """Close a position by ID"""
        try:
            # In production:
            # result = self.manager.PositionClose(position_id)
            return True
        except Exception as e:
            print(f"Position close error: {e}")
            return False
    
    def get_all_positions(self, account_login: int) -> List[Position]:
        """Get all open positions for an account"""
        return self.positions.get(account_login, [])
    
    def get_all_orders(self, account_login: int) -> List[Order]:
        """Get all pending orders for an account"""
        return self.orders.get(account_login, [])
    
    def get_account_info(self, account_login: int) -> Optional[MT5Account]:
        """Get account information"""
        return self.accounts.get(account_login)
    
    def modify_position(self, position_id: int, sl: Optional[float] = None, 
                       tp: Optional[float] = None) -> bool:
        """Modify position SL/TP"""
        try:
            # In production:
            # result = self.manager.PositionModify(position_id, sl, tp)
            return True
        except Exception as e:
            print(f"Position modify error: {e}")
            return False


# ===== FIX PROTOCOL ENGINE =====

class ConnectionStatus(Enum):
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    ERROR = "Error"

@dataclass
class PriceTick:
    symbol: str
    bid: float
    ask: float
    timestamp: datetime
    source: str
    latency_ms: float = 0.0

@dataclass
class LiquidityProvider:
    name: str
    status: str
    supported_symbols: List[str]
class FIXEngine:
    """
    FIX Protocol engine for LP connectivity
    Implements FIX 4.4 for liquidity provider connections
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.connected_lps: Dict[str, LiquidityProvider] = {}
        self.price_feeds: Dict[str, Dict[str, PriceTick]] = {}  # LP -> Symbol -> Price
        self.execution_reports: List[Dict] = []
        self._sequence_number = 0
        self._lock = threading.Lock()
        
    def create_session(self, lp_name: str, sender_comp_id: str, target_comp_id: str,
                      host: str, port: int, username: str = "", password: str = "") -> str:
        """Create a new FIX session"""
        session_id = f"{sender_comp_id}_{target_comp_id}"
        
        self.sessions[session_id] = {
            "lp_name": lp_name,
            "sender_comp_id": sender_comp_id,
            "target_comp_id": target_comp_id,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "status": ConnectionStatus.DISCONNECTED,
            "heartbeat_interval": 30,
            "last_heartbeat": None,
            "socket": None,
            "sequence_in": 0,
            "sequence_out": 0
        }
        
        return session_id
    
    def connect_session(self, session_id: str) -> bool:
        """Connect a FIX session"""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        
        try:
            # In production, this would establish TCP connection and send Logon message
            # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # sock.connect((session["host"], session["port"]))
            # self._send_logon(session_id)
            
            session["status"] = ConnectionStatus.CONNECTED
            session["last_heartbeat"] = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"FIX session connect error: {e}")
            session["status"] = ConnectionStatus.ERROR
            return False
    
    def disconnect_session(self, session_id: str) -> bool:
        """Disconnect a FIX session"""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        
        try:
            # In production, send Logout message and close socket
            # self._send_logout(session_id)
            # session["socket"].close()
            
            session["status"] = ConnectionStatus.DISCONNECTED
            return True
            
        except Exception as e:
            print(f"FIX session disconnect error: {e}")
            return False
    
    def _build_fix_message(self, msg_type: str, session_id: str, fields: Dict[int, str]) -> str:
        """Build a FIX message"""
        session = self.sessions[session_id]
        
        with self._lock:
            self._sequence_number += 1
            seq_num = self._sequence_number

            def update_market_data(self, session_id: str, symbol: str, bid: float, ask: float):
        """Update market data from LP"""
        
        # Create session if it doesn't exist
        if session_id not in self.sessions:
            # Extract LP name from session_id (remove "session_" prefix)
            lp_name = session_id.replace("session_", "")
            self.sessions[session_id] = {
                "lp_name": lp_name,
                "sender_comp_id": f"{lp_name}_SENDER",
                "target_comp_id": f"{lp_name}_TARGET", 
                "host": "localhost",
                "port": 9999,
                "username": "",
                "password": "",
                "status": ConnectionStatus.CONNECTED,
                "heartbeat_interval": 30,
                "last_heartbeat": datetime.now(),
                "socket": None,
                "sequence_in": 0,
                "sequence_out": 0
            }
        
        lp_name = self.sessions[session_id]["lp_name"]
        
        if lp_name not in self.price_feeds:
            self.price_feeds[lp_name] = {}
        
        self.price_feeds[lp_name][symbol] = PriceTick(
            symbol=symbol,
            bid=bid,
            ask=ask,
            timestamp=datetime.now(),
            source=lp_name,
            latency_ms=random.uniform(1, 15)
        )

    def get_best_prices(self, symbol: str) -> Dict[str, float]:
        """Get best bid/ask across all LPs for a symbol"""
        best_bid = 0
        best_ask = float('inf')
        
        for lp_name, symbols in self.price_feeds.items():
            if symbol in symbols:
                tick = symbols[symbol]
                if tick.bid > best_bid:
                    best_bid = tick.bid
                if tick.ask < best_ask:
                    best_ask = tick.ask
        
        return {"bid": best_bid, "ask": best_ask}

    def _build_fix_message(self, msg_type: str, session_id: str, fields: Dict[int, str]) -> str:
        
        # Standard header fields
        header = {
            8: "FIX.4.4",  # BeginString
            9: 0,  # BodyLength (calculated later)
            35: msg_type,  # MsgType
            49: session["sender_comp_id"],  # SenderCompID
            56: session["target_comp_id"],  # TargetCompID
            34: str(seq_num),  # MsgSeqNum
            52: datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]  # SendingTime
        }
        
        # Combine header and body
        all_fields = {**header, **fields}
        
        # Build message body
        body = ""
        for tag, value in all_fields.items():
            if tag not in [8, 9, 10]:  # Exclude BeginString, BodyLength, Checksum
                body += f"{tag}={value}\x01"
        
        # Calculate body length
        body_length = len(body)
        
        # Build final message
        message = f"8=FIX.4.4\x019={body_length}\x01{body}"
        
        # Calculate checksum
        checksum = sum(ord(c) for c in message) % 256
        message += f"10={checksum:03d}\x01"
        
        return message
    
    def _send_logon(self, session_id: str) -> bool:
        """Send FIX Logon message"""
        session = self.sessions[session_id]
        
        fields = {
            98: "0",  # EncryptMethod (None)
            108: str(session["heartbeat_interval"]),  # HeartBtInt
        }
        
        if session.get("username"):
            fields[553] = session["username"]  # Username
        if session.get("password"):
            fields[554] = session["password"]  # Password
        
        message = self._build_fix_message("A", session_id, fields)
        
        # In production, send over socket
        # session["socket"].send(message.encode())
        
        return True
    
    def send_new_order(self, session_id: str, symbol: str, side: OrderSide,
                      volume: float, order_type: OrderType, price: Optional[float] = None,
                      client_order_id: Optional[str] = None) -> Optional[str]:
        """Send new order request (FIX MsgType D)"""
        if session_id not in self.sessions:
            return None
            
        if not client_order_id:
            client_order_id = f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # FIX order sides
        fix_side = "1" if side == OrderSide.BUY else "2"
        
        # FIX order types
        fix_ord_type_map = {
            OrderType.MARKET: "1",
            OrderType.LIMIT: "2",
            OrderType.STOP: "3",
            OrderType.STOP_LIMIT: "4"
        }
        fix_ord_type = fix_ord_type_map.get(order_type, "1")
        
        fields = {
            11: client_order_id,  # ClOrdID
            55: symbol,  # Symbol
            54: fix_side,  # Side
            60: datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3],  # TransactTime
            40: fix_ord_type,  # OrdType
            38: str(volume),  # OrderQty
        }
        
        if price is not None:
            fields[44] = str(price)  # Price
        
        message = self._build_fix_message("D", session_id, fields)
        
        # In production, send over socket
        # self.sessions[session_id]["socket"].send(message.encode())
        
        return client_order_id
    
    def subscribe_market_data(self, session_id: str, symbols: List[str]) -> bool:
        """Subscribe to market data (FIX MsgType V)"""
        if session_id not in self.sessions:
            return False
        
        md_req_id = f"MD_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        fields = {
            262: md_req_id,  # MDReqID
            263: "1",  # SubscriptionRequestType (Snapshot + Updates)
            264: "0",  # MarketDepth (Full book)
            265: "1",  # MDUpdateType (Incremental)
            267: "2",  # NoMDEntryTypes
            269: "0",  # MDEntryType (Bid)
            269: "1",  # MDEntryType (Offer) - would be repeated in real FIX
        }
        
        # Add symbols
        fields[146] = str(len(symbols))  # NoRelatedSym
        for i, symbol in enumerate(symbols):
            fields[55] = symbol  # Symbol
        
        message = self._build_fix_message("V", session_id, fields)
        
        # In production, send over socket
        
        return True
    
    def process_execution_report(self, session_id: str, message: str) -> Optional[Dict]:
        """Process execution report (FIX MsgType 8)"""
        # Parse FIX message
        fields = {}
        for field in message.split('\x01'):
            if '=' in field:
                tag, value = field.split('=', 1)
                fields[int(tag)] = value
        
        exec_report = {
            "order_id": fields.get(37),  # OrderID
            "client_order_id": fields.get(11),  # ClOrdID
            "exec_id": fields.get(17),  # ExecID
            "exec_type": fields.get(150),  # ExecType
            "ord_status": fields.get(39),  # OrdStatus
            "symbol": fields.get(55),  # Symbol
            "side": fields.get(54),  # Side
            "qty": fields.get(38),  # OrderQty
            "price": fields.get(44),  # Price
            "avg_price": fields.get(6),  # AvgPx
            "last_qty": fields.get(32),  # LastQty
            "last_px": fields.get(31),  # LastPx
            "timestamp": datetime.now()
        }
        
        self.execution_reports.append(exec_report)
        
        return exec_report
    
def update_market_data(self, session_id: str, symbol: str, bid: float, ask: float):
    """Update market data from LP"""
    
    # Initialize sessions if it doesn't exist
    if not hasattr(self, 'sessions'):
        self.sessions = {}
    
    # Create session if it doesn't exist
    if session_id not in self.sessions:
        # Extract LP name from session_id (remove "session_" prefix)
        lp_name = session_id.replace("session_", "")
        self.sessions[session_id] = {"lp_name": lp_name}
    
    lp_name = self.sessions[session_id]["lp_name"]
    
    if lp_name not in self.price_feeds:
        self.price_feeds[lp_name] = {}
    
    self.price_feeds[lp_name][symbol] = PriceTick(
        symbol=symbol,
        bid=bid,
        ask=ask,
        timestamp=datetime.now(),
        source=lp_name,
        latency_ms=random.uniform(1, 15)
    )    
    def get_best_price(self, symbol: str) -> Optional[Dict]:
        """Get best bid/ask across all LPs"""
        best_bid = None
        best_ask = None
        best_bid_lp = None
        best_ask_lp = None
        
        for lp_name, symbols in self.price_feeds.items():
            if symbol in symbols:
                tick = symbols[symbol]
                
                if best_bid is None or tick.bid > best_bid:
                    best_bid = tick.bid
                    best_bid_lp = lp_name
                
                if best_ask is None or tick.ask < best_ask:
                    best_ask = tick.ask
                    best_ask_lp = lp_name
        
        if best_bid and best_ask:
            return {
                "symbol": symbol,
                "best_bid": best_bid,
                "best_bid_lp": best_bid_lp,
                "best_ask": best_ask,
                "best_ask_lp": best_ask_lp,
                "spread": best_ask - best_bid
            }
        
        return None


# ===== LATENCY ARBITRAGE ENGINE =====

class LatencyArbitrageEngine:
    """
    High-frequency latency arbitrage engine
    Detects and exploits price discrepancies between brokers
    """
    
    def __init__(self, mt5_manager: MT5ManagerAPI, fix_engine: FIXEngine):
        self.mt5 = mt5_manager
        self.fix = fix_engine
        self.monitoring = False
        self.opportunities: List[ArbitrageOpportunity] = []
        self.settings = {
            "min_profit_threshold": 1.0,  # Minimum profit in USD
            "max_position_size": 1.0,  # Maximum lot size
            "max_slippage": 0.5,  # Maximum acceptable slippage
            "max_daily_trades": 100,
            "max_exposure": 100000,
            "auto_execute": False,
            "symbols": ["XAUUSD", "EURUSD", "GBPUSD"],
            "price_sources": []  # List of broker names to monitor
        }
        self.stats = {
            "total_opportunities": 0,
            "executed_trades": 0,
            "today_pnl": 0.0,
            "total_pnl": 0.0,
            "success_rate": 0.0,
            "avg_profit": 0.0,
            "avg_execution_time": 0.0
        }
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
    def start_monitoring(self):
        """Start arbitrage monitoring"""
        if self._running:
            return
            
        self._running = True
        self.monitoring = True
        self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._thread.start()
    
    def stop_monitoring(self):
        """Stop arbitrage monitoring"""
        self._running = False
        self.monitoring = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                for symbol in self.settings["symbols"]:
                    self._check_arbitrage_opportunity(symbol)
                time.sleep(0.001)  # 1ms polling interval
            except Exception as e:
                print(f"Arbitrage monitoring error: {e}")
                time.sleep(0.1)
    
    def _check_arbitrage_opportunity(self, symbol: str):
        """Check for arbitrage opportunity on a symbol"""
        # Get prices from all sources
        prices: Dict[str, PriceTick] = {}
        
        # Get MT5 price
        mt5_price = self.mt5.get_price(symbol)
        if mt5_price:
            prices["MT5"] = mt5_price
        
        # Get LP prices
        for lp_name, lp_prices in self.fix.price_feeds.items():
            if symbol in lp_prices:
                prices[lp_name] = lp_prices[symbol]
        
        if len(prices) < 2:
            return
        
        # Find arbitrage opportunities
        best_bid = None
        best_bid_source = None
        best_ask = None
        best_ask_source = None
        
        for source, tick in prices.items():
            if best_bid is None or tick.bid > best_bid:
                best_bid = tick.bid
                best_bid_source = source
            
            if best_ask is None or tick.ask < best_ask:
                best_ask = tick.ask
                best_ask_source = source
        
        # Check if there's an arbitrage opportunity
        if best_bid_source != best_ask_source and best_bid > best_ask:
            spread = best_bid - best_ask
            profit_potential = spread * self.settings["max_position_size"] * 100  # Simplified
            
            if profit_potential >= self.settings["min_profit_threshold"]:
                opportunity = ArbitrageOpportunity(
                    timestamp=datetime.now(),
                    buy_broker=best_ask_source,
                    sell_broker=best_bid_source,
                    symbol=symbol,
                    buy_price=best_ask,
                    sell_price=best_bid,
                    spread=spread,
                    profit_potential=profit_potential,
                    volume=self.settings["max_position_size"],
                    status="Detected",
                    executed=False
                )
                
                with self._lock:
                    self.opportunities.append(opportunity)
                    self.stats["total_opportunities"] += 1
                
                if self.settings["auto_execute"]:
                    self._execute_arbitrage(opportunity)
    
    def _execute_arbitrage(self, opportunity: ArbitrageOpportunity) -> bool:
        """Execute an arbitrage trade"""
        start_time = datetime.now()
        
        try:
            # Place buy order on cheaper source
            # Place sell order on more expensive source
            
            # In production, this would be parallel execution
            # buy_result = self._place_order(opportunity.buy_broker, ...)
            # sell_result = self._place_order(opportunity.sell_broker, ...)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            opportunity.executed = True
            opportunity.status = "Executed"
            opportunity.execution_time_ms = execution_time
            
            with self._lock:
                self.stats["executed_trades"] += 1
                self.stats["today_pnl"] += opportunity.profit_potential
                self.stats["total_pnl"] += opportunity.profit_potential
                
                # Update success rate
                if self.stats["total_opportunities"] > 0:
                    self.stats["success_rate"] = (
                        self.stats["executed_trades"] / self.stats["total_opportunities"]
                    ) * 100
                
                # Update average profit
                if self.stats["executed_trades"] > 0:
                    self.stats["avg_profit"] = (
                        self.stats["total_pnl"] / self.stats["executed_trades"]
                    )
                
                # Update average execution time
                self.stats["avg_execution_time"] = (
                    (self.stats["avg_execution_time"] * (self.stats["executed_trades"] - 1) + execution_time)
                    / self.stats["executed_trades"]
                )
            
            return True
            
        except Exception as e:
            print(f"Arbitrage execution error: {e}")
            opportunity.status = "Failed"
            return False
    
    def execute_manual(self, opportunity_index: int) -> bool:
        """Manually execute an arbitrage opportunity"""
        if opportunity_index >= len(self.opportunities):
            return False
        
        opportunity = self.opportunities[opportunity_index]
        if opportunity.executed:
            return False
        
        return self._execute_arbitrage(opportunity)
    
    def get_recent_opportunities(self, limit: int = 50) -> List[ArbitrageOpportunity]:
        """Get recent arbitrage opportunities"""
        with self._lock:
            return list(reversed(self.opportunities[-limit:]))
    
    def update_settings(self, **kwargs):
        """Update arbitrage settings"""
        self.settings.update(kwargs)
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        with self._lock:
            self.stats["today_pnl"] = 0.0


# ===== LP BRIDGE / SMART ORDER ROUTER =====

class LPBridge:
    """
    Liquidity Provider Bridge - Similar to Centroid/T4B
    Handles LP connectivity, price aggregation, and smart order routing
    """
    
    def __init__(self, fix_engine: FIXEngine):
        self.fix = fix_engine
        self.liquidity_providers: Dict[str, LiquidityProvider] = {}
        self.routing_mode = RoutingMode.BEST_PRICE
        self.settings = {
            "failover_enabled": True,
            "failover_timeout_ms": 1000,
            "load_balancing": True,
            "max_lp_utilization": 80.0,
            "max_order_size": 1000000,
            "position_limits": True,
            "max_net_position": 10000000,
            "credit_limits": True,
            "max_credit_exposure": 5000000,
            "price_tolerance": 1.0,
            "execution_timeout_ms": 3000,
            "retry_attempts": 3,
            "markup_enabled": False,
            "markup_pips": 0.0
        }
        self.order_book: Dict[str, List[Dict]] = {}  # Symbol -> Orders
        self.execution_log: List[Dict] = []
        self._lock = threading.Lock()
        
    def add_lp(self, lp: LiquidityProvider) -> bool:
        """Add a liquidity provider"""
        self.liquidity_providers[lp.name] = lp
        return True
    
    def remove_lp(self, lp_name: str) -> bool:
        """Remove a liquidity provider"""
        if lp_name in self.liquidity_providers:
            del self.liquidity_providers[lp_name]
            return True
        return False
    
    def connect_lp(self, lp_name: str, fix_session_id: str) -> bool:
        """Connect to a liquidity provider"""
        if lp_name not in self.liquidity_providers:
            return False
        
        lp = self.liquidity_providers[lp_name]
        
        if self.fix.connect_session(fix_session_id):
            lp.status = ConnectionStatus.CONNECTED
            lp.session_id = fix_session_id
            return True
        
        return False
    
    def disconnect_lp(self, lp_name: str) -> bool:
        """Disconnect from a liquidity provider"""
        if lp_name not in self.liquidity_providers:
            return False
        
        lp = self.liquidity_providers[lp_name]
        
        if lp.session_id and self.fix.disconnect_session(lp.session_id):
            lp.status = ConnectionStatus.DISCONNECTED
            lp.session_id = None
            return True
        
        return False
    
    def get_aggregated_price(self, symbol: str) -> Optional[Dict]:
        """Get aggregated price from all LPs"""
        bids = []
        asks = []
        
        for lp_name, lp in self.liquidity_providers.items():
            if lp.status != ConnectionStatus.CONNECTED:
                continue
            
            if symbol not in lp.supported_symbols:
                continue
            
            # Get price from FIX engine
            if lp_name in self.fix.price_feeds and symbol in self.fix.price_feeds[lp_name]:
                tick = self.fix.price_feeds[lp_name][symbol]
                bids.append({"lp": lp_name, "price": tick.bid, "latency": tick.latency_ms})
                asks.append({"lp": lp_name, "price": tick.ask, "latency": tick.latency_ms})
        
        if not bids or not asks:
            return None
        
        # Sort by price
        bids.sort(key=lambda x: x["price"], reverse=True)  # Highest bid first
        asks.sort(key=lambda x: x["price"])  # Lowest ask first
        
        # Apply markup if enabled
        markup = self.settings["markup_pips"] * 0.0001 if self.settings["markup_enabled"] else 0
        
        return {
            "symbol": symbol,
            "best_bid": bids[0]["price"] - markup,
            "best_bid_lp": bids[0]["lp"],
            "best_ask": asks[0]["price"] + markup,
            "best_ask_lp": asks[0]["lp"],
            "spread": asks[0]["price"] - bids[0]["price"] + (markup * 2),
            "depth": {
                "bids": bids[:5],
                "asks": asks[:5]
            }
        }
    
    def route_order(self, symbol: str, side: OrderSide, volume: float,
                   order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None) -> Optional[Dict]:
        """
        Route order to best LP based on routing mode
        """
        # Check volume limits
        if volume * 100000 > self.settings["max_order_size"]:
            return {"error": "Order size exceeds maximum limit"}
        
        # Get aggregated price
        agg_price = self.get_aggregated_price(symbol)
        if not agg_price:
            return {"error": "No price available"}
        
        # Select LP based on routing mode
        target_lp = None
        target_price = None
        
        if self.routing_mode == RoutingMode.BEST_PRICE:
            if side == OrderSide.BUY:
                target_lp = agg_price["best_ask_lp"]
                target_price = agg_price["best_ask"]
            else:
                target_lp = agg_price["best_bid_lp"]
                target_price = agg_price["best_bid"]
        
        elif self.routing_mode == RoutingMode.LOWEST_LATENCY:
            # Find LP with lowest latency
            best_latency = float('inf')
            for lp_name, lp in self.liquidity_providers.items():
                if lp.status == ConnectionStatus.CONNECTED and lp.latency_ms < best_latency:
                    if symbol in lp.supported_symbols:
                        best_latency = lp.latency_ms
                        target_lp = lp_name
        
        elif self.routing_mode == RoutingMode.LOAD_BALANCED:
            # Find LP with lowest utilization
            best_utilization = 100.0
            for lp_name, lp in self.liquidity_providers.items():
                if lp.status == ConnectionStatus.CONNECTED and lp.utilization < best_utilization:
                    if symbol in lp.supported_symbols:
                        best_utilization = lp.utilization
                        target_lp = lp_name
        
        elif self.routing_mode == RoutingMode.ROUND_ROBIN:
            # Simple round-robin selection
            connected_lps = [
                lp_name for lp_name, lp in self.liquidity_providers.items()
                if lp.status == ConnectionStatus.CONNECTED and symbol in lp.supported_symbols
            ]
            if connected_lps:
                target_lp = connected_lps[len(self.execution_log) % len(connected_lps)]
        
        if not target_lp:
            return {"error": "No suitable LP found"}
        
        # Get LP and session
        lp = self.liquidity_providers[target_lp]
        
        if not lp.session_id:
            return {"error": "LP not connected"}
        
        # Check LP utilization
        if lp.utilization >= self.settings["max_lp_utilization"]:
            if self.settings["failover_enabled"]:
                # Try failover to another LP
                return self._failover_order(symbol, side, volume, order_type, price, target_lp)
            return {"error": "LP utilization exceeded"}
        
        # Send order via FIX
        client_order_id = self.fix.send_new_order(
            lp.session_id, symbol, side, volume, order_type, price
        )
        
        if client_order_id:
            execution = {
                "order_id": client_order_id,
                "symbol": symbol,
                "side": side.value,
                "volume": volume,
                "order_type": order_type.value,
                "price": price or target_price,
                "lp": target_lp,
                "timestamp": datetime.now(),
                "status": "Sent"
            }
            self.execution_log.append(execution)
            
            # Update LP utilization
            lp.utilization += (volume * 100000 / lp.total_liquidity) * 100
            
            return execution
        
        return {"error": "Order send failed"}
    
    def _failover_order(self, symbol: str, side: OrderSide, volume: float,
                       order_type: OrderType, price: Optional[float],
                       excluded_lp: str) -> Optional[Dict]:
        """Failover order to another LP"""
        for lp_name, lp in self.liquidity_providers.items():
            if lp_name == excluded_lp:
                continue
            
            if lp.status != ConnectionStatus.CONNECTED:
                continue
            
            if symbol not in lp.supported_symbols:
                continue
            
            if lp.utilization >= self.settings["max_lp_utilization"]:
                continue
            
            # Try this LP
            return self.route_order(symbol, side, volume, order_type, price)
        
        return {"error": "No failover LP available"}
    
    def get_lp_status(self) -> List[Dict]:
        """Get status of all LPs"""
        status_list = []
        
        for lp_name, lp in self.liquidity_providers.items():
            status_list.append({
                "name": lp.name,
                "type": lp.lp_type,
                "protocol": lp.protocol,
                "status": lp.status.value,
                "available_liquidity": lp.available_liquidity,
                "total_liquidity": lp.total_liquidity,
                "utilization": lp.utilization,
                "latency_ms": lp.latency_ms,
                "fill_rate": lp.fill_rate,
                "rejections_today": lp.rejections_today
            })
        
        return status_list


# ===== COMPLETE SESSION STATE INITIALIZATION =====

def init_session_state():
    """Initialize ALL session state data"""
    
    # Core navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    if 'theme' not in st.session_state:
        st.session_state.theme = "Dark"
    
    # Initialize MT5 Manager
    if 'mt5_manager' not in st.session_state:
        st.session_state.mt5_manager = MT5ManagerAPI()
    
    # Initialize FIX Engine
    if 'fix_engine' not in st.session_state:
        st.session_state.fix_engine = FIXEngine()
    
    # Initialize Latency Arbitrage Engine
    if 'arbitrage_engine' not in st.session_state:
        st.session_state.arbitrage_engine = LatencyArbitrageEngine(
            st.session_state.mt5_manager,
            st.session_state.fix_engine
        )
    
    # Initialize LP Bridge
    if 'lp_bridge' not in st.session_state:
        st.session_state.lp_bridge_engine = LPBridge(st.session_state.fix_engine)
    
    # MT5 Connection Status
    if 'mt5_connected' not in st.session_state:
        st.session_state.mt5_connected = False
    
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
                {'id': 101, 'symbol': 'USDJPY', 'type': 'BUY LIMIT', 'volume': 1.0, 'price': 149.50, 'sl': 149.00, 'tp': 150.00, 'broker': 'Kama Capital', 'status': 'Pending'},
                {'id': 102, 'symbol': 'AUDUSD', 'type': 'SELL STOP', 'volume': 0.5, 'price': 0.6500, 'sl': 0.6550, 'tp': 0.6450, 'broker': 'Divit Capital', 'status': 'Pending'}
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
                'login': 12345678,
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
                'login': 87654321,
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
                'login': 0,
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
    
    # XAUUSD Arbitrage system - Using new engine
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
            'opportunities': [],
            'stats': {
                'total_opportunities': 0,
                'today_pnl': 0.0,
                'total_pnl': 0.0,
                'success_rate': 0.0,
                'avg_profit': 0.0
            }
        }
    
    # LP Bridge system - Using new engine
    if 'lp_bridge' not in st.session_state:
        st.session_state.lp_bridge = {
            'liquidity_providers': [
                {
                    'id': 1,
                    'name': 'Prime Broker 1',
                    'type': 'Prime Broker',
                    'protocol': 'FIX 4.4',
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
                    'rejections_today': 2,
                    'fix_host': '192.168.1.100',
                    'fix_port': 9876,
                    'sender_comp_id': 'YANTRA',
                    'target_comp_id': 'PRIMEBR1'
                },
                {
                    'id': 2,
                    'name': 'ECN Bridge',
                    'type': 'ECN',
                    'protocol': 'FIX 4.4',
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
                    'rejections_today': 0,
                    'fix_host': '192.168.1.101',
                    'fix_port': 9877,
                    'sender_comp_id': 'YANTRA',
                    'target_comp_id': 'ECNBRIDGE'
                },
                {
                    'id': 3,
                    'name': 'Market Maker',
                    'type': 'Market Maker',
                    'protocol': 'FIX 4.4',
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
                    'rejections_today': 0,
                    'fix_host': '192.168.1.102',
                    'fix_port': 9878,
                    'sender_comp_id': 'YANTRA',
                    'target_comp_id': 'MM1'
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
                'retry_attempts': 3,
                'markup_enabled': False,
                'markup_pips': 0.0
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
    
    # Risk management
    if 'risk_management' not in st.session_state:
        st.session_state.risk_management = {
            'max_position_size': 10.0,
            'max_symbol_exposure': 20,
            'max_total_exposure': 100,
            'risk_per_trade': 2.0,
            'max_daily_loss': 1000,
            'max_consecutive_losses': 5,
            'margin_call_level': 100,
            'stop_out_level': 50,
            'auto_sl': True,
            'auto_tp': True,
            'auto_hedge': False,
            'emergency_close': True
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
    
    # Trading paused flag
    if 'trading_paused' not in st.session_state:
        st.session_state.trading_paused = False

init_session_state()


# ===== PRICE FEED SIMULATOR (FOR DEMO) =====

def simulate_price_feeds():
    """Simulate real-time price feeds for demonstration"""
    symbols_base = {
        'EURUSD': 1.0850,
        'GBPUSD': 1.2650,
        'USDJPY': 149.50,
        'AUDUSD': 0.6600,
        'USDCAD': 1.3550,
        'XAUUSD': 2655.00,
        'XAGUSD': 31.50,
        'BTCUSD': 45000.00
    }
    
    for symbol, base_price in symbols_base.items():
        # Add small random movement
        movement = random.uniform(-0.0005, 0.0005) * base_price
        new_price = base_price + movement
        spread = base_price * 0.0002  # 2 pip spread
        
        # Update MT5 Manager
        st.session_state.mt5_manager.update_price(
            symbol, 
            new_price - spread/2, 
            new_price + spread/2,
            "MT5"
        )
        
        # Update FIX Engine (simulate LP prices)
        for lp in st.session_state.lp_bridge['liquidity_providers']:
            if lp['status'] == 'Connected' and symbol in lp['supported_symbols']:
                # Each LP has slightly different prices
                lp_movement = random.uniform(-0.0002, 0.0002) * base_price
                lp_price = new_price + lp_movement
                lp_spread = base_price * (0.0001 + random.uniform(0, 0.0002))
                
                # Initialize fix_engine if it doesn't exist
                if 'fix_engine' not in st.session_state:
                    st.session_state.fix_engine = FIXEngine()
                
                st.session_state.fix_engine.update_market_data(
                    f"session_{lp['name']}",
                    symbol,
                    lp_price - lp_spread/2,
                    lp_price + lp_spread/2
                )
# Call price simulation
simulate_price_feeds()


# ===== COMPACT SIDEBAR WITH ALL NAVIGATION =====

with st.sidebar:
    st.markdown("# 🚀 YANTRA")
    st.markdown("**Professional Trading Suite**")
    
    # Connection status indicator
    mt5_status = "🟢" if st.session_state.mt5_connected else "🔴"
    st.markdown(f"MT5 Manager: {mt5_status}")
    
    # Main navigation pages
    main_pages = [
        ("📊", "Dashboard"), 
        ("💹", "Trading Terminal"), 
        ("📈", "Advanced Charts"),
        ("📊", "Tick Charts"), 
        ("🤖", "Auto Trading"), 
        ("👥", "Copy Trading"),
        ("🔄", "Backtesting"), 
        ("🥇", "XAUUSD Arbitrage"), 
        ("🌐", "LP Bridge Manager"),
        ("⚠️", "Risk Management"),
        ("📊", "Analytics"),
        ("⚙️", "Settings"),
        ("🔗", "MT5 Manager")
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
        short_name = name.split()[0][:8]
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


# ===== MT5 MANAGER CONNECTION PAGE =====

if st.session_state.page == "MT5 Manager":
    st.markdown("### 🔗 MT5 Manager API Connection")
    
    st.markdown("""
    #### About MT5 Manager API
    
    The MT5 Manager API provides full broker-level access to MetaTrader 5 servers including:
    - **Account Management**: View/manage all client accounts
    - **Position Management**: Monitor and control all positions
    - **Order Management**: Place, modify, cancel orders for any account
    - **Real-time Data**: Access tick-by-tick price feeds
    - **Risk Management**: Set margin requirements, leverage, limits
    - **Reporting**: Generate detailed trade reports
    
    ⚠️ **Important**: You need MT5 Manager API credentials from your broker (not regular MT5 trading credentials).
    """)
    
    st.markdown("---")
    
    # Connection form
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Primary Broker Connection")
        
        broker1_server = st.text_input("Server Address", "DivitCapital-Live", key="broker1_server")
        broker1_login = st.number_input("Manager Login", 0, 999999999, 12345678, key="broker1_login")
        broker1_password = st.text_input("Manager Password", type="password", key="broker1_password")
        
        if st.button("🔌 Connect Primary Broker", key="connect_broker1", use_container_width=True):
            with st.spinner("Connecting to MT5 Manager..."):
                time.sleep(1)  # Simulate connection
                
                result = st.session_state.mt5_manager.connect(
                    broker1_server, broker1_login, broker1_password
                )
                
                if result:
                    st.session_state.mt5_connected = True
                    st.session_state.brokers['Divit Capital']['status'] = 'Connected'
                    st.success("✅ Connected to Divit Capital MT5 Manager!")
                else:
                    st.error("❌ Connection failed. Check credentials.")
    
    with col2:
        st.markdown("#### Secondary Broker Connection")
        
        broker2_server = st.text_input("Server Address", "KamaCapital-Live", key="broker2_server")
        broker2_login = st.number_input("Manager Login", 0, 999999999, 87654321, key="broker2_login")
        broker2_password = st.text_input("Manager Password", type="password", key="broker2_password")
        
        if st.button("🔌 Connect Secondary Broker", key="connect_broker2", use_container_width=True):
            with st.spinner("Connecting to MT5 Manager..."):
                time.sleep(1)
                st.session_state.brokers['Kama Capital']['status'] = 'Connected'
                st.success("✅ Connected to Kama Capital MT5 Manager!")
    
    st.markdown("---")
    
    # Connection status
    st.markdown("#### 📊 Connection Status")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.markdown("**Divit Capital**")
        divit_status = st.session_state.brokers['Divit Capital']['status']
        status_color = "#10B981" if divit_status == 'Connected' else "#EF4444"
        st.markdown(f"<span style='color: {status_color}; font-size: 1.2em;'>● {divit_status}</span>", unsafe_allow_html=True)
        if divit_status == 'Connected':
            st.metric("Ping", f"{st.session_state.brokers['Divit Capital']['ping']}ms")
            st.metric("Positions", st.session_state.brokers['Divit Capital']['positions'])
    
    with status_col2:
        st.markdown("**Kama Capital**")
        kama_status = st.session_state.brokers['Kama Capital']['status']
        status_color = "#10B981" if kama_status == 'Connected' else "#EF4444"
        st.markdown(f"<span style='color: {status_color}; font-size: 1.2em;'>● {kama_status}</span>", unsafe_allow_html=True)
        if kama_status == 'Connected':
            st.metric("Ping", f"{st.session_state.brokers['Kama Capital']['ping']}ms")
            st.metric("Positions", st.session_state.brokers['Kama Capital']['positions'])
    
    with status_col3:
        st.markdown("**LP Bridge**")
        lp_status = st.session_state.brokers['LP Bridge']['status']
        status_color = "#10B981" if lp_status == 'Connected' else "#EF4444"
        st.markdown(f"<span style='color: {status_color}; font-size: 1.2em;'>● {lp_status}</span>", unsafe_allow_html=True)
        if lp_status == 'Connected':
            st.metric("Ping", f"{st.session_state.brokers['LP Bridge']['ping']}ms")
    
    st.markdown("---")
    
    # Manager API features
    st.markdown("#### 🛠️ Manager API Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("**Account Operations**")
        st.markdown("- View all accounts")
        st.markdown("- Check balances/equity")
        st.markdown("- Credit operations")
        st.markdown("- Leverage changes")
        
        if st.button("📋 View All Accounts", key="view_accounts", use_container_width=True):
            st.info("Account list would appear here")
    
    with feature_col2:
        st.markdown("**Position Operations**")
        st.markdown("- View all positions")
        st.markdown("- Close positions")
        st.markdown("- Modify SL/TP")
        st.markdown("- Partial close")
        
        if st.button("📊 View All Positions", key="view_all_positions", use_container_width=True):
            st.info("Position list would appear here")
    
    with feature_col3:
        st.markdown("**Reporting**")
        st.markdown("- Trade history")
        st.markdown("- Daily statements")
        st.markdown("- Risk reports")
        st.markdown("- Performance analytics")
        
        if st.button("📈 Generate Report", key="generate_report", use_container_width=True):
            st.info("Report generation would start here")


# ===== MAIN CONTENT - DASHBOARD =====

elif st.session_state.page == "Dashboard":
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
        # Market Overview
        st.markdown("### 📊 Market Overview")
        
        # Create market heatmap
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF', 'EURGBP']
        timeframes = ['1H', '4H', '1D', '1W']
        
        # Generate price change data
        heatmap_data = np.random.uniform(-2, 2, (len(symbols), len(timeframes)))
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=timeframes,
            y=symbols,
            colorscale='RdYlGn',
            zmid=0,
            text=np.round(heatmap_data, 2),
            texttemplate="%{text}%",
            textfont={"size": 12},
            colorbar=dict(title="Change %")
        ))
        
        fig.update_layout(
            title="Market Performance Heatmap (% Change)",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=400,
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
                # Get current price
                tick = st.session_state.mt5_manager.get_price(quick_symbol)
                entry_price = tick.ask if tick else random.uniform(1.0, 2.0)
                
                new_position = {
                    'id': len(st.session_state.portfolio['positions']) + 1,
                    'symbol': quick_symbol,
                    'type': 'BUY',
                    'volume': quick_volume,
                    'entry_price': entry_price,
                    'current_price': entry_price,
                    'pnl': 0.0,
                    'broker': quick_broker,
                    'open_time': datetime.now()
                }
                st.session_state.portfolio['positions'].append(new_position)
                st.success(f"✅ BUY {quick_volume} {quick_symbol} @ {entry_price:.5f}")
                st.rerun()
        
        with trade_col5:
            if st.button("🔴 SELL", key="quick_sell", use_container_width=True):
                tick = st.session_state.mt5_manager.get_price(quick_symbol)
                entry_price = tick.bid if tick else random.uniform(1.0, 2.0)
                
                new_position = {
                    'id': len(st.session_state.portfolio['positions']) + 1,
                    'symbol': quick_symbol,
                    'type': 'SELL',
                    'volume': quick_volume,
                    'entry_price': entry_price,
                    'current_price': entry_price,
                    'pnl': 0.0,
                    'broker': quick_broker,
                    'open_time': datetime.now()
                }
                st.session_state.portfolio['positions'].append(new_position)
                st.success(f"✅ SELL {quick_volume} {quick_symbol} @ {entry_price:.5f}")
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
            <div style="background: rgba(255,255,255,0.05); border-left: 4px solid {status_color}; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border: 1px solid #333;">
                <h4 style="color: #FFFFFF; margin: 0 0 0.5rem 0;">{'🟢' if broker_data['status'] == 'Connected' else '🔴'} {broker_name}</h4>
                <p style="color: {status_color}; margin: 0.25rem 0;">● {broker_data['status']}</p>
                <p style="color: #CCCCCC; margin: 0.25rem 0; font-size: 0.9rem;">Server: {broker_data['server']}</p>
                <p style="color: #FFFFFF; margin: 0.25rem 0;">Balance: ${broker_data['balance']:,}</p>
                <p style="color: #FFFFFF; margin: 0.25rem 0;">Equity: ${broker_data['equity']:,}</p>
                <p style="color: #FFFFFF; margin: 0.25rem 0;">Positions: {broker_data['positions']}</p>
                <p style="color: #FFFFFF; margin: 0.25rem 0;">Ping: {broker_data['ping']}ms</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Open positions
        st.markdown("### 📊 Open Positions")
        
        if st.session_state.portfolio['positions']:
            for pos in st.session_state.portfolio['positions']:
                pnl_color = "#10B981" if pos['pnl'] > 0 else "#EF4444"
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border-left: 4px solid {pnl_color}; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border: 1px solid #333;">
                    <h4 style="color: #FFFFFF; margin: 0 0 0.5rem 0;">{pos['symbol']} - {pos['type']}</h4>
                    <p style="color: #CCCCCC; margin: 0.25rem 0;">Volume: <span style="color: #FFFFFF;">{pos['volume']}</span></p>
                    <p style="color: #CCCCCC; margin: 0.25rem 0;">Entry: <span style="color: #FFFFFF;">{pos['entry_price']:.5f}</span></p>
                    <p style="color: #CCCCCC; margin: 0.25rem 0;">Current: <span style="color: #FFFFFF;">{pos['current_price']:.5f}</span></p>
                    <p style="color: {pnl_color}; margin: 0.25rem 0; font-weight: bold;">P&L: ${pos['pnl']:+.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No open positions")
        
        # Pending orders
        st.markdown("### 📋 Pending Orders")
        
        if st.session_state.portfolio.get('pending_orders', []):
            for order in st.session_state.portfolio.get('pending_orders', []):
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border-left: 4px solid #3B82F6; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border: 1px solid #333;">
                    <h4 style="color: #FFFFFF; margin: 0 0 0.5rem 0;">{order['symbol']} - {order['type']}</h4>
                    <p style="color: #CCCCCC; margin: 0.25rem 0;">Volume: <span style="color: #FFFFFF;">{order['volume']}</span></p>
                    <p style="color: #CCCCCC; margin: 0.25rem 0;">Price: <span style="color: #FFFFFF;">{order['price']}</span></p>
                    <p style="color: #3B82F6; margin: 0.25rem 0; font-weight: bold;">Status: {order.get('status', 'Pending')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No pending orders")
        
        # Recent activity
        st.markdown("### 📈 Recent Activity")
        
        recent_activities = [
            "🟢 BUY 1.0 EURUSD @ 1.0845 - Divit Capital",
            "🔴 SELL 0.5 GBPUSD @ 1.2650 - Kama Capital", 
            "✅ Closed XAUUSD +$125.50 profit",
            "🤖 Auto trade: RSI signal on USDJPY",
            "🔄 Arbitrage opportunity detected"
        ]
        
        for activity in recent_activities:
            st.markdown(f"• {activity}")


# ===== TRADING TERMINAL =====

elif st.session_state.page == "Trading Terminal":
    # Header metrics
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
        
        market_data = []
        for symbol in st.session_state.mt5_symbols[:15]:
            tick = st.session_state.mt5_manager.get_price(symbol)
            if tick:
                spread = (tick.ask - tick.bid)
                if 'JPY' in symbol:
                    spread_pips = spread * 100
                elif 'XAU' in symbol or 'BTC' in symbol:
                    spread_pips = spread
                else:
                    spread_pips = spread * 10000
                
                market_data.append({
                    'Symbol': symbol,
                    'Bid': f"{tick.bid:.5f}" if 'XAU' not in symbol and 'BTC' not in symbol else f"{tick.bid:.2f}",
                    'Ask': f"{tick.ask:.5f}" if 'XAU' not in symbol and 'BTC' not in symbol else f"{tick.ask:.2f}",
                    'Spread': f"{spread_pips:.1f}",
                    'Source': tick.source,
                    'Latency': f"{tick.latency_ms:.1f}ms"
                })
            else:
                # Generate fallback data
                if 'XAU' in symbol:
                    base = 2655.0
                elif 'BTC' in symbol:
                    base = 45000.0
                elif 'JPY' in symbol:
                    base = 149.50
                else:
                    base = 1.0850
                
                bid = base + random.uniform(-0.001, 0.001) * base
                ask = bid + random.uniform(0.0001, 0.0005) * base
                
                market_data.append({
                    'Symbol': symbol,
                    'Bid': f"{bid:.5f}" if 'XAU' not in symbol and 'BTC' not in symbol else f"{bid:.2f}",
                    'Ask': f"{ask:.5f}" if 'XAU' not in symbol and 'BTC' not in symbol else f"{ask:.2f}",
                    'Spread': f"{(ask-bid)*10000:.1f}",
                    'Source': 'MT5',
                    'Latency': f"{random.uniform(5, 20):.1f}ms"
                })
        
        market_df = pd.DataFrame(market_data)
        st.dataframe(market_df, use_container_width=True, hide_index=True)
        
        # Order entry
        st.markdown("### 📝 Order Entry")
        
        order_col1, order_col2, order_col3, order_col4 = st.columns(4)
        
        with order_col1:
            order_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="order_symbol")
            order_type = st.selectbox("Order Type", ["Market", "Limit", "Stop", "Stop Limit"], key="order_type")
            order_side = st.selectbox("Side", ["BUY", "SELL"], key="order_side")
        
        with order_col2:
            order_volume = st.number_input("Volume", 0.01, 100.0, 1.0, 0.01, key="order_volume")
            if order_type != "Market":
                order_price = st.number_input("Price", 0.0001, 100000.0, 1.0000, 0.0001, key="order_price")
            else:
                order_price = None
        
        with order_col3:
            order_sl = st.number_input("Stop Loss (pips)", 0.0, 1000.0, 0.0, 1.0, key="order_sl")
            order_tp = st.number_input("Take Profit (pips)", 0.0, 1000.0, 0.0, 1.0, key="order_tp")
        
        with order_col4:
            order_broker = st.selectbox("Broker", list(st.session_state.brokers.keys()), key="order_broker")
            order_comment = st.text_input("Comment", key="order_comment")
        
        # Place order button
        place_col1, place_col2, place_col3 = st.columns(3)
        
        with place_col1:
            if st.button("🚀 Place Order", key="place_order", use_container_width=True):
                tick = st.session_state.mt5_manager.get_price(order_symbol)
                
                if order_type == "Market":
                    entry_price = tick.ask if order_side == "BUY" else tick.bid if tick else random.uniform(1.0, 2.0)
                    
                    new_position = {
                        'id': len(st.session_state.portfolio['positions']) + 1,
                        'symbol': order_symbol,
                        'type': order_side,
                        'volume': order_volume,
                        'entry_price': entry_price,
                        'current_price': entry_price,
                        'pnl': 0.0,
                        'broker': order_broker,
                        'open_time': datetime.now(),
                        'comment': order_comment
                    }
                    st.session_state.portfolio['positions'].append(new_position)
                    st.success(f"✅ {order_side} {order_volume} {order_symbol} @ {entry_price:.5f}")
                else:
                    new_order = {
                        'id': len(st.session_state.portfolio['pending_orders']) + 100,
                        'symbol': order_symbol,
                        'type': f"{order_side} {order_type.upper()}",
                        'volume': order_volume,
                        'price': order_price,
                        'sl': order_sl if order_sl > 0 else None,
                        'tp': order_tp if order_tp > 0 else None,
                        'broker': order_broker,
                        'status': 'Pending',
                        'comment': order_comment
                    }
                    st.session_state.portfolio['pending_orders'].append(new_order)
                    st.success(f"✅ {order_side} {order_type} order placed")
                
                st.rerun()
        
        # Position management
        st.markdown("### 💼 Position Management")
        
        if st.session_state.portfolio['positions']:
            positions_data = []
            for pos in st.session_state.portfolio['positions']:
                positions_data.append({
                    'ID': pos['id'],
                    'Symbol': pos['symbol'],
                    'Type': pos['type'],
                    'Volume': pos['volume'],
                    'Entry': f"{pos['entry_price']:.5f}",
                    'Current': f"{pos['current_price']:.5f}",
                    'P&L': f"${pos['pnl']:+.2f}",
                    'Broker': pos['broker'],
                    'Duration': str(datetime.now() - pos['open_time']).split('.')[0]
                })
            
            positions_df = pd.DataFrame(positions_data)
            st.dataframe(positions_df, use_container_width=True, hide_index=True)
            
            pos_col1, pos_col2, pos_col3 = st.columns(3)
            
            with pos_col1:
                selected_position = st.selectbox(
                    "Select Position",
                    [f"{pos['id']} - {pos['symbol']} {pos['type']}" for pos in st.session_state.portfolio['positions']],
                    key="selected_position"
                )
            
            with pos_col2:
                if st.button("🔒 Close Position", key="close_position", use_container_width=True):
                    if selected_position:
                        pos_id = int(selected_position.split(' - ')[0])
                        st.session_state.portfolio['positions'] = [
                            p for p in st.session_state.portfolio['positions'] if p['id'] != pos_id
                        ]
                        st.success(f"✅ Position {pos_id} closed!")
                        st.rerun()
            
            with pos_col3:
                if st.button("🔄 Close All", key="close_all_positions", use_container_width=True):
                    total_pnl = sum([pos['pnl'] for pos in st.session_state.portfolio['positions']])
                    st.session_state.portfolio['positions'] = []
                    st.success(f"✅ All positions closed! Total P&L: ${total_pnl:+.2f}")
                    st.rerun()
        else:
            st.info("No open positions")
    
    with col2:
        # Order book
        st.markdown("### 📊 Order Book")
        
        selected_ob_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols[:5], key="orderbook_symbol")
        
        tick = st.session_state.mt5_manager.get_price(selected_ob_symbol)
        base_price = tick.bid if tick else 1.0850
        
        orderbook_data = []
        for i in range(10):
            bid_price = base_price - (i * 0.0001)
            ask_price = base_price + (i * 0.0001) + 0.0002
            bid_volume = random.randint(100, 1000) / 100
            ask_volume = random.randint(100, 1000) / 100
            
            orderbook_data.append({
                'Bid Vol': f"{bid_volume:.2f}",
                'Bid': f"{bid_price:.5f}",
                'Ask': f"{ask_price:.5f}",
                'Ask Vol': f"{ask_volume:.2f}"
            })
        
        orderbook_df = pd.DataFrame(orderbook_data)
        st.dataframe(orderbook_df, use_container_width=True, hide_index=True)
        
        # Account summary
        st.markdown("### 💰 Account Summary")
        
        total_volume = sum([pos['volume'] for pos in st.session_state.portfolio['positions']])
        avg_pnl = np.mean([pos['pnl'] for pos in st.session_state.portfolio['positions']]) if st.session_state.portfolio['positions'] else 0
        
        st.metric("Total Volume", f"{total_volume:.2f} lots")
        st.metric("Avg P&L per Position", f"${avg_pnl:.2f}")
        st.metric("Win Rate", "68.5%")


# ===== XAUUSD ARBITRAGE =====

elif st.session_state.page == "XAUUSD Arbitrage":
    st.markdown("### 🥇 Latency Arbitrage Engine")
    
    arb_engine = st.session_state.arbitrage_engine
    
    # Status header
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        status_text = "🟢 MONITORING" if arb_engine.monitoring else "🔴 STOPPED"
        st.markdown(f"**Status:** {status_text}")
    
    with col2:
        st.metric("Today P&L", f"${arb_engine.stats['today_pnl']:+.2f}")
    
    with col3:
        st.metric("Total P&L", f"${arb_engine.stats['total_pnl']:+.2f}")
    
    with col4:
        st.metric("Success Rate", f"{arb_engine.stats['success_rate']:.1f}%")
    
    with col5:
        if arb_engine.monitoring:
            if st.button("⏸️ Stop", key="stop_arbitrage", use_container_width=True):
                arb_engine.stop_monitoring()
                st.rerun()
        else:
            if st.button("🚀 Start", key="start_arbitrage", use_container_width=True):
                arb_engine.start_monitoring()
                st.rerun()
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Price feeds
        st.markdown("### 📊 Real-Time Price Comparison")
        
        # Get prices from all sources
        price_comparison = []
        
        for symbol in ['XAUUSD', 'EURUSD', 'GBPUSD']:
            mt5_tick = st.session_state.mt5_manager.get_price(symbol)
            
            if mt5_tick:
                price_comparison.append({
                    'Symbol': symbol,
                    'Source': 'MT5',
                    'Bid': f"{mt5_tick.bid:.5f}" if 'XAU' not in symbol else f"{mt5_tick.bid:.2f}",
                    'Ask': f"{mt5_tick.ask:.5f}" if 'XAU' not in symbol else f"{mt5_tick.ask:.2f}",
                    'Spread': f"{(mt5_tick.ask - mt5_tick.bid):.5f}" if 'XAU' not in symbol else f"{(mt5_tick.ask - mt5_tick.bid):.2f}",
                    'Latency': f"{mt5_tick.latency_ms:.1f}ms"
                })
            
            # Get LP prices
            for lp_name, lp_prices in st.session_state.fix_engine.price_feeds.items():
                if symbol in lp_prices:
                    lp_tick = lp_prices[symbol]
                    price_comparison.append({
                        'Symbol': symbol,
                        'Source': lp_name,
                        'Bid': f"{lp_tick.bid:.5f}" if 'XAU' not in symbol else f"{lp_tick.bid:.2f}",
                        'Ask': f"{lp_tick.ask:.5f}" if 'XAU' not in symbol else f"{lp_tick.ask:.2f}",
                        'Spread': f"{(lp_tick.ask - lp_tick.bid):.5f}" if 'XAU' not in symbol else f"{(lp_tick.ask - lp_tick.bid):.2f}",
                        'Latency': f"{lp_tick.latency_ms:.1f}ms"
                    })
        
        if price_comparison:
            price_df = pd.DataFrame(price_comparison)
            st.dataframe(price_df, use_container_width=True, hide_index=True)
        else:
            st.info("Waiting for price feeds...")
        
        # Arbitrage opportunities
        st.markdown("### 🎯 Detected Opportunities")
        
        opportunities = arb_engine.get_recent_opportunities(20)
        
        if opportunities:
            opp_data = []
            for i, opp in enumerate(opportunities):
                status_icon = "✅" if opp.executed else "⏳" if opp.status == "Detected" else "❌"
                opp_data.append({
                    'Index': i,
                    'Time': opp.timestamp.strftime('%H:%M:%S.%f')[:-3],
                    'Symbol': opp.symbol,
                    'Buy From': opp.buy_broker,
                    'Sell To': opp.sell_broker,
                    'Spread': f"${opp.spread:.2f}",
                    'Potential': f"${opp.profit_potential:.2f}",
                    'Status': f"{status_icon} {opp.status}",
                    'Exec Time': f"{opp.execution_time_ms:.1f}ms" if opp.executed else "-"
                })
            
            opp_df = pd.DataFrame(opp_data)
            st.dataframe(opp_df, use_container_width=True, hide_index=True)
            
            # Manual execution
            if not arb_engine.settings['auto_execute']:
                exec_col1, exec_col2 = st.columns(2)
                
                with exec_col1:
                    selected_opp = st.number_input("Opportunity Index", 0, len(opportunities)-1, 0, key="selected_opp")
                
                with exec_col2:
                    if st.button("⚡ Execute Selected", key="execute_selected", use_container_width=True):
                        result = arb_engine.execute_manual(selected_opp)
                        if result:
                            st.success("✅ Arbitrage executed!")
                        else:
                            st.error("❌ Execution failed")
                        st.rerun()
        else:
            st.info("No opportunities detected yet. Start monitoring to detect arbitrage opportunities.")
    
    with col2:
        # Settings
        st.markdown("### ⚙️ Arbitrage Settings")
        
        min_profit = st.number_input("Min Profit ($)", 0.1, 100.0, 
            arb_engine.settings['min_profit_threshold'], 0.1, key="arb_min_profit")
        
        max_position = st.number_input("Max Position Size", 0.1, 10.0, 
            arb_engine.settings['max_position_size'], 0.1, key="arb_max_position")
        
        max_slippage = st.number_input("Max Slippage ($)", 0.1, 10.0, 
            arb_engine.settings['max_slippage'], 0.1, key="arb_max_slippage")
        
        auto_execute = st.checkbox("Auto Execute", arb_engine.settings['auto_execute'], key="arb_auto")
        
        # Symbol selection
        st.markdown("#### 📊 Monitor Symbols")
        monitor_symbols = st.multiselect(
            "Symbols",
            st.session_state.mt5_symbols,
            default=arb_engine.settings['symbols'],
            key="arb_symbols"
        )
        
        if st.button("💾 Save Settings", key="save_arb_settings", use_container_width=True):
            arb_engine.update_settings(
                min_profit_threshold=min_profit,
                max_position_size=max_position,
                max_slippage=max_slippage,
                auto_execute=auto_execute,
                symbols=monitor_symbols
            )
            st.success("✅ Settings saved!")
        
        # Statistics
        st.markdown("### 📊 Statistics")
        
        st.metric("Total Opportunities", arb_engine.stats['total_opportunities'])
        st.metric("Executed Trades", arb_engine.stats['executed_trades'])
        st.metric("Avg Profit", f"${arb_engine.stats['avg_profit']:.2f}")
        st.metric("Avg Execution", f"{arb_engine.stats['avg_execution_time']:.1f}ms")
        
        if st.button("🔄 Reset Daily Stats", key="reset_daily", use_container_width=True):
            arb_engine.reset_daily_stats()
            st.success("✅ Daily stats reset!")


# ===== LP BRIDGE MANAGER =====

elif st.session_state.page == "LP Bridge Manager":
    st.markdown("### 🌐 Liquidity Provider Bridge Manager")
    st.markdown("*Similar to Centroid Solutions / T4B Bridge*")
    
    lps = st.session_state.lp_bridge['liquidity_providers']
    
    # Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        connected = len([lp for lp in lps if lp['status'] == 'Connected'])
        st.metric("Connected LPs", f"{connected}/{len(lps)}")
    
    with col2:
        total_liquidity = sum([lp['available_liquidity'] for lp in lps if lp['status'] == 'Connected'])
        st.metric("Available Liquidity", f"${total_liquidity:,}")
    
    with col3:
        avg_latency = np.mean([lp['latency'] for lp in lps if lp['status'] == 'Connected' and lp['latency'] > 0])
        st.metric("Avg Latency", f"{avg_latency:.1f}ms" if not np.isnan(avg_latency) else "N/A")
    
    with col4:
        total_volume = sum([lp['daily_volume'] for lp in lps])
        st.metric("Daily Volume", f"${total_volume:,}")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔗 Liquidity Providers")
        
        for i, lp in enumerate(lps):
            status_color = "#10B981" if lp['status'] == 'Connected' else "#EF4444"
            util_color = "#10B981" if lp['utilization'] < 70 else "#F59E0B" if lp['utilization'] < 90 else "#EF4444"
            
            with st.expander(f"🏦 {lp['name']} - {'🟢' if lp['status'] == 'Connected' else '🔴'} {lp['status']}"):
                lp_col1, lp_col2, lp_col3 = st.columns(3)
                
                with lp_col1:
                    st.markdown(f"**Type:** {lp['type']}")
                    st.markdown(f"**Protocol:** {lp['protocol']}")
                    st.markdown(f"**Status:** <span style='color: {status_color};'>● {lp['status']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Uptime:** {lp['uptime']:.1f}%")
                    st.markdown(f"**FIX Host:** {lp.get('fix_host', 'N/A')}")
                    st.markdown(f"**FIX Port:** {lp.get('fix_port', 'N/A')}")
                
                with lp_col2:
                    st.metric("Available", f"${lp['available_liquidity']:,}")
                    st.metric("Total", f"${lp['total_liquidity']:,}")
                    st.markdown(f"**Utilization:** <span style='color: {util_color};'>{lp['utilization']:.1f}%</span>", unsafe_allow_html=True)
                    st.metric("Commission", f"{lp['commission']:.2f}%")
                
                with lp_col3:
                    st.metric("Latency", f"{lp['latency']:.1f}ms" if lp['latency'] > 0 else "N/A")
                    st.metric("Fill Rate", f"{lp['fill_rate']:.1f}%")
                    st.metric("Avg Spread", f"{lp['avg_spread']:.1f} pips")
                    st.metric("Rejections", lp['rejections_today'])
                
                # LP controls
                ctrl_col1, ctrl_col2 = st.columns(2)
                
                with ctrl_col1:
                    if lp['status'] == 'Connected':
                        if st.button("🔌 Disconnect", key=f"disconnect_{i}", use_container_width=True):
                            st.session_state.lp_bridge['liquidity_providers'][i]['status'] = 'Disconnected'
                            st.session_state.lp_bridge['liquidity_providers'][i]['available_liquidity'] = 0
                            st.session_state.lp_bridge['liquidity_providers'][i]['latency'] = 0
                            st.success(f"✅ {lp['name']} disconnected!")
                            st.rerun()
                    else:
                        if st.button("🔌 Connect", key=f"connect_{i}", use_container_width=True):
                            # Create FIX session
                            session_id = st.session_state.fix_engine.create_session(
                                lp['name'],
                                lp.get('sender_comp_id', 'YANTRA'),
                                lp.get('target_comp_id', lp['name'].upper().replace(' ', '')),
                                lp.get('fix_host', '127.0.0.1'),
                                lp.get('fix_port', 9876)
                            )
                            
                            # Connect
                            st.session_state.fix_engine.connect_session(session_id)
                            
                            st.session_state.lp_bridge['liquidity_providers'][i]['status'] = 'Connected'
                            st.session_state.lp_bridge['liquidity_providers'][i]['available_liquidity'] = lp['total_liquidity'] // 2
                            st.session_state.lp_bridge['liquidity_providers'][i]['latency'] = random.uniform(5, 20)
                            st.success(f"✅ {lp['name']} connected!")
                            st.rerun()
                
                with ctrl_col2:
                    if st.button("⚙️ Configure", key=f"config_{i}", use_container_width=True):
                        st.info(f"Configure FIX session for {lp['name']}")
                
                st.markdown(f"**Supported:** {', '.join(lp['supported_symbols'])}")
        
        # Routing settings
        st.markdown("### 🔄 Smart Order Routing")
        
        routing_col1, routing_col2, routing_col3 = st.columns(3)
        
        with routing_col1:
            st.markdown("#### 🎯 Routing Mode")
            routing_mode = st.selectbox("Mode", ["Best Price", "Lowest Latency", "Load Balanced", "Round Robin"], 
                index=0, key="routing_mode")
            price_tolerance = st.number_input("Price Tolerance ($)", 0.1, 10.0, 1.0, 0.1, key="price_tolerance")
        
        with routing_col2:
            st.markdown("#### ⚖️ Load Balancing")
            load_balancing = st.checkbox("Enable", True, key="load_balancing")
            max_utilization = st.slider("Max Utilization %", 50, 100, 80, 5, key="max_util")
        
        with routing_col3:
            st.markdown("#### 🛡️ Risk Controls")
            position_limits = st.checkbox("Position Limits", True, key="pos_limits")
            max_position = st.number_input("Max Net Position", 1000000, 100000000, 10000000, key="max_pos")
        
        if st.button("💾 Save Routing Settings", key="save_routing", use_container_width=True):
            st.session_state.lp_bridge['settings'].update({
                'routing_mode': routing_mode,
                'price_tolerance': price_tolerance,
                'load_balancing': load_balancing,
                'max_lp_utilization': max_utilization,
                'position_limits': position_limits,
                'max_net_position': max_position
            })
            st.success("✅ Routing settings saved!")
    
    with col2:
        # Price aggregation
        st.markdown("### 📊 Price Aggregation")
        
        agg_symbol = st.selectbox("Symbol", ['EURUSD', 'GBPUSD', 'XAUUSD'], key="agg_symbol")
        
        # Get aggregated price
        best_price = st.session_state.fix_engine.get_best_price(agg_symbol)
        
        if best_price:
            st.metric("Best Bid", f"{best_price['best_bid']:.5f}", best_price['best_bid_lp'])
            st.metric("Best Ask", f"{best_price['best_ask']:.5f}", best_price['best_ask_lp'])
            st.metric("Spread", f"{best_price['spread']:.5f}")
        else:
            st.info("No price data available")
        
        # Order routing test
        st.markdown("### 🧪 Order Test")
        
        test_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols[:5], key="test_symbol")
        test_side = st.selectbox("Side", ["BUY", "SELL"], key="test_side")
        test_volume = st.number_input("Volume", 0.1, 10.0, 1.0, 0.1, key="test_volume")
        
        if st.button("📤 Send Test Order", key="send_test", use_container_width=True):
            # Route through LP Bridge
            side = OrderSide.BUY if test_side == "BUY" else OrderSide.SELL
            
            # For demo, simulate routing
            connected_lps = [lp['name'] for lp in lps if lp['status'] == 'Connected']
            if connected_lps:
                selected_lp = connected_lps[0]
                st.success(f"✅ Order routed to {selected_lp}")
                st.json({
                    "order_id": f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "symbol": test_symbol,
                    "side": test_side,
                    "volume": test_volume,
                    "routed_to": selected_lp,
                    "status": "Sent"
                })
            else:
                st.error("❌ No LPs connected")
        
        # System alerts
        st.markdown("### 🚨 System Alerts")
        
        alerts = [
            {"level": "warning", "message": "LP-3 high latency (45ms)"},
            {"level": "info", "message": "LP-1 utilization at 78%"},
            {"level": "success", "message": "All systems operational"}
        ]
        
        for alert in alerts:
            if alert['level'] == 'warning':
                st.warning(f"⚠️ {alert['message']}")
            elif alert['level'] == 'success':
                st.success(f"✅ {alert['message']}")
            else:
                st.info(f"ℹ️ {alert['message']}")


# ===== ADVANCED CHARTS =====

elif st.session_state.page == "Advanced Charts":
    # Chart controls
    chart_col1, chart_col2, chart_col3, chart_col4, chart_col5 = st.columns(5)
    
    with chart_col1:
        chart_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="chart_symbol")
    
    with chart_col2:
        timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "30M", "1H", "4H", "1D", "1W"], index=4, key="chart_timeframe")
    
    with chart_col3:
        chart_type = st.selectbox("Chart Type", ["Candlestick", "Line", "OHLC"], key="chart_type")
    
    with chart_col4:
        period = st.selectbox("Period", ["1D", "1W", "1M", "3M"], index=2, key="chart_period")
    
    with chart_col5:
        if st.button("🔄 Refresh", key="refresh_chart", use_container_width=True):
            st.rerun()
    
    # Generate chart data
    periods_map = {"1D": 24, "1W": 168, "1M": 720, "3M": 2160}
    num_points = periods_map[period]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=num_points)
    dates = pd.date_range(start=start_date, end=end_date, periods=min(num_points, 500))
    
    # Generate OHLC data
    if 'XAU' in chart_symbol:
        base_price = 2655.0
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
        trend = np.sin(i / 50) * 0.001
        noise = np.random.normal(0, volatility) * current_price
        current_price += (trend * current_price) + noise
        
        high = current_price + random.uniform(0, 0.005) * current_price
        low = current_price - random.uniform(0, 0.005) * current_price
        open_price = prices[-1]['close'] if prices else current_price
        close = current_price
        
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
    
    # Create chart
    col1, col2 = st.columns([4, 1])
    
    with col1:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.8, 0.2],
            subplot_titles=(f'{chart_symbol} - {timeframe}', 'Volume')
        )
        
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
        
        # Volume
        colors = ['#10B981' if close >= open else '#EF4444' 
                 for close, open in zip(df_chart['close'], df_chart['open'])]
        
        fig.add_trace(go.Bar(
            x=df_chart['datetime'],
            y=df_chart['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ), row=2, col=1)
        
        fig.update_layout(
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=600,
            xaxis_rangeslider_visible=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Indicators")
        
        show_ma = st.checkbox("Moving Average", key="show_ma")
        if show_ma:
            ma_period = st.number_input("MA Period", 1, 200, 20, key="ma_period")
        
        show_bb = st.checkbox("Bollinger Bands", key="show_bb")
        show_rsi = st.checkbox("RSI", key="show_rsi")
        
        st.markdown("### 📈 Price Info")
        
        last_price = df_chart['close'].iloc[-1]
        prev_price = df_chart['close'].iloc[-2]
        change = ((last_price / prev_price) - 1) * 100
        
        st.metric("Last Price", f"{last_price:.5f}" if 'XAU' not in chart_symbol else f"{last_price:.2f}")
        st.metric("Change", f"{change:+.2f}%")
        st.metric("High", f"{df_chart['high'].max():.5f}" if 'XAU' not in chart_symbol else f"{df_chart['high'].max():.2f}")
        st.metric("Low", f"{df_chart['low'].min():.5f}" if 'XAU' not in chart_symbol else f"{df_chart['low'].min():.2f}")


# ===== TICK CHARTS =====

elif st.session_state.page == "Tick Charts":
    st.markdown("### 📊 Real-Time Tick Charts")
    
    tick_col1, tick_col2, tick_col3 = st.columns(3)
    
    with tick_col1:
        tick_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols[:10], key="tick_symbol")
    
    with tick_col2:
        tick_count = st.selectbox("Tick Count", [100, 500, 1000], index=1, key="tick_count")
    
    with tick_col3:
        auto_scroll = st.checkbox("Auto Scroll", True, key="auto_scroll")
    
    # Generate tick data
    tick_data = []
    base_price = 1.0850 if 'USD' in tick_symbol else 2655.0
    current_price = base_price
    
    for i in range(tick_count):
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
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                       row_heights=[0.8, 0.2], subplot_titles=(f'{tick_symbol} - Tick Chart', 'Volume'))
    
    fig.add_trace(go.Scatter(x=tick_df['time'], y=tick_df['bid'], mode='lines', 
                            name='Bid', line=dict(color='#EF4444', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=tick_df['time'], y=tick_df['ask'], mode='lines',
                            name='Ask', line=dict(color='#10B981', width=1)), row=1, col=1)
    fig.add_trace(go.Bar(x=tick_df['time'], y=tick_df['volume'], name='Volume',
                        marker_color='#3B82F6', opacity=0.7), row=2, col=1)
    
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
        st.metric("Ticks/Second", f"{len(tick_df) / (tick_df['time'].max() - tick_df['time'].min()).total_seconds():.1f}")


# ===== AUTO TRADING =====

elif st.session_state.page == "Auto Trading":
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        status = "🟢 ACTIVE" if st.session_state.auto_trading['enabled'] else "🔴 INACTIVE"
        st.markdown(f"**Auto Trading:** {status}")
    
    with col2:
        st.metric("Trades Today", st.session_state.auto_trading['trades_today'])
    
    with col3:
        st.metric("Profit Today", f"${st.session_state.auto_trading['profit_today']:.2f}")
    
    with col4:
        total = len(st.session_state.auto_trading['strategies'])
        active = len([s for s in st.session_state.auto_trading['strategies'] if s['enabled']])
        st.metric("Active Strategies", f"{active}/{total}")
    
    with col5:
        if st.session_state.auto_trading['enabled']:
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
        
        for i, strategy in enumerate(st.session_state.auto_trading['strategies']):
            with st.expander(f"📊 {strategy['name']} - {'🟢 Active' if strategy['enabled'] else '🔴 Inactive'}"):
                strat_col1, strat_col2, strat_col3 = st.columns(3)
                
                with strat_col1:
                    st.markdown(f"**Type:** {strategy['type']}")
                    st.markdown(f"**Symbols:** {', '.join(strategy['symbols'])}")
                    st.markdown(f"**Timeframe:** {strategy['timeframe']}")
                
                with strat_col2:
                    st.metric("Trades Today", strategy['trades_today'])
                    st.metric("Profit Today", f"${strategy['profit_today']:.2f}")
                    st.metric("Win Rate", f"{strategy['win_rate']:.1f}%")
                
                with strat_col3:
                    st.metric("Total P&L", f"${strategy['total_pnl']:.2f}")
                    
                    if strategy['enabled']:
                        if st.button("⏸️ Stop", key=f"stop_strategy_{i}", use_container_width=True):
                            st.session_state.auto_trading['strategies'][i]['enabled'] = False
                            st.rerun()
                    else:
                        if st.button("🚀 Start", key=f"start_strategy_{i}", use_container_width=True):
                            st.session_state.auto_trading['strategies'][i]['enabled'] = True
                            st.rerun()
        
        # Add new strategy
        st.markdown("### ➕ Create New Strategy")
        
        new_col1, new_col2, new_col3 = st.columns(3)
        
        with new_col1:
            new_name = st.text_input("Strategy Name", key="new_strategy_name")
            new_type = st.selectbox("Type", ["MA Crossover", "RSI", "Bollinger Bands", "MACD"], key="new_type")
        
        with new_col2:
            new_symbols = st.multiselect("Symbols", st.session_state.mt5_symbols, default=['EURUSD'], key="new_symbols")
            new_timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "30M", "1H", "4H"], index=2, key="new_tf")
        
        with new_col3:
            new_risk = st.slider("Risk %", 0.1, 10.0, 2.0, 0.1, key="new_risk")
        
        if st.button("🚀 Create Strategy", key="create_strategy", use_container_width=True):
            if new_name and new_symbols:
                new_strategy = {
                    'name': new_name,
                    'type': new_type,
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
                st.success(f"✅ Strategy '{new_name}' created!")
                st.rerun()
    
    with col2:
        st.markdown("### 📊 Performance")
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
        equity_values = []
        current_equity = 10000
        
        for _ in dates:
            daily_return = np.random.normal(0.002, 0.015)
            current_equity *= (1 + daily_return)
            equity_values.append(current_equity)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=equity_values, mode='lines', name='Equity',
            line=dict(color='#10B981', width=3),
            fill='tonexty', fillcolor='rgba(16, 185, 129, 0.1)'
        ))
        
        fig.update_layout(
            title="30-Day Performance",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        total_return = ((equity_values[-1] / equity_values[0]) - 1) * 100
        st.metric("30-Day Return", f"{total_return:+.2f}%")


# ===== COPY TRADING =====

elif st.session_state.page == "Copy Trading":
    st.markdown("### 👥 Copy Trading Platform")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Subscriptions", len(st.session_state.copy_trading['subscriptions']))
    
    with col2:
        total_fees = sum([sub['monthly_fee'] for sub in st.session_state.copy_trading['subscriptions']])
        st.metric("Monthly Fees", f"${total_fees}")
    
    with col3:
        total_profit = sum([sub['profit_this_month'] for sub in st.session_state.copy_trading['subscriptions']])
        st.metric("This Month Profit", f"${total_profit:.2f}")
    
    with col4:
        total_trades = sum([sub['trades_copied'] for sub in st.session_state.copy_trading['subscriptions']])
        st.metric("Trades Copied", total_trades)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🏆 Signal Providers")
        
        for provider in st.session_state.copy_trading['available_providers']:
            prov_col1, prov_col2, prov_col3, prov_col4, prov_col5 = st.columns(5)
            
            with prov_col1:
                st.markdown(f"**{provider['name']}**")
                risk_color = "#10B981" if provider['risk'] <= 5 else "#F59E0B" if provider['risk'] <= 7 else "#EF4444"
                st.markdown(f"<span style='color: {risk_color};'>Risk: {provider['risk']}/10</span>", unsafe_allow_html=True)
            
            with prov_col2:
                st.metric("Return", f"{provider['return']:+.1f}%")
            
            with prov_col3:
                st.metric("Followers", f"{provider['followers']:,}")
            
            with prov_col4:
                st.metric("Fee", f"${provider['fee']}")
            
            with prov_col5:
                is_subscribed = any(sub['provider'] == provider['name'] for sub in st.session_state.copy_trading['subscriptions'])
                
                if is_subscribed:
                    if st.button("✅ Subscribed", key=f"unsub_{provider['name']}", use_container_width=True):
                        st.session_state.copy_trading['subscriptions'] = [
                            sub for sub in st.session_state.copy_trading['subscriptions']
                            if sub['provider'] != provider['name']
                        ]
                        st.rerun()
                else:
                    if st.button("📋 Subscribe", key=f"sub_{provider['name']}", use_container_width=True):
                        new_sub = {
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
                        st.session_state.copy_trading['subscriptions'].append(new_sub)
                        st.success(f"✅ Subscribed to {provider['name']}!")
                        st.rerun()
            
            st.markdown("---")
    
    with col2:
        st.markdown("### 📊 Copy Performance")
        
        if st.session_state.copy_trading['subscriptions']:
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
            
            fig = go.Figure()
            
            for sub in st.session_state.copy_trading['subscriptions']:
                performance = []
                current = 1000
                
                for _ in dates:
                    daily = np.random.normal(sub['monthly_return']/30/100, 0.02)
                    current *= (1 + daily)
                    performance.append(current)
                
                fig.add_trace(go.Scatter(
                    x=dates, y=performance, mode='lines',
                    name=sub['provider'].split()[0],
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="Copy Trading Performance",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)


# ===== BACKTESTING =====

elif st.session_state.page == "Backtesting":
    st.markdown("### 🔄 Strategy Backtesting Engine")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📋 Backtest Configuration")
        
        config_col1, config_col2, config_col3 = st.columns(3)
        
        with config_col1:
            bt_symbol = st.selectbox("Symbol", st.session_state.mt5_symbols, key="bt_symbol")
            bt_timeframe = st.selectbox("Timeframe", ["1M", "5M", "15M", "30M", "1H", "4H", "1D"], index=4, key="bt_timeframe")
            bt_balance = st.number_input("Initial Balance", 1000, 1000000, 10000, key="bt_balance")
        
        with config_col2:
            bt_start = st.date_input("Start Date", datetime(2023, 1, 1), key="bt_start")
            bt_end = st.date_input("End Date", datetime(2024, 12, 31), key="bt_end")
            bt_commission = st.number_input("Commission", 0.0, 100.0, 7.0, 0.1, key="bt_commission")
        
        with config_col3:
            bt_strategy = st.selectbox("Strategy", ["MA Crossover", "RSI Mean Reversion", "Bollinger Bands"], key="bt_strategy")
            bt_risk = st.slider("Risk per Trade %", 0.1, 10.0, 2.0, 0.1, key="bt_risk")
        
        if st.button("🚀 Run Backtest", key="run_backtest", use_container_width=True):
            with st.spinner("Running backtest..."):
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress.progress(i + 1)
                
                # Generate results
                num_trades = random.randint(50, 300)
                win_rate = random.uniform(45, 75)
                total_return = random.uniform(-20, 60)
                max_drawdown = random.uniform(5, 30)
                profit_factor = random.uniform(0.8, 2.5)
                sharpe_ratio = random.uniform(-0.5, 2.0)
                
                results = {
                    'symbol': bt_symbol,
                    'timeframe': bt_timeframe,
                    'strategy': bt_strategy,
                    'start_date': bt_start,
                    'end_date': bt_end,
                    'initial_balance': bt_balance,
                    'final_balance': bt_balance * (1 + total_return/100),
                    'total_return': total_return,
                    'num_trades': num_trades,
                    'win_rate': win_rate,
                    'max_drawdown': max_drawdown,
                    'profit_factor': profit_factor,
                    'sharpe_ratio': sharpe_ratio,
                    'avg_trade': (bt_balance * total_return/100) / num_trades if num_trades > 0 else 0,
                    'best_trade': random.uniform(50, 500),
                    'worst_trade': random.uniform(-200, -50),
                    'avg_trade_duration': random.uniform(2, 48),
                    'commission_paid': num_trades * bt_commission
                }
                
                st.session_state.backtesting['results'].append(results)
                st.success("✅ Backtest completed!")
                st.rerun()
        
        # Display results
        if st.session_state.backtesting['results']:
            latest = st.session_state.backtesting['results'][-1]
            
            st.markdown("#### 📊 Results")
            
            result_col1, result_col2, result_col3, result_col4, result_col5 = st.columns(5)
            
            with result_col1:
                st.metric("Total Return", f"{latest['total_return']:+.2f}%")
            with result_col2:
                st.metric("Win Rate", f"{latest['win_rate']:.1f}%")
            with result_col3:
                st.metric("Total Trades", latest['num_trades'])
            with result_col4:
                st.metric("Profit Factor", f"{latest['profit_factor']:.2f}")
            with result_col5:
                st.metric("Sharpe Ratio", f"{latest['sharpe_ratio']:.2f}")
            
            # Equity curve
            dates = pd.date_range(start=latest['start_date'], end=latest['end_date'], periods=latest['num_trades'])
            equity = [latest['initial_balance']]
            
            for _ in range(latest['num_trades']):
                if random.random() < latest['win_rate']/100:
                    profit = random.uniform(10, latest['best_trade'])
                else:
                    profit = random.uniform(latest['worst_trade'], -10)
                equity.append(equity[-1] + profit)
            
            dates = list(dates) + [latest['end_date']]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=equity, mode='lines', name='Equity',
                line=dict(color='#10B981', width=3),
                fill='tonexty', fillcolor='rgba(16, 185, 129, 0.1)'
            ))
            
            fig.update_layout(
                title=f"Backtest: {latest['symbol']} - {latest['strategy']}",
                template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 💾 Saved Strategies")
        
        for i, strategy in enumerate(st.session_state.backtesting['saved_strategies']):
            with st.expander(f"📊 {strategy['name']}"):
                st.markdown(f"**Symbol:** {strategy['symbol']}")
                st.markdown(f"**Strategy:** {strategy['strategy']}")
                st.metric("Return", f"{strategy['total_return']:+.1f}%")
                st.metric("Win Rate", f"{strategy['win_rate']:.1f}%")
                st.metric("Sharpe", f"{strategy['sharpe_ratio']:.2f}")


# ===== RISK MANAGEMENT =====

elif st.session_state.page == "Risk Management":
    st.markdown("### ⚠️ Risk Management")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        exposure = sum([abs(pos['volume'] * pos['current_price']) for pos in st.session_state.portfolio['positions']])
        st.metric("Current Exposure", f"${exposure:,.0f}")
    
    with col2:
        var_95 = exposure * 0.05
        st.metric("VaR (95%)", f"${var_95:,.0f}")
    
    with col3:
        margin_level = (st.session_state.portfolio['equity'] / st.session_state.portfolio['margin']) * 100 if st.session_state.portfolio['margin'] > 0 else 0
        margin_color = "#10B981" if margin_level > 200 else "#F59E0B" if margin_level > 100 else "#EF4444"
        st.markdown(f"**Margin Level:** <span style='color: {margin_color};'>{margin_level:.0f}%</span>", unsafe_allow_html=True)
    
    with col4:
        max_dd = random.uniform(5, 15)
        st.metric("Max Drawdown", f"{max_dd:.1f}%")
    
    with col5:
        risk_score = random.randint(3, 8)
        st.metric("Risk Score", f"{risk_score}/10")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Position Risk Analysis")
        
        if st.session_state.portfolio['positions']:
            risk_data = []
            for pos in st.session_state.portfolio['positions']:
                position_value = abs(pos['volume'] * pos['current_price'])
                risk_amount = position_value * 0.02
                
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
        
        # Stress testing
        st.markdown("### 🧪 Stress Testing")
        
        stress_col1, stress_col2, stress_col3 = st.columns(3)
        
        with stress_col1:
            st.markdown("#### Market Crash (-15%)")
            crash_loss = exposure * 0.15
            st.metric("Potential Loss", f"-${crash_loss:,.0f}")
        
        with stress_col2:
            st.markdown("#### Black Swan (-25%)")
            swan_loss = exposure * 0.25
            st.metric("Potential Loss", f"-${swan_loss:,.0f}")
        
        with stress_col3:
            st.markdown("#### Liquidity Crisis (-10%)")
            liq_loss = exposure * 0.10
            st.metric("Potential Loss", f"-${liq_loss:,.0f}")
    
    with col2:
        st.markdown("### 🛡️ Risk Limits")
        
        max_pos_size = st.number_input("Max Position Size", 0.1, 100.0, 
            st.session_state.risk_management['max_position_size'], 0.1, key="rm_max_pos")
        
        risk_per_trade = st.slider("Risk per Trade %", 0.1, 10.0,
            st.session_state.risk_management['risk_per_trade'], 0.1, key="rm_risk")
        
        max_daily_loss = st.number_input("Max Daily Loss",100, 10000,
            st.session_state.risk_management['max_daily_loss'], key="rm_daily_loss")
        
        auto_sl = st.checkbox("Auto Stop Loss", st.session_state.risk_management['auto_sl'], key="rm_auto_sl")
        auto_tp = st.checkbox("Auto Take Profit", st.session_state.risk_management['auto_tp'], key="rm_auto_tp")
        
        if st.button("💾 Save Settings", key="save_risk", use_container_width=True):
            st.session_state.risk_management.update({
                'max_position_size': max_pos_size,
                'risk_per_trade': risk_per_trade,
                'max_daily_loss': max_daily_loss,
                'auto_sl': auto_sl,
                'auto_tp': auto_tp
            })
            st.success("✅ Risk settings saved!")
        
        # Emergency controls
        st.markdown("### 🆘 Emergency")
        
        if st.button("🛑 CLOSE ALL", key="emergency_close", use_container_width=True):
            if st.session_state.portfolio['positions']:
                total_pnl = sum([pos['pnl'] for pos in st.session_state.portfolio['positions']])
                st.session_state.portfolio['positions'] = []
                st.error(f"🛑 All positions closed! P&L: ${total_pnl:+.2f}")
                st.rerun()


# ===== ANALYTICS =====

elif st.session_state.page == "Analytics":
    st.markdown("### 📊 Trading Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", random.randint(150, 500))
    with col2:
        st.metric("Win Rate", f"{random.uniform(55, 75):.1f}%")
    with col3:
        st.metric("Profit Factor", f"{random.uniform(1.2, 2.5):.2f}")
    with col4:
        st.metric("Sharpe Ratio", f"{random.uniform(0.8, 2.2):.2f}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Performance chart
        st.markdown("### 📈 Performance Analysis")
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=90), periods=90, freq='D')
        
        initial = 10000
        equity = [initial]
        daily_returns = []
        
        for _ in range(89):
            daily_return = np.random.normal(0.002, 0.02)
            daily_returns.append(daily_return)
            equity.append(equity[-1] * (1 + daily_return))
        
        # Drawdown
        peak = equity[0]
        drawdown = []
        for val in equity:
            if val > peak:
                peak = val
            drawdown.append(((val - peak) / peak) * 100)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                           row_heights=[0.7, 0.3], subplot_titles=('Equity Curve', 'Drawdown'))
        
        fig.add_trace(go.Scatter(x=dates, y=equity, mode='lines', name='Equity',
                                line=dict(color='#10B981', width=3),
                                fill='tonexty', fillcolor='rgba(16, 185, 129, 0.1)'), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=dates, y=drawdown, mode='lines', name='Drawdown',
                                line=dict(color='#EF4444', width=2),
                                fill='tonexty', fillcolor='rgba(239, 68, 68, 0.1)'), row=2, col=1)
        
        fig.update_layout(
            title="90-Day Performance",
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=500,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Key Metrics")
        
        total_return = ((equity[-1] / equity[0]) - 1) * 100
        ann_return = ((equity[-1] / equity[0]) ** (365 / 90) - 1) * 100
        volatility = np.std(daily_returns) * np.sqrt(252) * 100
        max_dd = min(drawdown)
        
        st.metric("Total Return", f"{total_return:+.2f}%")
        st.metric("Annualized Return", f"{ann_return:+.2f}%")
        st.metric("Volatility", f"{volatility:.2f}%")
        st.metric("Max Drawdown", f"{max_dd:.2f}%")
        
        calmar = ann_return / abs(max_dd) if max_dd != 0 else 0
        st.metric("Calmar Ratio", f"{calmar:.2f}")
        
        # Monthly returns heatmap
        st.markdown("### 🗓️ Monthly Returns")
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        years = ['2024']
        monthly_returns = np.random.normal(1.5, 3.0, (1, 6))
        
        fig = go.Figure(data=go.Heatmap(
            z=monthly_returns, x=months, y=years,
            colorscale='RdYlGn', zmid=0,
            text=np.round(monthly_returns, 1),
            texttemplate="%{text}%"
        ))
        
        fig.update_layout(
            template='plotly_dark' if st.session_state.theme == "Dark" else 'plotly_white',
            height=150,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)


# ===== SETTINGS =====

elif st.session_state.page == "Settings":
    st.markdown("### ⚙️ Platform Settings")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Appearance", "🔔 Notifications", "🔐 Security", "🔧 Advanced"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox("Theme", ["Light", "Dark"], 
                index=0 if st.session_state.theme == "Light" else 1, key="settings_theme")
            
            if theme != st.session_state.theme:
                st.session_state.theme = theme
                st.rerun()
            
            chart_style = st.selectbox("Chart Style", ["Modern", "Classic", "Minimal"], key="chart_style")
        
        with col2:
            font_size = st.selectbox("Font Size", ["Small", "Medium", "Large"], index=1, key="font_size")
            decimal_places = st.number_input("Decimal Places", 2, 8, 5, key="dec_places")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Trade Notifications**")
            notify_open = st.checkbox("Trade Opened", True, key="notify_open")
            notify_close = st.checkbox("Trade Closed", True, key="notify_close")
            notify_sl = st.checkbox("Stop Loss Hit", True, key="notify_sl")
        
        with col2:
            st.markdown("**Delivery Methods**")
            email_notif = st.checkbox("Email", True, key="email_notif")
            push_notif = st.checkbox("Push Notifications", True, key="push_notif")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Account Security**")
            two_fa = st.checkbox("Two-Factor Authentication", False, key="2fa")
            session_timeout = st.selectbox("Session Timeout", ["15 min", "30 min", "1 hour"], index=1, key="timeout")
        
        with col2:
            st.markdown("**Change Password**")
            current_pass = st.text_input("Current Password", type="password", key="curr_pass")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="conf_pass")
            
            if st.button("🔒 Change Password", key="change_pass"):
                if new_pass == confirm_pass and len(new_pass) >= 8:
                    st.success("✅ Password changed!")
                else:
                    st.error("❌ Passwords don't match or too short")
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Trading Configuration**")
            default_lot = st.number_input("Default Lot Size", 0.01, 10.0, 0.1, 0.01, key="def_lot")
            slippage = st.number_input("Slippage Tolerance (pips)", 0.1, 10.0, 2.0, 0.1, key="slippage")
            one_click = st.checkbox("One-Click Trading", False, key="one_click")
        
        with col2:
            st.markdown("**Data & Performance**")
            cache_size = st.selectbox("Cache Size", ["100MB", "500MB", "1GB"], index=1, key="cache")
            hardware_accel = st.checkbox("Hardware Acceleration", True, key="hw_accel")
            
            if st.button("🧹 Clear Cache", key="clear_cache"):
                st.success("✅ Cache cleared!")
    
    st.markdown("---")
    
    if st.button("💾 Save All Settings", key="save_all_settings", use_container_width=True):
        st.success("✅ All settings saved!")


# ===== FOOTER =====

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
    st.markdown("**Docs:** docs.yantra.trading")
