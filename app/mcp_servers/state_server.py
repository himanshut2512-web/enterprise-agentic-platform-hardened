from fastapi import FastAPI
from app.core.state import InMemoryStateStore

app=FastAPI(title="mcp-state-store")
store=InMemoryStateStore()

@app.post("/mcp")
def json_rpc(payload: dict):
    method=payload.get("method")
    params=payload.get("params",{})
    request_id=payload.get("id")
    if method=="get_session_facts":
        result=store.get_facts(params["tenant_id"],params["session_id"])
    elif method=="append_audit":
        result={"event_hash":store.append_audit(params)}
    else:
        return {"jsonrpc":"2.0","id":request_id,"error":{"code":-32601,"message":"Method not found"}}
    return {"jsonrpc":"2.0","id":request_id,"result":result}
