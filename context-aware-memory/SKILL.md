---
name: context-aware-memory
description: Context-Aware Memory Manager for AI Agents. Actively retrieves and pushes relevant memories based on current context (task, conversation, time, location). Implements predictive activation, value-weighted retrieval, and automatic decay. Use when the agent needs to recall relevant information from past interactions or when starting a new task that may benefit from historical context.

# Context-Aware Memory Manager
A smart memory management system that actively retrieves and surfaces relevant memories based on multi-dimensional context anchors.

## Core Concepts

### Context Anchors
- **Temporal**: Time of day, day of week, recency
- **Task-based**: Current task type, task stack depth
- **Conversational**: Topic keywords, mentioned entities, conversation flow
- **Location/Environment**: Working directory, active files, system state

### Memory Lifecycle
1. **Encoding**: Store with context anchors and value weight
2. **Activation**: Predictive trigger based on context similarity
3. **Retrieval**: Value-weighted ranking
4. **Decay**: Automatic depreciation over time
5. **Reinforcement**: Boost weight on successful retrieval

## Usage

### Check Memory Context
```bash

# Get relevant memories for current context
memory-context --task "current task description" --conversation "recent topics"
```

# Store a new memory with context anchors
memory-store --content "important insight" --tags "ai,agent,memory" --value 0.8

# View memory statistics and health
memory-stats

## Configuration
Memory storage location: `~/.agents/memory/`

Config file: `~/.agents/memory/config.json`

```json
{
 "decay_rate": 0.02,
 "max_memories": 10000,
 "activation_threshold": 0.3,
 "value_weight": 0.5,
 "recency_weight": 0.3,
 "context_weight": 0.2
}

## Integration Points

### With Silver Moon's Memory System
- Reads from `memory/YYYY-MM-DD.md` for daily logs
- Reads from `memory/projects/*.md` for project context
- Reads from `memory/modules/*.md` for knowledge base

### Output Format
Returns memories ranked by relevance score:
[Score: 0.85] Memory content here...
[Score: 0.72] Another relevant memory...

## Advanced Features

### Predictive Activation
Anticipates what memories might be needed before explicit request:
- Pattern recognition from past access
- Task type → memory type mapping
- Time-based triggers (daily standup → yesterday's tasks)

### Value Reinforcement
When a retrieved memory is acted upon:
- Weight increases, Decay rate decreases, Context anchors strengthened

### Automatic Cleanup
- Low-value memories decay faster
- Duplicate detection and merging
- Archive old memories with low access

## Example Workflow
1. **Agent starts new task**
 - Memory Manager receives context (task type, time, recent files)
 - Predictive activation triggers
 - Relevant memories surface

2. **Agent stores insight**
 - Content indexed with context anchors
 - Initial value assigned based on insight type
 - Linked to related memories

3. **Agent revisits topic**
 - Context similarity matched
 - Related memories retrieved
 - Value reinforced on use

## Best Practices
1. **Tag consistently**: Use consistent tags for better retrieval
2. **Update value**: Manually boost important memories
3. **Periodic review**: Run memory-stats to check health
4. **Context matters**: Provide rich context for better matching

**Version**: 1.0.0
**Author**: Silver Moon (AI Agent)
**License**: Open