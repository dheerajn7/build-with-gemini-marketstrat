"""SEC EDGAR public financial filing tools for MarketStrat."""
import json
import urllib.request
from typing import Any, Dict, List

SEC_HEADERS = {
    "User-Agent": "MarketStratAgent admin@marketstrat.internal"
}


def fetch_sec_filings(ticker: str, limit: int = 5) -> Dict[str, Any]:
    """Fetch official recent SEC regulatory filings (10-K, 10-Q, 8-K) from the US SEC EDGAR public API.

    Args:
        ticker: The stock ticker symbol (e.g. 'NVDA', 'AAPL', 'GOOGL', 'TSLA').
        limit: Number of recent filings to return (default: 5).

    Returns:
        A dictionary with company identification, SIC industry description, and recent SEC filings.
    """
    clean_ticker = ticker.strip().upper()
    try:
        # 1. Resolve ticker to SEC CIK number
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        req = urllib.request.Request(tickers_url, headers=SEC_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            mapping = json.loads(resp.read().decode("utf-8"))

        cik = None
        for entry in mapping.values():
            if entry.get("ticker") == clean_ticker:
                cik = str(entry.get("cik_str")).zfill(10)
                break

        if not cik:
            return {"error": f"Ticker '{clean_ticker}' not found in SEC EDGAR registry."}

        # 2. Fetch submissions from SEC EDGAR
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        sub_req = urllib.request.Request(submissions_url, headers=SEC_HEADERS)
        with urllib.request.urlopen(sub_req, timeout=10) as resp:
            company_data = json.loads(resp.read().decode("utf-8"))

        recent = company_data.get("filings", {}).get("recent", {})
        forms: List[str] = recent.get("form", [])
        filing_dates: List[str] = recent.get("filingDate", [])
        accession_numbers: List[str] = recent.get("accessionNumber", [])
        descriptions: List[str] = recent.get("primaryDocDescription", [])

        filings = []
        for i in range(min(len(forms), limit)):
            form_type = forms[i]
            acc_num = accession_numbers[i].replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/"
            filings.append({
                "form": form_type,
                "filing_date": filing_dates[i] if i < len(filing_dates) else None,
                "description": descriptions[i] if i < len(descriptions) else None,
                "sec_archive_url": filing_url,
            })

        return {
            "ticker": clean_ticker,
            "cik": cik,
            "company_name": company_data.get("name"),
            "sic_description": company_data.get("sicDescription"),
            "fiscal_year_end": company_data.get("fiscalYearEnd"),
            "recent_filings": filings,
        }
    except Exception as e:
        return {"error": f"Failed to retrieve SEC EDGAR filings for {clean_ticker}: {str(e)}"}
