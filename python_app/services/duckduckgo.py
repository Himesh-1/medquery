from duckduckgo_search import DDGS

def search_duckduckgo(query: str, domains: list[str] = None, max_results: int = 5):
    try:
        search_query = query
        if domains:
            # Construct site: filter
            # DDG supports (site:a.com OR site:b.com)
            site_filter = " OR ".join([f"site:{d}" for d in domains])
            search_query = f"{query} ({site_filter})"
            
        results = []
        with DDGS() as ddgs:
            # basic text search
            ddg_gen = ddgs.text(search_query, max_results=max_results)
            for r in ddg_gen:
                results.append({
                    "title": r.get('title'),
                    "snippet": r.get('body'),
                    "source": "Web", # Parse logic could go here
                    "year": "2024", # Placeholder
                    "url": r.get('href'),
                    "tier": "Tier 2/3: Web Discovery"
                })
                
        return results

    except Exception as e:
        print(f"DuckDuckGo Error: {e}")
        return []
