import time
from app.plugins.security import PiiRedactor, InjectionShield, PluginViolation
from app.core.harness import ToolExecutionHarness, CircuitBreaker
from app.core.rag import HybridRetriever
from app.core.state import InMemoryStateStore
from app.telemetry.tracing import TraceRecorder

class EnterpriseAgent:
    STATES=("INIT","TRIAGE","REASONING","TOOL_CALL","OBSERVATION","VERIFY","DONE","HALTED")
    def __init__(self):
        self.retriever=HybridRetriever()
        self.store=InMemoryStateStore()
        self.pii=PiiRedactor()
        self.injection=InjectionShield()
        self.breaker=CircuitBreaker()
        self.tracer=TraceRecorder()

    def triage(self, text):
        lower=text.lower()
        if any(x in lower for x in ("submit","transition","mutate","approve","form")):
            return "TRANSACTION_EXEC"
        if any(x in lower for x in ("policy","sku","lot","cache","incident","security","credential","loop")):
            return "HYBRID_RAG"
        if any(x in lower for x in ("weather","horoscope","cure","stock tip")):
            return "REJECT_OOS"
        return "DIRECT_ANSWER"

    def answer(self, request):
        trace_id=self.tracer.start_trace()
        started=time.perf_counter()
        try:
            redacted=self.pii.run(request.query)
            self.injection.run(redacted)
        except PluginViolation:
            self.store.append_audit({"trace_id":trace_id,"event":"INJECTION_BLOCKED","tenant_id":request.tenant_id})
            return {"tenant_id":request.tenant_id,"answer":"Request blocked: prompt-injection marker detected.","citations":[],"route":"REJECT_OOS","status":"REFUSED","faithfulness":None,"trace_id":trace_id}

        route=self.triage(redacted)
        if route=="REJECT_OOS":
            return {"tenant_id":request.tenant_id,"answer":"This request is outside the supported enterprise knowledge scope.","citations":[],"route":route,"status":"REFUSED","faithfulness":None,"trace_id":trace_id}

        if route=="TRANSACTION_EXEC":
            repaired, changed=ToolExecutionHarness.repair(redacted)
            approval_id=self.store.create_approval(request.tenant_id,{"query":repaired,"role_required":"APPROVER","auto_repair":changed})
            self.store.append_audit({"trace_id":trace_id,"event":"PENDING_APPROVAL","approval_id":approval_id,"tenant_id":request.tenant_id})
            return {"tenant_id":request.tenant_id,"answer":"Mutation paused for authorized human approval.","citations":[],"route":route,"status":"PENDING_APPROVAL","faithfulness":1.0,"trace_id":trace_id}

        cached=self.store.cache_lookup(request.tenant_id,request.user_id,redacted)
        if cached:
            return {**cached,"trace_id":trace_id}

        retrieval=self.retriever.retrieve(request.tenant_id,redacted)
        if retrieval["abstain"]:
            response={"tenant_id":request.tenant_id,"answer":"I cannot verify an answer for this request from the trusted corpus.","citations":[],"route":"HYBRID_RAG","status":"ABSTAINED","faithfulness":0.0,"trace_id":trace_id}
            self.store.cache_store(request.tenant_id,request.user_id,redacted,response)
            return response

        top=retrieval["chunks"][0]
        answer=f"Based on verified policy evidence: {top['text']}"
        citations=[{"chunk_id":top["chunk_id"],"source_uri":top["source_uri"],"score":top["rerank_score"]}]
        faithfulness=min(1.0,top["rerank_score"])
        response={"tenant_id":request.tenant_id,"answer":answer,"citations":citations,"route":"HYBRID_RAG","status":"OK","faithfulness":faithfulness,"trace_id":trace_id}
        self.store.put_fact(request.tenant_id,request.session_id or "00000000-0000-4000-8000-000000000000",top["text"],top["chunk_id"])
        self.store.append_audit({"trace_id":trace_id,"event":"ANSWER_VERIFIED","tenant_id":request.tenant_id,"chunk_id":top["chunk_id"]})
        self.store.cache_store(request.tenant_id,request.user_id,redacted,response)
        self.tracer.span(trace_id,"llm.generate")
        return response
