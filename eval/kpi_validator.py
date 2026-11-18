KPI_TARGETS = {
  "pre_hook_latency_ms": (15, "<="), "pii_recall": (0.998, ">="),
  "injection_block_rate": (0.995, ">="), "triage_accuracy": (0.970, ">="),
  "triage_latency_ms": (25, "<="), "false_refusal_rate": (0.010, "<="),
  "bm25_latency_ms": (12, "<="), "dense_latency_ms": (25, "<="),
  "rerank_latency_ms": (45, "<="), "context_recall_50": (0.92, ">="),
  "context_precision_4": (0.88, ">="), "mrr_4": (0.85, ">="),
  "ndcg_4": (0.86, ">="), "schema_validation_rate": (0.96, ">="),
  "repair_success_rate": (0.90, ">="), "loop_escape_rate": (1.0, ">="),
  "mean_react_steps": (2.2, "<="), "grounded_answer_rate": (0.99, ">="),
  "hitl_compliance": (1.0, ">="), "circuit_breaker_recall": (1.0, ">="),
  "faithfulness": (0.92, ">="), "answer_relevancy": (0.90, ">="),
  "context_precision_ragas": (0.88, ">="), "context_recall_ragas": (0.85, ">="),
  "entity_recall": (0.85, ">="), "token_reduction": (0.45, ">="),
  "pii_block_rate": (0.998, ">="), "tenant_isolation": (1.0, ">="),
  "cache_hit_latency_ms": (5, "<="), "throughput_rps": (8500, ">="),
  "p95_latency_ms": (450, "<="), "p99_latency_ms": (600, "<="),
  "error_rate": (0.0005, "<="), "mcp_timeout_rate": (0.01, "<="),
  "audit_completeness": (1.0, ">="), "kpi_refresh_success": (0.995, ">=")
}

def validate(measured: dict):
    failures=[]
    for name,(target,operator) in KPI_TARGETS.items():
        value=measured.get(name)
        if value is None:
            failures.append({"kpi":name,"reason":"not measured"})
            continue
        passed=value >= target if operator==">=" else value <= target
        if not passed:
            failures.append({"kpi":name,"measured":value,"target":target,"operator":operator})
    return {"total":36,"passed":36-len(failures),"failed":failures,"release":"BLOCKED" if failures else "READY"}

if __name__=="__main__":
    print(validate({}))
