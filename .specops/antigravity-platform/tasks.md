# Tasks: Add Google Antigravity as 5th Platform

## Task 1: Create platform adapter
- [x] Create `platforms/antigravity/platform.json`
- **Description:** Create the Antigravity platform adapter with `instructionFormat: "agents_rules"`, `installLocation.project: ".agents/rules/specops.md"`, `canDelegateTask: true`, generic natural language tool mappings, and `GET_SPECOPS_VERSION` that greps version from `.agents/rules/specops.md` HTML comment.
- **Domain:** backend
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** S
- **IssueID:** #184
- **Dependencies:** None
- **Acceptance Criteria:**
  - [x] `platform.json` is valid JSON with all required fields
  - [x] `canDelegateTask` is set to `true`
  - [x] `instructionFormat` is `"agents_rules"`
  - [x] `installLocation.project` is `".agents/rules/specops.md"`
- **Files to Modify:**
  - `platforms/antigravity/platform.json` (create)
- **Status:** Done

## Task 2: Create Jinja2 template
- [x] Create `generator/templates/antigravity.j2`
- **Description:** Create the Antigravity Jinja2 template based on `copilot.j2` structure (all 30+ module variables). No frontmatter in template -- generator prepends version comment. Include Antigravity-specific notes section mentioning Manager View for task delegation.
- **Domain:** backend
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** M
- **IssueID:** #185
- **Dependencies:** Task 1
- **Acceptance Criteria:**
  - [x] Template includes all module variables present in `copilot.j2`
  - [x] No YAML frontmatter section in the template
  - [x] Template renders successfully with the generator
- **Files to Modify:**
  - `generator/templates/antigravity.j2` (create)
- **Status:** Done

## Task 3: Integrate into generator
- [x] Modify `generator/generate.py`
- **Description:** Add `"antigravity"` to `SUPPORTED_PLATFORMS`. Add `generate_antigravity()` function that loads `antigravity.j2`, renders with module variables, substitutes tools, prepends `<!-- specops-version: "X.Y.Z" -->` as version marker (no YAML frontmatter), and writes to `platforms/antigravity/specops.md`. Add to `GENERATORS` dict.
- **Domain:** backend
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** M
- **IssueID:** #186
- **Dependencies:** Task 1, Task 2
- **Acceptance Criteria:**
  - [x] `antigravity` is in `SUPPORTED_PLATFORMS`
  - [x] `python3 generator/generate.py --platform antigravity` generates `platforms/antigravity/specops.md`
  - [x] `python3 generator/generate.py --all` generates all 5 platforms without error
  - [x] Generated output has HTML comment version marker, not YAML frontmatter
- **Files to Modify:**
  - `generator/generate.py`
- **Status:** Done

## Task 4: Run generator and verify output
- [x] Run `python3 generator/generate.py --all`
- **Description:** Run the generator to produce `platforms/antigravity/specops.md` and verify all 5 platform outputs are generated without error. Inspect the antigravity output to confirm no raw abstract operations remain.
- **Domain:** devops
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** S
- **IssueID:** #187
- **Dependencies:** Task 3
- **Acceptance Criteria:**
  - [x] All 5 platform outputs generated successfully
  - [x] `platforms/antigravity/specops.md` exists and is non-empty
  - [x] No raw abstract operations (READ_FILE, WRITE_FILE, etc.) in generated output
- **Files to Modify:**
  - `platforms/antigravity/specops.md` (generated)
- **Status:** Done

## Task 5: Integrate into validator
- [x] Modify `generator/validate.py`
- **Description:** Add `"antigravity": "specops.md"` to `platform_outputs` in `get_generated_files()`. Add `elif platform == "antigravity":` block in `validate_platform()` to validate version HTML comment is present instead of YAML frontmatter.
- **Domain:** backend
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** S
- **IssueID:** #188
- **Dependencies:** Task 4
- **Acceptance Criteria:**
  - [x] `python3 generator/validate.py` passes all checks including antigravity
  - [x] Antigravity-specific validation checks for HTML comment version marker
- **Files to Modify:**
  - `generator/validate.py`
- **Status:** Done

## Task 6: Run validator
- [x] Run `python3 generator/validate.py`
- **Description:** Run the validator to verify all 5 platforms pass 200+ checks including the new antigravity platform.
- **Domain:** devops
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** S
- **IssueID:** #189
- **Dependencies:** Task 5
- **Acceptance Criteria:**
  - [x] All validation checks pass for all 5 platforms
- **Files to Modify:** None
- **Status:** Done

## Task 7: Update test suite
- [x] Modify `tests/test_build.py` and `tests/test_platform_consistency.py`
- **Description:** Add `"antigravity": "specops.md"` to `EXPECTED_OUTPUTS` in `test_build.py` and to `PLATFORM_FILES` in `test_platform_consistency.py`.
- **Domain:** backend
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** S
- **IssueID:** #190
- **Dependencies:** Task 4
- **Acceptance Criteria:**
  - [x] `EXPECTED_OUTPUTS` includes `antigravity`
  - [x] `PLATFORM_FILES` includes `antigravity`
  - [x] All tests pass with `bash scripts/run-tests.sh`
- **Files to Modify:**
  - `tests/test_build.py`
  - `tests/test_platform_consistency.py`
- **Status:** Done

## Task 8: Run test suite
- [x] Run `bash scripts/run-tests.sh`
- **Description:** Run the full test suite to verify all tests pass with the antigravity platform included.
- **Domain:** devops
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** S
- **IssueID:** #191
- **Dependencies:** Task 7
- **Acceptance Criteria:**
  - [x] All tests pass
- **Files to Modify:** None
- **Status:** Done

## Task 9: Create install script and README
- [x] Create `platforms/antigravity/install.sh` and `platforms/antigravity/README.md`
- **Description:** Create the Antigravity install script modeled after `platforms/cursor/install.sh`, installing to `.agents/rules/specops.md`. Create platform README with install instructions, usage examples, and Antigravity-specific notes.
- **Domain:** devops
- **Ship Blocking:** Yes
- **Priority:** Medium
- **Effort:** M
- **IssueID:** #192
- **Dependencies:** Task 4
- **Acceptance Criteria:**
  - [x] `install.sh` installs to `.agents/rules/specops.md`
  - [x] `shellcheck platforms/antigravity/install.sh` passes with no errors
  - [x] `bash platforms/antigravity/install.sh /tmp/test-project` works correctly
  - [x] README includes install instructions and Antigravity-specific notes
- **Files to Modify:**
  - `platforms/antigravity/install.sh` (create)
  - `platforms/antigravity/README.md` (create)
- **Status:** Done

## Task 10: Update infrastructure scripts
- [x] Modify `setup.sh`, `scripts/remote-install.sh`, `scripts/bump-version.sh`, `verify.sh`, `hooks/pre-commit`
- **Description:** Add Antigravity detection to `setup.sh` (check for `antigravity` command or `/Applications/Antigravity.app`), add menu option. Add `antigravity` to valid platform cases in `remote-install.sh`. Add `platforms/antigravity/platform.json` to `FILES` array in `bump-version.sh`. Add antigravity template check, platform loop inclusion, and generated output check to `verify.sh`. Add `platforms/antigravity/specops.md` to `GENERATED_FILES` and `CHECKSUMMED_FILES` in `hooks/pre-commit`.
- **Domain:** devops
- **Ship Blocking:** Yes
- **Priority:** Medium
- **Effort:** L
- **IssueID:** #193
- **Dependencies:** Task 4, Task 9
- **Acceptance Criteria:**
  - [x] `setup.sh` detects Antigravity and shows it as an option
  - [x] `remote-install.sh` supports `antigravity` as a valid platform
  - [x] `bump-version.sh` updates version in antigravity `platform.json`
  - [x] `verify.sh` checks antigravity artifacts
  - [x] `hooks/pre-commit` includes antigravity files in generated and checksummed lists
- **Files to Modify:**
  - `setup.sh`
  - `scripts/remote-install.sh`
  - `scripts/bump-version.sh`
  - `verify.sh`
  - `hooks/pre-commit`
- **Status:** Done

## Task 11: Update CI workflow
- [x] Modify `.github/workflows/ci.yml`
- **Description:** Add `platforms/antigravity/platform.json` to JSON syntax check. Add `platforms/antigravity/install.sh` to ShellCheck list.
- **Domain:** devops
- **Ship Blocking:** Yes
- **Priority:** Medium
- **Effort:** S
- **IssueID:** #194
- **Dependencies:** Task 9
- **Acceptance Criteria:**
  - [x] CI workflow includes antigravity JSON syntax check
  - [x] CI workflow includes antigravity install.sh ShellCheck
- **Files to Modify:**
  - `.github/workflows/ci.yml`
- **Status:** Done

## Task 12: Update steering files
- [x] Modify `.specops/steering/structure.md` and `.specops/steering/product.md`
- **Description:** Update platform list references from "claude, cursor, codex, copilot" to include antigravity. Update "4 AI platforms" to "5 AI platforms".
- **Domain:** backend
- **Ship Blocking:** No
- **Priority:** Medium
- **Effort:** S
- **IssueID:** #195
- **Dependencies:** Task 4
- **Acceptance Criteria:**
  - [x] Structure steering file lists antigravity
  - [x] Product steering file references 5 platforms
- **Files to Modify:**
  - `.specops/steering/structure.md`
  - `.specops/steering/product.md`
- **Status:** Done

## Task 13: Update documentation
- [x] Modify `CLAUDE.md`, `README.md`, `QUICKSTART.md`, `docs/STRUCTURE.md`, `docs/COMPARISON.md`, `CONTRIBUTING.md`
- **Description:** Update "4 platforms" to "5 platforms" in CLAUDE.md. Add Antigravity to platform list and install examples in README.md. Add Antigravity install instructions to QUICKSTART.md. Add antigravity directory to tree in docs/STRUCTURE.md. Add Antigravity platform row to docs/COMPARISON.md if platform matrix exists. Update platform count in CONTRIBUTING.md if referenced.
- **Domain:** backend
- **Ship Blocking:** No
- **Priority:** Medium
- **Effort:** M
- **IssueID:** #196
- **Dependencies:** Task 4
- **Acceptance Criteria:**
  - [x] All documentation references updated platform count
  - [x] Antigravity appears in platform lists
  - [x] Install examples include Antigravity
- **Files to Modify:**
  - `CLAUDE.md`
  - `README.md`
  - `QUICKSTART.md`
  - `docs/STRUCTURE.md`
  - `docs/COMPARISON.md`
  - `CONTRIBUTING.md`
- **Status:** Done

## Task 14: Regenerate checksums
- [x] Regenerate `CHECKSUMS.sha256`
- **Description:** Add hashes for `platforms/antigravity/specops.md` and `platforms/antigravity/platform.json` to `CHECKSUMS.sha256`.
- **Domain:** devops
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** S
- **IssueID:** #197
- **Dependencies:** Task 4, Task 10
- **Acceptance Criteria:**
  - [x] `CHECKSUMS.sha256` includes antigravity files
  - [x] `shasum -a 256 -c CHECKSUMS.sha256` passes
- **Files to Modify:**
  - `CHECKSUMS.sha256`
- **Status:** Done

## Task 15: Final validation
- [x] Run full validation suite
- **Description:** Run `bash scripts/run-tests.sh && python3 generator/validate.py` to verify everything passes. Run `bash verify.sh` for structural integrity. Manually inspect `platforms/antigravity/specops.md` to confirm no raw abstract operations remain.
- **Domain:** devops
- **Ship Blocking:** Yes
- **Priority:** High
- **Effort:** S
- **IssueID:** #198
- **Dependencies:** Task 14
- **Acceptance Criteria:**
  - [x] All tests pass
  - [x] All validator checks pass
  - [x] `verify.sh` passes
  - [x] No raw abstract operations in antigravity output
- **Files to Modify:** None
- **Status:** Done
