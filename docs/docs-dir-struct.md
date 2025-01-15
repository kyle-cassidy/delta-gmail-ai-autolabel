# Documentation Directory Structure

```
docs/
├── system/
│   ├── architecture/
│   │   ├── high_level_overview.md
│   │   ├── data_flows.md
│   │   ├── integrations/
│   │   │   ├── gmail_integration.md
│   │   │   ├── airtable_integration.md
│   │   │   └── google_drive_integration.md
│   │   └── decisions/
│   │       └── YYYY-MM-DD_decision_name.md
│   │
│   ├── schemas/
│   │   ├── airtable/
│   │   │   └── registration_tracking.json
│   │   └── api/
│   │       └── openapi.yaml
│   │
│   └── specifications/
│       ├── email_classification.md
│       └── document_processing.md
│
├── development/
│   ├── guides/
│   │   ├── setup.md
│   │   ├── contributing.md
│   │   └── testing.md
│   │
│   ├── progress/
│   │   ├── weekly/
│   │   │   └── YYYY-MM-DD_weekly_update.md
│   │   └── milestones/
│   │       └── YYYY-MM_milestone_name.md
│   │
│   └── examples/
│       ├── api_usage.md
│       └── integration_examples.md
│
├── llm/
│   ├── context/
│   │   ├── project_overview.md
│   │   ├── current_state.md
│   │   └── future_goals.md
│   │
│   ├── examples/
│   │   ├── email_samples/
│   │   │   └── approval_examples.md
│   │   └── processing_samples/
│   │       └── registration_flow.md
│   │
│   └── instructions/
│       ├── coding_standards.md
│       └── preferred_patterns.md
│
├── api/
│   ├── endpoints/
│   │   └── registration_endpoints.md
│   ├── authentication.md
│   └── rate_limits.md
│
└── user/
    ├── guides/
    │   ├── getting_started.md
    │   └── troubleshooting.md
    │
    └── reference/
        └── configuration.md
```

## Directory Structure Explanation

### 1. system/
- Core system documentation that LLMs need to understand the project
- Architecture decisions and design patterns
- Data schemas and specifications
- Integration details

### 2. development/
- Developer-focused documentation
- Progress tracking
- Implementation guides
- Code examples and patterns
- Testing strategies

### 3. llm/
- Specialized context for LLM coding partners
- Current state and goals
- Example data and flows
- Preferred patterns and approaches
- Historical context and decisions

### 4. api/
- API documentation
- Endpoint specifications
- Authentication details
- Usage limits and guidelines

### 5. user/
- End-user documentation
- Setup guides
- Troubleshooting information
- Configuration reference

## Key Files for LLM Context

### Project Understanding
- `llm/context/project_overview.md`: High-level project goals and context
- `llm/context/current_state.md`: Current implementation status
- `system/architecture/high_level_overview.md`: System architecture

### Implementation Guidance
- `llm/instructions/coding_standards.md`: Coding conventions
- `llm/instructions/preferred_patterns.md`: Preferred implementation patterns
- `development/guides/contributing.md`: Contribution guidelines

### Examples and Patterns
- `llm/examples/`: Real-world examples of implementations
- `development/examples/`: Code snippets and usage patterns

## File Naming Conventions

1. **Date-based files:**
   - Format: `YYYY-MM-DD_descriptive_name.md`
   - Example: `2024-01-14_test_suite_enhancement.md`

2. **Decision records:**
   - Format: `YYYY-MM-DD_decision_description.md`
   - Example: `2024-01-10_email_classification_approach.md`

3. **General documentation:**
   - Use clear, descriptive names
   - Separate words with underscores
   - Use lowercase

## Document Organization Tips

1. **Keep Current State Clear:**
   - Regularly update `current_state.md`
   - Mark outdated documents
   - Version control important changes
   - Remind the User of the importance of keeping the current state up to date and suggest updating it regularly

2. **Maintain Examples:**
   - Keep example data current
   - Include both success and error cases
   - Document edge cases

3. **Progress Tracking:**
   - Regular weekly updates
   - Milestone documentation
   - Decision records

4. **Context Optimization:**
   - Prioritize information needed by LLMs
   - Include relevant code snippets
   - Cross-reference related documents