"""Firestore backend tools for MarketStrat agent."""
from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-62c2cc101cef"
COLLECTION_NAME = "companies"

_db_client: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def list_tracked_companies() -> List[Dict[str, Any]]:
    """List all tracked companies in the MarketStrat catalog.

    Returns:
        A list of company summaries with ticker, name, sector, stock price, and market sentiment.
    """
    db = get_db()
    docs = db.collection(COLLECTION_NAME).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append({
            "ticker": data.get("ticker"),
            "name": data.get("name"),
            "sector": data.get("sector"),
            "stock_price": data.get("stock_price"),
            "market_sentiment": data.get("market_sentiment"),
            "analyst_rating_consensus": data.get("analyst_rating_consensus"),
        })
    return results


def get_company_details(ticker: str) -> Dict[str, Any]:
    """Retrieve full financial fundamentals, analyst sentiment, and strategic priorities for a company.

    Args:
        ticker: The stock ticker symbol of the company (e.g. 'NVDA', 'GOOGL', 'TSLA', 'SNOW').

    Returns:
        A dictionary containing the company's full financials, analyst sentiment summary, and strategic recommendations.
    """
    doc_id = ticker.strip().lower()
    db = get_db()
    doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Company with ticker '{ticker.upper()}' not found in database."}

    return doc.to_dict()


def upsert_company(
    ticker: str,
    name: str,
    sector: str,
    stock_price: float,
    revenue_ttm_billions: float,
    revenue_growth_yoy_pct: float,
    operating_margin_pct: float,
    market_sentiment: str,
    analyst_rating_consensus: str,
    price_target_avg: float,
    analyst_summary: str,
    strategic_priorities: List[str],
) -> Dict[str, Any]:
    """Add a new company or update an existing company in the MarketStrat database.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL', 'MSFT').
        name: Full corporate name.
        sector: Primary industry sector.
        stock_price: Current stock price in USD.
        revenue_ttm_billions: Trailing 12-month revenue in billions of dollars.
        revenue_growth_yoy_pct: Year-over-year revenue growth percentage.
        operating_margin_pct: Operating margin percentage.
        market_sentiment: Current market sentiment (e.g. 'Bullish', 'Neutral', 'Bearish').
        analyst_rating_consensus: Wall Street consensus rating (e.g. 'Strong Buy', 'Hold').
        price_target_avg: Average analyst price target in USD.
        analyst_summary: Qualitative synthesis of analyst reports and market perception.
        strategic_priorities: List of key strategic recommendations to improve standing.

    Returns:
        A confirmation dictionary indicating success.
    """
    doc_id = ticker.strip().lower()
    payload = {
        "ticker": ticker.strip().upper(),
        "name": name.strip(),
        "sector": sector.strip(),
        "stock_price": float(stock_price),
        "revenue_ttm_billions": float(revenue_ttm_billions),
        "revenue_growth_yoy_pct": float(revenue_growth_yoy_pct),
        "operating_margin_pct": float(operating_margin_pct),
        "market_sentiment": market_sentiment.strip(),
        "analyst_rating_consensus": analyst_rating_consensus.strip(),
        "price_target_avg": float(price_target_avg),
        "analyst_summary": analyst_summary.strip(),
        "strategic_priorities": strategic_priorities,
    }
    db = get_db()
    db.collection(COLLECTION_NAME).document(doc_id).set(payload)
    return {"status": "success", "message": f"Successfully updated data for {ticker.upper()}.", "data": payload}
