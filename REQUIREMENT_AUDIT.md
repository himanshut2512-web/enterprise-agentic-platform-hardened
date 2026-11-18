# Enterprise Requirement Compliance Audit

**Project:** The Unreliable Assistant → Enterprise-Grade Agentic Platform
**Audit date:** 2026-11-18
**Evidence reviewed:**
- `Unreliable_Assistant_MidCheck_Enterprise_Blueprint_v2.docx`
- `Post_Hardening_Engineering_Audit_Report.docx`
- `SLM_Comprehensive_Guide.docx`
- `design.md`
- Repository source, tests, UI, MCP configuration, and runtime behavior

---

## 1. Executive conclusion

**Overall implementation status: PARTIAL / NOT PRODUCTION-CERTIFIED.**

The repository implements a demonstrable application skeleton and several core safety behaviors, but it does not implement the document's enterprise production architecture or prove any of the required 36-KPI release gates.

### Honest status summary

| Area | Status |
|---|---|
| Pre-build design artifact | Implemented |
| Workflow diagram | Partially implemented |
| API and basic workbench | Implemented |
| Pydantic strict models | Implemented |
| PII and injection regex controls | Partially implemented |
| Tier-3 pending approval | Partially implemented |
| Tenant-scoped cache key | Partially implemented |
| 3-stage hybrid retrieval | Not fully implemented |
| MCP SDK and MCP transports | Not fully implemented |
| Redis / PostgreSQL / pgvector | Not implemented |
| Real ONNX dense/rerank models | Not implemented |
| Bounded ReAct state machine | Not fully implemented |
| Goal anchoring / memory windows | Not implemented |
| Subagent isolation | Not implemented |
| RAGAS / NLI / 250-Q golden set | Not implemented |
| OpenTelemetry Collector / Grafana / Tempo | Not implemented |
| 50K load scripts and evidence | Not implemented |
| Obsidian / Graphify implementation | Not implemented |
| 36-KPI production measurement | Not implemented |

---

## 2. Gate-by-gate audit

### Gate 0 — Enterprise stack, MCP, plugins

| Requirement | Status | Evidence / finding |
|---|---|---|
| Python 3.11 / FastAPI / async runtime | **Partially implemented** | FastAPI, Pydantic and async dependencies exist, but runtime is synchronous endpoint logic and the repository virtual environment is Python 3.14 rather than the 3.11 design target. |
| NGINX / Envoy edge | **Missing** | No gateway, TLS, rate-limiter, or ingress fan-in configuration. |
| MCP JSON-RPC servers | **Partially implemented** | FastAPI `/mcp` JSON-RPC-shaped endpoints exist, but not the MCP SDK, MCP resources, stdio protocol, Streamable HTTP/SSE, signatures, or MCP client session wiring. |
| `mcp-hybrid-rag` | **Partially implemented** | `app/mcp_servers/rag_server.py` exists. It exposes a JSON-RPC-shaped HTTP endpoint only. |
| `mcp-state-store` | **Partially implemented** | `app/mcp_servers/state_server.py` exists. It uses separate in-memory state, not PostgreSQL/Redis. |
| `mcp-graphify-vault` | **Misleading / missing** | `app/mcp_servers/graphify_server.py` returns static/fake node and subgraph values. |
| Pluggy plugin registry | **Missing** | Direct Python classes implement PII/injection behavior; no Pluggy entry points or hot registry. |
| MCP configuration | **Partially implemented** | `mcp_config.json` exists, but it is not consumed by the main application. |

**Gate 0 verdict: NOT COMPLETE.**

### Gate 1 — `design.md`

| Requirement | Status | Evidence / finding |
|---|---|---|
| Mandatory pre-build artifact | **Implemented** | `design.md` exists and covers charter, contracts, topology, latency budget, KPI, FMEA, and ADR sections. |
| Seven required sections | **Implemented** | The document includes the requested design structure. |

**Gate 1 verdict: COMPLETE AS AN ARTIFACT; DRAFT NOT A LOCKED PRODUCTION CONTRACT.**

### Gate 2 — workflow orchestration image

| Requirement | Status | Evidence / finding |
|---|---|---|
| High-DPI workflow image | **Implemented** | `docs/workflow_orchestration.png` exists. |
| Source DOT/Python | **Missing** | The repository has no `docs/make_diagram.py` or `docs/workflow_orchestration.dot`, despite `design.md` referring to them. |
| Detailed zone/OTel rendering | **Partially implemented** | The image exists, but its implementation source and all required live routing/telemetry detail should be reverified against the rendered output. |

**Gate 2 verdict: PARTIALLY COMPLETE.**

### Gate 3 — hybrid RAG and reranking

| Requirement | Status | Evidence / finding |
|---|---|---|
| BM25Okapi + PorterStemmer + 50 candidates | **Partially implemented** | `rank-bm25` is not used. `app/core/rag.py` implements a custom BM25-like loop, no Porter stemmer, and no inverted index. |
| Dense bge-large ONNX + FAISS HNSW | **Missing** | Dense stage is Jaccard-like token-set overlap, not an embedding model or FAISS. |
| RRF k=60 / dedup / pool=40 | **Partially implemented** | RRF is present and uses k=60. It does not implement explicit chunk-hash deduplication or the full pool contract. |
| Cross-encoder reranker ONNX/FP16 | **Missing** | Reranking is a formula combining RRF and lexical overlap. |
| rerank_k=4 / threshold >0.42 | **Partially implemented** | The code returns four chunks and abstains below 0.42, but this is not a cross-encoder confidence score. |
| 250-Q stratified Golden Dataset | **Missing** | Only seven static corpus records exist. |
| RAGAS scoring | **Missing** | No RAGAS package or evaluator is integrated. |
| NLI verification subagent | **Missing** | Verification is only a highest-score heuristic; no claim-to-chunk NLI model. |

**Gate 3 verdict: NOT COMPLETE.**

### Gate 4 — tool harness and loop engineering

| Requirement | Status | Evidence / finding |
|---|---|---|
| Pydantic strict validation | **Implemented** | Strict models exist in `app/core/models.py`. |
| Deterministic regex repair | **Partially implemented** | SKU and LOT repair exists, but the harness is not integrated into general tool dispatch. |
| RBAC tier checks | **Partially implemented** | `ToolExecutionHarness.rbac()` exists but is not called by API/tool execution paths. |
| UUIDv4 idempotency keys | **Missing** | No idempotency-key validation or persistent duplicate-result behavior. |
| Circuit breaker | **Partially implemented** | `CircuitBreaker` exists but `EnterpriseAgent` creates it and never dispatches tools through it. |
| Deterministic state machine | **Missing** | `STATES` is only declared. `answer()` is imperative and has no `INIT -> TRIAGE -> ... -> DONE/HALTED` transitions. |
| 5 iterations / 120 ms / 450 ms budgets | **Missing** | No enforcement of the stated loop limits. |
| Zero recursive self-calls | **Not demonstrated** | No loop execution framework exists. |

**Gate 4 verdict: NOT COMPLETE.**

### Gate 5 — context retention and drift control

| Requirement | Status | Evidence / finding |
|---|---|---|
| Immutable `GoalAnchorBlock` | **Missing** | No immutable goal block. |
| Observation compression ≤180 tokens | **Missing** | No observation compressor. |
| Sliding window of last three turns | **Missing** | No 3-turn hot-memory window. |
| Dual-memory Redis/RAM + PostgreSQL | **Missing** | Single in-memory Python dictionaries hold both cache and facts. |
| Verified `session_facts` table | **Missing** | No PostgreSQL schema or `session_facts` table. |

**Gate 5 verdict: NOT COMPLETE.**

### Gate 6 and Gate 7 — triage and subagents

| Requirement | Status | Evidence / finding |
|---|---|---|
| Distilled classifier with temp=0 | **Missing** | Triage is keyword matching. |
| ≤25 ms triage telemetry | **Missing** | No model, inference measurement, or OTel triage span. |
| `(intent, domain, risk_tier, complexity)` output | **Missing** | Triage returns only a route string. |
| Retrieval subagent isolation | **Missing** | Retrieval is one direct method call in the agent. |
| Execution subagent isolation | **Missing** | No isolated execution subagent. |
| Verification subagent | **Missing** | No independent model/context. |
| Read-only / state-mutating boundaries | **Partially implemented** | Only application routing separates RAG and mutation conceptually; there is no MCP subagent allow-list enforcement. |

**Gate 6/7 verdict: NOT COMPLETE.**

### Gate 8 — continuous RAGAS evaluation

| Requirement | Status | Evidence / finding |
|---|---|---|
| Automated RAGAS suite | **Missing** | No evaluation runner or golden dataset. |
| Continuous release gate | **Missing** | No CI workflow or RAGAS threshold enforcement. |

**Gate 8 verdict: NOT COMPLETE.**

### Gate 9 — reliability patterns

| Requirement | Status | Evidence / finding |
|---|---|---|
| Idempotent circuit breaker | **Partially implemented** | Failure hash logic exists but it is never wired into tool dispatch and is not persistent/idempotent. |
| Bulkheads | **Missing** | No rag/db/llm pools or isolation. |
| Deterministic abstention | **Implemented at demo level** | Retrieval below threshold returns abstention. The score is heuristic, not cross-encoder confidence. |
| Asynchronous HITL | **Partially implemented** | It creates an in-memory pending approval, but no reviewer approval API, role identity, commit workflow, or database transaction. |

**Gate 9 verdict: NOT COMPLETE.**

### Gate 10 and Gate 11 — observability and incident response

| Requirement | Status | Evidence / finding |
|---|---|---|
| W3C TraceContext | **Missing** | Custom trace IDs exist, but no `traceparent` implementation. |
| Required span names | **Missing** | Only one custom span named `llm.generate` is recorded. |
| OTel Collector / Prometheus / Tempo / Grafana | **Missing** | OTel dependencies exist, but no exporter, collector, dashboards, or metrics. |
| Incident runbooks | **Missing** | No runbook or alert implementation for the four incident scenarios. |
| Automatic mitigation | **Missing** | No alert-triggered cache, reranker, MCP, or failover behavior. |

**Gate 10/11 verdict: NOT COMPLETE.**

### Gate 12 — 36 stage-level KPIs

**Verdict: NOT IMPLEMENTED AND NOT VERIFIED.**

The current KPI validator:
- defines 36 entries,
- but is run with an empty measured-data dictionary,
- reports all 36 as unmeasured,
- does not execute benchmark suites,
- does not measure the actual KPI definitions,
- and has mismatched surrogate names for several required KPIs.

The `/api/v1/kpis` endpoint falsely hard-codes `passed: 36` and `release_status: READY_FOR_VALIDATION` even though no measurement has occurred.

#### 36-KPI exact status matrix

| KPI | Required threshold | Implementation status |
|---|---|---|
| KPI-01 Pre-Hook p95 | ≤15 ms | Not measured |
| KPI-02 PII Recall | ≥99.8% | Regex exists; no benchmark |
| KPI-03 Injection Block | ≥99.5% | Marker regex exists; no 100/indirect benchmark |
| KPI-04 Triage Accuracy | ≥97% | Heuristic triage; no labeled set |
| KPI-05 Triage p95 | ≤25 ms | Not measured |
| KPI-06 Benign False Refusal | ≤1% | No benign control set |
| KPI-07 BM25 p95 | ≤12 ms | Timing recorded in code but no p95/OTel benchmark |
| KPI-08 Dense+FAISS p95 | ≤25 ms | Not real dense/FAISS retrieval |
| KPI-09 Reranker p95 | ≤45 ms | Heuristic rerank only; no p95 |
| KPI-10 Recall@50 | ≥0.92 | No IR benchmark |
| KPI-11 Precision@4 | ≥0.88 | No RAGAS evaluator |
| KPI-12 MRR@4 | ≥0.85 | Not measured |
| KPI-13 nDCG@4 | ≥0.86 | Not measured |
| KPI-14 Schema First-Pass | ≥96% | Pydantic exists; no KPI telemetry |
| KPI-15 Auto-Repair | ≥90% | SKU/LOT repair exists; no suite/metric |
| KPI-16 Loop Escape | 100% | No real loop chaos suite |
| KPI-17 Mean ReAct Steps | ≤2.2 | No ReAct loop |
| KPI-18 Goal Alignment | ≥0.85 | No embeddings or drift audit |
| KPI-19 HITL Enforcement | 100% | Pending state exists; no approval/commit enforcement |
| KPI-20 Faithfulness | ≥0.92 | No RAGAS/NLI |
| KPI-21 Answer Relevancy | ≥0.90 | No RAGAS |
| KPI-22 Context Entity Recall | ≥0.85 | No RAGAS |
| KPI-23 Abstention Accuracy | ≥98% | Basic heuristic only |
| KPI-24 Unsupported Claim/Hallucination | ≤0.5% | No claim verifier |
| KPI-25 TTFT p95 | ≤180 ms | No streaming/TTFT metric |
| KPI-26 Prompt Token Reduction | ≥45% | No Graphify/Obsidian/token counter |
| KPI-27 Cache Hit Ratio | ≥35% | No Redis hit/miss metric |
| KPI-28 Cross-Tenant Isolation | 100%/0 leaks | Key includes tenant/user; no concurrency probe |
| KPI-29 Cost/1000 | ≤$0.45 | No real model/token cost measurement |
| KPI-30 MCP Serialization p95 | ≤4 ms | No MCP timer |
| KPI-31 E2E p50 @50K | ≤240 ms | No 50K load data |
| KPI-32 E2E p95 @50K | ≤450 ms | No 50K load data |
| KPI-33 E2E p99 @50K | ≤590 ms | No 50K load data |
| KPI-34 5xx @50K | ≤0.05% | No load data |
| KPI-35 Throughput | ≥8500 RPS | No load data |
| KPI-36 RSS Growth 1-Hr | ≤3% | No soak data |

### Gate 13 — governance and security-in-build

| Requirement | Status | Evidence / finding |
|---|---|---|
| SHA-256 hash-chained audit | **Partially implemented** | `append_audit()` chains `previous_hash:event`, but storage is process memory and events can be lost/reset. |
| Immutable audit | **Missing** | No append-only database or signatures. |
| Tenant isolation in every query | **Partial** | Tenant exists in API/cache/fact keys, but no database-backed query layer or edge header/body enforcement. |
| Zero raw PII persistence | **Missing** | Although PII redaction happens in one flow, original requests and arbitrary state are not controlled by a storage policy; no persistence implementation proves this. |
| Signed MCP manifests | **Missing** | No signing or startup verification. |

**Gate 13 verdict: NOT COMPLETE.**

### Gate 14 — 100-prompt red-team suite

| Requirement | Status | Evidence / finding |
|---|---|---|
| Direct jailbreak suite | **Missing** | No benchmark runner. |
| Indirect injection in retrieved documents | **Missing** | Corpus contains no adversarial injection cases. |
| Multi-turn crescendo | **Missing** | No conversation-state attack suite. |
| Homoglyph / obfuscated PII | **Missing** | Regex catches basic `[at]` / `[dot]`, but Unicode homoglyphs and broader PII are not tested. |
| Argument overflow / SQLi fuzzing | **Missing** | No fuzz suite or SQL tool. |

**Gate 14 verdict: NOT COMPLETE.**

### Gate 15 and Gate 16 — scalability and 50K load testing

| Requirement | Status | Evidence / finding |
|---|---|---|
| Horizontal stateless workers | **Missing** | Uvicorn can run, but global in-process agent state is not stateless. |
| NGINX/Envoy | **Missing** | No deployment configuration. |
| Redis Cluster | **Missing** | Python dictionary cache only. |
| ONNX model workers | **Missing** | No ONNX Runtime or dynamic micro-batching. |
| vLLM / TensorRT | **Missing** | No LLM runtime or streaming generation. |
| k6 50K script | **Missing** | No `load_tests/k6_50k_load.js`. |
| JMeter distributed plan | **Missing** | No JMX or 10-worker topology. |
| 50K evidence | **Missing** | No k6/JMeter reports or dashboards. |

**Gate 15/16 verdict: NOT COMPLETE.**

### Gate 17 — Obsidian and Graphify token optimization

| Requirement | Status | Evidence / finding |
|---|---|---|
| Atomic Obsidian vault | **Missing** | `knowledge_vault/` and YAML-frontmatter wikilink notes do not exist. |
| Structural graph build | **Missing** | No `graph.json` or graph build workflow. |
| 1–2 hop runtime pruning | **Missing** | Graphify endpoint does not traverse graph or reduce tokens. |
| ≥45% prompt reduction | **Not measured** | No token counter or baseline comparison. |

**Gate 17 verdict: NOT COMPLETE.**

### Gate 18 — six-tab Streamlit workbench

| Requirement | Status | Evidence / finding |
|---|---|---|
| Six tabs | **Partially implemented** | The UI declares exactly six tabs. |
| Architecture and workflow | **Partially implemented** | Workflow image is rendered. ReAct trace, live routing inspector, and approve/reject controls are incomplete. |
| Hybrid RAG lab | **Missing** | No BM25/dense/RRF/reranker side-by-side lab or sliders. |
| MCP/plugin inspector | **Partially implemented** | Raw MCP config is shown, but no live status or JSON-RPC inspector/toggles. |
| Memory/Graphify tokens | **Missing** | No graph visualizer, token gauge, or Redis/SQLite browser. |
| Red-team/circuit breaker | **Missing** | No red-team runner or trip/reset controls. |
| 36-KPI/load scorecard | **Misleading** | It hard-codes success values and has no measured OTel/RAGAS/k6/JMeter data. |

**Gate 18 verdict: PARTIAL DEMO ONLY.**

---

## 3. SLM guide requirement audit

The SLM guide is an implementation reference, not a full set of separate mandatory gates. The repository does not:

- include the catalog/model-selection matrix;
- implement a triage SLM;
- use QLoRA/Unsloth/TRL;
- evaluate the guide's SLM-specific hyperparameters;
- implement TTFT ≤45 ms for an SLM deployment;
- implement ≥99% schema compliance or ≥92% task F1.

The original blueprint explicitly says no model fine-tuning pipeline, so SLM fine-tuning is not a hard pre-build gate. It is a future implementation option or roadmap item. Any SLM triage model would still be required by Gate 6, but the current keyword triage is not compliant.

---

## 4. Functional requirement audit

| FR | Requirement | Status |
|---|---|---|
| FR-01 | Header/body tenant consistency | Missing |
| FR-02 | PII and injection before model | Partially implemented |
| FR-03 | Tenant-scoped semantic cache hit | Partially implemented |
| FR-04 | Four-route triage | Implemented by keyword heuristic |
| FR-05 | Hybrid retrieval + ≤4 citations | Partially implemented; real dense/reranker missing |
| FR-06 | Cross-encoder abstention | Partial heuristic; threshold present |
| FR-07 | Validation, repair, RBAC, idempotency | Partial |
| FR-08 | Bounded loop and circuit breaker | Missing |
| FR-09 | Tier-3 pending approval | Partial |
| FR-10 | Independent NLI verification | Missing |
| FR-11 | Hash-chained audit and OTel | Partial audit; OTel missing |
| FR-12 | KPI and red-team/load suites | Missing |

---

## 5. Risk summary

### Critical risks

1. **Misrepresentation risk:** The UI and `/kpis` endpoint claim a 36-KPI pass and release readiness when no KPI was measured. This is not acceptable for an enterprise release gate.
2. **Tenant security risk:** Cache isolation is only a process-local hash. There is no Redis/PostgreSQL isolation, header/body tenant enforcement, or cross-tenant concurrency proof.
3. **Mutation risk:** Tier-3 actions only create a pending approval record. There is no approve endpoint, reviewer identity verification, committed state transition, or audit integrity boundary.
4. **Hallucination risk:** Retrieval is heuristic Jaccard/BM25-like logic, not an actual dense or cross-encoder grounded pipeline. No independent NLI or RAGAS veto exists.
5. **Availability risk:** No real MCP timeouts, bulkheads, Redis, retry, or 50K load isolation.
6. **PII risk:** Regex redaction is limited; obfuscated, Unicode, phone variants, account identifiers, and persistence policies are not fully covered.
7. **Audit risk:** The hash-chain is process-local and can disappear on restart. It is not append-only, immutable, or signed.

### Must-fix items

- Remove hard-coded 36-KPI pass/release claims.
- Implement real 36-KPI measurement and CI release blocking.
- Replace the in-memory cache/store with Redis/PostgreSQL and enforce tenant IDs across every query.
- Implement real MCP SDK resources/tools and separate MCP processes.
- Implement the actual BGE dense embedding, FAISS, ONNX cross-encoder, RRF, and RAGAS/NLI pipeline.
- Implement the bounded state machine and wire the circuit breaker, idempotency, RBAC, and loop budgets.
- Implement GoalAnchorBlock, observation compression, sliding window, and PostgreSQL session facts.
- Add real approval endpoints and tested Tier-3 mutation commit flow.
- Add W3C TraceContext, OTel export, Prometheus/Tempo/Grafana, and incident runbooks.
- Implement Obsidian vault, Graphify graph construction, and token/cost measurement.
- Create k6/JMeter load suites and 100-prompt red-team suite.

### Should-fix items

- Add `X-Tenant-ID` validation and 403 mismatch handling.
- Add deterministic JSON-RPC error-code mapping and 429/Retry-After behavior.
- Add MCP manifest signing and startup verification.
- Add `k1`, `b`, RRF, threshold, and stage comparison controls to the RAG UI.
- Add live MCP/plugin status and circuit-breaker controls.
- Add approval/reject controls and full audit trace in the UI.
- Replace wildcard CORS with explicit origins.
- Add Docker and Kubernetes deployment definitions.

---

## 6. Suggested test additions

- Pydantic validation and extra-field rejection tests.
- SKU/LOT repair boundary tests.
- PII email, phone, SSN, obfuscated email, homoglyph, Unicode, and phone-format tests.
- Direct and indirect prompt-injection tests.
- Header/body tenant mismatch tests.
- Cross-tenant cache concurrency probe.
- MCP timeout, malformed JSON-RPC, signer, and unavailable-server tests.
- Circuit-breaker failure/half-open/reset tests.
- ReAct state-transition and budget tests.
- HITL approve/reject/expired/unauthorized tests.
- 250-query RAGAS golden set with stratification.
- IR benchmarks for Recall@50, Precision@4, MRR@4, nDCG@4.
- NLI hallucination and abstention tests.
- k6 10K/50K ramp and JMeter distributed tests.
- 1-hour RSS soak test.
- Restart/recovery tests for audit and cache state.

---

## 7. Final verdict

The application is suitable as a **prototype, demonstration, and architectural implementation starting point**. It is not suitable as an enterprise release and cannot currently claim any of the 36-KPI gates or 50,000-VU performance requirements.
