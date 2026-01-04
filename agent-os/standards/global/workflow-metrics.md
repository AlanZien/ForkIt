# Workflow Metrics Standard

**Version**: 1.0 | **Applies to**: All agent-os workflow executions

## Purpose

Track and analyze workflow execution metrics to identify bottlenecks, optimize processes, and measure implementation quality over time.

## Metrics Categories

### 1. Execution Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| `spec_duration` | Total time from spec start to verification | minutes |
| `task_group_durations` | Time per task group | minutes |
| `test_execution_time` | Time to run all tests | seconds |
| `standards_check_time` | Time for verify-standards.sh | seconds |

### 2. Quality Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `tests_passed_rate` | % of tests passing | ≥95% |
| `standards_compliance` | Pass/fail for each check | All pass |
| `regressions_introduced` | New failing tests | 0 |
| `blockers_encountered` | Blocking issues logged | Minimize |

### 3. Complexity Metrics

| Metric | Description |
|--------|-------------|
| `track_used` | 🚀 FAST / ⚙️ STANDARD / 🏗️ COMPLEX |
| `complexity_points` | Total points calculated |
| `task_groups_count` | Number of task groups |
| `files_created` | New files in implementation |
| `files_modified` | Existing files modified |

## Collection Points

Metrics are collected at these workflow stages:

```
┌─────────────────────────────────────────────────────────────┐
│  WORKFLOW STAGE          │  METRICS COLLECTED              │
├─────────────────────────────────────────────────────────────┤
│  1. Spec Shaping         │  complexity_points, track_used  │
│  2. Task Creation        │  task_groups_count              │
│  3. Implementation       │  task_group_durations           │
│  4. Testing              │  tests_*, test_execution_time   │
│  5. Verification         │  standards_*, spec_duration     │
└─────────────────────────────────────────────────────────────┘
```

## Metrics Report Format

The implementation-verifier includes a metrics section in the final verification report:

```markdown
## 7. Workflow Metrics

### Execution Summary
| Metric | Value |
|--------|-------|
| Track | ⚙️ STANDARD |
| Complexity Points | 15 |
| Total Duration | 45 min |
| Task Groups | 4 |

### Task Group Breakdown
| Task Group | Duration | Tests |
|------------|----------|-------|
| 1. Backend API | 12 min | 8 |
| 2. Frontend Store | 10 min | 12 |
| 3. UI Components | 15 min | 6 |
| 4. Integration | 8 min | 4 |

### Quality Summary
| Check | Status | Details |
|-------|--------|---------|
| Tests | ✅ 30/30 | 100% passing |
| Linting | ✅ | No issues |
| Types | ✅ | No errors |
| Security | ✅ | No secrets |
| API Sync | ✅ | Types aligned |

### Comparison to Estimates
| Metric | Estimated | Actual | Delta |
|--------|-----------|--------|-------|
| Duration | 50 min | 45 min | -10% |
| Tests | 25 | 30 | +5 |
```

## Metrics Log File

All spec metrics are appended to `agent-os/metrics/workflow-log.json`:

```json
{
  "specs": [
    {
      "spec_id": "2026-01-04-onboarding-flow",
      "date": "2026-01-04",
      "track": "STANDARD",
      "complexity_points": 15,
      "duration_minutes": 45,
      "task_groups": 5,
      "tests": {
        "total": 30,
        "passed": 30,
        "failed": 0
      },
      "standards": {
        "linting": "pass",
        "types": "pass",
        "security": "pass",
        "api_sync": "pass"
      },
      "files": {
        "created": 14,
        "modified": 4
      }
    }
  ]
}
```

## Using Metrics

### View Historical Metrics

```bash
# Pretty print workflow log
python scripts/workflow-metrics.py --view

# Export to CSV
python scripts/workflow-metrics.py --export metrics.csv

# Calculate averages by track
python scripts/workflow-metrics.py --summary
```

### Analyze Trends

The metrics log enables:
- **Velocity tracking**: Average duration per complexity point
- **Quality trends**: Test pass rate over time
- **Estimation accuracy**: Predicted vs actual duration
- **Bottleneck detection**: Which phases take longest

## Integration

### For Implementation-Verifier

Add metrics section to final verification report:

1. Read `planning/track.md` for complexity data
2. Count task groups from `tasks.md`
3. Extract test results from test run output
4. Record standards check results
5. Write metrics section to report
6. Append to `agent-os/metrics/workflow-log.json`

### For Implementer

Track task group start/end times in implementation reports:

```markdown
## Implementation: Task Group 1

**Started:** 2026-01-04 10:00
**Completed:** 2026-01-04 10:12
**Duration:** 12 minutes
**Tests Written:** 8
```

---

**Token Count**: ~500 tokens | **Critical for**: Workflow optimization and continuous improvement
