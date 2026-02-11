# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

---

## Project-Specific Context: Todo Full-Stack Web Application

### Project Overview
**Phase II: Todo Full-Stack Web Application**

Transform a console application into a modern multi-user web application with persistent storage using the Agentic Dev Stack workflow.

**Objective:** Implement all 5 Basic Level features as a web application with RESTful API endpoints, responsive frontend interface, and persistent database storage.

**Development Approach:** Use Spec-Kit Plus workflow:
1. Write spec → 2. Generate plan → 3. Break into tasks → 4. Implement via Claude Code

**No manual coding allowed.** All development must be done through Claude Code agents.

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16+ (App Router) |
| Backend | Python FastAPI |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth |
| Spec-Driven Dev | Claude Code + Spec-Kit Plus |

### Agent Assignment Guidelines

**CRITICAL:** Use specialized agents for their respective domains. Do NOT attempt to implement features outside agent expertise.

#### 1. Authentication & Security → `auth-security-handler`
**Use this agent for:**
- User signup/signin implementation
- Better Auth integration and configuration
- JWT token generation and validation
- Password hashing and security
- Authentication middleware
- Session management
- Security vulnerability detection in auth code
- Password reset flows
- Email verification

**Example triggers:**
- "Implement user registration"
- "Add JWT authentication to API"
- "Review login security"
- "Set up Better Auth"

#### 2. Frontend Development → `nextjs-ui-builder`
**Use this agent for:**
- Next.js App Router pages and layouts
- UI components (forms, lists, modals)
- Responsive design with Tailwind CSS
- Client-side state management
- Form validation and error handling
- Loading states and suspense patterns
- Navigation and routing
- Server Components vs Client Components
- Image optimization

**Example triggers:**
- "Create todo list page"
- "Build signup form"
- "Add responsive navigation"
- "Implement todo item component"

#### 3. Database Design & Operations → `neon-db-manager`
**Use this agent for:**
- Database schema design
- SQLModel model definitions
- Database migrations
- Neon PostgreSQL configuration
- Query optimization
- Index strategies
- N+1 query detection
- Connection pooling setup
- Multi-tenant data isolation

**Example triggers:**
- "Design todo database schema"
- "Create user and todo models"
- "Optimize todo queries"
- "Set up Neon database"

#### 4. Backend API Development → `fastapi-backend-dev`
**Use this agent for:**
- FastAPI endpoint implementation
- Request/response validation with Pydantic
- API route organization
- CORS configuration
- Error handling and status codes
- Dependency injection
- Background tasks
- File uploads
- API documentation
- Middleware configuration

**Example triggers:**
- "Create todo CRUD endpoints"
- "Add API validation"
- "Implement error handling"
- "Set up CORS for Next.js"

### Authentication Flow (Better Auth + JWT)

**How It Works:**

1. **User Login (Frontend → Better Auth)**
   - User submits credentials on Next.js frontend
   - Better Auth validates credentials and creates session
   - Better Auth issues JWT token containing user information

2. **API Request (Frontend → Backend)**
   - Frontend makes API call to FastAPI backend
   - Includes JWT token in header: `Authorization: Bearer <token>`

3. **Token Verification (Backend)**
   - FastAPI receives request and extracts token from header
   - Backend verifies JWT signature using shared secret key
   - Backend decodes token to extract user ID, email, etc.

4. **Data Filtering (Backend)**
   - Backend matches decoded user ID with user ID in request URL/body
   - Backend filters database queries to return only data belonging to authenticated user
   - Returns user-specific todos only

**Security Requirements:**
- Never hardcode JWT secret keys (use `.env`)
- Validate token signature on every protected endpoint
- Match user ID from token with user ID in request
- Implement proper error handling for invalid/expired tokens
- Use HTTPS in production

### Development Workflow

**For every feature implementation:**

1. **Specification Phase** (`/sp.specify`)
   - Define feature requirements clearly
   - Include acceptance criteria
   - Specify API contracts and data models

2. **Planning Phase** (`/sp.plan`)
   - Use appropriate agent based on domain:
     - Auth features → `auth-security-handler`
     - Frontend features → `nextjs-ui-builder`
     - Database design → `neon-db-manager`
     - API endpoints → `fastapi-backend-dev`
   - Generate architectural plan
   - Identify dependencies and risks

3. **Task Breakdown** (`/sp.tasks`)
   - Break plan into testable tasks
   - Assign tasks to appropriate agents
   - Define acceptance criteria for each task

4. **Implementation** (`/sp.implement`)
   - Execute tasks using assigned agents
   - Follow TDD approach where applicable
   - Create PHRs for each implementation session

5. **Validation**
   - Test all endpoints
   - Verify authentication flow
   - Check database queries
   - Validate frontend functionality

### Multi-Agent Coordination

**When features span multiple domains:**

Example: "Implement user todo list feature"

1. **Database** (`neon-db-manager`): Design schema for users and todos
2. **Backend** (`fastapi-backend-dev`): Create CRUD API endpoints
3. **Auth** (`auth-security-handler`): Add JWT middleware to protect endpoints
4. **Frontend** (`nextjs-ui-builder`): Build todo list UI with API integration

**Coordination Strategy:**
- Start with database schema (foundation)
- Then backend API (business logic)
- Then authentication (security layer)
- Finally frontend (user interface)

### Project Constraints

**Must Follow:**
- All data must be user-scoped (no cross-user data leaks)
- All API endpoints must validate JWT tokens
- All database queries must filter by authenticated user ID
- All secrets must be in `.env` files
- All changes must be testable and reversible
- No manual coding - use Claude Code agents only

**Non-Goals:**
- Real-time collaboration features
- Mobile app development
- Advanced analytics or reporting
- Third-party integrations (beyond Better Auth)

### Success Criteria

**Technical:**
- RESTful API with proper HTTP methods and status codes
- Responsive frontend works on mobile and desktop
- Database properly normalized and indexed
- Authentication secure with JWT validation
- All endpoints protected and user-scoped

**Process:**
- All features developed through Spec-Kit Plus workflow
- PHRs created for all implementation sessions
- ADRs created for significant architectural decisions
- All code generated by Claude Code agents (no manual coding)

## Active Technologies
- Neon Serverless PostgreSQL (cloud-hosted, production-grade) (001-todo-fullstack-app)
- TypeScript/JavaScript with Next.js 16+ (App Router) + Next.js 16+, React 18+, Tailwind CSS (styling), Fetch API (HTTP client) (003-frontend-integration)
- N/A (frontend consumes backend API, no local data persistence beyond auth tokens) (003-frontend-integration)
- Python 3.11+ (backend), TypeScript (frontend) + FastAPI, OpenAI Agents SDK (`openai-agents`), SQLModel, Next.js 16+ (004-ai-agent-chat)
- Neon Serverless PostgreSQL (existing) — new tables: `conversations`, `messages` (004-ai-agent-chat)

## Recent Changes
- 001-todo-fullstack-app: Added Neon Serverless PostgreSQL (cloud-hosted, production-grade)
