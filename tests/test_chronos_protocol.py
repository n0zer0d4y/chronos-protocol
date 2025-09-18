"""
Comprehensive test suite for Chronos Protocol MCP Server

Tests cover:
- Input validation functions
- TimeServer core functionality
- Database operations
- Error handling
- Edge cases
"""

import asyncio
import os
import tempfile
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from chronos_protocol.server import (
    TimeServer, Database, TaskScope, ActivityLog,
    validate_timezone, validate_time_format, IDGenerator
)
from mcp.shared.exceptions import McpError


class TestInputValidation:
    """Test input validation functions"""

    @pytest.mark.parametrize("valid_timezone", [
        "system", "local", "America/New_York", "Europe/London", "UTC"
    ])
    def test_validate_timezone_valid(self, valid_timezone):
        """Test timezone validation with valid inputs"""
        result = validate_timezone(valid_timezone)
        assert result == valid_timezone

    @pytest.mark.parametrize("invalid_timezone", [
        "", "Invalid/Timezone", None, 123
    ])
    def test_validate_timezone_invalid(self, invalid_timezone):
        """Test timezone validation with invalid inputs"""
        with pytest.raises(ValueError):
            validate_timezone(invalid_timezone)

    @pytest.mark.parametrize("valid_time", [
        "00:00", "12:30", "23:59", "09:45"
    ])
    def test_validate_time_format_valid(self, valid_time):
        """Test time format validation with valid inputs"""
        result = validate_time_format(valid_time)
        assert result == valid_time

    @pytest.mark.parametrize("invalid_time", [
        "", "25:00", "12:60", "ab:cd", None
    ])
    def test_validate_time_format_invalid(self, invalid_time):
        """Test time format validation with invalid inputs"""
        with pytest.raises(ValueError):
            validate_time_format(invalid_time)


class TestIDGenerator:
    """Test ID generation functionality"""

    def test_generate_short_id(self):
        """Test short ID generation"""
        generator = IDGenerator("short")
        id1 = generator.generate_id()
        id2 = generator.generate_id()

        assert len(id1) == 22  # ShortUUID default length
        assert len(id2) == 22
        assert id1 != id2  # Should be unique

    def test_generate_uuid_id(self):
        """Test UUID ID generation"""
        generator = IDGenerator("uuid")
        id1 = generator.generate_id()

        assert len(id1) == 36  # UUID format
        assert id1.count('-') == 4  # Standard UUID format

    def test_generate_custom_id(self):
        """Test custom length ID generation"""
        generator = IDGenerator("custom", 10)
        id1 = generator.generate_id()
        id2 = generator.generate_id()

        assert len(id1) == 10
        assert len(id2) == 10
        assert id1 != id2


class TestDatabase:
    """Test database operations"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Database(temp_dir)
            # Ensure the database file exists
            if not os.path.exists(db.db_file):
                db.save_data()  # Create the file
            yield db

    def test_database_initialization(self, temp_db):
        """Test database initialization"""
        assert temp_db.data_dir is not None
        assert os.path.exists(temp_db.db_file)

    def test_add_and_get_activity_log(self, temp_db):
        """Test adding and retrieving activity logs"""
        log = ActivityLog(
            activityId="test-123",
            activityType="testing",
            task_scope=TaskScope.EPIC_PLANNING,
            description="Test activity",
            tags=["test"],
            startTime=datetime.now(ZoneInfo('UTC')).isoformat(),
            status="started"
        )

        # Add log
        temp_db.add_activity_log(log)

        # Get all logs
        logs = temp_db.get_activity_logs({})
        assert len(logs) == 1
        assert logs[0]["activityId"] == "test-123"
        assert logs[0]["activityType"] == "testing"

    def test_get_activity_logs_with_filters(self, temp_db):
        """Test filtering activity logs"""
        # Add multiple logs
        logs_data = [
            {
                "activityId": "test-1",
                "activityType": "coding",
                "task_scope": "feature-implementation",
                "description": "Feature 1",
                "startTime": datetime.now(ZoneInfo('UTC')).isoformat(),
                "status": "completed"
            },
            {
                "activityId": "test-2",
                "activityType": "debugging",
                "task_scope": "debugging",  # Fixed: was "bug-fixing"
                "description": "Bug fix",
                "startTime": datetime.now(ZoneInfo('UTC')).isoformat(),
                "status": "started"
            }
        ]

        for log_data in logs_data:
            log = ActivityLog(**log_data)
            temp_db.add_activity_log(log)

        # Test filtering by activity type
        coding_logs = temp_db.get_activity_logs({"activityType": "coding"})
        assert len(coding_logs) == 1
        assert coding_logs[0]["activityId"] == "test-1"

    def test_add_and_get_reminders(self, temp_db):
        """Test adding and retrieving reminders"""
        from chronos_protocol.server import Reminder

        reminder = Reminder(
            reminderId="reminder-123",
            reminderTime=(datetime.now(ZoneInfo('UTC')) + timedelta(hours=1)).isoformat(),
            message="Test reminder",
            relatedTaskId="task-123",
            status="pending",
            createdTime=datetime.now(ZoneInfo('UTC')).isoformat()
        )

        # Add reminder
        temp_db.add_reminder(reminder)

        # Get reminders
        reminders = temp_db.get_reminders(120)  # 2 hours
        assert len(reminders) == 1
        assert reminders[0]["reminderId"] == "reminder-123"


class TestTimeServer:
    """Test TimeServer core functionality"""

    @pytest.fixture
    def time_server(self):
        """Create a TimeServer instance for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Database(temp_dir)
            # Ensure the database file exists
            if not os.path.exists(db.db_file):
                db.save_data()  # Create the file
            server = TimeServer(database=db, id_format="short")
            return server

    def test_get_current_time(self, time_server):
        """Test getting current time in different timezones"""
        # Test UTC timezone
        result = time_server.get_current_time("UTC")
        assert "timezone" in result.model_dump()
        assert result.timezone == "UTC"
        assert "datetime" in result.model_dump()

        # Test system timezone
        result = time_server.get_current_time("system")
        assert isinstance(result, type(time_server.get_current_time("UTC")))

    def test_convert_time(self, time_server):
        """Test time conversion between timezones"""
        result = time_server.convert_time("UTC", "14:30", "America/New_York")

        assert "source" in result.model_dump()
        assert "target" in result.model_dump()
        assert "time_difference" in result.model_dump()
        assert result.source.timezone == "UTC"
        assert result.target.timezone == "America/New_York"

    def test_start_activity_log(self, time_server):
        """Test starting a new activity log"""
        log = time_server.start_activity_log(
            "testing",
            TaskScope.FEATURE_IMPLEMENTATION,
            "Test activity",
            ["test", "unit"]
        )

        assert isinstance(log, ActivityLog)
        assert log.activityType == "testing"
        assert log.task_scope == TaskScope.FEATURE_IMPLEMENTATION
        assert log.description == "Test activity"
        assert log.tags == ["test", "unit"]
        assert log.status == "started"
        assert log.activityId is not None

    def test_end_activity_log(self, time_server):
        """Test ending an activity log"""
        # Start a log first
        log = time_server.start_activity_log(
            "testing",
            TaskScope.FEATURE_IMPLEMENTATION,
            "Test activity"
        )

        # End the log
        ended_log = time_server.end_activity_log(
            log.activityId,
            "Completed successfully",
            "All tests passed"
        )

        assert ended_log.status == "completed"
        assert ended_log.result == "Completed successfully"
        assert ended_log.notes == "All tests passed"
        assert ended_log.endTime is not None
        assert ended_log.duration is not None

    def test_get_elapsed_time(self, time_server):
        """Test getting elapsed time for an activity"""
        # Start a log
        log = time_server.start_activity_log(
            "testing",
            TaskScope.FEATURE_IMPLEMENTATION
        )

        # Get elapsed time
        elapsed = time_server.get_elapsed_time(log.activityId)
        assert "activityId" in elapsed
        assert "elapsedTime" in elapsed
        assert "status" in elapsed

    def test_create_time_reminder(self, time_server):
        """Test creating a time reminder"""
        from chronos_protocol.server import Reminder

        future_time = (datetime.now(ZoneInfo('UTC')) + timedelta(hours=2)).isoformat()

        reminder = time_server.create_time_reminder(
            future_time,
            "Test reminder message",
            "task-123"
        )

        assert isinstance(reminder, Reminder)
        assert reminder.message == "Test reminder message"
        assert reminder.relatedTaskId == "task-123"
        assert reminder.status == "pending"

    def test_check_time_reminders(self, time_server):
        """Test checking for upcoming reminders"""
        # Create a reminder for soon
        soon_time = (datetime.now(ZoneInfo('UTC')) + timedelta(minutes=30)).isoformat()

        time_server.create_time_reminder(
            soon_time,
            "Upcoming reminder",
            "task-123"
        )

        # Check for reminders in next hour
        reminders = time_server.check_time_reminders(60)
        assert len(reminders) >= 1


class TestActivityLog:
    """Test ActivityLog model functionality"""

    def test_activity_log_creation(self):
        """Test creating an ActivityLog instance"""
        log = ActivityLog(
            activityId="test-123",
            activityType="coding",
            task_scope=TaskScope.FEATURE_IMPLEMENTATION,
            description="Test activity",
            tags=["test"],
            startTime=datetime.now(ZoneInfo('UTC')).isoformat(),
            status="started"
        )

        assert log.activityId == "test-123"
        assert log.activityType == "coding"
        assert log.task_scope == TaskScope.FEATURE_IMPLEMENTATION
        assert log.description == "Test activity"
        assert log.tags == ["test"]
        assert log.status == "started"


    def test_activity_log_model_dump(self):
        """Test model serialization includes activityId"""
        log = ActivityLog(
            activityId="test-123",
            activityType="coding",
            task_scope=TaskScope.FEATURE_IMPLEMENTATION,
            startTime=datetime.now(ZoneInfo('UTC')).isoformat(),
            status="started"
        )

        data = log.model_dump()
        assert "activityId" in data
        assert data["activityId"] == "test-123"
        assert "activityType" in data


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_invalid_timezone_get_current_time(self):
        """Test error handling for invalid timezone in get_current_time"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Database(temp_dir)
            if not os.path.exists(db.db_file):
                db.save_data()
            server = TimeServer(database=db, id_format="short")

            with pytest.raises(McpError):  # Should raise McpError for invalid timezone
                server.get_current_time("Invalid/Timezone")

    def test_invalid_time_convert_time(self):
        """Test error handling for invalid time in convert_time"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Database(temp_dir)
            if not os.path.exists(db.db_file):
                db.save_data()
            server = TimeServer(database=db, id_format="short")

            with pytest.raises(ValueError):  # Should raise ValueError from validation
                server.convert_time("UTC", "25:00", "America/New_York")

    def test_nonexistent_activity_id(self):
        """Test error handling for non-existent activity ID"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Database(temp_dir)
            if not os.path.exists(db.db_file):
                db.save_data()
            server = TimeServer(database=db, id_format="short")

            with pytest.raises(ValueError):
                server.end_activity_log("nonexistent-id", "result", "notes")

    def test_get_elapsed_time_nonexistent(self):
        """Test error handling for non-existent activity ID in get_elapsed_time"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Database(temp_dir)
            if not os.path.exists(db.db_file):
                db.save_data()
            server = TimeServer(database=db, id_format="short")

            with pytest.raises(ValueError):
                server.get_elapsed_time("nonexistent-id")


class TestIntegration:
    """Integration tests combining multiple components"""

    def test_full_activity_workflow(self):
        """Test complete activity workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Database(temp_dir)
            if not os.path.exists(db.db_file):
                db.save_data()
            server = TimeServer(database=db, id_format="short")

            # Start activity
            log = server.start_activity_log(
                "development",
                TaskScope.FEATURE_IMPLEMENTATION,
                "Complete feature",
                ["backend", "api"]
            )

            # Check it was created
            elapsed = server.get_elapsed_time(log.activityId)
            assert elapsed["status"] == "ongoing"

            # End activity
            ended_log = server.end_activity_log(
                log.activityId,
                "Feature completed",
                "All tests passing"
            )

            # Verify completion
            final_elapsed = server.get_elapsed_time(log.activityId)
            assert final_elapsed["status"] == "completed"

    def test_multiple_timezones_conversion(self):
        """Test time conversion across multiple timezone pairs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Database(temp_dir)
            if not os.path.exists(db.db_file):
                db.save_data()
            server = TimeServer(database=db, id_format="short")

            test_cases = [
                ("UTC", "14:30", "America/New_York"),
                ("Europe/London", "09:15", "Asia/Tokyo"),
                ("Australia/Sydney", "20:45", "UTC"),
            ]

            for source_tz, time_str, target_tz in test_cases:
                result = server.convert_time(source_tz, time_str, target_tz)
                assert result.source.timezone == source_tz
                assert result.target.timezone == target_tz


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])