from os import getcwd
from os.path import join

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import joblib

model_filename = "model_pipeline.pkl"
model_path = join(getcwd(), model_filename)

PIPELINE = joblib.load(model_path)

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

class Prompt(BaseModel):
    pipeline: str
    prompt: str

class Completion(BaseModel):
    pipeline: str
    prompt: str
    sparql: str
    rawresults: str
    summary: str

class DummyPipeline:

    def generate_sparql(self, prompt):
        return "this is supposed to be a sparql query"

    def run_sparql(self, query):
        return "this is supposed to be sparql query results"

    def generate_summary(self, prompt, sparql_results):
        return "this is supposed to be a summary"
            
def getPipeline(pipeline):
    return DummyPipeline()

@app.post("/completions/")
async def complete(p: Prompt):

    # choose the pipeline
    pipeline = getPipeline(p.pipeline)
    
    # generate sparql
    sparql = pipeline.generate_sparql(p.prompt)

    # run the sparql query
    rawresults = pipeline.run_sparql(sparql)

    # generate a summary
    summary = pipeline.generate_summary(p.prompt, rawresults)

    completion = Completion(pipeline=p.pipeline,
                            prompt=p.prompt,
                            sparql=sparql,
                            rawresults=rawresults,
                            summary=summary)
                            
    return completion


