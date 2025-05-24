import requests
import json
import os
import google.generativeai as genai

MCP_SERVER_URL = "http://localhost:9000"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_mcp_info(server_url):
    """Fetches information from the MCP server."""
    try:
        response = requests.get(f"{server_url}/mcp/info")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to MCP server info endpoint: {e}")
        return None

def query_mcp_server(server_url, provider_id, query_id="test-query-123", kind="text/log"):
    """Queries the MCP server for data."""
    payload = {
        "query_id": query_id,
        "provider": provider_id,
        "kind": kind
    }
    try:
        response = requests.post(f"{server_url}/mcp/query", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying MCP server: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from MCP server. Response text: {response.text}")
        return None

def analyze_logs_with_gemini(logs_content, api_key, prompt_text="Summarize the following log data and identify any potential issues or errors mentioned. Provide a brief overview."):
    """Sends log content to Gemini API for analysis."""
    if not api_key:
        print("GEMINI_API_KEY not found. Please set it as an environment variable.")
        print("Skipping Gemini analysis.")
        return "Gemini API key not configured."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        full_prompt = f"{prompt_text}\n\n--- LOG DATA ---\n{logs_content}\n--- END OF LOG DATA ---"

        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Error interacting with Gemini API: {e}")
        if "API_KEY_INVALID" in str(e) or "API_KEY_MISSING" in str(e) :
             return "Gemini API call failed due to an invalid or missing API key. Please check your GEMINI_API_KEY environment variable."
        return f"Gemini API call failed: {e}"

def main():
    print(f"Attempting to connect to MCP server at {MCP_SERVER_URL}...\n")

    mcp_info = get_mcp_info(MCP_SERVER_URL)
    if not mcp_info:
        print("Could not retrieve MCP info. Exiting.")
        return

    print("--- MCP Server Info ---")
    print(json.dumps(mcp_info, indent=2))
    print("-" * 25 + "\n")

    provider_id = mcp_info.get("provider_id")
    capabilities = mcp_info.get("capabilities", [])

    if not provider_id:
        print("Provider ID not found in MCP info. Exiting.")
        return

    if "text/log" not in capabilities:
        print(f"'text/log' capability not found for provider '{provider_id}'. Exiting.")
        return

    print(f"Querying MCP server for '{provider_id}' with kind 'text/log'...\n")
    query_results = query_mcp_server(MCP_SERVER_URL, provider_id, kind="text/log")

    if not query_results:
        print("Failed to retrieve data from MCP server. Exiting.")
        return

    print("--- MCP Query Results ---")
    if isinstance(query_results, list) and len(query_results) > 0:
        log_data = query_results[0]
        print(json.dumps(log_data, indent=2))
        print("-" * 25 + "\n")

        log_content = log_data.get("content")
        log_source = log_data.get("metadata", {}).get("source")

        if log_content:
            print(f"Successfully retrieved logs from {log_source or 'unknown source'}.")
            print(f"Log content preview (first 200 chars):\n{log_content[:200]}...\n")

            print("Sending logs to Gemini API for analysis...\n")
            custom_prompt = input("Enter a custom prompt for Gemini (or press Enter for default summary): ").strip()

            gemini_analysis_prompt = custom_prompt if custom_prompt else "Summarize the following log data and identify any potential critical errors or warnings. Provide a brief overview."

            gemini_response = analyze_logs_with_gemini(log_content, GEMINI_API_KEY, prompt_text=gemini_analysis_prompt)

            print("--- Gemini API Analysis ---")
            print(gemini_response)
            print("-" * 25 + "\n")
        else:
            print("No 'content' found in the MCP query response.")
    else:
        print("MCP query did not return the expected list format or was empty.")
        print(f"Received: {query_results}")


if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("Error: The GEMINI_API_KEY environment variable is not set.")
    main()
