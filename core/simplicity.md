## Simplicity Principle

Prefer the simplest solution that meets the requirements. Complexity must be justified — never assumed.

### During Spec Generation (Phase 2)
- **Scale specs to the task**: A small feature doesn't need a full rollout plan, caching strategy, or future enhancements section. Only include design.md sections that are genuinely relevant.
- **Skip empty sections**: If a template section (e.g., "Security Considerations", "Data Model Changes", "Migration Strategy") doesn't apply, omit it entirely rather than filling it with boilerplate or "N/A".
- **Minimal task breakdown**: Break work into the fewest tasks needed. Don't create separate tasks for trivial steps that are naturally part of a larger task.
- **Avoid speculative requirements**: Don't add acceptance criteria, non-functional requirements, or design considerations that the user didn't ask for and the task doesn't demand.

### During Implementation (Phase 3)
- **No premature abstractions**: Don't introduce patterns, wrappers, base classes, or utility functions unless the current task requires them. Three similar lines of code are better than an unnecessary abstraction.
- **No speculative features**: Implement exactly what the spec requires. Don't add configuration options, feature flags, or extensibility points "for the future."
- **Use existing code**: Prefer using existing project utilities and patterns over creating new ones. Don't reinvent what's already available.
- **Minimal dependencies**: Don't introduce new libraries or frameworks when the standard library or existing project dependencies can do the job.

### Recognizing Over-Engineering
Watch for these patterns and actively avoid them:
- Creating abstractions used only once
- Adding error handling for scenarios that cannot occur
- Building configuration for values that won't change
- Designing for hypothetical future requirements not in the spec
- Adding layers of indirection that don't serve a current need
