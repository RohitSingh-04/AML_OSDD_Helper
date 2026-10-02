import os
import json
import logging
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from langchain_ollama import ChatOllama
from models import EntitySearchResult, AddressSearchResult, NegativeNewsResult, FinalAssessment, FinalOSDDResult, AnalyzeRequest
from scraper import perform_osdd_searches
import prompts
import summarizer

# Configure the logging setup to save to file and show on console
logger = logging.getLogger("aml_osdd_helper")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs/aml_osdd_logs.log")
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


load_dotenv()

app = FastAPI(title="AML OSDD Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = os.getenv("OLLAMA_MODEL", "dolphin3:latest")

llm = ChatOllama(model=MODEL_NAME, temperature=0)

entity_llm = llm.with_structured_output(EntitySearchResult)
address_llm = llm.with_structured_output(AddressSearchResult)
negative_news_llm = llm.with_structured_output(NegativeNewsResult)
final_llm = llm.with_structured_output(FinalAssessment)


@app.post("/api/analyze", response_model=FinalOSDDResult)
async def analyze_entity(request: AnalyzeRequest):
    entity_name = request.entity_name.strip()
    address = request.address.strip()

    if not entity_name:
        logger.warning("Analyze request rejected: entity_name is missing")
        raise HTTPException(status_code=400, detail="entity_name is required")
    
    logger.info("_" * 70)
    logger.info(f"[OSDD ANALYSIS START] Entity: {entity_name} | Address: {address}")
    logger.info("_" * 70)

    try:
        search_results = perform_osdd_searches(entity_name, address)

        if not search_results:
            logger.warning(f"No sources found for {entity_name}")
            raise HTTPException(status_code=404, detail="No sources found.")

        #split the bucket
        entity_search_bucket = search_results["entity_search"]
        address_search_bucket = search_results["address_search"]
        negative_news_bucket = search_results["negative_news_search"]

        #start summarizing
        logger.info("Summarizing entity sources...")
        entity_summary = await summarizer.summarize_sources(entity_search_bucket, entity_name, llm)

        logger.info("Summarizing address sources...")
        address_search_summary = await summarizer.summarize_sources(address_search_bucket, entity_name, llm)

        logger.info("Summarizing negative news sources...")
        negative_news_summary = await summarizer.summarize_negative_sources(negative_news_bucket, entity_name, llm)

        #start analysis
        logger.info("[LLM 1]: Executing entity analysis")
        entity_prompt = prompts.ENTITY_PROMPT.format(entity=entity_name) + "\n\nSEARCH RESULTS:\n" + json.dumps([summary.model_dump() for summary in entity_summary], ensure_ascii=False)
        entity_result = await entity_llm.ainvoke(entity_prompt)
        entity_result.sources = list(entity_search_bucket.keys())

        logger.debug(f"Entity Results:\n{entity_result.model_dump_json()}")

        logger.info("[LLM 2]: Executing address analysis")
        address_prompt = prompts.ADDRESS_PROMPT.format(entity=entity_name) + "\n\nSEARCH RESULTS:\n" + json.dumps([summary.model_dump() for summary in address_search_summary], ensure_ascii=False)
        address_result = await address_llm.ainvoke(address_prompt)
        address_result.sources = list(address_search_bucket.keys())
        
        logger.debug(f"Address Results:\n{address_result.model_dump_json()}")

        logger.info("[LLM 3]: Executing negative news analysis")
        negative_prompt = prompts.NEGATIVE_NEWS_PROMPT.format(entity=entity_name) + "\n\nSEARCH RESULTS:\n" + json.dumps([summary.model_dump() for summary in negative_news_summary], ensure_ascii=False)
        negative_result = await negative_news_llm.ainvoke(negative_prompt)
        negative_result.sources = list(negative_news_bucket.keys())
        
        logger.debug(f"Negative News Result:\n{negative_result.model_dump_json()}")

        logger.info("[LLM 4]: Executing final assessment")
        final_prompt = prompts.FINAL_OSDD_PROMPT.format(entity=entity_name, entity_report=entity_result.model_dump_json(), address_report=address_result.model_dump_json(), negative_news_report=negative_result.model_dump_json())
        
        assessment_result = await final_llm.ainvoke(final_prompt)
        logger.debug(f"Assessment Results:\n{assessment_result.model_dump_json()}")
        
        final_result = FinalOSDDResult(
            entity=entity_result.entity, 
            entity_type=entity_result.entity_type,  
            industry=entity_result.industry, 
            jurisdiction=entity_result.jurisdiction, 
            addresses=list(dict.fromkeys(entity_result.addresses + address_result.addresses)), 
            description=entity_result.description, 
            sources=list(dict.fromkeys(entity_result.sources + address_result.sources + negative_result.sources)), 
            negative_news=negative_result.negative_news, 
            negative_news_summary=(negative_result.negative_news_summary), 
            negative_news_sources=(negative_result.sources if negative_result.negative_news else []), 
            risk_factors=negative_result.risk_factors, 
            sanctions=negative_result.sanctions, 
            pep_association=negative_result.pep_association, 
            related_entities=list(dict.fromkeys(entity_result.related_entities + address_result.associated_entities + negative_result.related_entities)), 
            risk_score=assessment_result.risk_score, 
            risk_level=assessment_result.risk_level, 
            confidence=assessment_result.confidence, 
            assessment_summary=assessment_result.assessment_summary, 
            limitations=assessment_result.limitations
        )

        logger.info(f"[OSDD ANALYSIS COMPLETE] Successfully analyzed: {entity_name}")
        return final_result

    except HTTPException:
        raise

    except Exception as exc:
        # 2. Capture the exact traceback as a string
        tb_str = traceback.format_exc()
        
        # 3. Log it cleanly via the logger (or send tb_str to a database/monitoring tool)
        logger.error(f"[ANALYSIS ERROR] Failed analyzing {entity_name}. Exception: {exc}\nTraceback:\n{tb_str}")
        
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred during analysis."
        )


@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "AML OSDD Analyzer",
        "model": MODEL_NAME
    }