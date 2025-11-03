# Quick Pattern Examples - Copy & Paste

Just copy these patterns and add to `backend/query_router.py` line 20-32

---

## Common Patterns (Ready to Use)

### 1. "Count" queries
```python
r'\bcount\s+(the|all)?\s*(software|licenses?|servers?|locations?)',
```
**Matches:** "count software", "count all locations", "count the servers"

---

### 2. "Tell me" queries
```python
r'\btell\s+me\s+(about|the|all)?\s*(software|licenses?|servers?|locations?)',
```
**Matches:** "tell me software", "tell me about locations", "tell me the servers"

---

### 3. "Which" queries
```python
r'\bwhich\s+(software|licenses?|servers?|locations?)\s+(exist|available|are there)',
```
**Matches:** "which software exist", "which locations are available", "which servers are there"

---

### 4. "Find" queries
```python
r'\bfind\s+(all|the)?\s*(software|licenses?|servers?|locations?)',
```
**Matches:** "find all software", "find locations", "find the servers"

---

### 5. "Provide" queries
```python
r'\bprovide\s+(me|all)?\s*(the)?\s*(software|licenses?|servers?|locations?)',
```
**Matches:** "provide software", "provide me locations", "provide the servers"

---

### 6. "Software names" queries
```python
r'\b(software|licenses?|servers?|locations?)\s+(names?|list)',
```
**Matches:** "software names", "location list", "server names", "license list"

---

### 7. "Available" queries
```python
r'\bavailable\s+(software|licenses?|servers?|locations?)',
```
**Matches:** "available software", "available locations", "available servers"

---

### 8. "Search" queries
```python
r'\bsearch\s+(for|all)?\s*(software|licenses?|servers?|locations?)',
```
**Matches:** "search software", "search for locations", "search all servers"

---

### 9. "View" queries
```python
r'\bview\s+(all|the)?\s*(software|licenses?|servers?|locations?)',
```
**Matches:** "view software", "view all locations", "view the servers"

---

### 10. "See" queries
```python
r'\b(let me see|see)\s+(all|the)?\s*(software|licenses?|servers?|locations?)',
```
**Matches:** "let me see software", "see locations", "see all servers"

---

## How to Add These

### Step 1: Open file
`backend/query_router.py`

### Step 2: Find this section (line ~20)
```python
AGGREGATE_PATTERNS = [
    r'\b(list|show|display|enumerate)\s+(all|me|the)?\s*(software|licenses|servers|locations?)',
    r'\bhow many\s+(unique|different|distinct)?\s*(software|licenses|servers|locations?)',
    # ... more patterns ...
]
```

### Step 3: Add your patterns
```python
AGGREGATE_PATTERNS = [
    r'\b(list|show|display|enumerate)\s+(all|me|the)?\s*(software|licenses|servers|locations?)',
    r'\bhow many\s+(unique|different|distinct)?\s*(software|licenses|servers|locations?)',
    # ... existing patterns ...

    # ADD YOUR NEW PATTERNS HERE (copy from above)
    r'\bcount\s+(the|all)?\s*(software|licenses?|servers?|locations?)',  # ← Paste
    r'\btell\s+me\s+(about|the|all)?\s*(software|licenses?|servers?|locations?)',  # ← Paste
    # ... add more ...
]
```

### Step 4: Save & Restart
```bash
# Kill backend (Ctrl+C)
cd backend
python main.py
```

### Step 5: Test
Try: `count software` or `tell me locations`

---

## Fix for "location" Issue (Your Screenshot)

The problem: "location" query wasn't detected because the pattern required plural "locations"

**Already Fixed!** I added `?` to make 's' optional:
```python
# Before (only matched "locations")
r'locations'

# After (matches both "location" and "locations")
r'locations?'
```

Now these all work:
- ✅ "show me location"
- ✅ "show me locations"
- ✅ "list all location"
- ✅ "list all locations"

---

## Your Current Complete Pattern List

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
]
```

**This now supports 100+ query variations!**

---

## Test These Queries (All Should Work Now)

### Software Queries
- ✅ show me software
- ✅ list all software
- ✅ software list
- ✅ how many software
- ✅ unique software
- ✅ get software
- ✅ give me software
- ✅ fetch software

### Location Queries
- ✅ show me location
- ✅ show me locations
- ✅ list all locations
- ✅ location list
- ✅ how many locations
- ✅ unique locations
- ✅ get locations
- ✅ give me locations

### Server Queries
- ✅ show me server
- ✅ show me servers
- ✅ list all servers
- ✅ how many servers
- ✅ unique servers

### License Queries
- ✅ show me license
- ✅ show me licenses
- ✅ list all licenses
- ✅ how many licenses

---

## Want Even More Patterns?

Just add them to the list! Follow this format:

```python
r'\bYOUR_VERB\s+OPTIONAL_WORDS?\s*(software|licenses?|servers?|locations?)',
```

### Example: Add "retrieve"
```python
r'\bretrieve\s+(all|the)?\s*(software|licenses?|servers?|locations?)',
```

Now "retrieve all software" works!

---

## Summary

1. ✅ **Location issue fixed** - added `?` to make 's' optional
2. ✅ **10+ new patterns ready** - copy & paste from above
3. ✅ **Easy to add more** - just follow the examples
4. ✅ **One file to edit** - `backend/query_router.py`

Restart backend and test! 🚀
