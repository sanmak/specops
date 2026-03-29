## Dependency Introduction Gate

LLMs casually install packages during implementation without evaluating alternatives or checking project conventions. The dependency introduction gate ensures all new dependency decisions happen during spec creation (Phase 2) and that Phase 3 only installs what the spec approved. This complements the existing Dependency Safety module (CVE/EOL audit) by controlling *which* dependencies enter the project, not just whether existing ones are safe.

The gate is always active. There are no config knobs, no bypass, and no `enabled: false` switch. If a spec has no new dependencies, the gate passes trivially.

### Install Command Patterns

Detect install commands across supported ecosystems. These patterns are used in Phase 2 (scanning design.md) and Phase 3 (enforcement before execution).

| Ecosystem | Install Command Patterns | Lock File |
| --- | --- | --- |
| Node.js | `npm install`, `npm i`, `yarn add`, `pnpm add`, `npx` | `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` |
| Python | `pip install`, `pip3 install`, `poetry add`, `pipenv install`, `uv add` | `requirements.txt` / `Pipfile.lock` / `poetry.lock` |
| Rust | `cargo add`, `cargo install` | `Cargo.lock` |
| Ruby | `gem install`, `bundle add` | `Gemfile.lock` |
| Go | `go get`, `go install` | `go.sum` |
| PHP | `composer require` | `composer.lock` |
| Java/Kotlin | Maven/Gradle dependency additions (manual `pom.xml` or `build.gradle` edits) | `pom.xml` / `build.gradle` |

### Build-vs-Install Evaluation Framework

For each new dependency identified, evaluate against these 5 criteria before recommending approval or rejection:

| # | Criterion | Question | Approve Signal | Reject Signal |
| --- | --- | --- | --- | --- |
| 1 | Scope Match | Does the package solve the exact problem needed? | Package's primary purpose aligns with the requirement | Package is a large toolkit and only a small utility is needed |
| 2 | Maintenance Health | Is the package actively maintained? | Regular releases, responsive issues, active contributors | No releases in 12+ months, unresolved critical issues, single maintainer with no activity |
| 3 | Size Proportionality | Is the package size proportionate to the value it provides? | Small footprint relative to the functionality gained | Large dependency tree for a simple utility (e.g., full lodash for one function) |
| 4 | Security Surface | Does the package expand the project's attack surface? | Minimal transitive dependencies, no native bindings, no network access | Extensive transitive tree, native code compilation, ambient network access |
| 5 | License Compatibility | Is the package license compatible with the project? | MIT, Apache-2.0, BSD, or project-compatible license | GPL (if project is not GPL), SSPL, or unknown license |

**Evaluation output format** (presented to user via ASK_USER):

```text
Dependency Evaluation: <package-name>@<version> (<ecosystem>)

1. Scope Match:        [Good/Acceptable/Poor] - <brief reason>
2. Maintenance Health: [Good/Acceptable/Poor] - <metrics summary>
3. Size Proportionality: [Good/Acceptable/Poor] - <size/dep count>
4. Security Surface:   [Good/Acceptable/Poor] - <transitive dep count, native bindings>
5. License:            [Good/Acceptable/Poor] - <license name>

Recommendation: [Approve / Reject / Needs Discussion]
Rationale: <1-2 sentence summary>
```

### Maintenance Profile Intelligence

Assess dependency maintenance health using a 3-layer approach. Each layer compensates for the previous layer's failures.

**Layer 1 -- Registry APIs:**

Query the package registry for download statistics and publish activity:

- Node.js: RUN_COMMAND(`curl -s --max-time 10 "https://registry.npmjs.org/<package>"`) -- extract `time.modified`, version count, latest version date
- Python: RUN_COMMAND(`curl -s --max-time 10 "https://pypi.org/pypi/<package>/json"`) -- extract `info.version`, `releases` dates
- Other ecosystems: skip Layer 1, fall through to Layer 2

If the request times out or returns an error, NOTIFY_USER("Registry query failed for <package> -- falling through to source repo check.") and proceed to Layer 2.

**Layer 2 -- Source Repository APIs:**

Query the source repository for activity metrics:

- If the package metadata includes a repository URL pointing to GitHub: RUN_COMMAND(`curl -s --max-time 10 "https://api.github.com/repos/<owner>/<repo>"`) -- extract `stargazers_count`, `pushed_at`, `open_issues_count`
- If no repository URL or not on GitHub: skip to Layer 3

If the request times out or returns an error, NOTIFY_USER("Source repo query failed for <package> -- falling through to LLM assessment.") and proceed to Layer 3.

**Layer 3 -- LLM Knowledge Fallback:**

Use training data knowledge to assess the dependency:

- Assess known maintenance status, popularity, and common alternatives
- Every assessment from this layer MUST be annotated: "(based on training data -- may not reflect current status)"
- The gate still runs -- it never silently passes

### Phase 2 Gate Procedure (Step 5.8)

**Dependency Introduction Gate -- runs after code-grounded plan validation (step 5.7), before external issue creation (step 6).**

Procedure:

1. READ_FILE(`<specsDir>/<spec-name>/design.md`) and scan for:
   - Explicit install commands matching the Install Command Patterns table
   - Package names referenced in code examples, import statements, or dependency listings
   - References to external libraries, frameworks, or tools not already in the project

2. READ_FILE(`<specsDir>/steering/dependencies.md`) to get the Detected Dependencies list (auto-populated by the dependency safety gate).

3. Compare the packages found in design.md against the Detected Dependencies. Identify **net-new dependencies** -- packages that appear in design.md but are not in the Detected Dependencies list. If no net-new dependencies are found, the gate passes -- record "No new dependencies introduced" in design.md and proceed.

4. For each net-new dependency (maximum 10):
   a. Run Maintenance Profile Intelligence (3-layer assessment)
   b. Run Build-vs-Install Evaluation Framework (5 criteria)
   c. ASK_USER with the evaluation output, asking for approval or rejection:
      - "Approve: add <package> as an approved dependency for this spec"
      - "Reject: build the functionality in-house instead"

5. Record all decisions in design.md by adding or updating a `### Dependency Decisions` section:

   ```markdown
   ### Dependency Decisions

   | Package | Version | Ecosystem | Decision | Rationale |
   | ------- | ------- | --------- | -------- | --------- |
   | <name>  | <ver>   | <eco>     | Approved/Rejected | <evaluation summary> |
   ```

6. EDIT_FILE(`<specsDir>/<spec-name>/design.md`) to write the Dependency Decisions table.

7. Update the Dependency Introduction Policy in dependencies.md (see Auto-Intelligence Policy Generation).

### Phase 3 Spec Adherence Enforcement

**MANDATORY enforcement rule for Phase 3 implementation.** This runs as part of the implementation gates (Phase 3 step 1).

**Pre-install verification:**

WHEN the agent is about to execute any command matching the Install Command Patterns table (npm install, pip install, cargo add, etc.), the agent MUST:

1. READ_FILE(`<specsDir>/<spec-name>/design.md`) and locate the `### Dependency Decisions` section
2. Verify the target package appears in the Dependency Decisions table with `Decision: Approved`
3. If approved: proceed with the install command
4. If NOT approved (missing from table, or Decision is Rejected): this is a **protocol breach**. NOTIFY_USER("Protocol breach: attempting to install unapproved dependency '<package>'. This package is not listed in design.md ### Dependency Decisions. Options: (1) Add it to the spec by re-running the dependency introduction gate, (2) Remove the install and build the functionality in-house.") and HALT until the user resolves the situation.

**No Dependency Decisions section:** If design.md has no `### Dependency Decisions` section, any install command is a protocol breach -- the dependency introduction gate was skipped or the spec predates this feature. For backward compatibility with pre-existing specs (specs with `specopsCreatedWith` earlier than the version that introduced this gate): NOTIFY_USER with a warning but allow the install to proceed. For specs created with the current version or later: enforce as a protocol breach.

**Post-Phase-3 verification:**

After all tasks are completed but before Phase 3 exit:

1. READ_FILE(`<specsDir>/<spec-name>/design.md`) and extract all packages with `Decision: Approved` from the Dependency Decisions table
2. For each approved package, verify it was actually installed by checking the project's manifest or lock files
3. If an approved package was NOT installed: NOTIFY_USER("Warning: dependency '<package>' was approved in design.md but was not installed during implementation. This may indicate a phantom approval or a change in approach. Please confirm this is intentional.") -- this is a warning, not a blocking error

### Auto-Intelligence Policy Generation

The Dependency Introduction Policy accumulates governance intelligence in the `dependencies.md` steering file across spec runs.

**First-run creation:**

WHEN the dependency introduction gate runs and `dependencies.md` does not contain a `## Dependency Introduction Policy` section:

1. Detect the project's primary ecosystem from indicator files (same detection as Dependency Safety module)
2. Determine the default policy stance based on the project vertical:
   - `builder` or `library` vertical: **conservative** (prefer building over installing)
   - All other verticals: **moderate** (evaluate case-by-case)
3. EDIT_FILE(`<specsDir>/steering/dependencies.md`) to add:

```markdown
## Dependency Introduction Policy

**Default stance:** <conservative|moderate> (<vertical> vertical)
**Primary ecosystem:** <ecosystem> (detected from <indicator file>)

### Approved Patterns

[Accumulated from approved dependency decisions across specs]

### Rejected Patterns

[Accumulated from rejected dependencies with reasons]
```

**Decision pattern accumulation:**

WHEN a dependency decision is made (approved or rejected):

- For approved dependencies: EDIT_FILE to add an entry under `### Approved Patterns` with the package category and rationale (e.g., "HTTP server frameworks: approved when scope requires request handling")
- For rejected dependencies: EDIT_FILE to add an entry under `### Rejected Patterns` with the rejection reason (e.g., "Utility libraries for single functions: prefer native/built-in alternatives")

**Team-section preservation:**

The agent MUST preserve all existing sections in dependencies.md when updating. The Dependency Introduction Policy section is appended after the existing team-maintained sections. Existing content (Detected Dependencies, Runtime & Framework Status, Approved Versions, Banned Libraries, Migration Timelines, Known Accepted Risks) must not be modified by this gate.

### Platform Adaptation

All supported platforms have `canExecuteCode: true`, so the full registry API + curl workflow is available everywhere.

- **`canAskInteractive = true`**: Present Build-vs-Install evaluation and ask user for approval/rejection of each new dependency.
- **`canAskInteractive = false`**: Present the evaluation and default to the recommendation. Record the recommendation as the decision. NOTIFY_USER with the full evaluation output so the user can review.
- **`canTrackProgress = false`**: Report gate progress in text output rather than a progress tracker.
