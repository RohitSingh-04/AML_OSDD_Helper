import os
import httpx
from dotenv import load_dotenv
import serpapi
import trafilatura
import pymupdf
import re
import concurrent.futures
import json

load_dotenv()
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def search_urls(query: str, num_results: int = 20) -> list[str]:
    client = serpapi.Client(api_key=SERPAPI_API_KEY)
    results = client.search({
        "engine": "google",
        "q": query,
        "num": num_results
    })
    return [result["link"] for result in results.get("organic_results", []) if result.get("link")]

def youtube_cc(url: str) -> str:
    # return "NA"
    pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    
    match = re.search(pattern, url, re.IGNORECASE)
    
    if match:
        v_id = match.group(1) 

    else:
        raise Exception("video not found")

    client = serpapi.Client(api_key=SERPAPI_API_KEY)
    response = client.search({"engine": "youtube_video_transcript", "v": v_id, "type": "asr"})

    if 'transcript' not in response:
        raise Exception("Error: The key 'transcript' was not found in the provided JSON.")
        
    snippets = []

    for item in response['transcript']:
        snippet = item.get('snippet', '').strip()
        if snippet:
            snippets.append(snippet)
            
    full_text = ' '.join(snippets)

    cleaned_text = ' '.join(full_text.split())
    
    return cleaned_text


def extract_data(url: str) -> str | None:
    try:
        pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
            
        match = re.search(pattern, url, re.IGNORECASE)

        if match:
            return youtube_cc(url)
            
        response = httpx.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            follow_redirects=True,
            timeout=10
        )

        # Skip blocked / bad responses
        if response.status_code >= 400:
            print(f"Skipped [{response.status_code}]: {url}")
            return None

        content_type = response.headers.get("content-type", "").lower()

        if "application/pdf" in content_type:
            try:
                with pymupdf.open(stream=response.content, filetype="pdf") as document:
                    text = "\n".join(page.get_text() for page in document)

                return text.strip() or None

            except Exception as e:
                print(f"Unreadable PDF: {url} -> {e}")
                return None

        if ("text/html" in content_type or "application/xhtml+xml" in content_type):
            text = trafilatura.extract(response.text)

            return text.strip() if text else None

        print(f"Skipped unsupported file: {url}")
        return None

    except Exception as e:
        print(f"Failed: {url} -> {e}")
        return None

def extract_datas(urls: list[str]) -> dict:
    data = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_url = {executor.submit(extract_data, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                temp_data = future.result()
                if temp_data:
                    data[url] = temp_data
            except Exception as exc:
                raise Exception(f"{url} generated an exception: {exc}")
                
    return data

def perform_osdd_searches(entity, address = ""):

    with open("scraping.json") as fh:
        result = json.load(fh)
    return result 

    STRING_SEARCH_TEXT = 'AND (arrest OR corruption OR sentencing OR money laundering OR AML OR launder OR embezzle OR evad OR evad OR Crimes OR corrupt OR bribe OR theft OR extort OR drug OR traffic OR trafficking OR felony OR sanctions OR counterfeit OR terror)'
    if address:
        results = {"entity_search": extract_datas(search_urls(entity)), "address_search": extract_datas(list(set(search_urls(entity + address, 10)) | set(search_urls(address, 10)))), "negative_news_search": extract_datas(search_urls(f'''"{entity}" {STRING_SEARCH_TEXT}'''))}
    else:
        results = {"entity_search": extract_datas(search_urls(entity)), "address_search": extract_datas(list(set(search_urls("address of " + entity, 10)) | set(search_urls(entity + "is located at?", 10)))), "negative_news_search": extract_datas(search_urls(f'''"{entity}" {STRING_SEARCH_TEXT}'''))}

    with open("scraping.json", 'w') as fh:
        json.dump(results, fh)

    return results