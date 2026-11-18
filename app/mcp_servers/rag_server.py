from fastapi import FastAPI
from app.core.rag import HybridRetriever

app=FastAPI(title="mcp-hybrid-rag")
retriever=HybridRetriever()

@app.post("/mcp")
def json_rpc(payload: dict):
    request_id=payload.get("id")
    params=payload.get("params",{})
    try:
        result=retriever.retrieve(params["tenant_id"],params["query"],params.get("threshold",0.42),params.get("rerank_k",4))
        return {"jsonrpc":"2.0","id":request_id,"result":result}
    except Exception as exc:
        return {"jsonrpc":"2.0","id":request_id,"error":{"code":-32602,"message":str(exc)}}

@app.get("/health")
def health():
    return {"status":"healthy","server":"mcp-hybrid-rag"}
