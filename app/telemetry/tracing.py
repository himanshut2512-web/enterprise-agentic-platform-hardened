import time
import uuid
from contextlib import contextmanager

class TraceRecorder:
    def __init__(self):
        self.spans = []

    def start_trace(self):
        return uuid.uuid4().hex

    @contextmanager
    def span(self, trace_id: str, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            self.spans.append({"trace_id": trace_id, "name": name, "duration_ms": round(elapsed, 3)})
