from os import getcwd
from os.path import join

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import joblib

# model_filename = "model_pipeline.pkl"
# model_path = join(getcwd(), model_filename)

# PIPELINE = joblib.load(model_path)

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}


# Raises 422 if bad parameter automatically by FastAPI
@app.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}


# /docs endpoint is defined by FastAPI automatically
# /openapi.json returns a json object automatically by FastAPI

class Question(BaseModel):
    pipeline: str
    question: str

class Answer(BaseModel):
    pipeline: str
    question: str
    sparql: str
    rawresults: str
    summary: str

class DummyPipeline:

    def generate_sparql(self, question):
        return "this is supposed to be a sparql query"

    def run_sparql(self, query):
        return "this is supposed to be sparql query results"

    def generate_summary(self, question, sparql_results):
        return "this is supposed to be a summary"
            
def getPipeline(pipeline):
    return DummyPipeline()

@app.post("/ask/")
async def ask(p: Question):

    # choose the pipeline
    pipeline = getPipeline(p.pipeline)
    
    # generate sparql
    sparql = pipeline.generate_sparql(p.question)

    # run the sparql query
    rawresults = pipeline.run_sparql(sparql)

    # generate a summary
    summary = pipeline.generate_summary(p.question, rawresults)

    completion = Answer(pipeline=p.pipeline,
                        question=p.question,
                        sparql=sparql,
                        rawresults=rawresults,
                        summary=summary)
                            
    return completion


