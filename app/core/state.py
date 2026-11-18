import hashlib
import random
from copy import deepcopy

class InMemoryStateStore:
    def __init__(self):
        self.session_facts = {}
        self.cache = {}
        self.approvals = {}
        self.audit = []
        self.idempotency = {}

    @staticmethod
    def cache_key(tenant_id: str, user_id: str, query: str) -> str:
        normalized = " ".join(query.lower().split())
        return hashlib.sha256(f"{tenant_id}:{user_id}:{normalized}".encode()).hexdigest()

    def cache_lookup(self, tenant_id: str, user_id: str, query: str):
        return deepcopy(self.cache.get(self.cache_key(tenant_id, user_id, query)))

    def cache_store(self, tenant_id: str, user_id: str, query: str, value):
        self.cache[self.cache_key(tenant_id, user_id, query)] = deepcopy(value)

    def put_fact(self, tenant_id: str, session_id: str, fact: str, source_chunk_id: str):
        key = (tenant_id, session_id)
        item = {"fact": fact, "source_chunk_id": source_chunk_id}
        self.session_facts.setdefault(key, []).append(item)
        return len(self.session_facts[key])

    def get_facts(self, tenant_id: str, session_id: str):
        return deepcopy(self.session_facts.get((tenant_id, session_id), []))

    def create_approval(self, tenant_id: str, payload: dict):
        approval_id = hashlib.sha256(str(payload).encode()).hexdigest()[:24]
        self.approvals[approval_id] = {"tenant_id": tenant_id, "status": "PENDING_APPROVAL", "payload": payload}
        return approval_id

    def append_audit(self, event: dict):
        previous = self.audit[-1]["hash"] if self.audit else "0" * 64
        encoded = f"{previous}:{event}".encode()
        item = {**deepcopy(event), "hash": hashlib.sha256(encoded).hexdigest()}
        self.audit.append(item)
        return item["hash"]
