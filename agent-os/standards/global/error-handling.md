# Error & Blocking Management

## Overview

This document defines how agents should handle errors, blocking situations, and escalation to ensure visibility and proper tracking.

## Error Categories

| Category | Description | Action |
|----------|-------------|--------|
| **Recoverable** | Temporary issues (network, timeout) | Retry up to 3 times, then escalate |
| **Fixable** | Code/config errors agent can fix | Attempt fix, verify, continue |
| **Blocking** | Cannot proceed without help | Log bug + alert user |
| **Critical** | Security/data integrity at risk | Stop immediately + alert user |

## Blocking Detection

An agent is **blocked** when ANY of these conditions are met:

1. **Time threshold exceeded**: Spent >30 minutes on single issue without progress
2. **Retry exhausted**: Same error after 3 fix attempts
3. **Missing dependency**: Required file/service/credential unavailable
4. **Ambiguous requirements**: Spec contradicts itself or is unclear
5. **Permission denied**: Cannot access required resource
6. **External service down**: Third-party API/service unavailable

## Escalation Protocol

### Step 1: Detect Blocking Condition

```
IF (time_on_issue > 30 minutes) OR
   (fix_attempts >= 3) OR
   (missing_critical_dependency) OR
   (ambiguous_requirements)
THEN → BLOCKED
```

### Step 2: Log Bug in Notion

Use `mcp__plugin_Notion_notion__notion-create-pages` to create entry in 🐛 Bugs database.

**Database ID:** `collection://9bc9eef1-dad7-4839-a7fd-689f1eff91ad`

**Required Properties:**

| Property | Value |
|----------|-------|
| `Name` | `[BLOCKED] {brief description}` |
| `Severity` | Based on impact (see below) |
| `Status` | "New" |
| `Blocking Agent` | Agent name (implementer, spec-shaper, etc.) |
| `Spec` | Link to current spec folder |
| `Error Message` | Full error output |
| `Context` | What was being attempted |
| `Attempts Made` | List of fix attempts |
| `date:Reported Date:start` | Today's date |

**Severity Mapping:**

| Situation | Severity |
|-----------|----------|
| Cannot complete critical task | "Critical" |
| Feature partially blocked | "High" |
| Non-critical path blocked | "Medium" |
| Nice-to-have blocked | "Low" |

### Step 3: Alert User

After logging bug, output a clear alert:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 BLOCKED - Need Human Input
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: {brief description}
Spec: {spec-path}
Time spent: {X} minutes
Attempts: {N}

What I tried:
1. {attempt 1}
2. {attempt 2}
3. {attempt 3}

Error:
{error message}

Bug logged in Notion: ✅

Options:
1. Provide guidance to continue
2. Skip this task for now
3. Modify requirements

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 4: Wait for User Response

**DO NOT** continue with other tasks until user responds with one of:
- Guidance to resolve the issue
- Permission to skip
- Modified requirements

## Example MCP Call

```json
{
  "parent": {"type": "data_source_id", "data_source_id": "9bc9eef1-dad7-4839-a7fd-689f1eff91ad"},
  "pages": [{
    "properties": {
      "Name": "[BLOCKED] Cannot connect to Supabase - missing credentials",
      "Severity": "Critical",
      "Status": "New",
      "Error Message": "SUPABASE_URL environment variable not set",
      "Context": "Implementing user authentication for onboarding-flow spec",
      "Steps to Reproduce": "1. Tried reading .env file - not found\n2. Checked .env.example - exists but no .env\n3. Asked user in previous message - no response",
      "date:Reported Date:start": "2026-01-04",
      "date:Reported Date:is_datetime": 0
    }
  }]
}
```

## Integration Points

This error handling applies to ALL agents:

| Agent | When to Apply |
|-------|---------------|
| `spec-shaper` | Requirements unclear after follow-up questions |
| `spec-writer` | Cannot determine technical approach |
| `task-list-creator` | Dependencies cannot be resolved |
| `implementer` | Code/test failures after 30 min |
| `implementation-verifier` | Cannot run verification steps |

## Metrics to Track

For workflow optimization, track:

1. **Block frequency**: How often each agent gets blocked
2. **Block duration**: Time from blocked → resolved
3. **Block categories**: Most common blocking reasons
4. **Resolution types**: User fix vs skip vs requirement change

These can be queried from Notion 🐛 Bugs database with `Blocking Agent` filter.

## Best Practices

1. **Be specific**: Include exact error messages, not summaries
2. **Show attempts**: Document what was tried before escalating
3. **Provide options**: Give user actionable choices
4. **Don't loop**: If blocked, stop and wait - don't retry indefinitely
5. **Context is key**: Include spec path, task being worked on, and relevant code
