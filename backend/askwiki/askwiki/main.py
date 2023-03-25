import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .gpt3_sparql import Gpt3SparqlGenerator
from .wikibase_sparql_runner import WikibaseSparqlRunner
from .t5_summarizer import T5Summarizer

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}


class PipelineName(BaseModel):
    pipeline_name: str

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
        lst = [['http://www.wikidata.org/entity/Q3486420', 'Sky']]
        df = pd.DataFrame(lst, columns=['obj', 'objLabel'])
        return df

    def generate_summary(self, question, df):
        return "this is supposed to be a summary"

class Gpt3T5Pipeline:
    def __init__(self):
        self.sparql_generator = Gpt3SparqlGenerator()
        self.sparql_runner = WikibaseSparqlRunner()
        self.summarizer = T5Summarizer()

    def generate_sparql(self, question):
        sparql = self.sparql_generator.generate_sparql(question)
        return sparql

    def run_sparql(self, query):
        df = self.sparql_runner.run_sparql_to_df(query)
        return df

    def generate_summary(self, question, df):
        # find the objects in the result
        wikiobjects = []
        for index, row in df.iterrows():
            for col in df.columns:
                v = row[col]
                if v.find('http://www.wikidata.org/entity/') >= 0:
                    wikiobjects.append(col_.replace('http://www.wikidata.org/entity/', ''))
        assertions = self.summarizer.get_wiki_prop(['Q6853', 'Q154869', 'Q157661'])
        wikibase_input = f"AskWiki NLG: {'&&'.join(assertions)}  </s>"
        summary = self.summarizer.generate_summary(wikibase_input)
        return summary

PIPELINES = {
    'default': DummyPipeline,
    'gpt3_t5': Gpt3T5Pipeline
}

def getPipeline(pipeline):
    if pipeline in PIPELINES:
        return PIPELINES[pipeline]()
    return DummyPipeline()


@app.get("/pipelines/")
async def pipelines():
    pipeline_names = [PipelineName(pipeline_name=n) for n in PIPELINES]
    return pipeline_names

@app.post("/ask/")
async def ask(p: Question):

    # choose the pipeline
    pipeline = getPipeline(p.pipeline)
    
    # generate sparql
    sparql = pipeline.generate_sparql(p.question)

    # run the sparql query
    df_results = pipeline.run_sparql(sparql)
    rawresults = df_results.to_csv()

    # generate a summary
    summary = pipeline.generate_summary(p.question, df_results)

    completion = Answer(pipeline=p.pipeline,
                        question=p.question,
                        sparql=sparql,
                        rawresults=rawresults,
                        summary=summary)
                            
    return completion



