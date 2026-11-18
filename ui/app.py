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
html, body, [class*="css"] { font-family: Inter, "Segoe UI", Arial, sans-serif; }
:root { --ae-navy:#172033; --ae-border:#dfe5ec; --ae-blue:#3157a5; }
header[data-testid="stHeader"] { background:#ffffff; height:52px; min-height:52px; border-bottom:1px solid #edf0f4; }
#MainMenu, footer { visibility:hidden; }
[data-testid="stToolbar"] { display:none !important; }
[data-testid="stDecoration"] { display:none !important; }
[data-testid="stStatusWidget"] { display:none !important; }
.stApp { background:#f5f7fa; }
.block-container { max-width:1180px; margin:0 auto; padding:1.5rem 2rem 3rem 2rem; overflow:visible; }
section[data-testid="stSidebar"] { background:#172033; border-right:1px solid #25314a; }
section[data-testid="stSidebar"] > div { padding-top:1.25rem; }
section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] .caption { color:#dbe5f3 !important; }
section[data-testid="stSidebar"] .stTextInput input { background:#202d46; color:#f8fafc; border:1px solid #3a4964; border-radius:8px; }
section[data-testid="stSidebar"] hr { border-color:#344158; }
.app-header { min-height:76px; height:76px; display:flex; align-items:center; justify-content:space-between; margin:0 0 18px 0; padding:14px 18px; background:#ffffff; border:1px solid var(--ae-border); border-radius:12px; box-shadow:0 2px 10px rgba(31,42,68,.04); overflow:hidden; }
.app-brand { display:flex; align-items:center; gap:13px; min-width:0; height:48px; }
.app-mark { flex:0 0 42px; width:42px; height:42px; display:grid; place-items:center; border-radius:10px; background:#3157a5; color:#ffffff; font-size:20px; font-weight:800; }
.app-title { height:25px; color:#172033; font-size:20px; font-weight:750; line-height:25px; white-space:nowrap; overflow:visible; }
.app-subtitle { height:18px; color:#667085; font-size:13px; line-height:18px; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.app-status { display:flex; align-items:center; gap:8px; color:#35604d; font-size:12px; font-weight:700; white-space:nowrap; margin-left:16px; }
.status-pulse { width:8px; height:8px; border-radius:50%; background:#16835a; box-shadow:0 0 0 4px #e5f4ee; }
.status-pulse-off { background:#b42318; box-shadow:0 0 0 4px #fee4e2; }
[data-testid="stMetric"] { background:#ffffff; border:1px solid var(--ae-border); border-radius:10px; padding:12px 14px; }
[data-testid="stMetricLabel"] { color:#667085; white-space:normal; }
[data-testid="stMetricValue"] { color:#172033; white-space:normal; overflow:visible; }
.stTabs [data-baseweb="tab-list"] { gap:4px; border-bottom:1px solid var(--ae-border); }
.stTabs [data-baseweb="tab"] { height:46px; color:#667085; font-weight:650; padding:0 12px; }
.stTabs [aria-selected="true"] { color:#3157a5; border-bottom-color:#3157a5; }
[data-testid="stChatMessage"] { background:#ffffff; border:1px solid var(--ae-border); border-radius:10px; color:#253047; }
[data-testid="stChatInput"] textarea { border:1px solid #bcc7d5; border-radius:9px; }
[data-testid="stDataFrame"] { border:1px solid var(--ae-border); border-radius:8px; }
.status-card { border:1px solid #344158; background:#202d46; border-radius:8px; padding:10px 12px; }
.status-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#65b891; margin-right:7px; }

.app-header {
  align-items: center;
}

@media (max-width: 720px) {
  .block-container { padding:1rem 1rem 2rem 1rem; }
  .app-header { height:auto; min-height:82px; align-items:flex-start; }
  .app-brand { height:auto; }
  .app-title { height:auto; white-space:normal; }
  .app-subtitle { height:auto; max-width:240px; white-space:normal; }
  .app-status { display:none; }
}
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

header_status = "SYSTEM AVAILABLE" if locals().get("api_status") == "Operational" else "SYSTEM OFFLINE"
status_class = "status-pulse" if locals().get("api_status") == "Operational" else "status-pulse status-pulse-off"
st.markdown(f"""
<div class="app-header">
  <div class="app-brand">
    <div class="app-mark">A</div>
    <div>
      <div class="app-title">Aegis Grounded Agent</div>
      <div class="app-subtitle">Enterprise operations console · Policy-grounded retrieval · Controlled execution</div>
    </div>
  </div>
  <div class="app-status"><span class="{status_class}"></span> {header_status}</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Platform Status", api_status if 'api_status' in locals() else "Unavailable")
col2.metric("Retrieval Mode", "Grounded Hybrid RAG")
col3.metric("Release Gate", "Evidence Required")

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
