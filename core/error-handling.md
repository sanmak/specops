## Error Handling

If you encounter issues:
1. **Document the blocker** in `implementation.md`
2. **Update task status** to indicate the blocker
3. **Analyze alternatives** and document them
4. **Ask for guidance** if truly stuck
5. **Never silently skip tasks** - always communicate blockers

## Review Process

If `config.team.reviewRequired` is true:
1. Complete spec generation
2. Present spec to user for review
3. Wait for approval before implementing
4. Address feedback and iterate on spec
5. Only proceed to implementation after explicit approval

## Success Criteria

A successful SpecOps workflow completion means:
- All spec files are complete and well-structured
- All acceptance criteria are met
- All tasks are completed or documented as blocked
- Tests pass (or testing strategy followed)
- Code follows team conventions
- Implementation matches design (or deviations documented)
- User is informed of completion with clear summary

## Secure Error Handling

- Never expose internal file paths, stack traces, or system details in user-facing error messages
- Use generic messages for failures; log details internally
- Don't leak configuration values or secrets in error output
- Sanitize error context before including in spec files or commit messages

## Implementation Best Practices

1. **Read before writing**: Always read existing files before modifying
2. **Incremental changes**: Implement one task at a time
3. **Test as you go**: Run tests after each significant change
4. **Update tasks**: Mark tasks as completed in `tasks.md` as you finish them
5. **Document deviations**: If implementation differs from design, note it
6. **Maintain context**: Reference file:line_number for specific code locations
7. **Security first**: Never introduce vulnerabilities
8. **Keep it simple**: Follow the Simplicity Principle — implement the minimum needed to meet the spec
