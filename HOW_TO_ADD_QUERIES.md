# How to Add More Query Patterns

## Quick Start Guide

Want to add support for new questions? Just edit **ONE file**: `backend/query_router.py`

---

## Step-by-Step Instructions

### Step 1: Open the File

Edit: **`backend/query_router.py`**

Find this section (around line 20):

```python
AGGREGATE_PATTERNS = [
    r'\b(list|show|display|enumerate)\s+(all|me|the)?\s*(software|licenses|servers|locations?)',
    r'\bhow many\s+(unique|different|distinct)?\s*(software|licenses|servers|locations?)',
    ...
]
```

### Step 2: Add Your Pattern

Add a new line with your pattern. Let me show you examples:

---

## Examples: How to Add Common Questions

### Example 1: "Count the software"

**Question you want to support:**
```
count the software
count all locations
```

**Add this pattern:**
```python
AGGREGATE_PATTERNS = [
    # ... existing patterns ...
    r'\bcount\s+(the|all)?\s*(software|licenses|servers|locations?)',  # ← Add this
]
```

---

### Example 2: "Tell me the software"

**Question you want to support:**
```
tell me the software
tell me all locations
```

**Add this pattern:**
```python
AGGREGATE_PATTERNS = [
    # ... existing patterns ...
    r'\btell\s+me\s+(the|all)?\s*(software|licenses|servers|locations?)',  # ← Add this
]
```

---

### Example 3: "Which software exist"

**Question you want to support:**
```
which software exist
which locations are available
```

**Add this pattern:**
```python
AGGREGATE_PATTERNS = [
    # ... existing patterns ...
    r'\bwhich\s+(software|licenses|servers|locations?)\s+(exist|available)',  # ← Add this
]
```

---

### Example 4: "Software names"

**Question you want to support:**
```
software names
all location names
```

**Add this pattern:**
```python
AGGREGATE_PATTERNS = [
    # ... existing patterns ...
    r'\b(software|licenses|servers|locations?)\s+names',  # ← Add this
]
```

---

## Pattern Syntax Guide

### Basic Building Blocks

| Syntax | Meaning | Example |
|--------|---------|---------|
| `\b` | Word boundary | `\bshow` matches "show" but not "showing" |
| `\s+` | One or more spaces | `show\s+me` matches "show me" |
| `\s*` | Zero or more spaces | `show\s*me` matches "showme" or "show me" |
| `(word1\|word2)` | Either word1 OR word2 | `(list\|show)` matches "list" or "show" |
| `?` | Optional | `(all)?` matches "all" or nothing |
| `*` | Zero or more | `\w*` matches any word characters |

### Common Patterns

```python
# Match "show", "list", or "display"
r'\b(show|list|display)'

# Match optional "all" or "the"
r'(all|the)?'

# Match "software", "server", "servers", "location", or "locations"
r'(software|licenses?|servers?|locations?)'

# Match "how many" followed by optional "unique"
r'\bhow many\s+(unique)?'
```

---

## Real Examples from Your System

### Current Working Patterns

```python
AGGREGATE_PATTERNS = [
    # Pattern 1: "show me software", "list all servers", etc.
    r'\b(list|show|display|enumerate)\s+(all|me|the)?\s*(software|licenses|servers|locations?)',

    # Pattern 2: "how many software", "how many unique locations", etc.
    r'\bhow many\s+(unique|different|distinct)?\s*(software|licenses|servers|locations?)',

    # Pattern 3: "what software are available", "what locations exist", etc.
    r'\bwhat\s+(software|licenses|servers|locations?)\s+(are|do)\s+(available|exist)',

    # Pattern 4: "all software", "all the locations", etc.
    r'\ball\s+(the\s+)?(software|licenses|servers|locations?)',

    # Pattern 5: "total software", "total number of servers", etc.
    r'\btotal\s+(number\s+of\s+)?(software|licenses|servers|locations?)',

    # Pattern 6: "complete list"
    r'\bcomplete\s+list',

    # Pattern 7: "unique software", "unique locations", etc.
    r'\bunique\s+(software|licenses|servers|locations?)',

    # Pattern 8: "get all software", "get me the locations", etc.
    r'\bget\s+(all|the|me)?\s*(software|licenses|servers|locations?)\s*(list)?',

    # Pattern 9: "give me software", "give all locations", etc.
    r'\bgive\s+(me|all)?\s*(the)?\s*(software|licenses|servers|locations?)',

    # Pattern 10: "fetch all software", "fetch locations", etc.
    r'\bfetch\s+(all|the)?\s*(software|licenses|servers|locations?)',
]
```

---

## Your Use Cases

### Want to support: "location list"

**Add this:**
```python
r'\b(software|licenses?|servers?|locations?)\s+list',
```

**This will match:**
- "software list"
- "location list"
- "server list"
- "license list"

---

### Want to support: "available software"

**Add this:**
```python
r'\bavailable\s+(software|licenses?|servers?|locations?)',
```

**This will match:**
- "available software"
- "available locations"
- "available servers"

---

### Want to support: "find all software"

**Add this:**
```python
r'\bfind\s+(all|the)?\s*(software|licenses?|servers?|locations?)',
```

**This will match:**
- "find all software"
- "find the locations"
- "find software"

---

## Testing Your Patterns

### Method 1: Use Python Console

```bash
cd backend
python
```

```python
import re
from query_router import QueryRouter

router = QueryRouter()

# Test your query
query_type, subject = router.classify_query("location list")
print(f"Type: {query_type}, Subject: {subject}")
# Expected: Type: aggregate, Subject: location
```

### Method 2: Test with Live System

1. Restart backend
2. Try your query: `location list`
3. Check response includes: `"query_type": "aggregate"`

---

## Common Mistakes

### ❌ Mistake 1: Forgetting word boundaries

**Wrong:**
```python
r'(show|list)'
```
This matches "showing" and "listing" too!

**Correct:**
```python
r'\b(show|list)\b'
```
This only matches "show" and "list" as complete words.

---

### ❌ Mistake 2: Not making plurals optional

**Wrong:**
```python
r'locations'
```
This only matches "locations", not "location"!

**Correct:**
```python
r'locations?'
```
The `?` makes the 's' optional, matching both "location" and "locations".

---

### ❌ Mistake 3: Forgetting to escape special characters

**Wrong:**
```python
r'what's'
```
The `'` is a special character in strings!

**Correct:**
```python
r'what\'s'  # or use double quotes: r"what's"
```

---

## Template for Adding New Patterns

Use this template when adding new patterns:

```python
AGGREGATE_PATTERNS = [
    # ... existing patterns ...

    # Your new pattern - describe what it matches
    r'\bYOUR_PATTERN_HERE',  # Matches: "example query 1", "example query 2"
]
```

### Example:

```python
AGGREGATE_PATTERNS = [
    # ... existing patterns ...

    # Support "provide me software"
    r'\bprovide\s+(me|all)?\s*(the)?\s*(software|licenses?|servers?|locations?)',  # Matches: "provide me software", "provide the locations"
]
```

---

## Complete Example: Adding Support for "Where" Questions

**Want to support:**
- "where can I find software"
- "where are the locations"

**Solution:**

```python
AGGREGATE_PATTERNS = [
    r'\b(list|show|display|enumerate)\s+(all|me|the)?\s*(software|licenses|servers|locations?)',
    r'\bhow many\s+(unique|different|distinct)?\s*(software|licenses|servers|locations?)',
    r'\bwhat\s+(software|licenses|servers|locations?)\s+(are|do)\s+(available|exist)',
    r'\ball\s+(the\s+)?(software|licenses|servers|locations?)',
    r'\btotal\s+(number\s+of\s+)?(software|licenses|servers|locations?)',
    r'\bcomplete\s+list',
    r'\bunique\s+(software|licenses|servers|locations?)',
    r'\bget\s+(all|the|me)?\s*(software|licenses|servers|locations?)\s*(list)?',
    r'\bgive\s+(me|all)?\s*(the)?\s*(software|licenses|servers|locations?)',
    r'\bfetch\s+(all|the)?\s*(software|licenses|servers|locations?)',

    # NEW: Support "where" questions
    r'\bwhere\s+(can I find|are)\s+(the)?\s*(software|licenses?|servers?|locations?)',  # ← Add this
]
```

---

## After Adding Patterns

### Step 1: Save the file
Save `backend/query_router.py`

### Step 2: Restart backend
Kill and restart your backend server:
```bash
# Kill current backend (Ctrl+C or kill process)
# Then restart:
cd backend
python main.py
```

### Step 3: Test your new queries
Try your new query patterns and verify they work!

---

## Quick Reference: Subject Detection

After matching a pattern, the system detects the subject:

```python
# From query_router.py (around line 45)
def classify_query(self, query: str) -> Tuple[str, str]:
    query_lower = query.lower()

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
```

**So make sure your patterns include the keywords:**
- `software`
- `server` or `servers`
- `location` or `locations`
- `license` or `licenses`

---

## Troubleshooting

### Problem: My query isn't detected as aggregate

**Solution 1:** Check logs
Look for: `INFO:__main__:Using LLM to format aggregate response for: software`

If you see: `INFO:llm_handler:Sending request to Ollama` instead
→ Your pattern didn't match!

**Solution 2:** Test pattern in Python
```python
import re
pattern = r'\byour pattern here'
query = "your test query"
match = re.search(pattern, query, re.IGNORECASE)
print(match)  # Should not be None if it matches
```

---

## Summary

1. **Edit one file:** `backend/query_router.py`
2. **Find the list:** `AGGREGATE_PATTERNS = [...]`
3. **Add your pattern:** `r'\byour_pattern_here',`
4. **Save and restart** backend
5. **Test** your new queries!

That's it! No need to modify any other files. 🎉

---

## Need Help?

### Pattern Builder Tool

Use this simple Python script to test patterns:

```python
# test_pattern.py
import re

def test_pattern(pattern, test_queries):
    regex = re.compile(pattern, re.IGNORECASE)
    print(f"Testing pattern: {pattern}\n")
    for query in test_queries:
        match = regex.search(query)
        result = "✅ MATCH" if match else "❌ NO MATCH"
        print(f"{result}: '{query}'")
    print()

# Example usage
pattern = r'\b(show|list)\s+(all|me)?\s*(software|locations?)'
test_queries = [
    "show me software",
    "list all locations",
    "show location",
    "display software",  # Won't match - no "display" in pattern
]

test_pattern(pattern, test_queries)
```

Run it:
```bash
python test_pattern.py
```

This helps you verify patterns before adding them!
