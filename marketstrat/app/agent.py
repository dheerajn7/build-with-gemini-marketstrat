# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.genai import types


from app.analyst_tools import (
    get_analyst_sentiment_summary,
    read_full_analyst_report,
    store_analyst_report,
)
from app.firestore_tools import (
    get_company_details,
    list_tracked_companies,
    upsert_company,
)
from app.market_tools import fetch_market_snapshot
from app.sec_edgar_tools import fetch_sec_filings


MODEL = "gemini-3.8-flash"


def _get_sandbox_code_executor() -> AgentEngineSandboxCodeExecutor:
    metadata_path = Path(__file__).resolve().parent.parent / "deployment_metadata.json"
    agent_engine_resource_name = "projects/652647694787/locations/us-east1/reasoningEngines/5954898900941799424"
    if metadata_path.exists():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                agent_engine_resource_name = meta.get("remote_agent_runtime_id", agent_engine_resource_name)
        except Exception:
            pass
    return AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_resource_name)


from app.a2ui_utils import a2ui_callback

_INSTRUCTION_PATH = os.path.join(os.path.dirname(__file__), "a2ui_instruction.txt")
if os.path.exists(_INSTRUCTION_PATH):
    with open(_INSTRUCTION_PATH, "r", encoding="utf-8") as f:
        instruction = f.read()
else:
    instruction = (
        "You are MarketStrat, an elite corporate strategy and equity intelligence agent. "
        "Your mission is to provide comprehensive, thorough strategic briefings on companies. "
        "When analyzing a company, conduct a multi-dimensional evaluation covering financial fundamentals, "
        "Wall Street sentiment, stock price correlation, and actionable corporate strategy."
    )


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=_get_sandbox_code_executor(),
    after_model_callback=a2ui_callback,
    tools=[
        fetch_market_snapshot,
        fetch_sec_filings,
        get_analyst_sentiment_summary,
        read_full_analyst_report,
        store_analyst_report,
        list_tracked_companies,
        get_company_details,
        upsert_company,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
