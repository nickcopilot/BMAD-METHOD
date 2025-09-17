"""
Database models and schema for Vietnam Stock Analysis System
Based on architecture document data models
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class Sector(Enum):
    SECURITIES = "securities"
    BANKING = "banking"
    REAL_ESTATE = "real_estate"
    STEEL = "steel"


class Exchange(Enum):
    HOSE = "HOSE"
    HNX = "HNX"
    UPCOM = "UPCOM"


class Recommendation(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class Stock:
    symbol: str
    name: str
    name_en: str
    sector: str
    exchange: str
    market_cap: float
    industry_group: str
    listing_date: str
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class PriceData:
    stock_symbol: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    value: float
    foreign_buy: float = 0.0
    foreign_sell: float = 0.0


@dataclass
class FinancialData:
    stock_symbol: str
    period: str
    period_type: str  # 'quarterly' or 'annual'
    revenue: float
    profit: float
    total_assets: float
    equity: float
    debt: float
    roe: float
    roa: float
    pe_ratio: float
    pb_ratio: float
    debt_equity: float
    report_date: str


@dataclass
class EconomicIndicator:
    indicator_code: str
    indicator_name: str
    period: str
    value: float
    unit: str
    source: str
    category: str
    release_date: str
    created_at: Optional[str] = None


@dataclass
class EICScore:
    stock_symbol: str
    date: str
    economy_score: float
    industry_score: float
    company_score: float
    total_score: float
    economy_weight: float = 0.30
    industry_weight: float = 0.35
    company_weight: float = 0.35
    recommendation: str = "HOLD"
    confidence_level: float = 0.5
    calculation_version: str = "1.0"
    created_at: Optional[str] = None


@dataclass
class Portfolio:
    stock_symbol: str
    position_size: int
    entry_price: float
    entry_date: str
    eic_score_at_entry: float
    user_id: str = "default"


@dataclass
class Alert:
    stock_symbol: str
    alert_type: str
    trigger_value: float
    current_value: float
    created_at: str
    is_read: bool = False


class DatabaseManager:
    """Manages SQLite database connection and operations"""

    def __init__(self, db_path: str = "data/vietnam_stocks.db"):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database with all tables"""
        with self.get_connection() as conn:
            # Stocks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    symbol TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    name_en TEXT,
                    sector TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    market_cap REAL,
                    industry_group TEXT,
                    listing_date TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Price data table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_data (
                    stock_symbol TEXT,
                    date TEXT,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    value REAL NOT NULL,
                    foreign_buy REAL DEFAULT 0,
                    foreign_sell REAL DEFAULT 0,
                    PRIMARY KEY (stock_symbol, date),
                    FOREIGN KEY (stock_symbol) REFERENCES stocks(symbol)
                )
            """)

            # Financial data table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS financial_data (
                    stock_symbol TEXT,
                    period TEXT,
                    period_type TEXT NOT NULL,
                    revenue REAL,
                    profit REAL,
                    total_assets REAL,
                    equity REAL,
                    debt REAL,
                    roe REAL,
                    roa REAL,
                    pe_ratio REAL,
                    pb_ratio REAL,
                    debt_equity REAL,
                    report_date TEXT,
                    PRIMARY KEY (stock_symbol, period),
                    FOREIGN KEY (stock_symbol) REFERENCES stocks(symbol)
                )
            """)

            # Economic indicators table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS economic_indicators (
                    indicator_code TEXT,
                    period TEXT,
                    indicator_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    source TEXT,
                    category TEXT,
                    release_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (indicator_code, period)
                )
            """)

            # EIC scores table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS eic_scores (
                    stock_symbol TEXT,
                    date TEXT,
                    economy_score REAL NOT NULL,
                    industry_score REAL NOT NULL,
                    company_score REAL NOT NULL,
                    total_score REAL NOT NULL,
                    economy_weight REAL DEFAULT 0.30,
                    industry_weight REAL DEFAULT 0.35,
                    company_weight REAL DEFAULT 0.35,
                    recommendation TEXT DEFAULT 'HOLD',
                    confidence_level REAL DEFAULT 0.5,
                    calculation_version TEXT DEFAULT '1.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (stock_symbol, date),
                    FOREIGN KEY (stock_symbol) REFERENCES stocks(symbol)
                )
            """)

            # Portfolio table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT DEFAULT 'default',
                    stock_symbol TEXT NOT NULL,
                    position_size INTEGER NOT NULL,
                    entry_price REAL NOT NULL,
                    entry_date TEXT NOT NULL,
                    eic_score_at_entry REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_symbol) REFERENCES stocks(symbol)
                )
            """)

            # Alerts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_symbol TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    trigger_value REAL NOT NULL,
                    current_value REAL NOT NULL,
                    is_read BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_symbol) REFERENCES stocks(symbol)
                )
            """)

            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_price_data_symbol_date ON price_data(stock_symbol, date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_eic_scores_date ON eic_scores(date DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(is_read, created_at)")

            conn.commit()

    def insert_stock(self, stock: Stock) -> bool:
        """Insert a new stock"""
        try:
            with self.get_connection() as conn:
                stock_dict = asdict(stock)
                if stock_dict['created_at'] is None:
                    stock_dict['created_at'] = datetime.now().isoformat()
                if stock_dict['updated_at'] is None:
                    stock_dict['updated_at'] = datetime.now().isoformat()

                conn.execute("""
                    INSERT OR REPLACE INTO stocks
                    (symbol, name, name_en, sector, exchange, market_cap, industry_group,
                     listing_date, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(stock_dict.values()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting stock {stock.symbol}: {e}")
            return False

    def get_stocks_by_sector(self, sector: str) -> List[Dict[str, Any]]:
        """Get all stocks in a specific sector"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM stocks WHERE sector = ? AND is_active = 1 ORDER BY symbol",
                (sector,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def insert_eic_score(self, eic_score: EICScore) -> bool:
        """Insert EIC score"""
        try:
            with self.get_connection() as conn:
                score_dict = asdict(eic_score)
                if score_dict['created_at'] is None:
                    score_dict['created_at'] = datetime.now().isoformat()

                conn.execute("""
                    INSERT OR REPLACE INTO eic_scores
                    (stock_symbol, date, economy_score, industry_score, company_score,
                     total_score, economy_weight, industry_weight, company_weight,
                     recommendation, confidence_level, calculation_version, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(score_dict.values()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting EIC score for {eic_score.stock_symbol}: {e}")
            return False

    def get_latest_eic_scores(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest EIC scores"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT e.*, s.name, s.sector
                FROM eic_scores e
                JOIN stocks s ON e.stock_symbol = s.symbol
                ORDER BY e.date DESC, e.total_score DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def insert_price_data(self, price_data: PriceData) -> bool:
        """Insert price data"""
        try:
            with self.get_connection() as conn:
                price_dict = asdict(price_data)
                conn.execute("""
                    INSERT OR REPLACE INTO price_data
                    (stock_symbol, date, open, high, low, close, volume, value, foreign_buy, foreign_sell)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(price_dict.values()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting price data for {price_data.stock_symbol}: {e}")
            return False

    def insert_financial_data(self, financial_data: FinancialData) -> bool:
        """Insert financial data"""
        try:
            with self.get_connection() as conn:
                financial_dict = asdict(financial_data)
                conn.execute("""
                    INSERT OR REPLACE INTO financial_data
                    (stock_symbol, period, period_type, revenue, profit, total_assets, equity, debt,
                     roe, roa, pe_ratio, pb_ratio, debt_equity, report_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(financial_dict.values()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting financial data for {financial_data.stock_symbol}: {e}")
            return False

    def insert_economic_indicator(self, indicator: EconomicIndicator) -> bool:
        """Insert economic indicator"""
        try:
            with self.get_connection() as conn:
                indicator_dict = asdict(indicator)
                if indicator_dict['created_at'] is None:
                    indicator_dict['created_at'] = datetime.now().isoformat()

                conn.execute("""
                    INSERT OR REPLACE INTO economic_indicators
                    (indicator_code, period, indicator_name, value, unit, source, category,
                     release_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(indicator_dict.values()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting economic indicator {indicator.indicator_code}: {e}")
            return False

    def get_price_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get price data for a symbol within date range"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM price_data
                WHERE stock_symbol = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (symbol, start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]

    def get_latest_economic_indicators(self, category: str = None) -> List[Dict[str, Any]]:
        """Get latest economic indicators, optionally filtered by category"""
        with self.get_connection() as conn:
            if category:
                cursor = conn.execute("""
                    SELECT * FROM economic_indicators
                    WHERE category = ?
                    ORDER BY period DESC, created_at DESC
                """, (category,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM economic_indicators
                    ORDER BY period DESC, created_at DESC
                """)
            return [dict(row) for row in cursor.fetchall()]


# Global database instance
db_manager = DatabaseManager()


def get_db() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager