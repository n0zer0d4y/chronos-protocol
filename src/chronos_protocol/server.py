import asyncio
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import uuid
from typing import Sequence, Optional, Dict, Any, List

from zoneinfo import ZoneInfo
from tzlocal import get_localzone_name
import shortuuid
from shortuuid import ShortUUID

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource, ErrorData
from mcp.shared.exceptions import McpError

from pydantic import BaseModel, Field

from .storage import resolve_data_dir, validate_and_create_data_dir


def validate_timezone(timezone: str) -> str:
    """Validate and provide helpful error messages for timezone inputs."""
    if not isinstance(timezone, str):
        raise ValueError("Timezone must be a string")

    # Handle special cases
    if timezone in ["system", "local"]:
        return timezone

    # Validate IANA timezone format
    try:
        ZoneInfo(timezone)
        return timezone
    except Exception:
        raise ValueError(
            f"Invalid timezone '{timezone}'. "
            f"Supported formats: 'system', 'local', or IANA names like "
            f"'America/New_York', 'Europe/London', 'Asia/Tokyo', 'UTC'"
        )


def validate_time_format(time_str: str) -> str:
    """Validate time format and provide helpful error messages."""
    if not isinstance(time_str, str):
        raise ValueError("Time must be a string")

    # Check HH:MM format
    if not time_str or len(time_str) != 5 or time_str[2] != ':':
        raise ValueError(
            f"Invalid time format '{time_str}'. Expected 24-hour format HH:MM (00:00-23:59)"
        )

    try:
        hours, minutes = time_str.split(':')
        hours = int(hours)
        minutes = int(minutes)

        if not (0 <= hours <= 23):
            raise ValueError(f"Hours must be between 00-23, got {hours:02d}")

        if not (0 <= minutes <= 59):
            raise ValueError(f"Minutes must be between 00-59, got {minutes:02d}")

        return time_str
    except ValueError as e:
        if "too many values" in str(e) or "not enough values" in str(e):
            raise ValueError(
                f"Invalid time format '{time_str}'. Expected HH:MM format (e.g., 14:30)"
            )
        raise


class TimeTools(str, Enum):
    GET_CURRENT_TIME = "get_current_time"
    CONVERT_TIME = "convert_time"
    START_ACTIVITY_LOG = "start_activity_log"
    END_ACTIVITY_LOG = "end_activity_log"
    GET_ELAPSED_TIME = "get_elapsed_time"
    GET_ACTIVITY_LOGS = "get_activity_logs"
    UPDATE_ACTIVITY_LOG = "update_activity_log"
    CREATE_TIME_REMINDER = "create_time_reminder"
    CHECK_TIME_REMINDERS = "check_time_reminders"


class TaskScope(str, Enum):
    EPIC_PLANNING = "epic-planning"
    FEATURE_IMPLEMENTATION = "feature-implementation"
    COMPONENT_IMPLEMENTATION = "component-implementation"
    DEBUGGING = "debugging"
    INTEGRATION_TASKS = "integration-tasks"
    OPTIMIZATION_TASKS = "optimization-tasks"
    SETUP_TASKS = "setup-tasks"
    TESTING_TASKS = "testing-tasks"


class TimeResult(BaseModel):
    timezone: str
    datetime: str
    formatted_timezone: str
    day_of_week: str
    is_dst: bool


class TimeConversionResult(BaseModel):
    source: TimeResult
    target: TimeResult
    time_difference: str


class ActivityLog(BaseModel):
    activityId: str  # Changed from timeId for better naming
    activityType: str
    task_scope: TaskScope
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    startTime: str
    endTime: Optional[str] = None
    duration: Optional[str] = None
    durationSeconds: Optional[int] = None
    result: Optional[str] = None
    notes: Optional[str] = None
    status: str  # "started", "completed"


class Reminder(BaseModel):
    reminderId: str
    reminderTime: str
    message: str
    relatedTaskId: Optional[str] = None
    status: str  # "pending", "completed"
    createdTime: str


class Database:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.db_file = os.path.join(data_dir, "time_server_data.json")
        self.ensure_data_dir()
        self.load_data()

    def ensure_data_dir(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.activity_logs = data.get('activityLogs', [])
                    self.reminders = data.get('reminders', [])
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start with empty data
                self.activity_logs = []
                self.reminders = []
        else:
            self.activity_logs = []
            self.reminders = []

    def save_data(self):
        """Save data to JSON file"""
        # Ensure the data directory exists
        self.ensure_data_dir()

        data = {
            'activityLogs': self.activity_logs,
            'reminders': self.reminders
        }
        try:
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            raise McpError(ErrorData(code=500, message=f"Failed to save data: {str(e)}", data=None))

    def add_activity_log(self, log: ActivityLog):
        """Add a new activity log"""
        self.activity_logs.append(log.model_dump())
        self.save_data()

    def update_activity_log(self, activity_id: str, updates: Dict[str, Any]):
        """Update an existing activity log"""
        for log in self.activity_logs:
            if log.get('activityId') == activity_id:
                log.update(updates)
                self.save_data()
                return True
        return False

    def get_activity_log(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Get an activity log by activity ID"""
        for log in self.activity_logs:
            if log.get('activityId') == activity_id:
                return log
        return None

    def get_activity_logs(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get activity logs with optional filtering"""
        logs = self.activity_logs.copy()
        
        if filters:
            if 'activityType' in filters:
                logs = [log for log in logs if log['activityType'] == filters['activityType']]
            if 'task_scope' in filters:
                logs = [log for log in logs if log['task_scope'] == filters['task_scope']]
            if 'startDate' in filters:
                start_date = datetime.fromisoformat(filters['startDate'].replace('Z', '+00:00'))
                logs = [log for log in logs if datetime.fromisoformat(log['startTime'].replace('Z', '+00:00')) >= start_date]
            if 'endDate' in filters:
                end_date = datetime.fromisoformat(filters['endDate'].replace('Z', '+00:00'))
                logs = [log for log in logs if datetime.fromisoformat(log['startTime'].replace('Z', '+00:00')) <= end_date]
        
        # Sort by start time (newest first)
        logs.sort(key=lambda x: x['startTime'], reverse=True)
        
        if filters and 'limit' in filters:
            logs = logs[:filters['limit']]
        
        return logs

    def add_reminder(self, reminder: Reminder):
        """Add a new reminder"""
        self.reminders.append(reminder.model_dump())
        self.save_data()

    def update_reminder(self, reminder_id: str, updates: Dict[str, Any]):
        """Update an existing reminder"""
        for reminder in self.reminders:
            if reminder['reminderId'] == reminder_id:
                reminder.update(updates)
                self.save_data()
                return True
        return False

    def get_reminders(self, upcoming_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get reminders due within the specified minutes"""
        now = datetime.now(ZoneInfo('UTC'))
        cutoff_time = now + timedelta(minutes=upcoming_minutes)
        
        due_reminders = []
        for reminder in self.reminders:
            if reminder['status'] == 'pending':
                reminder_time = datetime.fromisoformat(reminder['reminderTime'].replace('Z', '+00:00'))
                
                # Fix: Ensure timezone-aware comparison (handles both naive and aware datetimes)
                if reminder_time.tzinfo is None:
                    reminder_time = reminder_time.replace(tzinfo=ZoneInfo('UTC'))
                
                if reminder_time <= cutoff_time:
                    due_reminders.append(reminder)
        
        return due_reminders


class IDGenerator:
    """Generate IDs based on format preference"""
    
    def __init__(self, format_type: str = "short", custom_length: int = 12):
        self.format_type = format_type
        if format_type == "short":
            self.generator = shortuuid
        elif format_type == "custom":
            self.generator = ShortUUID(alphabet="23456789ABCDEFGHJKMNPQRSTUVWXYZ")
            self.custom_length = custom_length
        elif format_type == "uuid":
            self.generator = uuid
        else:
            raise ValueError(f"Unsupported ID format: {format_type}")
    
    def generate_id(self) -> str:
        if self.format_type == "short":
            return self.generator.uuid()
        elif self.format_type == "custom":
            return self.generator.uuid()[:self.custom_length]
        elif self.format_type == "uuid":
            return str(self.generator.uuid4())


def get_local_tz(local_tz_override: str | None = None) -> ZoneInfo:
    if local_tz_override:
        return ZoneInfo(local_tz_override)

    # Get local timezone from datetime.now()
    local_tzname = get_localzone_name()
    if local_tzname is not None:
        return ZoneInfo(local_tzname)
    raise McpError(ErrorData(code=500, message="Could not determine local timezone - tzinfo is None", data=None))


def get_zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except Exception as e:
        raise McpError(ErrorData(code=400, message=f"Invalid timezone: {str(e)}", data=None))


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return f"{hours}h {remaining_minutes}m {remaining_seconds}s"


class TimeServer:
    def __init__(self, database: Database, id_format: str = "short"):
        self.db = database
        self.id_generator = IDGenerator(id_format)

    def get_current_time(self, timezone_name: str) -> TimeResult:
        """Get current time in specified timezone (defaults to system time)"""
        # Get local system time first (this is the primary time)
        local_time = datetime.now()
        local_tz_name = str(get_local_tz())
        
        # If no specific timezone requested or if requesting system timezone, use local time
        if timezone_name.lower() in ["system", "local", local_tz_name.lower()]:
            current_time = local_time
            display_timezone = f"System ({local_tz_name})"
            actual_timezone = local_tz_name
        else:
            # Use requested timezone
            timezone = get_zoneinfo(timezone_name)
            current_time = datetime.now(timezone)
            display_timezone = timezone_name
            actual_timezone = timezone_name

        # Create formatted timezone display
        formatted_timezone = current_time.strftime("%B %d, %Y at %I:%M:%S %p")
        if timezone_name.lower() == "utc":
            formatted_timezone += " UTC"
        elif timezone_name.lower() in ["system", "local"]:
            formatted_timezone += f" (System Time - {local_tz_name})"
        else:
            formatted_timezone += f" ({timezone_name})"

        result = TimeResult(
            timezone=actual_timezone,
            datetime=current_time.isoformat(timespec="seconds"),
            formatted_timezone=formatted_timezone,
            day_of_week=current_time.strftime("%A"),
            is_dst=bool(current_time.dst()),
        )
        
        return result

    def convert_time(
        self, source_tz: str, time_str: str, target_tz: str
    ) -> TimeConversionResult:
        """Convert time between timezones (defaults to system time)"""
        local_tz_name = str(get_local_tz())
        
        # Handle system/local timezone references
        actual_source_tz = source_tz
        if source_tz.lower() in ["system", "local"]:
            actual_source_tz = local_tz_name
        
        actual_target_tz = target_tz
        if target_tz.lower() in ["system", "local"]:
            actual_target_tz = local_tz_name
            
        source_timezone = get_zoneinfo(actual_source_tz)
        target_timezone = get_zoneinfo(actual_target_tz)

        try:
            parsed_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            raise ValueError("Invalid time format. Expected HH:MM [24-hour format]")

        now = datetime.now(source_timezone)
        source_time = datetime(
            now.year,
            now.month,
            now.day,
            parsed_time.hour,
            parsed_time.minute,
            tzinfo=source_timezone,
        )

        target_time = source_time.astimezone(target_timezone)
        source_offset = source_time.utcoffset() or timedelta()
        target_offset = target_time.utcoffset() or timedelta()
        hours_difference = (target_offset - source_offset).total_seconds() / 3600

        if hours_difference.is_integer():
            time_diff_str = f"{hours_difference:+.1f}h"
        else:
            # For fractional hours like Nepal's UTC+5:45
            time_diff_str = f"{hours_difference:+.2f}".rstrip("0").rstrip(".") + "h"

        # Create formatted timezone displays
        source_formatted = source_time.strftime("%B %d, %Y at %I:%M:%S %p")
        target_formatted = target_time.strftime("%B %d, %Y at %I:%M:%S %p")
        
        if source_tz.lower() in ["system", "local"]:
            source_formatted += f" (System Time - {local_tz_name})"
            display_source_tz = f"System ({local_tz_name})"
        else:
            source_formatted += f" ({source_tz})"
            display_source_tz = source_tz
            
        if target_tz.lower() in ["system", "local"]:
            target_formatted += f" (System Time - {local_tz_name})"
            display_target_tz = f"System ({local_tz_name})"
        else:
            target_formatted += f" ({target_tz})"
            display_target_tz = target_tz

        return TimeConversionResult(
            source=TimeResult(
                timezone=display_source_tz,
                datetime=source_time.isoformat(timespec="seconds"),
                formatted_timezone=source_formatted,
                day_of_week=source_time.strftime("%A"),
                is_dst=bool(source_time.dst()),
            ),
            target=TimeResult(
                timezone=display_target_tz,
                datetime=target_time.isoformat(timespec="seconds"),
                formatted_timezone=target_formatted,
                day_of_week=target_time.strftime("%A"),
                is_dst=bool(target_time.dst()),
            ),
            time_difference=time_diff_str,
        )

    def start_activity_log(
        self, 
        activity_type: str, 
        task_scope: TaskScope, 
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ActivityLog:
        """Start a new activity log"""
        time_id = self.id_generator.generate_id()
        start_time = datetime.now(ZoneInfo('UTC')).isoformat(timespec="seconds")
        
        log = ActivityLog(
            activityId=time_id,  # Changed from timeId to activityId
            activityType=activity_type,
            task_scope=task_scope,
            description=description,
            tags=tags,
            startTime=start_time,
            status="started"
        )
        
        self.db.add_activity_log(log)
        return log

    def end_activity_log(
        self,
        activity_id: str,
        result: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ActivityLog:
        """End an activity log and calculate duration"""
        log_data = self.db.get_activity_log(activity_id)
        if not log_data:
            raise ValueError(f"Activity log with ID {activity_id} not found")

        if log_data['status'] == 'completed':
            raise ValueError(f"Activity log with ID {activity_id} is already completed")
        
        end_time = datetime.now(ZoneInfo('UTC')).isoformat(timespec="seconds")
        start_time = datetime.fromisoformat(log_data['startTime'].replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        duration_seconds = int((end_dt - start_time).total_seconds())
        duration_str = format_duration(duration_seconds)
        
        updates = {
            'endTime': end_time,
            'duration': duration_str,
            'durationSeconds': duration_seconds,
            'result': result,
            'notes': notes,
            'status': 'completed'
        }
        
        self.db.update_activity_log(activity_id, updates)

        # Return updated log
        updated_log_data = self.db.get_activity_log(activity_id)
        return ActivityLog(**updated_log_data)

    def get_elapsed_time(self, activity_id: str) -> Dict[str, Any]:
        """Get elapsed time for an activity"""
        log_data = self.db.get_activity_log(activity_id)
        if not log_data:
            raise ValueError(f"Activity log with ID {activity_id} not found")

        start_time = datetime.fromisoformat(log_data['startTime'].replace('Z', '+00:00'))

        if log_data['status'] == 'completed':
            end_time = datetime.fromisoformat(log_data['endTime'].replace('Z', '+00:00'))
            elapsed_seconds = int((end_time - start_time).total_seconds())
            return {
                'activityId': activity_id,
                'startTime': log_data['startTime'],
                'endTime': log_data['endTime'],
                'elapsedTime': format_duration(elapsed_seconds),
                'elapsedSeconds': elapsed_seconds,
                'status': 'completed'
            }
        else:
            current_time = datetime.now(ZoneInfo('UTC'))
            elapsed_seconds = int((current_time - start_time).total_seconds())
            return {
                'activityId': activity_id,
                'startTime': log_data['startTime'],
                'currentTime': current_time.isoformat(timespec="seconds"),
                'elapsedTime': format_duration(elapsed_seconds),
                'elapsedSeconds': elapsed_seconds,
                'status': 'ongoing'
            }

    def update_activity_log(self, activity_id: str, updates: Dict[str, Any]) -> ActivityLog:
        """Update an existing activity log"""
        log_data = self.db.get_activity_log(activity_id)
        if not log_data:
            raise ValueError(f"Activity log with ID {activity_id} not found")
        
        # Filter out None values and convert enum values to strings
        filtered_updates = {}
        for key, value in updates.items():
            if value is not None:
                if isinstance(value, TaskScope):
                    filtered_updates[key] = value.value
                else:
                    filtered_updates[key] = value
        
        self.db.update_activity_log(activity_id, filtered_updates)

        # Return updated log
        updated_log_data = self.db.get_activity_log(activity_id)
        return ActivityLog(**updated_log_data)

    def create_time_reminder(
        self, 
        reminder_time: str, 
        message: str, 
        related_task_id: Optional[str] = None
    ) -> Reminder:
        """Create a time-based reminder"""
        reminder_id = self.id_generator.generate_id()
        created_time = datetime.now(ZoneInfo('UTC')).isoformat(timespec="seconds")
        
        # Validate reminder time format
        try:
            # Handle both 'Z' suffix and existing timezone info
            if reminder_time.endswith('Z'):
                parsed_time = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))
            else:
                parsed_time = datetime.fromisoformat(reminder_time)
        except ValueError:
            raise ValueError("Invalid reminder time format. Expected ISO 8601 format")
        
        reminder = Reminder(
            reminderId=reminder_id,
            reminderTime=reminder_time,
            message=message,
            relatedTaskId=related_task_id,
            status="pending",
            createdTime=created_time
        )
        
        self.db.add_reminder(reminder)
        return reminder

    def check_time_reminders(self, upcoming_minutes: int = 60) -> List[Reminder]:
        """Check for due or upcoming time reminders"""
        reminders_data = self.db.get_reminders(upcoming_minutes)
        return [Reminder(**reminder) for reminder in reminders_data]


async def serve(local_timezone: str | None = None, data_dir: str = "./chronos-data", storage_mode: str = "centralized", project_root: str = None, id_format: str = "short", timeout: int = 60) -> None:
    # Startup validation and logging
    import sys
    import logging
    
    # Set up basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("chronos-protocol")
    
    # Log startup information
    logger.info("🚀 Starting Chronos Protocol MCP Server")
    # Data directory will be logged after resolution
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"🌍 Local timezone override: {local_timezone or 'None (auto-detect)'}")
    
    # Resolve actual data directory based on storage configuration
    try:
        resolved_data_dir = resolve_data_dir(storage_mode, project_root, data_dir)
        validate_and_create_data_dir(resolved_data_dir)
        
        # Log storage configuration for diagnostics
        logger.info(f"🗂️  Storage mode: {storage_mode}")
        logger.info(f"📁 Data directory: {resolved_data_dir}")
        if project_root:
            logger.info(f"🎯 Explicit project root: {project_root}")
        
    except Exception as e:
        logger.error(f"❌ Storage configuration failed: {str(e)}")
        raise McpError(ErrorData(code=500, message=f"Storage setup failed: {str(e)}", data=None))
    
    # Initialize server components
    try:
        server = Server("chronos-protocol")
        database = Database(str(resolved_data_dir))
        time_server = TimeServer(database, id_format)
        local_tz = str(get_local_tz(local_timezone))
        
        logger.info(f"🌍 Using timezone: {local_tz}")
        logger.info("✅ Server components initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Server initialization failed: {str(e)}")
        raise

    # Store timeout for use in tool calls
    operation_timeout = timeout

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available time tools."""
        logger.info("📋 Listing available tools for MCP client")
        
        tools = [
            Tool(
                name=TimeTools.GET_CURRENT_TIME.value,
                description="Get current time (defaults to system time, supports any timezone)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string", 
                            "description": f"Timezone to display. Use 'system' or 'local' for user's local time ({local_tz}). Use IANA names like 'America/New_York', 'Europe/London', or 'UTC' for other timezones. System time is the default and most practical choice.",
                        }
                    },
                    "required": ["timezone"],
                },
            ),
            Tool(
                name=TimeTools.CONVERT_TIME.value,
                description="Convert time between timezones (defaults to system time for source/target)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_timezone": {
                            "type": "string",
                            "description": f"Source timezone. Use 'system' or 'local' for user's local time ({local_tz}), or IANA names like 'America/New_York', 'UTC'. System time is the most practical default.",
                        },
                        "time": {
                            "type": "string",
                            "description": "Time to convert in 24-hour format (HH:MM)",
                        },
                        "target_timezone": {
                            "type": "string", 
                            "description": f"Target timezone. Use 'system' or 'local' for user's local time ({local_tz}), or IANA names like 'Asia/Tokyo', 'UTC'. System time is the most practical default.",
                        },
                    },
                    "required": ["source_timezone", "time", "target_timezone"],
                },
            ),
            Tool(
                name=TimeTools.START_ACTIVITY_LOG.value,
                description="Start a new activity log with system timestamp and unique Time ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "activityType": {
                            "type": "string",
                            "description": "Type of activity being performed (e.g., 'code_review', 'debugging', 'planning')",
                        },
                        "task_scope": {
                            "type": "string",
                            "enum": [scope.value for scope in TaskScope],
                            "description": "Scope of the task",
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the activity",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for categorizing the activity",
                        },
                    },
                    "required": ["activityType", "task_scope"],
                },
            ),
            Tool(
                name=TimeTools.END_ACTIVITY_LOG.value,
                description="End an activity log with system timestamp and calculate duration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "activityId": {
                            "type": "string",
                            "description": "Unique identifier of the activity log to end",
                        },
                        "result": {
                            "type": "string",
                            "description": "Result or outcome of the activity",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Detailed notes for traceability and session continuity. Include: what was accomplished, key decisions made, challenges encountered, solutions implemented, and any critical context for future reference. This enables other AI agents to understand your work, backtrack steps if issues arise, and continue development effectively. Be specific about code changes, architectural decisions, and debugging insights.",
                        },
                    },
                    "required": ["activityId"],
                },
            ),
            Tool(
                name=TimeTools.GET_ELAPSED_TIME.value,
                description="Get the elapsed time for an ongoing or completed activity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "activityId": {
                            "type": "string",
                            "description": "Unique identifier of the activity log",
                        },
                    },
                    "required": ["activityId"],
                },
            ),
            Tool(
                name=TimeTools.GET_ACTIVITY_LOGS.value,
                description="Retrieve activity logs with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "activityType": {
                            "type": "string",
                            "description": "Filter by activity type",
                        },
                        "task_scope": {
                            "type": "string",
                            "enum": [scope.value for scope in TaskScope],
                            "description": "Filter by task scope",
                        },
                        "startDate": {
                            "type": "string",
                            "description": "Filter by start date (ISO 8601 format)",
                        },
                        "endDate": {
                            "type": "string",
                            "description": "Filter by end date (ISO 8601 format)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of logs to return",
                        },
                    },
                },
            ),
            Tool(
                name=TimeTools.UPDATE_ACTIVITY_LOG.value,
                description="Update an existing activity log",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "activityId": {
                            "type": "string",
                            "description": "Unique identifier of the activity log to update",
                        },
                        "activityType": {
                            "type": "string",
                            "description": "Updated activity type",
                        },
                        "task_scope": {
                            "type": "string",
                            "enum": [scope.value for scope in TaskScope],
                            "description": "Updated task scope",
                        },
                        "description": {
                            "type": "string",
                            "description": "Updated description",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Updated tags",
                        },
                        "result": {
                            "type": "string",
                            "description": "Updated result",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Updated traceability notes for session continuity and auditability. Document progress, changes in approach, new findings, or corrections made. Include specific details about what was modified, why changes were needed, and any insights gained. This ensures other AI agents can follow your thought process, understand context, and continue work seamlessly without losing critical information.",
                        },
                    },
                    "required": ["activityId"],
                },
            ),
            Tool(
                name=TimeTools.CREATE_TIME_REMINDER.value,
                description="Create a time-based reminder using system time for scheduling",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "reminderTime": {
                            "type": "string",
                            "description": "Time for the reminder (ISO 8601 format with explicit timezone offset, e.g., '2025-09-11T14:00:00+08:00' for local time or '2025-09-11T14:00:00+00:00' for UTC)",
                        },
                        "message": {
                            "type": "string",
                            "description": "Reminder message",
                        },
                        "relatedTaskId": {
                            "type": "string",
                            "description": "ID of related task or activity",
                        },
                    },
                    "required": ["reminderTime", "message"],
                },
            ),
            Tool(
                name=TimeTools.CHECK_TIME_REMINDERS.value,
                description="Check for due or upcoming time reminders",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "upcomingMinutes": {
                            "type": "integer",
                            "description": "Check for reminders due within this many minutes (default: 60)",
                        },
                    },
                },
            ),
        ]
        
        logger.info(f"✅ Providing {len(tools)} tools to MCP client")
        return tools

    async def _execute_tool(name: str, arguments: dict) -> Any:
        """Execute tool logic."""
        try:
            match name:
                case TimeTools.GET_CURRENT_TIME.value:
                    timezone = arguments.get("timezone")
                    if not timezone:
                        raise ValueError("Missing required argument: timezone")

                    # Validate timezone with helpful error messages
                    validated_timezone = validate_timezone(timezone)
                    result = time_server.get_current_time(validated_timezone)

                case TimeTools.CONVERT_TIME.value:
                    if not all(
                        k in arguments
                        for k in ["source_timezone", "time", "target_timezone"]
                    ):
                        raise ValueError("Missing required arguments")

                    # Validate inputs with helpful error messages
                    source_tz = validate_timezone(arguments["source_timezone"])
                    target_tz = validate_timezone(arguments["target_timezone"])
                    validated_time = validate_time_format(arguments["time"])

                    result = time_server.convert_time(source_tz, validated_time, target_tz)

                case TimeTools.START_ACTIVITY_LOG.value:
                    if not all(k in arguments for k in ["activityType", "task_scope"]):
                        raise ValueError("Missing required arguments: activityType and task_scope")

                    result = time_server.start_activity_log(
                        arguments["activityType"],
                        TaskScope(arguments["task_scope"]),
                        arguments.get("description"),
                        arguments.get("tags"),
                    )

                case TimeTools.END_ACTIVITY_LOG.value:
                    activity_id = arguments.get("activityId")
                    if not activity_id:
                        raise ValueError("Missing required argument: activityId")

                    result = time_server.end_activity_log(
                        activity_id,
                        arguments.get("result"),
                        arguments.get("notes"),
                    )

                case TimeTools.GET_ELAPSED_TIME.value:
                    activity_id = arguments.get("activityId")
                    if not activity_id:
                        raise ValueError("Missing required argument: activityId")

                    result = time_server.get_elapsed_time(activity_id)

                case TimeTools.GET_ACTIVITY_LOGS.value:
                    filters = {}
                    for key in ["activityType", "task_scope", "startDate", "endDate", "limit"]:
                        if key in arguments:
                            filters[key] = arguments[key]

                    result = time_server.db.get_activity_logs(filters)

                case TimeTools.UPDATE_ACTIVITY_LOG.value:
                    activity_id = arguments.get("activityId")
                    if not activity_id:
                        raise ValueError("Missing required argument: activityId")

                    updates = {}
                    for key in ["activityType", "task_scope", "description", "tags", "result", "notes"]:
                        if key in arguments:
                            updates[key] = arguments[key]

                    result = time_server.update_activity_log(activity_id, updates)

                case TimeTools.CREATE_TIME_REMINDER.value:
                    if not all(k in arguments for k in ["reminderTime", "message"]):
                        raise ValueError("Missing required arguments: reminderTime and message")

                    result = time_server.create_time_reminder(
                        arguments["reminderTime"],
                        arguments["message"],
                        arguments.get("relatedTaskId"),
                    )

                case TimeTools.CHECK_TIME_REMINDERS.value:
                    upcoming_minutes = arguments.get("upcomingMinutes", 60)
                    result = time_server.check_time_reminders(upcoming_minutes)

                case _:
                    raise ValueError(f"Unknown tool: {name}")

            logger.info(f"✅ Tool {name} executed successfully")

            # Handle different result types for JSON serialization
            if isinstance(result, list):
                if result and hasattr(result[0], 'model_dump'):
                    # Handle non-empty list of Pydantic models
                    serialized_result = [item.model_dump() for item in result]
                else:
                    # Handle empty list or list of non-Pydantic objects
                    serialized_result = result
            elif hasattr(result, 'model_dump'):
                # Handle single Pydantic model
                serialized_result = result.model_dump()
            else:
                # Handle other types (dict, str, int, etc.)
                serialized_result = result

            return [
                TextContent(type="text", text=json.dumps(serialized_result, indent=2))
            ]

        except Exception as e:
            logger.error(f"❌ Tool {name} failed: {str(e)}")
            raise McpError(ErrorData(code=500, message=f"Error processing chronos-protocol query: {str(e)}", data=None))

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls for time queries and activity logging."""
        logger.info(f"🔧 Tool called: {name} (timeout: {operation_timeout}s)")
        try:
            # Execute tool with timeout
            result = await asyncio.wait_for(
                _execute_tool(name, arguments),
                timeout=operation_timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"❌ Tool {name} timed out after {operation_timeout} seconds")
            raise McpError(ErrorData(code=408, message=f"Tool {name} timed out after {operation_timeout} seconds", data=None))
        except Exception as e:
            logger.error(f"❌ Tool {name} failed: {str(e)}")
            raise McpError(ErrorData(code=500, message=f"Error processing chronos-protocol query: {str(e)}", data=None))

    options = server.create_initialization_options()
    logger.info("🔌 Starting MCP server with stdio transport")
    logger.info("📡 Ready to receive MCP client connections")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, options)
    except Exception as e:
        logger.error(f"❌ Server error: {str(e)}")
        raise