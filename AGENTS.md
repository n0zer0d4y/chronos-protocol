_**Integration Note**: You may integrate these rules with your existing Cursor Rules. Customize the `*_TASK_LIST.md` filename pattern to match your project's naming convention._

---

# Activity Logging Protocol

**ALWAYS** use Chronos Protocol's activity logging system for all coding tasks:

1. **Start Every Task**: Call `start_activity_log` at the beginning of each coding task

   - Use appropriate `activityType` (debugging, feature-implementation, etc.)
   - Use matching `task_scope` from predefined options
   - Capture the returned `activityId`

2. **Track Task Progress**: Input `activityId` into your `task_list.md` ActivityId column immediately after starting

3. **Complete Tasks Religiously**: Call `end_activity_log` when finished

   - Include `result` and detailed `notes` for future reference
   - Update task status to "completed" in the active `*_TASK_LIST.md`
   - Record actual duration in ActualDuration column

4. **Monitor Ongoing Work**: Use `get_elapsed_time(activityId)` to check progress on long-running tasks

**Example Workflow:**

```python
# 1. Start activity and capture ID
activity_id = start_activity_log(
    activityType="debugging",
    task_scope="feature-implementation",
    description="Fix authentication module login flow"
)

# 2. Immediately update *_TASK_LIST.md with activityId
# 3. Work on the task...
# 4. Complete with results
end_activity_log(
    activity_id,
    result="Authentication module completed successfully"
)
```

**Critical**: Never skip activity logging. Every coding task must be tracked for traceability and performance analysis.
