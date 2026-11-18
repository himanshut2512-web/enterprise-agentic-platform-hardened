import json
import math
import re
import time
from pathlib import Path

class HybridRetriever:
    def __init__(self, corpus_path="data/corpus.json"):
        self.docs = json.loads(Path(corpus_path).read_text())

    @staticmethod
    def tokenize(text):
        return re.findall(r"[a-z0-9]+", text.lower())

    def bm25(self, query, top_k=50):
        q = self.tokenize(query)
        docs = [self.tokenize(d["text"]) for d in self.docs]
        avgdl = sum(map(len, docs)) / max(len(docs), 1)
        scores=[]
        for doc, tokens in zip(self.docs, docs):
            score=0.0
            for term in set(q):
                tf=tokens.count(term)
                if not tf: continue
                df=sum(term in d for d in docs)
                idf=math.log(1+(len(docs)-df+0.5)/(df+0.5))
                score += idf * tf*2.5/(tf+1.25*(0.25+0.75*len(tokens)/avgdl))
            scores.append((doc, score))
        return sorted(scores, key=lambda x:x[1], reverse=True)[:top_k]

    def dense(self, query, top_k=50):
        q=set(self.tokenize(query))
        results=[]
        for doc in self.docs:
            d=set(self.tokenize(doc["text"]))
            cosine=len(q & d)/math.sqrt(max(len(q)*len(d),1))
            results.append((doc, cosine))
        return sorted(results, key=lambda x:x[1], reverse=True)[:top_k]

    def retrieve(self, tenant_id, query, threshold=0.42, rerank_k=4):
        t=time.perf_counter()
        bm25=self.bm25(query)
        bm25_ms=(time.perf_counter()-t)*1000
        t=time.perf_counter()
        dense=self.dense(query)
        dense_ms=(time.perf_counter()-t)*1000
        t=time.perf_counter()
        fused={}
        for rank,(doc,score) in enumerate(bm25):
            fused[doc["chunk_id"]]={"doc":doc,"score":0.0,"bm25":score,"cosine":None,"rrf_rank":rank+1}
            fused[doc["chunk_id"]]["score"] += 1/(60+rank+1)
        for rank,(doc,score) in enumerate(dense):
            item=fused.setdefault(doc["chunk_id"],{"doc":doc,"score":0.0,"bm25":None,"cosine":score,"rrf_rank":rank+1})
            item["cosine"]=score
            item["score"] += 1/(60+rank+1)
            if item["rrf_rank"] > rank+1: item["rrf_rank"]=rank+1
        rrf_ms=(time.perf_counter()-t)*1000
        t=time.perf_counter()
        qterms=set(self.tokenize(query))
        chunks=[]
        for item in sorted(fused.values(),key=lambda x:x["score"],reverse=True)[:40]:
            dterms=set(self.tokenize(item["doc"]["text"]))
            overlap=len(qterms & dterms)/max(len(qterms),1)
            rerank=min(1.0, item["score"]*120 + overlap*0.65)
            chunks.append({"chunk_id":item["doc"]["chunk_id"],"text":item["doc"]["text"],"source_uri":item["doc"]["source_uri"],"bm25":item["bm25"],"cosine":item["cosine"],"rrf_rank":item["rrf_rank"],"rerank_score":round(rerank,4)})
        chunks=sorted(chunks,key=lambda x:x["rerank_score"],reverse=True)[:rerank_k]
        rerank_ms=(time.perf_counter()-t)*1000
        top_score=max((c["rerank_score"] for c in chunks),default=0.0)
        return {"chunks":chunks,"top_score":top_score,"abstain":top_score<threshold,"stage_ms":{"bm25":round(bm25_ms,3),"dense":round(dense_ms,3),"rrf":round(rrf_ms,3),"rerank":round(rerank_ms,3)}}
