# backend/query_router.py

from typing import List, Dict, Tuple
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryRouter:
    """
    Determines query intent and routes to appropriate handling strategy.

    Query Types:
    1. AGGREGATE: Questions asking for complete lists, counts, or summaries across all data
    2. SEMANTIC: Questions about specific items or contexts (use RAG)
    """

    # Patterns that indicate aggregate/list queries
    AGGREGATE_PATTERNS = [
        r'\b(list|show|display|enumerate)\s+(all|me|the)?\s*(software|licenses|servers|locations)',
        r'\bhow many\s+(unique|different|distinct)?\s*(software|licenses|servers)',
        r'\bwhat\s+(software|licenses|servers|locations)\s+(are|do)\s+(available|exist)',
        r'\ball\s+(the\s+)?(software|licenses|servers|locations)',
        r'\btotal\s+(number\s+of\s+)?(software|licenses|servers)',
        r'\bcomplete\s+list',
        r'\bunique\s+(software|licenses|servers)',
    ]

    def __init__(self):
        self.aggregate_regex = re.compile('|'.join(self.AGGREGATE_PATTERNS), re.IGNORECASE)

    def classify_query(self, query: str) -> Tuple[str, str]:
        """
        Classify query type and extract subject.

        Returns:
            Tuple of (query_type, subject) where:
            - query_type: "aggregate" or "semantic"
            - subject: "software", "server", "location", "license", or None
        """
        query_lower = query.lower()

        # Check for aggregate patterns
        if self.aggregate_regex.search(query):
            # Extract subject
            if 'software' in query_lower:
                return ("aggregate", "software")
            elif 'server' in query_lower:
                return ("aggregate", "server")
            elif 'location' in query_lower:
                return ("aggregate", "location")
            elif 'license' in query_lower:
                return ("aggregate", "license")
            else:
                return ("aggregate", None)

        # Default to semantic search
        return ("semantic", None)


def get_aggregate_data(records: List[Dict], subject: str) -> Dict:
    """
    Extract aggregate information from all records.

    Args:
        records: Complete dataset
        subject: Field to aggregate (software, server, location, license)

    Returns:
        Dictionary with aggregated results
    """
    if not records or len(records) == 0:
        logger.warning("No records available for aggregate query")
        return {
            "error": "No data loaded yet",
            "message": "The system is initializing. Please wait a moment and try again."
        }

    if subject == "software":
        unique_items = set(r.get('software') for r in records if r.get('software'))
        return {
            "type": "software_list",
            "count": len(unique_items),
            "items": sorted(list(unique_items))
        }

    elif subject == "server":
        unique_items = set(r.get('server') for r in records if r.get('server'))
        return {
            "type": "server_list",
            "count": len(unique_items),
            "items": sorted(list(unique_items))
        }

    elif subject == "location":
        unique_items = set(r.get('location') for r in records if r.get('location'))
        return {
            "type": "location_list",
            "count": len(unique_items),
            "items": sorted(list(unique_items))
        }

    elif subject == "license":
        unique_items = set(r.get('license') for r in records if r.get('license'))
        return {
            "type": "license_list",
            "count": len(unique_items),
            "items": sorted(list(unique_items))
        }

    else:
        # General statistics
        return {
            "type": "general_stats",
            "total_records": len(records),
            "unique_software": len(set(r.get('software') for r in records if r.get('software'))),
            "unique_servers": len(set(r.get('server') for r in records if r.get('server'))),
            "unique_locations": len(set(r.get('location') for r in records if r.get('location'))),
        }


def format_aggregate_response(aggregate_data: Dict, query: str) -> str:
    """
    Format aggregate data into a natural language response.

    Args:
        aggregate_data: Dictionary with aggregated results
        query: Original user query

    Returns:
        Formatted response string
    """
    if "error" in aggregate_data:
        error_msg = aggregate_data["error"]
        if "message" in aggregate_data:
            return f"{error_msg}\n\n{aggregate_data['message']}"
        return error_msg

    data_type = aggregate_data.get("type")

    if data_type == "software_list":
        items = aggregate_data["items"]
        count = aggregate_data["count"]
        return f"There are {count} unique software products in the license data:\n\n" + \
               "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))

    elif data_type == "server_list":
        items = aggregate_data["items"]
        count = aggregate_data["count"]
        return f"There are {count} unique license servers:\n\n" + \
               "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))

    elif data_type == "location_list":
        items = aggregate_data["items"]
        count = aggregate_data["count"]
        return f"There are {count} unique locations:\n\n" + \
               "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))

    elif data_type == "license_list":
        items = aggregate_data["items"]
        count = aggregate_data["count"]
        # Limit license list to first 20 to avoid overwhelming response
        display_items = items[:20]
        response = f"There are {count} unique licenses in the data"
        if len(items) > 20:
            response += f" (showing first 20):\n\n"
        else:
            response += ":\n\n"
        response += "\n".join(f"{i+1}. {item}" for i, item in enumerate(display_items))
        return response

    elif data_type == "general_stats":
        return (
            f"Database Statistics:\n"
            f"- Total Records: {aggregate_data['total_records']}\n"
            f"- Unique Software: {aggregate_data['unique_software']}\n"
            f"- Unique Servers: {aggregate_data['unique_servers']}\n"
            f"- Unique Locations: {aggregate_data['unique_locations']}"
        )

    return "Unable to format aggregate data."
