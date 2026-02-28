
import json
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Job Matching API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = []
candidates = []

vectorizer = TfidfVectorizer()
job_vectors = None
candidate_vectors = None


def load_data():
    global jobs, candidates

    with open("data/jobs.json") as f:
        jobs = json.load(f)

    with open("data/candidates.json") as f:
        candidates = json.load(f)


def compute_vectors():
    global job_vectors, candidate_vectors

    job_texts = [j["title"] + " " + j["description"] for j in jobs]
    candidate_texts = [
        c["summary"] + " " + " ".join(c["skills"])
        for c in candidates
    ]

    corpus = job_texts + candidate_texts
    vectorizer.fit(corpus)

    job_vectors = vectorizer.transform(job_texts)
    candidate_vectors = vectorizer.transform(candidate_texts)


@app.on_event("startup")
def startup_event():
    load_data()
    compute_vectors()


@app.get("/jobs")
def get_jobs():
    return jobs


@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    for job in jobs:
        if job["id"] == job_id:
            return job
    raise HTTPException(status_code=404, detail="Job not found")


@app.get("/candidates")
def get_candidates():
    return candidates


@app.get("/jobs/{job_id}/matches")
def get_matches(job_id: int, top_k: int = Query(5)):
    job = next((j for j in jobs if j["id"] == job_id), None)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_text = job["title"] + " " + job["description"]
    job_vec = vectorizer.transform([job_text])

    similarities = cosine_similarity(job_vec, candidate_vectors)[0]

    scores = []
    for idx, score in enumerate(similarities):
        candidate = candidates[idx]
        scores.append({
            "id": candidate["id"],
            "name": candidate["name"],
            "score": round(float(score), 3)
        })

    scores.sort(key=lambda x: x["score"], reverse=True)

    return scores[:top_k]
