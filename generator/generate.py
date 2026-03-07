#!/usr/bin/env python3
"""
SpecOps Platform Generator

Assembles platform-specific instruction files from core modules + platform adapters.
Generated files are checked into git so users never need to run this build step.

Usage:
    python3 generator/generate.py --all
    python3 generator/generate.py --platform claude
    python3 generator/generate.py --platform cursor
    python3 generator/generate.py --platform codex
    python3 generator/generate.py --platform copilot
"""

import argparse
import json
import os
import sys

# Root of the repository
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(ROOT_DIR, "core")
PLATFORMS_DIR = os.path.join(ROOT_DIR, "platforms")
TEMPLATES_DIR = os.path.join(ROOT_DIR, "generator", "templates")
EXAMPLES_DIR = os.path.join(ROOT_DIR, "examples")
SKILLS_DIR = os.path.join(ROOT_DIR, "skills")
PLUGIN_DIR = os.path.join(ROOT_DIR, ".claude-plugin")

SUPPORTED_PLATFORMS = ["claude", "cursor", "codex", "copilot"]


def read_file(path):
    """Read a file and return its contents."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    """Write content to a file, creating directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Generated: {os.path.relpath(path, ROOT_DIR)}")


def load_core_modules():
    """Load all core module files into a dictionary."""
    modules = {}

    # Load top-level core modules
    for filename in os.listdir(CORE_DIR):
        filepath = os.path.join(CORE_DIR, filename)
        if os.path.isfile(filepath) and filename.endswith(".md"):
            key = filename.replace(".md", "")
            modules[key] = read_file(filepath)

    # Load template files
    templates_dir = os.path.join(CORE_DIR, "templates")
    if os.path.isdir(templates_dir):
        modules["_templates"] = {}
        for filename in sorted(os.listdir(templates_dir)):
            filepath = os.path.join(templates_dir, filename)
            if os.path.isfile(filepath) and filename.endswith(".md"):
                key = filename.replace(".md", "")
                modules["_templates"][key] = read_file(filepath)

    return modules


def load_platform_config(platform_name):
    """Load a platform's configuration."""
    config_path = os.path.join(PLATFORMS_DIR, platform_name, "platform.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_template(platform_name):
    """Load a platform's Jinja2-style template."""
    template_path = os.path.join(TEMPLATES_DIR, f"{platform_name}.j2")
    return read_file(template_path)


def substitute_tools(content, tool_mapping):
    """Replace abstract tool operations with platform-specific language."""
    for abstract, concrete in tool_mapping.items():
        content = content.replace(abstract, concrete)
    return content


def render_templates_section(templates):
    """Render all spec templates into a single section."""
    sections = []

    template_order = [
        ("feature-requirements", "requirements.md (Feature)"),
        ("bugfix", "bugfix.md (Bug Fix)"),
        ("refactor", "refactor.md (Refactor)"),
        ("design", "design.md"),
        ("tasks", "tasks.md"),
        ("implementation", "implementation.md (Decision Journal)"),
        ("reviews", "reviews.md (Review Feedback)"),
    ]

    for key, title in template_order:
        if key in templates:
            sections.append(f"### {title}\n\n```markdown\n{templates[key].strip()}\n```")

    return "\n\n".join(sections)


def render_template(template_str, context):
    """Simple template rendering with {{ variable }} substitution."""
    result = template_str
    for key, value in context.items():
        placeholder = "{{ " + key + " }}"
        result = result.replace(placeholder, str(value))
        # Also handle without spaces
        placeholder_nospace = "{{" + key + "}}"
        result = result.replace(placeholder_nospace, str(value))
    return result


def build_example_invocations(platform_config):
    """Build example invocations section based on platform entry point."""
    entry = platform_config.get("entryPoint", {})
    entry_type = entry.get("type", "keyword")

    if entry_type == "slash_command":
        command = entry.get("command", "/specops")
        return f"""## Example Invocations

**Feature Request:**
User: "{command} Add OAuth authentication for GitHub and Google"

Your workflow:
1. Read `.specops.json` config
2. Explore existing auth system
3. Create `.specops/oauth-auth/` with full specs
4. Implement following tasks.md
5. Run tests
6. Report completion

**Bug Fix:**
User: "{command} Users getting 500 errors on checkout"

Your workflow:
1. Read config
2. Investigate error logs and checkout code
3. Create `.specops/bugfix-checkout-500/` with root cause analysis
4. Implement fix per design
5. Test thoroughly
6. Report completion

**Refactor:**
User: "{command} Refactor the API layer to use repository pattern"

Your workflow:
1. Read config
2. Analyze current API layer structure
3. Create `.specops/refactor-api-repository/` with refactoring rationale and migration plan
4. Implement incrementally, preserving external behavior
5. Run existing tests to verify no regressions
6. Report completion

**Infrastructure Feature:**
User: "{command} Set up Kubernetes auto-scaling for the API service"

Your workflow:
1. Read config, detect vertical as `infrastructure`
2. Analyze existing infrastructure files (Terraform, K8s manifests)
3. Create `.specops/infra-k8s-autoscaling/` with infrastructure-adapted specs
   - requirements.md uses "Infrastructure Requirements" instead of "User Stories"
   - design.md uses "Infrastructure Topology" and "Resource Definitions"
4. Implement following tasks.md
5. Validate with dry-run/plan
6. Report completion

**Interview Mode (Vague Idea):**
User: "{command} interview I want to build something for restaurants"

Your workflow:
1. Detect "interview" keyword or vague request
2. Enter interview mode: gather answers for 5 categories (Problem, Users, Features, Constraints, Done Criteria)
3. Ask follow-up clarifications when answers are vague
4. Show summary and confirm captured idea
5. Proceed to Phase 1 with enriched context
6. Create `.specops/restaurant-platform/` with full specs
7. Implement following tasks.md
8. Report completion

**Existing Spec:**
User: "{command} implement auth-feature"

Your workflow:
1. Read `.specops/auth-feature/` specs
2. Validate specs are complete
3. Execute tasks sequentially
4. Track progress
5. Report completion

**View Spec:**
User: "{command} view auth-feature"

Your workflow:
1. Read `.specops.json` config for specsDir
2. Read spec files from `.specops/auth-feature/`
3. Present a formatted summary view

**View Specific Section:**
User: "{command} view auth-feature design"

Your workflow:
1. Read `.specops.json` config for specsDir
2. Read `.specops/auth-feature/design.md`
3. Present the design section with metadata header

**List All Specs:**
User: "{command} list"

Your workflow:
1. Read `.specops.json` config for specsDir
2. Read `.specops/index.json` (or scan spec directories)
3. Present formatted spec overview table"""
    else:
        return """## Example Invocations

**Feature Request:**
User: "Use specops to add OAuth authentication for GitHub and Google"

Your workflow:
1. Read `.specops.json` config
2. Explore existing auth system
3. Create `.specops/oauth-auth/` with full specs
4. Implement following tasks.md
5. Run tests
6. Report completion

**Bug Fix:**
User: "Create a spec for fixing the 500 errors on checkout"

Your workflow:
1. Read config
2. Investigate error logs and checkout code
3. Create `.specops/bugfix-checkout-500/` with root cause analysis
4. Implement fix per design
5. Test thoroughly
6. Report completion

**Refactor:**
User: "Spec-driven refactor of the API layer to use repository pattern"

Your workflow:
1. Read config
2. Analyze current API layer structure
3. Create `.specops/refactor-api-repository/` with refactoring rationale and migration plan
4. Implement incrementally, preserving external behavior
5. Run existing tests to verify no regressions
6. Report completion

**Interview Mode (Vague Idea):**
User: "Use specops interview for this idea I have"

Your workflow:
1. Detect "interview" keyword or determine request is vague
2. Enter interview mode: gather answers for 5 categories (Problem, Users, Features, Constraints, Done Criteria)
3. Ask follow-up clarifications when answers are vague
4. Show summary and confirm captured idea
5. Proceed to Phase 1 with enriched context
6. Create spec directory with full specs
7. Implement following tasks.md
8. Report completion

**Existing Spec:**
User: "Implement the auth-feature spec"

Your workflow:
1. Read `.specops/auth-feature/` specs
2. Validate specs are complete
3. Execute tasks sequentially
4. Track progress
5. Report completion

**View Spec:**
User: "View the auth-feature spec"

Your workflow:
1. Read `.specops.json` config for specsDir
2. Read spec files from `.specops/auth-feature/`
3. Present a formatted summary view

**View Specific Section:**
User: "Show me the auth-feature design"

Your workflow:
1. Read `.specops.json` config for specsDir
2. Read `.specops/auth-feature/design.md`
3. Present the design section with metadata header

**List All Specs:**
User: "List all specops specs"

Your workflow:
1. Read `.specops.json` config for specsDir
2. Read `.specops/index.json` (or scan spec directories)
3. Present formatted spec overview table"""


def build_init_templates_section():
    """Build the init config templates section from example configs."""
    config_files = [
        (".specops.minimal.json", "Minimal"),
        (".specops.json", "Standard"),
        (".specops.full.json", "Full"),
        (".specops.review.json", "Review"),
        (".specops.builder.json", "Builder"),
    ]
    sections = []
    for filename, name in config_files:
        filepath = os.path.join(EXAMPLES_DIR, filename)
        content = read_file(filepath).strip()
        sections.append(f"#### Template: {name}\n\n```json\n{content}\n```")
    return "\n\n".join(sections)


def generate_claude(core, platform_config):
    """Generate Claude Code platform files."""
    template = load_template("claude")
    templates_section = render_templates_section(core["_templates"])
    examples = build_example_invocations(platform_config)

    # Build init content with injected config templates (Claude-only feature)
    init_content = core["init"].replace(
        "{{ init_templates }}", build_init_templates_section()
    )

    context = {
        "workflow": core["workflow"],
        "config_handling": core["config-handling"],
        "review_workflow": core["review-workflow"],
        "view": core["view"],
        "interview": core["interview"],
        "init": init_content,
        "safety": core["safety"],
        "simplicity": core["simplicity"],
        "data_handling": core["data-handling"],
        "verticals": core["verticals"],
        "custom_templates": core["custom-templates"],
        "error_handling": core["error-handling"],
        "task_tracking": core["task-tracking"],
        "templates_section": templates_section,
        "examples": examples,
    }

    output = render_template(template, context)
    output = substitute_tools(output, platform_config["toolMapping"])

    # Generate SKILL.md (Claude Code skill format: YAML frontmatter + prompt content)
    frontmatter = (
        '---\n'
        'name: specops\n'
        'description: "Spec-driven development workflow - transforms ideas into'
        ' structured specifications (requirements, design, tasks) before'
        ' implementation. Use when building features, fixing bugs, refactoring,'
        ' or designing systems."\n'
        'argument-hint: "[mode] [description]"\n'
        '---\n\n'
    )
    skill_md_path = os.path.join(PLATFORMS_DIR, "claude", "SKILL.md")
    skill_content = frontmatter + output
    write_file(skill_md_path, skill_content)

    # Sync legacy skills directory
    legacy_skill_path = os.path.join(SKILLS_DIR, "specops", "SKILL.md")
    write_file(legacy_skill_path, skill_content)



def generate_plugin_manifests():
    """Generate Claude Code plugin and marketplace manifests."""
    # Read version from claude platform.json (authoritative source)
    claude_config = load_platform_config("claude")
    version = claude_config.get("version", "1.0.0")

    print("\nGenerating: plugin manifests")

    # .claude-plugin/plugin.json
    plugin_json = {
        "name": "specops",
        "description": (
            "Spec-driven development workflow - transforms ideas into structured"
            " specifications (requirements, design, tasks) before implementation."
        ),
        "version": version,
        "author": {"name": "Sanket Makhija"},
        "repository": "https://github.com/sanmak/specops",
        "homepage": "https://github.com/sanmak/specops",
        "license": "MIT",
        "keywords": [
            "spec-driven",
            "specifications",
            "workflow",
            "requirements",
            "design",
            "tasks",
        ],
    }
    plugin_path = os.path.join(PLUGIN_DIR, "plugin.json")
    write_file(plugin_path, json.dumps(plugin_json, indent=2) + "\n")

    # .claude-plugin/marketplace.json
    marketplace_json = {
        "name": "specops-marketplace",
        "owner": {"name": "Sanket Makhija"},
        "metadata": {
            "description": (
                "SpecOps - spec-driven development workflow for AI coding assistants"
            ),
            "version": version,
        },
        "plugins": [
            {
                "name": "specops",
                "source": "./",
                "description": (
                    "Spec-driven development workflow with /specops command"
                    " (includes init, view, list, interview subcommands)."
                ),
                "version": version,
                "category": "development-workflows",
                "tags": ["spec-driven", "workflow", "planning"],
                "homepage": "https://github.com/sanmak/specops",
            }
        ],
    }
    marketplace_path = os.path.join(PLUGIN_DIR, "marketplace.json")
    write_file(marketplace_path, json.dumps(marketplace_json, indent=2) + "\n")


def generate_cursor(core, platform_config):
    """Generate Cursor platform files."""
    template = load_template("cursor")
    templates_section = render_templates_section(core["_templates"])
    examples = build_example_invocations(platform_config)

    context = {
        "workflow": core["workflow"],
        "config_handling": core["config-handling"],
        "review_workflow": core["review-workflow"],
        "view": core["view"],
        "interview": core["interview"],
        "safety": core["safety"],
        "simplicity": core["simplicity"],
        "data_handling": core["data-handling"],
        "verticals": core["verticals"],
        "custom_templates": core["custom-templates"],
        "error_handling": core["error-handling"],
        "task_tracking": core["task-tracking"],
        "templates_section": templates_section,
        "examples": examples,
    }

    output = render_template(template, context)
    output = substitute_tools(output, platform_config["toolMapping"])

    output_path = os.path.join(PLATFORMS_DIR, "cursor", "specops.mdc")
    write_file(output_path, output)


def generate_codex(core, platform_config):
    """Generate OpenAI Codex platform files."""
    template = load_template("codex")
    templates_section = render_templates_section(core["_templates"])
    examples = build_example_invocations(platform_config)

    context = {
        "workflow": core["workflow"],
        "config_handling": core["config-handling"],
        "review_workflow": core["review-workflow"],
        "view": core["view"],
        "interview": core["interview"],
        "safety": core["safety"],
        "simplicity": core["simplicity"],
        "data_handling": core["data-handling"],
        "verticals": core["verticals"],
        "custom_templates": core["custom-templates"],
        "error_handling": core["error-handling"],
        "task_tracking": core["task-tracking"],
        "templates_section": templates_section,
        "examples": examples,
    }

    output = render_template(template, context)
    output = substitute_tools(output, platform_config["toolMapping"])

    # Generate SKILL.md (Codex skill format: YAML frontmatter + prompt content)
    frontmatter = (
        '---\n'
        'name: specops\n'
        'description: "Spec-driven development workflow - transforms ideas into'
        ' structured specifications (requirements, design, tasks) before'
        ' implementation. Use when building features, fixing bugs, refactoring,'
        ' or designing systems."\n'
        '---\n\n'
    )
    skill_md_path = os.path.join(PLATFORMS_DIR, "codex", "SKILL.md")
    write_file(skill_md_path, frontmatter + output)


def generate_copilot(core, platform_config):
    """Generate GitHub Copilot platform files."""
    template = load_template("copilot")
    templates_section = render_templates_section(core["_templates"])
    examples = build_example_invocations(platform_config)

    context = {
        "workflow": core["workflow"],
        "config_handling": core["config-handling"],
        "review_workflow": core["review-workflow"],
        "view": core["view"],
        "interview": core["interview"],
        "safety": core["safety"],
        "simplicity": core["simplicity"],
        "data_handling": core["data-handling"],
        "verticals": core["verticals"],
        "custom_templates": core["custom-templates"],
        "error_handling": core["error-handling"],
        "task_tracking": core["task-tracking"],
        "templates_section": templates_section,
        "examples": examples,
    }

    output = render_template(template, context)
    output = substitute_tools(output, platform_config["toolMapping"])

    # Generate specops.instructions.md (Copilot scoped instructions: applyTo frontmatter)
    frontmatter = (
        '---\n'
        'applyTo: "**"\n'
        '---\n\n'
    )
    output_path = os.path.join(PLATFORMS_DIR, "copilot", "specops.instructions.md")
    write_file(output_path, frontmatter + output)


GENERATORS = {
    "claude": generate_claude,
    "cursor": generate_cursor,
    "codex": generate_codex,
    "copilot": generate_copilot,
}


def main():
    parser = argparse.ArgumentParser(description="Generate platform-specific SpecOps files")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Generate for all platforms")
    group.add_argument("--platform", choices=SUPPORTED_PLATFORMS, help="Generate for a specific platform")
    args = parser.parse_args()

    print("SpecOps Platform Generator")
    print("=" * 40)

    # Load core modules
    print("\nLoading core modules...")
    core = load_core_modules()
    print(f"  Loaded {len(core) - 1} modules + {len(core.get('_templates', {}))} templates")

    # Determine which platforms to generate
    platforms = SUPPORTED_PLATFORMS if args.all else [args.platform]

    for platform_name in platforms:
        print(f"\nGenerating: {platform_name}")
        platform_config = load_platform_config(platform_name)
        generator = GENERATORS[platform_name]
        generator(core, platform_config)

    # Generate plugin manifests (only when generating claude or all)
    if args.all or args.platform == "claude":
        generate_plugin_manifests()

    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
