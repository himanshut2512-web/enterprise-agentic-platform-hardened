from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

TenantId = Annotated[str, StringConstraints(pattern=r"^tenant_[A-Za-z0-9_-]{1,64}$")]
UserId = Annotated[str, StringConstraints(pattern=r"^user_[A-Za-z0-9_-]{1,64}$")]
SessionId = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")]
ChunkId = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{16,64}$")]
RiskTier = Literal["TIER_1_READ", "TIER_2_COMPUTE", "TIER_3_MUTATE"]

class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

class AgentQueryRequest(StrictModel):
    tenant_id: TenantId
    user_id: UserId
    session_id: SessionId | None = None
    query: Annotated[str, StringConstraints(min_length=1, max_length=4000)]

class Citation(StrictModel):
    chunk_id: ChunkId
    source_uri: str
    score: float = Field(ge=0, le=1)

class AgentQueryResponse(StrictModel):
    tenant_id: TenantId
    answer: str
    citations: list[Citation] = []
    route: Literal["DIRECT_ANSWER", "HYBRID_RAG", "TRANSACTION_EXEC", "REJECT_OOS"]
    status: Literal["OK", "ABSTAINED", "PENDING_APPROVAL", "HALTED_BREAKER", "REFUSED"]
    faithfulness: float | None = Field(default=None, ge=0, le=1)
    trace_id: str

class HybridRetrieveIn(StrictModel):
    tenant_id: TenantId
    query: Annotated[str, StringConstraints(min_length=1, max_length=2000)]
    bm25_top_k: int = Field(default=50, ge=1, le=100)
    dense_top_k: int = Field(default=50, ge=1, le=100)
    rrf_k: int = Field(default=60, ge=1, le=200)
    pool: int = Field(default=40, ge=4, le=100)
    rerank_k: int = Field(default=4, ge=1, le=10)
    threshold: float = Field(default=0.42, ge=0, le=1)
    idempotency_key: UUID

class ScoredChunk(StrictModel):
    chunk_id: ChunkId
    text: str
    bm25: float | None = None
    cosine: float | None = None
    rrf_rank: int | None = None
    rerank_score: float = Field(ge=0, le=1)

class HybridRetrieveOut(StrictModel):
    chunks: list[ScoredChunk]
    top_score: float
    abstain: bool
    stage_ms: dict[str, float]
