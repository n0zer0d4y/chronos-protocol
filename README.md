# Chronos Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Development Status](https://img.shields.io/badge/status-production--stable-green.svg)](https://pypi.org/project/chronos-protocol/)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![MCP Server](https://badge.mcpx.dev?type=server "MCP Server")](https://modelcontextprotocol.io)
[![MCP Server with Tools](https://badge.mcpx.dev?type=server&features=tools "MCP server with tools")](https://modelcontextprotocol.io)

> MCP server providing time intelligence, persistent memory and complete traceability for AI coding agents.

Chronos Protocol transforms AI development workflows by eliminating temporal blindness in automated systems. The MCP server provides complete traceability and session continuity, enabling AI agents to maintain context across sessions while delivering enterprise-grade time tracking, intelligent scheduling, and comprehensive development analytics.

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [API](#api)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Background

### Core Capabilities

Chronos Protocol addresses critical gaps in AI development workflows through sophisticated time intelligence and persistent memory systems designed specifically for automated coding environments.

#### System Time First Approach

Chronos Protocol transforms how automated systems handle time by prioritizing **your computer's local system time** as the intelligent default. No more timezone confusion - just use `"system"` or `"local"` and get instant, contextual time awareness that adapts to your environment.

#### Core Time Intelligence

**`get_current_time` - Temporal Awareness Made Simple**

Chronos Protocol prioritizes your computer's local system time as the intelligent default. Most AI IDEs already embed system time in their prompts, but Chronos Protocol provides explicit, structured temporal context that works across all MCP clients.

Get standardized timestamps with system time context:

- **System Time Priority**: Uses your local system time as the intelligent default
- **Cross-Timezone Collaboration**: Show local time alongside team timezone for global projects
- **Temporal Context**: AI agents always know "when" they're operating for better decision-making

**`convert_time` - Smart Timezone Translation**

Eliminate timezone calculation errors with intelligent conversion:

- **Meeting Scheduling**: Convert times between global timezones
- **Release Planning**: Coordinate deployments across regions
- **Time Difference Analysis**: Calculate timezone offsets with DST handling

#### Activity Intelligence System

**`start_activity_log` - Intelligent Context Initialization**

Start sophisticated activity monitoring with unique Activity IDs and rich metadata for agentic development workflows:

- **Autonomous Session Management**: Track coding sessions, debugging processes, and feature implementations with persistent context
- **Intelligent Task Analysis**: Monitor and learn from task completion patterns to optimize future planning
- **Context Preservation**: Maintain precise records for cross-session continuity and seamless task resumption

**`end_activity_log` - Success Documentation & Analytics**

Complete activities with automatic duration calculation and rich outcome data for performance intelligence:

- **Self-Performance Analysis**: Analyze actual vs. estimated completion times for better future planning accuracy
- **Autonomous Documentation**: Document accomplishments and lessons learned for persistent knowledge retention
- **Adaptive Performance**: Build historical intelligence on development velocity and success patterns

**`get_elapsed_time` - Real-Time Progress Monitoring**

Monitor ongoing activities without interrupting execution flow:

- **Long-Running Task Management**: Check progress on extended debugging or complex implementations
- **Intelligent Time Boxing**: Monitor and optimize work sessions for maximum efficiency
- **Context Awareness**: Track duration of different phases in problem-solving processes

**`get_activity_logs` - Historical Intelligence & Pattern Analysis**

Query and analyze development patterns with sophisticated filtering:

- **Autonomous Pattern Recognition**: Generate performance reports and identify optimization opportunities
- **Self-Learning Analytics**: Identify which task types require more resources and adapt approach accordingly
- **Cross-Project Learning**: Leverage experience from different projects to improve overall effectiveness

**`update_activity_log` - Intelligent Activity Management**

Modify completed activities with updated insights and corrections:

- **Autonomous Learning**: Add insights discovered after task completion for future reference
- **Self-Correction**: Fix timing errors or update task descriptions based on new information
- **Continuous Documentation**: Update results and learnings as projects evolve and new context emerges

#### Intelligent Reminder System

**`create_time_reminder` - Contextual Task Scheduling**

Set smart reminders linked to your development workflow:

- **Code Review Follow-ups**: Never forget to check on pending pull requests
- **Dependency Updates**: Schedule regular checks for outdated packages and security patches
- **Release Checkpoints**: Set reminders for deployment, testing, and rollback windows

**`check_time_reminders` - Proactive Awareness System**

Stay ahead of important tasks with intelligent reminder detection:

- **Upcoming Deadlines**: Get advance warning of approaching project milestones
- **Maintenance Windows**: Be reminded of scheduled system maintenance or deployments
- **Team Coordination**: Never miss collaborative sessions or important check-ins

### Problem Statement

#### Solves Real Problems

- **Eliminates AI Temporal Blindness**: Your AI agents can actively check current time and make time-aware decisions instead of relying solely on embedded system time in the its System Prompt
- **Reduces Context Switching**: AI agents can track time without interrupting your flow
- **Cross-Project Continuity**: Start tracking in Project A, finish in Project B - everything stays connected
- **Developer-Centric Design**: Built specifically for agentic coding workflows, not generic time tracking

### Architecture

#### Flexible Storage Architecture

Chronos Protocol supports dual storage modes to fit your development workflow:

**Centralized Mode (Traditional)**

- **Single database** for all projects
- **Cross-project analytics** and historical intelligence
- **Perfect for**: Teams wanting unified time tracking across all work
- **AI Framework Integration**: Persistent memory works across all projects

**Per-Project Mode (Dynamic)**

- **Automatic project detection** with zero configuration
- **Isolated storage** per project (`{project-root}/chronos-data/time_server_data.json`)
- **Perfect for**: Individual developers who prefer project-specific tracking
- **Zero Setup**: Just use `--storage-mode per-project` and it works everywhere

### Context Engineering Framework Integration

Chronos Protocol's activity logging system provides persistent memory for AI frameworks like [Claude Task Master](https://github.com/eyaltoledano/claude-task-master), [Agent OS](https://github.com/buildermethods/agent-os), and [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD), enabling enhanced task tracking, centralized activity logging, and historical analysis with persistent Activity IDs across agent operations.

**Integration Guide**: For AI coding agents, refer to the sample prompt template in `AGENTS.md` which provides Cursor Rules that can be integrated with your existing workflow rules. This template demonstrates the complete activity logging protocol with customizable task list filename patterns.

#### Persistent Memory Benefits

- **Cross-Session Continuity**: Tasks started in one session can be tracked and completed in another
- **Framework-Agnostic Storage**: JSON database works with any AI framework that can append Activity IDs
- **Rich Context Preservation**: Full activity metadata including duration, outcomes, and custom tags
- **Historical Intelligence**: AI frameworks can query past activities for pattern recognition and optimization

## Install

### Prerequisites

- **Python**: 3.10 or higher
- **MCP Support**: AI client with Model Context Protocol support

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/n0zer0d4y/chronos-protocol.git
cd chronos-protocol

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install in editable mode (required for MCP)
pip install -e .

# 4. Verify installation
python -m chronos_protocol --help
```

After installation, configure Chronos Protocol in your MCP client using the appropriate configuration schema in the [Configuration](#configuration) section.

## Usage

### Basic Time Intelligence Operations

#### Get Current Time with Context

```bash
# Get current time in your system's timezone
get_current_time(timezone="system")
# Returns: Current time with full timezone context
```

#### Smart Timezone Conversion

```bash
# Convert meeting time across timezones
convert_time(
  source_timezone="America/New_York",
  time="15:00",
  target_timezone="Europe/London"
)
# Returns: Converted time with timezone difference
```

### Activity Intelligence Workflow

#### Complete Development Session Tracking

```python
# 1. Start activity logging
activity_id = start_activity_log(
    activityType="debugging",
    task_scope="feature-implementation",
    description="Fix authentication module login flow"
)

# 2. AI agent works on the task...
# Monitor progress with get_elapsed_time(activity_id)

# 3. Complete with results
end_activity_log(
    activity_id,
    result="Authentication module completed successfully"
)
```

#### Intelligent Task Analysis

```python
# Get activity history for pattern analysis
activities = get_activity_logs(
    activityType="debugging",
    task_scope="feature-implementation"
)

# AI learns from patterns and timing
for activity in activities:
    analyze_completion_time(activity)
    identify_successful_patterns(activity)
```

#### Cross-Session Continuity

```python
# Check for ongoing activities
ongoing = get_activity_logs(status="ongoing")
if ongoing:
    # Resume where you left off
    continue_activity(ongoing[0]["activityId"])

# Learning from history
debug_sessions = get_activity_logs(
    activityType="debugging",
    start_date="2024-01-01"
)
```

### AI Framework Integration Example

```python
# Example: AI Framework Integration
activity_id = start_activity_log(
    activityType="framework_task",
    task_scope="feature-implementation",
    description="AI agent implementing authentication module",
    tags=["ai-agent", "claude-task-master"]
)

# Your framework stores the activity_id with task data
# Later: end_activity_log(activity_id, result="Authentication module completed")
```

This creates an intelligent feedback loop where AI frameworks learn from historical task performance and timing patterns!

## API

### Time Intelligence Functions

#### `get_current_time(timezone)`

Get standardized timestamps with system time context.

**Parameters:**

- `timezone` (string): Target timezone. Use `"system"` or `"local"` for user's local time, or IANA names like `"America/New_York"`, `"Europe/London"`, `"UTC"`

**Returns:** Current time with full timezone context and metadata

#### `convert_time(source_timezone, time, target_timezone)`

Convert time between timezones with intelligent handling of DST.

**Parameters:**

- `source_timezone` (string): Source timezone
- `time` (string): Time in 24-hour format (HH:MM)
- `target_timezone` (string): Target timezone

**Returns:** Converted time with timezone difference information

### Activity Intelligence Functions

#### `start_activity_log(activityType, task_scope, description, tags?)`

Initialize activity monitoring with unique Activity ID and rich metadata.

**Parameters:**

- `activityType` (string): Type of activity (e.g., 'debugging', 'feature-implementation')
- `task_scope` (string): Scope of the task from predefined options
- `description` (string): Detailed description of the activity
- `tags` (array, optional): Array of strings for categorizing the activity

**Returns:** Unique Activity ID for tracking

#### `end_activity_log(activityId, result?, notes?)`

Complete activity with automatic duration calculation and rich outcome data.

**Parameters:**

- `activityId` (string): Unique identifier of the activity to end
- `result` (string, optional): Result or outcome of the activity
- `notes` (string, optional): Additional notes about the activity

**Returns:** Completed activity with duration and timestamps

#### `get_elapsed_time(activityId)`

Monitor ongoing activities without interrupting execution flow.

**Parameters:**

- `activityId` (string): Unique identifier of the activity

**Returns:** Elapsed time information for the specified activity

#### `get_activity_logs(filters?)`

Query and analyze development patterns with sophisticated filtering.

**Parameters:**

- `filters` (object, optional): Filtering options including:
  - `activityType` (string): Filter by activity type
  - `task_scope` (string): Filter by task scope
  - `startDate` (string): Filter by start date (ISO 8601 format)
  - `endDate` (string): Filter by end date (ISO 8601 format)
  - `limit` (integer): Maximum number of logs to return

**Returns:** Array of activity logs matching the criteria

#### `update_activity_log(activityId, updates)`

Modify completed activities with updated insights and corrections.

**Parameters:**

- `activityId` (string): Unique identifier of the activity to update
- `updates` (object): Object containing fields to update

**Returns:** Updated activity log

### Reminder System Functions

#### `create_time_reminder(reminderTime, message, relatedTaskId?)`

Create time-based reminder using system time for scheduling.

**Parameters:**

- `reminderTime` (string): Time for the reminder (ISO 8601 format with timezone)
- `message` (string): Reminder message
- `relatedTaskId` (string, optional): ID of related task or activity

**Returns:** Created reminder with unique identifier

#### `check_time_reminders(upcomingMinutes?)`

Check for due or upcoming time reminders.

**Parameters:**

- `upcomingMinutes` (integer, optional): Check for reminders due within this many minutes (default: 60)

**Returns:** Array of due and upcoming reminders

## Configuration

Chronos Protocol supports two storage modes:

| Mode        | Use Case                     | Data Location                                       |
| ----------- | ---------------------------- | --------------------------------------------------- |
| Per-Project | Individual project isolation | `{project-root}/chronos-data/time_server_data.json` |
| Centralized | Cross-project analytics      | Custom directory via `--data-dir`                   |

### ID Format Options

| Format   | Example                                | Length   | Use Case                         |
| -------- | -------------------------------------- | -------- | -------------------------------- |
| `custom` | `28RCD6M8A64P`                         | 12 chars | **Ultra-compact** for task lists |
| `short`  | `vytxeTZskVKR7C7WgdSP3d`               | 22 chars | Balanced readability             |
| `uuid`   | `bb401d9e-1c3e-41d4-a201-733baa48c13d` | 36 chars | Legacy compatibility             |

### Important: Type Parameter Warning

**DO NOT** add `"type": "stdio"` to your MCP configuration.

**Why this causes failures:**

- Chronos Protocol is hardcoded to use stdio transport
- When clients add `"type": "stdio"`, it can interfere with variable resolution
- Variable substitution happens before type validation
- Results in invalid paths like `C:\Program Files\VSCode\${workspaceFolder}`

**Correct approach:**

- Let Chronos Protocol handle transport selection automatically
- Only specify `"type"` if your MCP client requires it AND you're not using variables
- Most MCP clients work perfectly without explicit type declaration

### VS Code Extensions and forks

#### Roo Code Extension

```json
{
  "mcpServers": {
    "chronos-protocol": {
      "command": "python",
      "args": [
        "-m",
        "chronos_protocol",
        "--storage-mode",
        "per-project",
        "--project-root",
        "${workspaceFolder}",
        "--id-format",
        "custom"
      ]
    }
  }
}
```

### VS Code Forks

#### Cursor & Trae

```json
{
  "mcpServers": {
    "chronos-protocol": {
      "command": "python",
      "args": [
        "-m",
        "chronos_protocol",
        "--storage-mode",
        "per-project",
        "--project-root",
        "${workspaceFolder}",
        "--id-format",
        "custom"
      ]
    }
  }
}
```

### CLI Clients

#### Claude Code & Gemini CLI

```json
{
  "chronos-protocol": {
    "command": "python",
    "args": [
      "-m",
      "chronos_protocol",
      "--storage-mode",
      "per-project",
      "--id-format",
      "custom"
    ]
  }
}
```

### Limited Support Clients

#### Cline & Qoder

Known Limitations:

- Does not support `${workspaceFolder}` variable substitution
- Cannot use per-project storage mode
- Will fail if `--project-root` argument is included
- Limited to centralized storage only

Working Configuration:

```json
{
  "chronos-protocol": {
    "disabled": false,
    "timeout": 60,
    "command": "python",
    "args": [
      "-m",
      "chronos_protocol",
      "--storage-mode",
      "centralized",
      "--data-dir",
      "/path/to/centralized/chronos-data",
      "--id-format",
      "custom"
    ]
  }
}
```

Do NOT add:

- `--project-root "${workspaceFolder}"` (causes failures)
- `"type": "stdio"` parameter (see Important section above)

### Important: Type Parameter Warning

DO NOT add `"type": "stdio"` to your MCP configuration

Why this causes failures:

- Chronos Protocol is hardcoded to use stdio transport
- When clients add `"type": "stdio"`, it can interfere with variable resolution
- Variable substitution happens before type validation
- Results in invalid paths like `C:\Program Files\VSCode\${workspaceFolder}`

Correct approach:

- Let Chronos Protocol handle transport selection automatically
- Only specify `"type"` if your MCP client requires it AND you're not using variables
- Most MCP clients work perfectly without explicit type declaration

## Troubleshooting

### Common Issues

#### "No tools or prompts" Error

**Symptoms:**

- MCP server appears connected
- Tools are not available in the client
- No error messages visible

**Solutions by Client:**

**Cursor:**

- Ensure `--project-root "${workspaceFolder}"` is included
- Check that workspace is properly opened

**Claude Code:**

- Remove `--project-root` argument (use default detection)
- Do not add `"type": "stdio"` parameter

**Cline/Qoder:**

- Use centralized storage mode
- Remove all workspace variables
- Set explicit `--data-dir` path

#### Variable Substitution Issues

**Problem:** `${workspaceFolder}` not resolving
**Affected Clients:** Cline, Qoder, some Claude Code configurations

**Solution:**

```json
{
  "chronos-protocol": {
    "command": "python",
    "args": [
      "-m",
      "chronos_protocol",
      "--storage-mode",
      "centralized",
      "--data-dir",
      "/explicit/path/to/chronos-data"
    ]
  }
}
```

#### Storage Permission Errors

**Error:** Cannot create chronos-data directory
**Solution:**

- Ensure write permissions in project directory
- For per-project mode, check workspace permissions
- For centralized mode, verify `--data-dir` accessibility

#### Python Module Not Found

**Error:** `ModuleNotFoundError: No module named 'chronos_protocol'`
**Solution:**

```bash
# Ensure editable installation
pip install -e .
   # Verify installation
python -m chronos_protocol --help
```

### Client-Specific Issues

#### VS Code Extensions

- Ensure MCP extension is enabled
- Check VS Code version compatibility
- Verify workspace is properly opened

#### VS Code Forks

- Some forks may have custom MCP implementations
- Check fork-specific documentation
- Report issues to fork maintainers

#### CLI Clients

- Ensure proper JSON formatting
- Check file permissions for configuration files
- Verify Python environment setup

### Performance Optimization

#### Large Activity Logs

- Use appropriate ID format for your use case
- Consider centralized storage for cross-project analytics
- Archive old activities periodically

#### Memory Usage

- Per-project mode isolates memory usage
- Centralized mode may accumulate data over time
- Monitor storage directory sizes

### Getting Help

#### Community Support

- Check GitHub issues for similar problems
- Provide detailed error logs and configuration
- Include client version and platform information

#### Debug Information

```bash
# Get detailed server logs
python -m chronos_protocol --verbose

# Check MCP client logs
# (varies by client - check client documentation)
```

## Contributing

### Development Setup

```bash
# Fork and clone
git clone https://github.com/n0zer0d4y/chronos-protocol.git
cd chronos-protocol

# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# Run tests
pytest tests/

# Run with debug logging
python -m chronos_protocol --debug
```

### Code Standards

- **Python**: Follow PEP 8 style guidelines
- **Documentation**: Use Google-style docstrings
- **Testing**: Maintain >90% test coverage
- **Commits**: Use conventional commit format

### Testing MCP Clients

When adding support for new MCP clients:

1. Test with both storage modes
2. Verify all tools work correctly
3. Check error handling scenarios
4. Update configuration documentation
5. Add to compatibility matrix

### Reporting Bugs

**Bug Report Template:**

- MCP client name and version
- Configuration used
- Expected vs actual behavior
- Error logs (if available)
- Steps to reproduce

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/n0zer0d4y/chronos-protocol/blob/master/LICENSE) file for details.

## Acknowledgments

- **Anthropic** for the Model Context Protocol specification
- **MCP Community** for client implementations and testing
- **Contributors** for their valuable feedback and bug reports

---

Ready to transform your AI development workflow? Configure Chronos Protocol in your MCP client and start building with complete traceability and session continuity.
