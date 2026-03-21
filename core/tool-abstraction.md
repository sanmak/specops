## Tool Abstraction Layer

SpecOps requires a set of tool operations that vary by platform. This document defines abstract operations used throughout the workflow. Each platform adapter maps these to platform-specific tools or language.

### Required Operations

#### File Operations

- **READ_FILE(path)** → content: Read file at given path
- **WRITE_FILE(path, content)**: Create or overwrite file with content
- **EDIT_FILE(path, changes)**: Apply targeted edits to existing file
- **LIST_DIR(path)** → entries: List directory contents
- **FILE_EXISTS(path)** → boolean: Check if file exists

#### Shell Operations

- **RUN_COMMAND(command)** → output: Execute shell command
- **GET_SPECOPS_VERSION** → version_string: Extract the installed SpecOps version by running a deterministic command. Never guess or infer the version.

#### User Interaction

- **ASK_USER(question)** → response: Ask user for clarification
- **NOTIFY_USER(message)**: Display message to user

#### Progress Tracking

- **UPDATE_PROGRESS(task_id, status)**: Track task completion status

### Platform Capability Flags

Not all platforms support all operations. Use these flags to adapt behavior:

| Flag | Description |
| --- | --- |
| `canExecuteCode` | Can the platform run shell commands? |
| `canEditFiles` | Can the platform modify files directly? |
| `canCreateFiles` | Can the platform create new files? |
| `canAskInteractive` | Can the platform ask follow-up questions? |
| `canTrackProgress` | Does the platform have a built-in progress/todo system? |
| `canAccessGit` | Can the platform run git commands? |
| `canDelegateTask` | Can the platform spawn isolated fresh-context agents for task execution? |

### Capability-Based Behavior Adaptation

When a capability is unavailable:

- **canExecuteCode = false**: Suggest commands for the user to run manually instead of executing them
- **canEditFiles = false**: Present file changes as suggestions/diffs for the user to apply
- **canAskInteractive = false**: Note assumptions in the spec and proceed; list any ambiguities that the user should review
- **canTrackProgress = false**: Track progress in the response text or in `tasks.md` file updates
- **canDelegateTask = false**: Execute tasks sequentially in the current context. If `canAskInteractive` is true, write a checkpoint after each task and prompt the user to start a fresh session. If `canAskInteractive` is also false, use enhanced checkpointing with detailed Session Log entries.
