import os
import requests

def search_web(query, num_results=3):
    """
    Executes a Google Custom Search and returns the top snippets.
    Requires GOOGLE_API_KEY and GOOGLE_CX to be set in the environment.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    cx = os.environ.get("GOOGLE_CX")

    if not api_key or not cx:
        return "Search tool error: GOOGLE_API_KEY or GOOGLE_CX environment variables not set."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": num_results
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results_str = ""
        if "items" in data:
            for item in data["items"]:
                results_str += f"Title: {item.get('title')}\n"
                results_str += f"Link: {item.get('link')}\n"
                results_str += f"Snippet: {item.get('snippet')}\n\n"
            return results_str
        else:
            return "No results found for this query."

    except Exception as e:
        return f"Error executing search: {e}"
