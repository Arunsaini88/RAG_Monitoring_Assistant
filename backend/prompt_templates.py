# backend/prompt_templates.py

from typing import List, Dict

def build_context_snippet(records: List[Dict], max_items: int = 6) -> str:
    """
    Build a compact textual context from records.

    Args:
        records: List of record dictionaries
        max_items: Maximum number of records to include

    Returns:
        Formatted string with record information
    """
    if not records:
        return "No relevant records found."

    lines = []
    for r in records[:max_items]:
        # pick important fields
        lines.append(
            f"{r.get('software','')} | {r.get('server','')} | {r.get('location','')} | "
            f"license:{r.get('license','')} | latest:{r.get('latest_license_issued',0)} | "
            f"day_peak:{r.get('license_day_peak',0)} | day_avg:{r.get('license_day_average',0)} | "
            f"work_peak:{r.get('license_work_peak',0)} | work_avg:{r.get('license_work_average',0)}"
        )
    return "\n".join(lines)

def build_conversation_history(history: List[Dict], max_exchanges: int = 3) -> str:
    """
    Build conversation history string from recent exchanges.

    Args:
        history: List of conversation messages with role and content
        max_exchanges: Maximum number of recent exchanges to include

    Returns:
        Formatted conversation history string
    """
    if not history:
        return ""

    # Take only recent exchanges (limit to avoid token overflow)
    recent = history[-(max_exchanges * 2):] if len(history) > max_exchanges * 2 else history

    lines = []
    for msg in recent:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        if role == 'user':
            lines.append(f"User: {content}")
        elif role == 'assistant':
            lines.append(f"Assistant: {content}")

    return "\n".join(lines)

def build_prompt(question: str, context_records: List[Dict], conversation_history: List[Dict] = None) -> str:
    """
    Build the complete prompt for the LLM including context, conversation history, and question.

    Args:
        question: The user's question
        context_records: List of relevant records to use as context
        conversation_history: Previous conversation exchanges for continuity

    Returns:
        Formatted prompt string for the LLM
    """
    context = build_context_snippet(context_records)

    # Build conversation history section (reduced to 2 exchanges for speed)
    history_text = ""
    if conversation_history:
        history_str = build_conversation_history(conversation_history, max_exchanges=2)
        if history_str:
            history_text = f"\nPrevious:\n{history_str}\n"

    # Optimized shorter prompt for faster LLM processing
    prompt = (
        f"License data:\n{context}"
        f"{history_text}\n"
        f"Q: {question}\n"
        f"A (2-3 sentences):"
    )
    return prompt
