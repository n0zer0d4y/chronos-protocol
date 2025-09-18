# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2025-09-17

### Changed

- Enhanced notes parameter descriptions for END_ACTIVITY_LOG and UPDATE_ACTIVITY_LOG tools to emphasize traceability and session continuity
- Updated END_ACTIVITY_LOG notes from "Additional notes about the activity" to detailed traceability guidance
- Updated UPDATE_ACTIVITY_LOG notes from "Updated notes" to comprehensive auditability instructions
- Added MIT license and standard-readme badges following industry standards
- Integrated smart system time approach into get_current_time tool description
- Reduced Activity Intelligence System tools to 3 bullet points each for clarity
- Streamlined Core Time Intelligence section acknowledging AI IDE system time embedding
- Removed all emojis from README.md for professional appearance
- Maintained bold formatting for bullet point items in feature descriptions
- **BREAKING**: Standardized all parameter names to use `activityId` exclusively, removing backward compatibility with `timeId`
- **BREAKING**: Standardized data folder name to `chronos-data` across all storage modes and documentation
- **BREAKING**: Renamed `formatted_local` to `formatted_timezone` in time tool outputs for clearer timezone context
- **BREAKING**: Removed redundant `system_time`, `system_timezone`, and `system_formatted_local` fields from time tool outputs
- Updated all code examples and documentation to use consistent `activityId` and `chronos-data` naming
- Removed backward compatibility properties and methods that supported `timeId` parameter names
- Enhanced data folder naming consistency across per-project and centralized storage modes

## [1.5.0] - 2025-09-12

### Fixed

- Fixed McpError constructor issues causing "'str' object has no attribute 'message'" errors across MCP clients
- Resolved MCP client compatibility issues by updating all error handling to use proper ErrorData objects
- Database now properly creates chronos-data directories during save operations
- Renamed `timeId` parameters to `activityId` for better API consistency across all tools
- Enhanced timezone and time format validation with helpful error messages

### Added

- Comprehensive unit test suite with 41 tests covering all functionality
- `--timeout` CLI parameter for configurable operation timeouts (default: 60 seconds)
- Input validation enhancements with specific, actionable error messages
- pytest, pytest-asyncio, and pytest-cov as development dependencies
- Backward compatibility support for both `timeId` and `activityId` field names

### Changed

- Updated all documentation examples to use `activityId` instead of `timeId`
- Enhanced error messages to provide more specific guidance for troubleshooting
- Improved database initialization with immediate path resolution and validation

## [1.4.0] - 2025-09-11

### Fixed

- Fixed missing per-project storage implementation causing Cursor compatibility issues
- Server now properly resolves data directories during startup instead of per-tool-call
- Added proper working directory detection for Cursor and other MCP clients
- Enhanced storage resolution with priority-based project root detection

### Added

- Complete `storage.py` module with robust directory resolution logic
- `--project-root` argument for explicit project context passing
- Support for environment variables: `MCP_PROJECT_ROOT`, `PROJECT_ROOT`, `MCP_DATA_DIR`
- Universal MCP configuration support for all clients (Cursor, Windsurf, Qoder, etc.)
- Comprehensive diagnostic logging for troubleshooting
- Write permission validation for data directories

### Changed

- Server initialization now resolves data directories at startup
- Improved error handling with fail-fast validation and clear error messages
- Updated documentation with Cursor-specific configuration examples

## [1.3.0] - 2025-09-09

### Added

- Complete ShortUUID integration for more manageable activity and reminder IDs
- `IDGenerator` class supporting multiple ID formats (short, uuid, custom)
- `--id-format` CLI parameter for configurable ID generation
- Backward compatibility utilities for UUID conversion and format detection
- 22-character ShortUUIDs as default (61% size reduction from standard UUIDs)

### Changed

- Default ID format from 36-character UUIDs to 22-character ShortUUIDs
- Activity logs and reminders now support multiple ID formats seamlessly
- `mcp-config.json` converted to universal `${workspaceFolder}` configuration
- README examples now use generic paths instead of hardcoded examples
- Improved software portability and rename-safety across different environments

### Fixed

- Removed all hardcoded directory paths from user-facing files
- `install.ps1` now uses dynamic path detection for portability

---

## [1.2.0] - 2025-09-07

### Fixed

- Fixed per-project mode data directory creation bug
- Database initialization now properly resolves and creates directories
- Enhanced error handling with fail-fast validation

### Added

- `--project-root` argument for explicit project context
- Universal MCP configuration support for all clients
- Priority-based project root detection (explicit → environment → current directory)
- Comprehensive startup diagnostic logging
- Write permission validation for data directories

### Changed

- Server initialization creates directories at startup instead of per-tool-call
- Enhanced error messages with more specific troubleshooting guidance
- **BREAKING**: Renamed `human_readable` parameter to `formatted_local` across all time-related tools for better clarity
- **BREAKING**: Renamed `system_human_readable` to `system_formatted_local` in time result objects

### Changed

- Updated `mcp` dependency from `>=1.0.0` to `>=1.13.1` for latest MCP SDK features
- Updated `pydantic` from `>=2.9.2` to `>=2.11.7` for performance improvements
- Updated `jsonschema` from `>=4.23.0` to `>=4.25.0` for enhanced validation
- Updated `pydantic` to `>=2.9.2` for security patches and features
- Updated `tzdata` to `>=2025.2` for current timezone data
- Updated `jsonschema` from `>=4.23.0` to `>=4.25.0` for enhanced validation
- Improved Makefile with UV support and enhanced Docker configuration
- All tools now default to user's local system time
- Enhanced timezone handling with better DST support
- Improved error messages and tool descriptions
- Updated documentation with system time configuration examples
- Enhanced error handling with detailed diagnostic messages
- Improved documentation with comprehensive installation guide and troubleshooting

### Fixed

- Fixed JSON serialization bug in `check_time_reminders` tool
- Enhanced serialization logic for Pydantic objects and lists
- Fixed MCP configuration issues causing "no tools or prompts" error
- Fixed relative path issues in MCP settings and module discovery problems
- Fixed data directory path resolution for cross-project accessibility

### Added

- Documentation files for bug analysis and testing results
- Development dependencies (`pytest`, `ruff`, `pyright`, `freezegun`) to `pyproject.toml`
- Comprehensive documentation and testing files
- System time first approach with auto-detection using `tzlocal`
- Human-readable timestamps alongside ISO 8601 formatting
- Enhanced `TimeResult` model with system time fields
- Comprehensive logging throughout server initialization
- Startup validation with data directory and write permission checks
- Automated installation script (`install.ps1`) for Windows users
- MCP Inspector testing procedures and validation checklists
- Complete temporal awareness toolkit with 9 core MCP tools
- Activity logging and time tracking capabilities
- Timezone conversion and reminder system
- MCP Protocol compliance with full implementation
- Cross-project accessibility and centralized data storage
- Pydantic data models and ISO 8601 datetime formatting

### Core Tools

- `get_current_time` - Current time queries with timezone support
- `convert_time` - Cross-timezone time conversion
- `start_activity_log` - Activity tracking initiation
- `get_elapsed_time` - Real-time duration calculation
- `update_activity_log` - Dynamic activity updates
- `end_activity_log` - Activity completion with duration tracking
- `get_activity_logs` - Historical activity retrieval
- `create_time_reminder` - Future reminder scheduling
- `check_time_reminders` - Reminder detection and retrieval

## Contributing

When contributing to this project, please:

1. Update the changelog following the established format
2. Use the `get_current_time` tool to obtain accurate timestamps
3. Categorize changes appropriately (Added/Changed/Deprecated/Removed/Fixed/Security)
4. Document breaking changes clearly
5. Include validation results for new features
