# Spec Shaping Process

You are helping me shape and plan the scope for a new feature.  The following process is aimed at documenting our key decisions regarding scope, design and architecture approach.  We will use our findings from this process later when we write the formal spec document (but we are NOT writing the formal spec yet).

This process will follow 3 main phases, each with their own workflow steps:

Process overview (details to follow)

PHASE 1. Initilize spec
PHASE 2. Research requirements for this spec
PHASE 3. Inform the user that the spec has been initialized

Follow each of these phases and their individual workflows IN SEQUENCE:

## Multi-Phase Process:

### PHASE 1: Initialize Spec

Use the **spec-shaper** subagent to initialize a new spec.

IF the user has provided a description, provide that to the spec-initializer.

The spec-initializer will provide the path to the dated spec folder (YYYY-MM-DD-spec-name) they've created.

### PHASE 2: Research Requirements

After spec-initializer completes, immediately use the **spec-shaper** subagent:

Provide the spec-shaper with:
- The spec folder path from spec-initializer

The spec-shaper will give you several separate responses that you MUST show to the user. These include:
1. Numbered clarifying questions along with a request for visual assets (show these to user, wait for user's response)
2. Follow-up questions if needed (based on user's answers and provided visuals)

**IMPORTANT**:
- Display these questions to the user and wait for their response
- The spec-shaper may ask you to relay follow-up questions that you must present to user

### PHASE 3: Present Complexity Analysis and Track Selection

The spec-shaper will return a complexity analysis with a recommended track. Present this to the user:

```
Spec shaping is complete!

✅ Spec folder created: `[spec-path]`
✅ Requirements gathered
✅ Visual assets: [Found X files / No files provided]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 COMPLEXITY ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Display the complexity score and breakdown from spec-shaper]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 RECOMMENDED TRACK: [TRACK NAME]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Display the recommended workflow steps]

Do you accept this track? (yes/override with: fast, standard, complex)
```

Wait for user response.

### PHASE 4: Confirm Track and Show Next Steps

Based on user's response:

**If user accepts (yes, ok, enter, or no response):**
Use the recommended track.

**If user overrides (fast, standard, or complex):**
Use the specified track instead.

Save the selected track to `[spec-path]/planning/track.md`:

```markdown
# Workflow Track

**Selected Track:** [🚀 FAST / ⚙️ STANDARD / 🏗️ COMPLEX]
**Selection Method:** [Recommended / User Override]
**Complexity Score:** [X] points

## Workflow Steps

1. [Step 1]
2. [Step 2]
3. [...]
```

Then inform the user with track-specific next steps:

**For 🚀 FAST track:**
```
Track confirmed: 🚀 FAST

NEXT STEPS:
1. /write-spec → Generate specification
2. /create-tasks → Create task list
3. /implement-tasks → Implement the feature

Run `/write-spec` to continue.
```

**For ⚙️ STANDARD track:**
```
Track confirmed: ⚙️ STANDARD

NEXT STEPS:
1. /write-spec → Generate specification
2. /plan-tests → Create test plan (REQUIRED)
3. /create-tasks → Create task list
4. /implement-tasks → Implement with TDD
5. Implementation verification

Run `/write-spec` to continue.
```

**For 🏗️ COMPLEX track:**
```
Track confirmed: 🏗️ COMPLEX

NEXT STEPS:
1. /verify-spec → Validate specification coherence (REQUIRED)
2. /write-spec → Generate specification
3. /plan-tests → Create comprehensive test plan (REQUIRED)
4. /create-tasks → Create task list
5. /orchestrate-tasks → Parallel implementation
6. Full verification suite

Run `/verify-spec` to continue (or /write-spec if spec already validated).
```
