import hashlib
import re

SKU_RE = re.compile(r"(?i)^SKU\s*[-]?\s*(\d{2,6})$")
LOT_RE = re.compile(r"(?i)^LOT\s*[-]?\s*(\d{2,5})$")

class CircuitBreaker:
    def __init__(self, max_identical_calls=2):
        self.failures = {}
        self.open = set()
        self.max_identical_calls = max_identical_calls

    def dispatch(self, tool_name: str, args: dict, fn):
        canonical = repr(sorted(args.items()))
        key = (tool_name, hashlib.sha256(canonical.encode()).hexdigest())
        if key in self.open:
            return {"status": "HALTED_BREAKER", "message": "Repeated tool failure; halt and retry after remediation."}
        try:
            result = fn()
            self.failures.pop(key, None)
            return result
        except Exception:
            self.failures[key] = self.failures.get(key, 0) + 1
            if self.failures[key] >= self.max_identical_calls:
                self.open.add(key)
            raise

class ToolExecutionHarness:
    @staticmethod
    def repair(value: str) -> tuple[str, bool]:
        value = value.strip()
        match = SKU_RE.match(value)
        if match:
            return f"SKU-{int(match.group(1)):03d}", value != f"SKU-{int(match.group(1)):03d}"
        match = LOT_RE.match(value)
        if match:
            return f"LOT-{int(match.group(1)):05d}", value != f"LOT-{int(match.group(1)):05d}"
        return value, False

    @staticmethod
    def rbac(role: str, tier: str) -> bool:
        ranks = {"VIEWER": 1, "OPERATOR": 2, "APPROVER": 3, "ADMIN": 3}
        required = {"TIER_1_READ": 1, "TIER_2_COMPUTE": 2, "TIER_3_MUTATE": 3}
        return ranks.get(role, 0) >= required[tier]
