"""Market intelligence and financial data tools for MarketStrat."""
from typing import Any, Dict
import yfinance as yf


def fetch_market_snapshot(ticker: str) -> Dict[str, Any]:
    """Fetch real-time stock price and core valuation metrics for a given ticker symbol.

    Args:
        ticker: The stock ticker symbol (e.g., 'NVDA', 'AAPL', 'MSFT', 'GOOGL').

    Returns:
        A dictionary with live market price, 52-week range, market cap, and valuation indicators.
    """
    clean_ticker = ticker.strip().upper()
    try:
        t = yf.Ticker(clean_ticker)
        fast = t.fast_info
        info = t.info or {}

        return {
            "ticker": clean_ticker,
            "current_price": round(fast.last_price, 2) if getattr(fast, "last_price", None) else None,
            "currency": getattr(fast, "currency", "USD"),
            "market_cap": getattr(fast, "market_cap", None),
            "fifty_two_week_high": round(fast.year_high, 2) if getattr(fast, "year_high", None) else None,
            "fifty_two_week_low": round(fast.year_low, 2) if getattr(fast, "year_low", None) else None,
            "forward_pe": round(info.get("forwardPE", 0), 2) if info.get("forwardPE") else None,
            "trailing_pe": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else None,
            "price_to_sales": round(info.get("priceToSalesTrailing12Months", 0), 2) if info.get("priceToSalesTrailing12Months") else None,
        }
    except Exception as e:
        return {"error": f"Failed to fetch market data for {clean_ticker}: {str(e)}"}
