"""Seed Cloud Storage with full text analyst reports and Firestore with indexed metadata."""
from google.cloud import firestore, storage
import datetime

PROJECT_ID = "qwiklabs-gcp-04-62c2cc101cef"
BUCKET_NAME = "marketstrat-assets-qwiklabs-gcp-04-62c2cc101cef"
REPORTS_COLLECTION = "analyst_reports"

SAMPLE_REPORTS = [
    {
        "report_id": "nvda_goldman_2026_q3",
        "ticker": "NVDA",
        "firm": "Goldman Sachs Equity Research",
        "analyst": "Toshiya Hari",
        "date": "2026-09-15",
        "rating": "Strong Buy",
        "target_price": 165.0,
        "sentiment_score": 0.92,  # -1.0 to 1.0
        "sentiment_label": "Very Bullish",
        "headline": "Blackwell Architecture Supercycle Exceeding Expectations; Hyperscaler Capex Expanding",
        "key_takeaways": [
            "Blackwell production yield ramps faster than feared; cloud supply commits sold out through next 3 quarters.",
            "Software monetization layer (CUDA / NIMs) creating sticky enterprise enterprise moat.",
            "Risk factor: Geopolitical export controls and high custom ASIC competition from Google TPU / AWS Trainium."
        ],
        "full_text": """
GOLDMAN SACHS EQUITY RESEARCH | COMPANY UPDATE
Date: September 15, 2026
Ticker: NVDA (NVIDIA Corporation) | Current Price: $128.50 | Target: $165.00 | Rating: BUY (Conviction List)

EXECUTIVE SUMMARY:
We reiterate our Conviction Buy rating on NVIDIA Corporation following comprehensive checks across the semiconductor supply chain in Taiwan and North American hyperscaler capex forecasts. Demand for the Blackwell architecture is demonstrating unprecedented durability.

FINANCIAL TRAJECTORY & MARKET PERCEPTION:
Hyperscalers (Google, Microsoft, Meta) are continuously revising their infrastructure capex upwards, confirming that compute constraints remain the primary limiter of frontier AI deployment. Operating margins above 60% reflect extraordinary pricing power.

RISK & STRATEGIC RECOMMENDATIONS:
1. Sovereign AI investments across Europe and the Middle East will provide a critical hedge as US hyperscaler capex inevitably normalizes.
2. NVIDIA must maintain relentless software development around NIM (Inference Microservices) to prevent hyperscalers from defecting to internal custom ASICs.
        """
    },
    {
        "report_id": "nvda_morganstanley_2026_q3",
        "ticker": "NVDA",
        "firm": "Morgan Stanley",
        "analyst": "Joseph Moore",
        "date": "2026-09-28",
        "rating": "Overweight",
        "target_price": 150.0,
        "sentiment_score": 0.85,
        "sentiment_label": "Bullish",
        "headline": "Datacenter Momentum Intact; Networking (Spectrum-X) Emerging as Strong Second Engine",
        "key_takeaways": [
            "Datacenter networking revenue is growing in tandem with GPU clusters.",
            "Customer concentration in top 4 hyperscalers remains elevated at ~40% of revenue.",
            "Gross margin stability above 70% anticipated through fiscal year-end."
        ],
        "full_text": """
MORGAN STANLEY RESEARCH | EQUITY PERSPECTIVE
Date: September 28, 2026
Ticker: NVDA (NVIDIA Corp) | Rating: OVERWEIGHT | Target: $150.00

KEY OBSERVATIONS:
While investor debate has shifted towards inference workloads versus training workloads, NVIDIA's full-stack approach (GPU + Spectrum-X Ethernet + InfiniBand) continues to capture premium enterprise budgets. 

MARKET PERCEPTION VS FUNDAMENTALS:
Consensus sentiment is extraordinarily positive. Any minor quarterly guidance deceleration could prompt short-term multiple compression, but structural leadership remains unchallenged.
        """
    },
    {
        "report_id": "googl_jpmorgan_2026_q3",
        "ticker": "GOOGL",
        "firm": "JPMorgan Chase",
        "analyst": "Doug Anmuth",
        "date": "2026-09-20",
        "rating": "Overweight",
        "target_price": 210.0,
        "sentiment_score": 0.78,
        "sentiment_label": "Bullish",
        "headline": "Google Cloud Inflection and Vertex AI Ecosystem Driving Multi-Cloud Wins",
        "key_takeaways": [
            "Google Cloud operating margins expanding rapidly towards 15%+.",
            "AI Overviews in Search showing stabilized monetizable CTR (click-through rates).",
            "Sixth-generation TPU (Trillium) offering substantial cost-per-token advantages."
        ],
        "full_text": """
JPMORGAN EQUITY RESEARCH | NORTH AMERICA TECHNOLOGY
Date: September 20, 2026
Ticker: GOOGL (Alphabet Inc.) | Rating: OVERWEIGHT | Price Target: $210.00

OVERVIEW:
Alphabet is demonstrating that its integrated full-stack infrastructure (custom silicon, frontier Gemini models, massive consumer surface area) provides strong defensive moats against standalone AI competitors.

PERCEPTION IN THE MARKET:
Wall Street sentiment has markedly improved from earlier antitrust and search disruption anxieties. Cloud revenue acceleration has repositioned Alphabet as an AI-native winner.
        """
    },
    {
        "report_id": "tsla_bernstein_2026_q3",
        "ticker": "TSLA",
        "firm": "Bernstein Research",
        "analyst": "Toni Sacconaghi",
        "date": "2026-09-10",
        "rating": "Underperform",
        "target_price": 140.0,
        "sentiment_score": -0.45,
        "sentiment_label": "Bearish",
        "headline": "Core Auto Margins Under Structural Threat; Autonomous Valuation Premature",
        "key_takeaways": [
            "Automotive gross margins excluding regulatory credits struggling to stay above 14%.",
            "FSD adoption curves plateauing in key markets like Europe and China.",
            "Robotaxi hardware economics require regulatory approvals that are multi-year hurdles."
        ],
        "full_text": """
BERNSTEIN RESEARCH | GLOBAL AUTOMOTIVE & MOBILITY
Date: September 10, 2026
Ticker: TSLA (Tesla, Inc.) | Rating: UNDERPERFORM | Price Target: $140.00

ANALYSIS:
We remain skeptical of Tesla's near-term earnings inflection. While enthusiasm for robotics (Optimus) and Robotaxis dominates retail market sentiment, institutional investors face deteriorating automotive ASPs and fierce competition from BYD and European legacy OEMs.

STRATEGIC DIRECTIVES:
Tesla must accelerate its low-cost sub-$25k vehicle platform to reignite unit delivery volume before autonomous software monetization can materialize at scale.
        """
    }
]


def seed():
    print(f"Connecting to Cloud Storage bucket '{BUCKET_NAME}' and Firestore project '{PROJECT_ID}'...")
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    firestore_client = firestore.Client(project=PROJECT_ID)
    reports_col = firestore_client.collection(REPORTS_COLLECTION)

    for item in SAMPLE_REPORTS:
        report_id = item["report_id"]
        blob_path = f"analyst_reports/{item['ticker'].lower()}/{report_id}.txt"
        
        # 1. Upload full report text to Cloud Storage
        blob = bucket.blob(blob_path)
        blob.upload_from_string(item["full_text"].strip(), content_type="text/plain; charset=utf-8")
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_path}"
        print(f"Uploaded full report to GCS: {blob_path}")

        # 2. Store indexed metadata and sentiment in Firestore
        doc_data = {
            "report_id": report_id,
            "ticker": item["ticker"].upper(),
            "firm": item["firm"],
            "analyst": item["analyst"],
            "date": item["date"],
            "rating": item["rating"],
            "target_price": item["target_price"],
            "sentiment_score": item["sentiment_score"],
            "sentiment_label": item["sentiment_label"],
            "headline": item["headline"],
            "key_takeaways": item["key_takeaways"],
            "storage_blob_path": blob_path,
            "storage_url": public_url,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        reports_col.document(report_id).set(doc_data)
        print(f"Indexed metadata in Firestore collection '{REPORTS_COLLECTION}': doc '{report_id}'")

    print("\nAnalyst report storage & database seeding completed successfully!")


if __name__ == "__main__":
    seed()
