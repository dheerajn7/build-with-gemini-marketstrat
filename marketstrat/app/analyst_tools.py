"""Analyst report storage & market sentiment tools for MarketStrat."""
from typing import Any, Dict, List, Optional
import datetime
from google.cloud import firestore, storage

PROJECT_ID = "qwiklabs-gcp-04-62c2cc101cef"
BUCKET_NAME = "marketstrat-assets-qwiklabs-gcp-04-62c2cc101cef"
REPORTS_COLLECTION = "analyst_reports"

_firestore_client: Optional[firestore.Client] = None
_storage_client: Optional[storage.Client] = None


def get_firestore() -> firestore.Client:
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client(project=PROJECT_ID)
    return _firestore_client


def get_storage_bucket():
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client.bucket(BUCKET_NAME)


def get_analyst_sentiment_summary(ticker: str) -> Dict[str, Any]:
    """Retrieve indexed analyst sentiment, consensus price targets, and key research notes for a company.

    Args:
        ticker: The stock ticker symbol (e.g., 'NVDA', 'GOOGL', 'TSLA').

    Returns:
        A dictionary containing overall sentiment rating, average target price, list of analyst reports,
        and key takeaways.
    """
    clean_ticker = ticker.strip().upper()
    db = get_firestore()
    query = db.collection(REPORTS_COLLECTION).where("ticker", "==", clean_ticker).stream()

    reports = []
    total_target = 0.0
    total_sentiment = 0.0
    count = 0

    for doc in query:
        data = doc.to_dict()
        reports.append({
            "report_id": data.get("report_id"),
            "firm": data.get("firm"),
            "analyst": data.get("analyst"),
            "date": data.get("date"),
            "rating": data.get("rating"),
            "target_price": data.get("target_price"),
            "sentiment_score": data.get("sentiment_score"),
            "sentiment_label": data.get("sentiment_label"),
            "headline": data.get("headline"),
            "key_takeaways": data.get("key_takeaways", []),
            "storage_url": data.get("storage_url"),
        })
        if data.get("target_price"):
            total_target += float(data.get("target_price"))
        if data.get("sentiment_score") is not None:
            total_sentiment += float(data.get("sentiment_score"))
        count += 1

    if count == 0:
        return {
            "ticker": clean_ticker,
            "message": f"No analyst reports found in repository for {clean_ticker}."
        }

    avg_target = round(total_target / count, 2) if count > 0 else None
    avg_sentiment = round(total_sentiment / count, 2) if count > 0 else None
    sentiment_grade = (
        "Very Bullish" if avg_sentiment >= 0.7
        else "Bullish" if avg_sentiment >= 0.3
        else "Neutral" if avg_sentiment >= -0.2
        else "Bearish"
    )

    return {
        "ticker": clean_ticker,
        "reports_count": count,
        "consensus_target_price": avg_target,
        "average_sentiment_score": avg_sentiment,
        "market_sentiment_label": sentiment_grade,
        "reports": reports,
    }


def read_full_analyst_report(report_id: str) -> Dict[str, Any]:
    """Read the complete original text of an analyst report stored in Google Cloud Storage.

    Args:
        report_id: The unique identifier of the report (e.g. 'nvda_goldman_2026_q3').

    Returns:
        A dictionary containing report metadata and the complete text of the analyst report.
    """
    db = get_firestore()
    doc_ref = db.collection(REPORTS_COLLECTION).document(report_id.strip())
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Report '{report_id}' not found in database."}

    data = doc.to_dict()
    blob_path = data.get("storage_blob_path")

    try:
        bucket = get_storage_bucket()
        blob = bucket.blob(blob_path)
        content = blob.download_as_text()
        return {
            "report_id": report_id,
            "ticker": data.get("ticker"),
            "firm": data.get("firm"),
            "date": data.get("date"),
            "rating": data.get("rating"),
            "target_price": data.get("target_price"),
            "headline": data.get("headline"),
            "storage_url": data.get("storage_url"),
            "full_text": content,
        }
    except Exception as e:
        return {"error": f"Failed to download report from storage: {str(e)}"}


def store_analyst_report(
    ticker: str,
    firm: str,
    analyst: str,
    date: str,
    rating: str,
    target_price: float,
    sentiment_score: float,
    sentiment_label: str,
    headline: str,
    key_takeaways: List[str],
    full_report_text: str,
) -> Dict[str, Any]:
    """Store a new analyst research note or earnings commentary into Cloud Storage and index in Firestore.

    Args:
        ticker: Stock ticker symbol (e.g. 'MSFT', 'NVDA').
        firm: Investment bank / research firm (e.g., 'Morgan Stanley', 'Goldman Sachs').
        analyst: Name of the publishing equity research analyst.
        date: Publication date (YYYY-MM-DD).
        rating: Investment rating ('Strong Buy', 'Buy', 'Hold', 'Sell').
        target_price: Analyst 12-month target price.
        sentiment_score: Numerical sentiment score from -1.0 (extremely bearish) to 1.0 (extremely bullish).
        sentiment_label: High level perception ('Very Bullish', 'Bullish', 'Neutral', 'Bearish').
        headline: Main report title.
        key_takeaways: Bulleted list of strategic insights or catalysts.
        full_report_text: Unabridged research note content.

    Returns:
        A confirmation dictionary with the stored report ID and public Cloud Storage URL.
    """
    clean_ticker = ticker.strip().upper()
    slug_firm = firm.lower().replace(" ", "_")[:12]
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_id = f"{clean_ticker.lower()}_{slug_firm}_{timestamp}"

    blob_path = f"analyst_reports/{clean_ticker.lower()}/{report_id}.txt"

    # 1. Upload to GCS
    bucket = get_storage_bucket()
    blob = bucket.blob(blob_path)
    blob.upload_from_string(full_report_text.strip(), content_type="text/plain; charset=utf-8")
    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_path}"

    # 2. Index in Firestore
    doc_payload = {
        "report_id": report_id,
        "ticker": clean_ticker,
        "firm": firm.strip(),
        "analyst": analyst.strip(),
        "date": date.strip(),
        "rating": rating.strip(),
        "target_price": float(target_price),
        "sentiment_score": float(sentiment_score),
        "sentiment_label": sentiment_label.strip(),
        "headline": headline.strip(),
        "key_takeaways": key_takeaways,
        "storage_blob_path": blob_path,
        "storage_url": public_url,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    db = get_firestore()
    db.collection(REPORTS_COLLECTION).document(report_id).set(doc_payload)

    return {
        "status": "success",
        "report_id": report_id,
        "storage_url": public_url,
        "message": f"Analyst report for {clean_ticker} successfully stored in Cloud Storage and indexed in Firestore."
    }
