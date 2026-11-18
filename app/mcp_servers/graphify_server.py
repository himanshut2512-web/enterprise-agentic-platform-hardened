from fastapi import FastAPI

app=FastAPI(title="mcp-graphify-vault")

@app.post("/mcp")
def json_rpc(payload: dict):
    method=payload.get("method")
    params=payload.get("params",{})
    request_id=payload.get("id")
    if method=="resolve_anchor":
        result={"node_id":"policy-anchor","query":params.get("query","")}
    elif method=="expand_subgraph":
        result={"nodes":[params.get("node_id")],"edges":[],"token_budget":params.get("token_budget",320)}
    else:
        return {"jsonrpc":"2.0","id":request_id,"error":{"code":-32601,"message":"Method not found"}}
    return {"jsonrpc":"2.0","id":request_id,"result":result}
