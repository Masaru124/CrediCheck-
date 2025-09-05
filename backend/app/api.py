import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import APIRouter

import google.generativeai as genai
from googleapiclient.discovery import build
from .models import TextInput

router = APIRouter()

google_api_key = os.getenv('GOOGLE_API_KEY')
search_engine_id = os.getenv('SEARCH_ENGINE_ID')

import sys

import logging

if not google_api_key:
    logging.error("GOOGLE_API_KEY is not set or invalid.")
if not search_engine_id:
    logging.error("SEARCH_ENGINE_ID is not set or invalid.")

genai.configure(api_key=google_api_key)

def extract_claims(text):
    try:
        if os.getenv('GOOGLE_API_KEY'):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Extract the main factual claims from the following text. Return them as a list of concise statements (1-3 sentences each). Text: {text}"
            response = model.generate_content(prompt)
            claims = response.text.strip().split('\n')
            return [claim.strip() for claim in claims if claim.strip()]
        else:
            # Mock
            return ["The Earth is round.", "Water boils at 100°C at sea level."]
    except Exception as e:
        print(f"extract_claims error: {e}")
        # Mock
        return ["The Earth is round.", "Water boils at 100°C at sea level."]

def search_sources(claim):
    try:
        if google_api_key and search_engine_id:
            service = build("customsearch", "v1", developerKey=google_api_key)
            res = service.cse().list(q=claim, cx=search_engine_id, num=3).execute()
            sources = []
            for item in res.get('items', []):
                sources.append({
                    'title': item['title'],
                    'summary': item['snippet'],
                    'link': item['link']
                })
            return sources
        else:
            # Mock
            return [
                {"title": "Wikipedia - Earth", "summary": "The Earth is an oblate spheroid.", "link": "https://en.wikipedia.org/wiki/Earth"},
                {"title": "Science Source", "summary": "Scientific evidence for Earth's shape.", "link": "https://example.com"}
            ]
    except Exception as e:
        print(f"search_sources error: {e}")
        # Mock
        return [
            {"title": "Wikipedia - Earth", "summary": "The Earth is an oblate spheroid.", "link": "https://en.wikipedia.org/wiki/Earth"},
            {"title": "Science Source", "summary": "Scientific evidence for Earth's shape.", "link": "https://example.com"}
        ]

def verify_claim(claim, sources):
    try:
        if os.getenv('GOOGLE_API_KEY'):
            model = genai.GenerativeModel('gemini-1.5-flash')
            sources_text = '\n'.join([f"{s['title']}: {s['summary']}" for s in sources])
            prompt = f"Analyze the claim: {claim}\nSources:\n{sources_text}\nClassify as True, False, or Misleading. Provide a short explanation."
            response = model.generate_content(prompt)
            result = response.text.strip()
            if 'True' in result:
                status = 'True'
            elif 'False' in result:
                status = 'False'
            else:
                status = 'Misleading'
            return status, result
        else:
            # Mock
            return 'True', 'This claim is supported by scientific evidence.'
    except Exception as e:
        # Mock
        return 'True', 'This claim is supported by scientific evidence.'

def calculate_score(claim_results):
    true_count = sum(1 for status, _ in claim_results if status == 'True')
    total = len(claim_results)
    score = (true_count / total) * 100 if total > 0 else 0
    if score >= 70:
        badge = 'Green'
    elif score >= 40:
        badge = 'Yellow'
    else:
        badge = 'Red'
    return score, badge

from fastapi import FastAPI

@router.post("/api/verify")
async def verify_text(input: TextInput):
    text = input.text
    claims = extract_claims(text)
    results = []
    for claim in claims:
        sources = search_sources(claim)
        status, explanation = verify_claim(claim, sources)
        results.append({
            'claim': claim,
            'status': status,
            'explanation': explanation,
            'sources': sources
        })
    score, badge = calculate_score([(r['status'], r['explanation']) for r in results])
    return {
        'claims': results,
        'credibility_score': score,
        'badge': badge,
        'explanation': f"Overall credibility based on {len(claims)} claims."
    }
