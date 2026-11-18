import json
import os
from pathlib import Path

import httpx
import streamlit as st

API_BASE_URL = os.getenv("AGENT_API_URL", "http://localhost:8000")
PROJECT_ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="Aegis | Grounded Agent Operations",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root { --aegis-navy: #0f172a; --aegis-blue: #2563eb; --aegis-bg: #f4f7fb; }
.stApp { background: var(--aegis-bg); }
.block-container { max-width: 1180px; padding-top: 1.5rem; }
section[data-testid="stSidebar"] { background: #111827; }
section[data-testid="stSidebar"] * { color: #e5e7eb; }
section[data-testid="stSidebar"] .stTextInput input { background: #1f2937; border: 1px solid #374151; }
.brand { display:flex; align-items:center; gap:12px; margin-bottom:4px; }
.brand-mark { width:38px; height:38px; border-radius:10px; background:linear-gradient(135deg,#2563eb,#1d4ed8); display:grid; place-items:center; color:white; font-weight:800; }
.brand-title { font-size:26px; font-weight:760; color:#0f172a; line-height:1.1; }
.brand-subtitle { color:#64748b; font-size:13px; margin-top:5px; }
.status-card { border:1px solid #dbe4f0; background:white; border-radius:12px; padding:14px 16px; }
.status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#16a34a; margin-right:7px; }
[data-testid="stMetric"] { background:white; border:1px solid #e2e8f0; border-radius:12px; padding:14px; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { height:44px; border-radius:8px 8px 0 0; padding-left:14px; padding-right:14px; }
div[data-testid="stChatMessage"] { border:1px solid #e2e8f0; background:white; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Aegis Control Plane")
    st.caption("Grounded Agent Operations")
    st.divider()

    st.markdown("**Request Context**")
    tenant_id = st.text_input("Tenant ID", value="tenant_acme")
    user_id = st.text_input("User ID", value="user_1001")
    session_id = st.text_input(
        "Session ID",
        value="00000000-0000-4000-8000-000000000001",
    )

    st.divider()
    try:
        health = httpx.get(f"{API_BASE_URL}/health", timeout=3).json()
        api_status = "Operational"
        st.markdown('<div class="status-card"><span class="status-dot"></span><b>API Operational</b></div>', unsafe_allow_html=True)
        st.caption(f"Mode: {health.get('mode', 'enterprise').upper()}")
    except httpx.HTTPError:
        api_status = "Unavailable"
        st.warning("API is unavailable")

st.markdown("""
<div class="brand">
  <div class="brand-mark">A</div>
  <div>
    <div class="brand-title">Aegis Grounded Agent</div>
    <div class="brand-subtitle">Enterprise operations console · policy-grounded retrieval · controlled execution</div>
  </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Platform Status", api_status if 'api_status' in locals() else "Unavailable")
col2.metric("Retrieval Mode", "Hybrid RAG")
col3.metric("Release Gate", "Validation Required")

st.divider()

overview_tab, workflow_tab, mcp_tab, approvals_tab, telemetry_tab, scorecard_tab = st.tabs([
    "Overview & Query",
    "Workflow Architecture",
    "MCP & Plugins",
    "Approval Queue",
    "Trace Explorer",
    "Release Scorecard",
])

with overview_tab:
    left, right = st.columns([2.2, 1])
    with left:
        st.subheader("Grounded Assistant")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        query = st.chat_input("Ask a policy or product question")
        if query:
            st.session_state.chat_history.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.write(query)

            try:
                response = httpx.post(
                    f"{API_BASE_URL}/api/v1/agent/query",
                    json={
                        "tenant_id": tenant_id,
                        "user_id": user_id,
                        "session_id": session_id,
                        "query": query,
                    },
                    timeout=10,
                )
                response.raise_for_status()
                payload = response.json()
                assistant_text = payload["answer"]

                with st.chat_message("assistant"):
                    st.write(assistant_text)
                    if payload.get("citations"):
                        st.caption("Evidence")
                        for citation in payload["citations"]:
                            st.markdown(
                                f"- `{citation['chunk_id']}` · "
                                f"{citation['source_uri']} · "
                                f"score `{citation['score']:.3f}`"
                            )

                st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})
            except httpx.HTTPError as exc:
                with st.chat_message("assistant"):
                    st.error(f"The agent service could not complete the request: {exc}")

    with right:
        st.subheader("Request Controls")
        st.selectbox("Environment", ["Development", "Staging", "Production"], disabled=True)
        st.selectbox("Response Mode", ["Grounded Answer", "Abstain on Low Confidence"], disabled=True)
        st.checkbox("PII Redaction", value=True, disabled=True)
        st.checkbox("Prompt-Injection Shield", value=True, disabled=True)
        st.checkbox("Tier-3 HITL Gate", value=True, disabled=True)

with workflow_tab:
    st.subheader("System Workflow")
    image_path = PROJECT_ROOT / "docs" / "workflow_orchestration.png"
    if image_path.exists():
        st.image(str(image_path), width="stretch")
    else:
        st.warning("Workflow diagram is not available at the configured path.")

    st.subheader("Architecture Contract")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingress", "Security & Cache")
    c2.metric("Triage", "Deterministic Routes")
    c3.metric("Retrieval", "BM25 + RRF")
    c4.metric("Control", "Loop + HITL")

with mcp_tab:
    st.subheader("MCP Server & Plugin Configuration")
    config_path = PROJECT_ROOT / "mcp_config.json"
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        left, right = st.columns([1.4, 1])
        with left:
            st.json(config)
        with right:
            st.markdown("**Registered MCP Servers**")
            for name in config.get("mcpServers", {}):
                st.markdown(f"- `{name}`")
            st.markdown("**Registered Plugins**")
            for plugin in config.get("plugins", []):
                st.markdown(f"- `{plugin['name']}` · `{plugin['stage']}`")
    else:
        st.warning("MCP configuration file was not found.")

with approvals_tab:
    st.subheader("Pending Human Review")
    try:
        approvals = httpx.get(f"{API_BASE_URL}/api/v1/approvals", timeout=5).json()
        if approvals:
            st.dataframe(
                [
                    {"Approval ID": approval_id, **approval}
                    for approval_id, approval in approvals.items()
                ],
                width="stretch",
            )
        else:
            st.info("No pending approvals.")
    except httpx.HTTPError as exc:
        st.warning(f"Approval service unavailable: {exc}")

with telemetry_tab:
    st.subheader("Distributed Trace Explorer")
    trace_id = st.text_input("Trace ID")
    if trace_id:
        try:
            trace = httpx.get(f"{API_BASE_URL}/api/v1/trace/{trace_id}", timeout=5).json()
            span_left, audit_right = st.columns(2)
            with span_left:
                st.markdown("**Spans**")
                st.json(trace.get("spans", []))
            with audit_right:
                st.markdown("**Audit Events**")
                st.json(trace.get("audit", []))
        except httpx.HTTPError as exc:
            st.warning(f"Trace service unavailable: {exc}")

with scorecard_tab:
    st.subheader("Enterprise Release Scorecard")
    st.caption("This view reports measured release evidence only. It must not be used as an approval until benchmark datasets are executed.")

    try:
        kpis = httpx.get(f"{API_BASE_URL}/api/v1/kpis", timeout=5).json()
    except httpx.HTTPError:
        kpis = {
            "mode": "validation",
            "passed": 0,
            "total": 36,
            "release_status": "NOT MEASURED",
        }

    passed = kpis.get("passed", 0)
    total = kpis.get("total", 36)
    c1, c2, c3 = st.columns(3)
    c1.metric("Measured KPIs", f"{passed}/{total}")
    c2.metric("Release Status", kpis.get("release_status", "NOT MEASURED"))
    c3.metric("Current Evidence", "Partial prototype")

    st.progress(min(passed / total, 1.0) if total else 0.0)
    if passed < total:
        st.error("Release blocked: benchmark evidence is incomplete.")
