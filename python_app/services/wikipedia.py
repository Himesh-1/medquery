import requests

BASE_URL = 'https://en.wikipedia.org/w/api.php'
HEADERS = {
    'User-Agent': 'MedQueryBot/1.0 (mailto:test@example.com)'
}

def search_wikipedia(query: str):
    try:
        # 1. Search for title
        params_search = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'format': 'json',
            'srlimit': 1
        }
        res = requests.get(BASE_URL, params=params_search, headers=HEADERS)
        data = res.json()
        
        if not data.get('query', {}).get('search'):
            return []
            
        page_title = data['query']['search'][0]['title']
        
        # 2. Get content
        params_content = {
            'action': 'query',
            'prop': 'extracts|info',
            'exintro': True,
            'explaintext': True,
            'inprop': 'url',
            'titles': page_title,
            'format': 'json'
        }
        res_content = requests.get(BASE_URL, params=params_content, headers=HEADERS)
        pages = res_content.json().get('query', {}).get('pages', {})
        
        results = []
        for page_id, page_data in pages.items():
            if page_id == "-1":
                continue
            
            results.append({
                "title": page_data.get('title'),
                "snippet": page_data.get('extract', '')[:500] + "...",
                "source": "Wikipedia",
                "year": "N/A",
                "url": page_data.get('fullurl'),
                "tier": "Tier 4: Open Knowledge"
            })
            
        return results

    except Exception as e:
        print(f"Wikipedia Error: {e}")
        return []
