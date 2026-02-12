# Chat History Index

**Project:** create_object  
**Last Updated:** February 12, 2026

---

## Overview

This directory contains all development conversations for the create_object project. Each conversation is saved as both JSON (machine-readable) and Markdown (human-readable) formats.

---

## Conversations

*No conversations saved yet.*

---

## Adding New Conversations

Use the save_chat.py script:

```bash
python scripts/save_chat.py
```

Follow the prompts to save conversation with topic, tags, and metadata.

---

## File Naming Convention

**Format:** `YYYYMMDD_HHMM_TopicName.{json,md}`

**Example:**
- `20260212_1430_Initial_Setup.json`
- `20260212_1430_Initial_Setup.md`

---

## Common Tags

**Technical:**
- `setup`, `configuration`, `testing`, `debugging`
- `implementation`, `refactoring`, `optimization`
- `bug-fix`, `performance`, `documentation`

**Phases:**
- `planning`, `design`, `development`, `review`

**Components:**
- `ec2-setup`, `tdd-workflow`, `data-analysis`

---

## Search Tips

**By Topic:**
```bash
grep -r "topic_keyword" docs/chat_history/*.md
```

**By Tag:**
```bash
grep -r "\"testing\"" docs/chat_history/*.json
```

**By Date:**
```bash
ls docs/chat_history/202602*.md
```

---

**Note:** Never delete chat history. All conversations are part of project documentation.

