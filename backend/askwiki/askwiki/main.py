import logging
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .gpt3_sparql import Gpt3SparqlGenerator
from .wikibase_sparql_runner import WikibaseSparqlRunner
from .t5_summarizer import T5Summarizer
from .langchain_sparql import LangchainSparqlGenerator

log = logging.getLogger("askwiki")
log.setLevel(logging.INFO)

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
    rawresults: dict
    summary: str

class DummyPipeline:

    def generate_sparql(self, question):
        return "this is supposed to be a sparql query"

    def run_sparql(self, query):
        df = pd.DataFrame({"sbj": ["wd:Q351363", "wd:Q331835", "wd:Q11533909"],
                           "sbj_label": ["seamanship", "suction", "Senshoku ginōshi"]})
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
        assertions = self.summarizer.get_wiki_prop(wikiobjects)
        wikibase_input = f"AskWiki NLG: {'&&'.join(assertions)}  </s>"
        summary = self.summarizer.generate_summary(wikibase_input)
        return summary

class LangchainT5Pipeline:
    def __init__(self):
        self.sparql_generator = LangchainSparqlGenerator()
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
        assertions = self.summarizer.get_wiki_prop(wikiobjects)
        wikibase_input = f"AskWiki NLG: {'&&'.join(assertions)}  </s>"
        summary = self.summarizer.generate_summary(wikibase_input)
        return summary

pipeline_cache = {
    'default': {'class': DummyPipeline, 'instance': DummyPipeline()},
    'gpt3_t5': {'class': Gpt3T5Pipeline, 'instance': Gpt3T5Pipeline()},
    'langchain_t5': {'class': LangchainT5Pipeline, 'instance': LangchainT5Pipeline()}
}

def getPipeline(pipeline):
    if pipeline not in pipeline_cache:
        print(f"can't find pipeline {pipeline}, using default")
        pipeline = 'default'
    else:
        print(f'found pipeline {pipeline}')
    pipeline_dict = pipeline_cache[pipeline]
    if pipeline_dict['instance'] is None:
        print(f'instantiating pipeline {pipeline}')
        pipeline_dict['instance'] = pipeline_dict['class']()
    return pipeline_dict['instance']


@app.get("/pipelines/")
async def pipelines():
    pipeline_names = [PipelineName(pipeline_name=n) for n in pipeline_cache]
    return pipeline_names

@app.post("/ask/")
async def ask(p: Question):

    # choose the pipeline
    pipeline = getPipeline(p.pipeline)
    
    # generate sparql
    sparql = pipeline.generate_sparql(p.question)
    log.info(f'sparql {sparql}')

    # run the sparql query
    df_results = pipeline.run_sparql(sparql)
    log.info(f'df_results {df_results}')
    rawresults = {c: list(df_results[c]) for c in df_results.columns}
    log.info(f'rawresults {df_results}')

    # generate a summary
    summary = pipeline.generate_summary(p.question, df_results)
    log.info(f'summary {summary}')

    completion = Answer(pipeline=p.pipeline,
                        question=p.question,
                        sparql=sparql,
                        rawresults=rawresults,
                        summary=summary)
                            
    return completion



