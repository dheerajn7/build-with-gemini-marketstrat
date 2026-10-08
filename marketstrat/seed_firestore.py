"""Seed Firestore with sample companies for MarketStrat."""
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-62c2cc101cef"
COLLECTION_NAME = "companies"

SEEDED_COMPANIES = [
    {
        "ticker": "NVDA",
        "name": "NVIDIA Corporation",
        "sector": "Semiconductors & AI Hardware",
        "stock_price": 128.50,
        "revenue_ttm_billions": 112.8,
        "revenue_growth_yoy_pct": 122.0,
        "operating_margin_pct": 62.5,
        "market_sentiment": "Very Bullish",
        "analyst_rating_consensus": "Strong Buy",
        "price_target_avg": 150.00,
        "analyst_summary": "Dominates AI accelerator market; Blackwell ramp driving sustained enterprise & hyperscaler demand, though supply constraints remain key bottleneck.",
        "strategic_priorities": [
            "Diversify revenue into sovereign AI infrastructure",
            "Accelerate software ecosystem monetization via CUDA & enterprise AI bundles",
            "Mitigate geopolitical supply chain concentration"
        ]
    },
    {
        "ticker": "GOOGL",
        "name": "Alphabet Inc.",
        "sector": "Internet & Cloud Computing",
        "stock_price": 182.20,
        "revenue_ttm_billions": 350.0,
        "revenue_growth_yoy_pct": 14.5,
        "operating_margin_pct": 32.0,
        "market_sentiment": "Bullish",
        "analyst_rating_consensus": "Buy",
        "price_target_avg": 205.00,
        "analyst_summary": "Cloud growth accelerated by Vertex AI and TPU adoption; Search advertising resilient despite AI transition questions.",
        "strategic_priorities": [
            "Protect search ad economics while scaling AI Overviews",
            "Drive enterprise multi-cloud deals via Gemini integration",
            "Optimize cost structure with custom silicon (TPUs)"
        ]
    },
    {
        "ticker": "TSLA",
        "name": "Tesla, Inc.",
        "sector": "Automotive & Clean Energy",
        "stock_price": 245.80,
        "revenue_ttm_billions": 97.2,
        "revenue_growth_yoy_pct": 2.8,
        "operating_margin_pct": 8.2,
        "market_sentiment": "Neutral / Volatile",
        "analyst_rating_consensus": "Hold",
        "price_target_avg": 230.00,
        "analyst_summary": "Auto gross margins under pressure from EV price competition; market perception increasingly tethered to Robotaxi & FSD autonomous execution.",
        "strategic_priorities": [
            "Lower next-gen vehicle manufacturing costs",
            "Prove commercial regulatory viability of unsupervised FSD / Robotaxi",
            "Scale energy storage business to offset auto margin compression"
        ]
    },
    {
        "ticker": "SNOW",
        "name": "Snowflake Inc.",
        "sector": "Data Cloud & Enterprise Software",
        "stock_price": 125.40,
        "revenue_ttm_billions": 3.4,
        "revenue_growth_yoy_pct": 28.0,
        "operating_margin_pct": -8.5,
        "market_sentiment": "Cautious",
        "analyst_rating_consensus": "Moderate Buy",
        "price_target_avg": 145.00,
        "analyst_summary": "Solid net retention and enterprise data lock-in, but product gross margins pressured by GPU infrastructure investments and competition from Databricks and Hyperscalers.",
        "strategic_priorities": [
            "Drive adoption of Cortex AI native workloads on Snowflake data",
            "Accelerate path toward GAAP operating profitability",
            "Deepen partnerships with major hyperscalers"
        ]
    }
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for item in SEEDED_COMPANIES:
        doc_id = item["ticker"].lower()
        print(f"Saving company {item['name']} ({item['ticker']}) to doc '{doc_id}'...")
        collection.document(doc_id).set(item)

    print("Seeding completed successfully!")


if __name__ == "__main__":
    seed()
