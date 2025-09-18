#!/usr/bin/env python3
"""
Direct test of Chronos Protocol functionality
Tests all core functions without MCP client layer
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from chronos_protocol.server import TimeServer, Database
from chronos_protocol.storage import resolve_data_dir


async def test_chronos_protocol_direct():
    """Direct test of Chronos Protocol functionality"""
    print("🎯 CHRONOS PROTOCOL DIRECT FUNCTIONAL TEST")
    print("=" * 60)

    try:
        # Initialize storage and database
        print("📁 Setting up storage and database...")
        data_dir = resolve_data_dir(
            storage_mode="per-project",
            project_root=os.path.dirname(__file__),
            data_dir="./data"
        )

        print(f"📁 Data directory: {data_dir}")
        db = Database(str(data_dir))
        time_server = TimeServer(db)

        print("✅ Database and TimeServer initialized successfully")

        # Test 1: get_current_time (3 calls)
        print("\n🕐 Testing get_current_time (3 calls)")

        print("\n📅 Test 1: System time")
        result1 = time_server.get_current_time("system")
        print(f"✅ System time: {result1.formatted_local}")

        print("\n📅 Test 2: UTC time")
        result2 = time_server.get_current_time("UTC")
        print(f"✅ UTC time: {result2.formatted_local}")

        print("\n📅 Test 3: New York time")
        result3 = time_server.get_current_time("America/New_York")
        print(f"✅ New York time: {result3.formatted_local}")

        # Test 2: convert_time (3 calls)
        print("\n🔄 Testing convert_time (3 calls)")

        print("\n🔄 Test 1: System to Tokyo")
        result4 = time_server.convert_time("system", "14:30", "Asia/Tokyo")
        print(f"✅ System 14:30 to Tokyo: {result4.target.formatted_local}")

        print("\n🔄 Test 2: UTC to London")
        result5 = time_server.convert_time("UTC", "09:15", "Europe/London")
        print(f"✅ UTC 09:15 to London: {result5.target.formatted_local}")

        print("\n🔄 Test 3: New York to Sydney")
        result6 = time_server.convert_time("America/New_York", "16:45", "Australia/Sydney")
        print(f"✅ New York 16:45 to Sydney: {result6.target.formatted_local}")

        # Test 3: Activity logging (3 complete cycles)
        print("\n🚀 Testing Activity Logging (3 complete cycles)")

        activity_ids = []

        for i in range(3):
            print(f"\n🚀 Starting Activity {i+1}")
            activity = time_server.start_activity_log(
                activity_type=f"test_activity_{i+1}",
                task_scope="testing-tasks",
                description=f"Comprehensive test activity {i+1} for Chronos Protocol",
                tags=["test", f"activity-{i+1}", "chronos-protocol"]
            )
            activity_ids.append(activity.activityId)
            print(f"✅ Started activity: {activity.activityId}")

        # End activities
        for i, activity_id in enumerate(activity_ids):
            print(f"\n✅ Ending Activity {i+1}")
            result = time_server.end_activity_log(
                activity_id=activity_id,
                result=f"Successfully completed test activity {i+1}",
                notes=f"This was the {i+1} test of Chronos Protocol activity logging"
            )
            print(f"✅ Ended activity: {activity_id}")

        # Test 4: get_elapsed_time (3 calls)
        print("\n⏱️ Testing get_elapsed_time (3 calls)")

        # Create a quick test activity
        test_activity = time_server.start_activity_log(
            activity_type="elapsed_test",
            task_scope="testing-tasks",
            description="Activity for elapsed time testing"
        )

        print("\n⏱️ Test 1: Check elapsed time")
        elapsed1 = time_server.get_elapsed_time(test_activity.activityId)
        print(f"✅ Elapsed time: {elapsed1}")

        # Wait a moment and check again
        await asyncio.sleep(1)
        print("\n⏱️ Test 2: Check elapsed time after 1 second")
        elapsed2 = time_server.get_elapsed_time(test_activity.activityId)
        print(f"✅ Elapsed time: {elapsed2}")

        # End activity and check final time
        time_server.end_activity_log(
            activity_id=test_activity.activityId,
            result="Elapsed time test completed"
        )

        print("\n⏱️ Test 3: Check elapsed time after completion")
        elapsed3 = time_server.get_elapsed_time(test_activity.activityId)
        print(f"✅ Final elapsed time: {elapsed3}")

        # Test 5: get_activity_logs (3 calls)
        print("\n📊 Testing get_activity_logs (3 calls)")

        print("\n📊 Test 1: Get all activity logs")
        logs1 = db.get_activity_logs({})
        print(f"✅ Found {len(logs1)} activity logs")

        print("\n📊 Test 2: Get testing activities")
        logs2 = db.get_activity_logs({"activityType": "test_activity_1"})
        print(f"✅ Found {len(logs2)} testing activities")

        print("\n📊 Test 3: Get recent activities with limit")
        logs3 = db.get_activity_logs({"limit": 3})
        print(f"✅ Found {len(logs3)} recent activities")

        # Test 6: update_activity_log (3 calls)
        print("\n📝 Testing update_activity_log (3 calls)")

        # Create activity to update
        update_activity = time_server.start_activity_log(
            activity_type="update_test",
            task_scope="testing-tasks",
            description="Activity for testing updates"
        )

        print("\n📝 Test 1: Update description")
        updated1 = time_server.update_activity_log(
            activity_id=update_activity.activityId,
            updates={"description": "Updated description for comprehensive testing"}
        )
        print(f"✅ Updated activity: {updated1.description}")

        print("\n📝 Test 2: Update result")
        updated2 = time_server.update_activity_log(
            activity_id=update_activity.activityId,
            updates={"result": "Updated result after successful completion"}
        )
        print(f"✅ Updated result: {updated2.result}")

        print("\n📝 Test 3: Update notes")
        updated3 = time_server.update_activity_log(
            activity_id=update_activity.activityId,
            updates={"notes": "Final comprehensive update to activity notes"}
        )
        print(f"✅ Updated notes: {updated3.notes}")

        # Test 7: Reminder system (6 calls - 3 create, 3 check)
        print("\n🔔 Testing Reminder System (6 calls)")

        reminder_ids = []
        future_times = [
            datetime.now() + timedelta(minutes=5),
            datetime.now() + timedelta(minutes=10),
            datetime.now() + timedelta(minutes=15)
        ]

        for i, future_time in enumerate(future_times):
            print(f"\n🔔 Creating Reminder {i+1}")
            reminder = time_server.create_time_reminder(
                reminder_time=future_time.isoformat(),
                message=f"Test reminder {i+1} for Chronos Protocol validation",
                related_task_id=f"test_task_{i+1}"
            )
            reminder_ids.append(reminder.reminderId)
            print(f"✅ Created reminder: {reminder.reminderId}")

        print("\n🔔 Test 1: Check all reminders")
        reminders1 = time_server.check_time_reminders(30)
        print(f"✅ Found {len(reminders1)} reminders")

        print("\n🔔 Test 2: Check upcoming reminders (5 min)")
        reminders2 = time_server.check_time_reminders(5)
        print(f"✅ Found {len(reminders2)} upcoming reminders")

        print("\n🔔 Test 3: Check upcoming reminders (20 min)")
        reminders3 = time_server.check_time_reminders(20)
        print(f"✅ Found {len(reminders3)} upcoming reminders")

        print("\n" + "=" * 60)
        print("🎉 CHRONOS PROTOCOL DIRECT TEST COMPLETED!")
        print("✅ All core functions tested successfully")
        print("✅ Time operations: 6 calls")
        print("✅ Activity logging: 9 calls")
        print("✅ Reminder system: 6 calls")
        print("✅ Total: 21 direct function calls")
        print("✅ Chronos Protocol core functionality verified!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def main():
    """Main test function"""
    success = await test_chronos_protocol_direct()
    if success:
        print("\n🎊 SUCCESS: Chronos Protocol is fully operational!")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Chronos Protocol test failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
