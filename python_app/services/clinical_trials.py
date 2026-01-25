import requests

BASE_URL = 'https://clinicaltrials.gov/api/v2/studies'

def search_clinical_trials(query: str, max_results: int = 3):
    try:
        params = {
            'query.term': query,
            'filter.overallStatus': 'RECRUITING|COMPLETED',
            'pageSize': max_results
        }
        
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if not data or 'studies' not in data:
            return []
            
        results = []
        for study in data['studies']:
            protocol = study.get('protocolSection', {})
            id_module = protocol.get('identificationModule', {})
            desc_module = protocol.get('descriptionModule', {})
            status_module = protocol.get('statusModule', {})
            
            nct_id = id_module.get('nctId')
            if not nct_id:
                continue
                
            results.append({
                "title": id_module.get('briefTitle', 'No Title'),
                "snippet": desc_module.get('briefSummary', 'No summary available.'),
                "source": "ClinicalTrials.gov",
                "year": status_module.get('startDateStruct', {}).get('date', 'N/A').split('-')[0],
                "url": f"https://clinicaltrials.gov/study/{nct_id}",
                "tier": "Tier 1: Clinical Trials"
            })
            
        return results

    except Exception as e:
        print(f"ClinicalTrials Error: {e}")
        return []
