from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.core.models import AgentQueryRequest
from app.core.agent import EnterpriseAgent

app=FastAPI(title="Aegis Grounded Agent — Enterprise Operations API",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
agent=EnterpriseAgent()

@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422,content={"detail":exc.errors(),"error_code":"INVALID_PARAMS"})

@app.get("/health")
def health():
    return {"status":"healthy","mode":"enterprise","gate1":"locked"}

@app.post("/api/v1/agent/query")
def query(payload: AgentQueryRequest):
    return agent.answer(payload)

@app.get("/api/v1/trace/{trace_id}")
def trace(trace_id: str):
    spans=[s for s in agent.tracer.spans if s["trace_id"]==trace_id]
    audit=[e for e in agent.store.audit if e.get("trace_id")==trace_id]
    return {"trace_id":trace_id,"spans":spans,"audit":audit}

@app.get("/api/v1/approvals")
def approvals():
    return agent.store.approvals

@app.get("/api/v1/kpis")
def kpis():
    return {"mode":"validation","passed":0,"total":36,"release_status":"NOT_MEASURED"}
