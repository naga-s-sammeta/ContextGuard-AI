# ContextGuard AI

# Day-Wise Jira Plan for Two-Resource Team

**Team model:** Two-resource delivery  
**Resource 1:** Data/AI Engineer  
**Resource 2:** Product/Frontend Engineer  
**Primary platform:** Snowflake-first POC  
**Estimated duration:** 30 working days / 6 weeks  
**Target outcome:** Usable Snowflake-first POC with governed natural-language analytics, automatic charts, basic admin governance, document intelligence, and evaluation dashboard.

---

## Working Assumptions

This plan assumes a realistic POC, not the final enterprise SaaS product. The two resources work in parallel, open feature branches, create pull requests, and review each other's work. Some days include research or setup work because Snowflake Cortex, semantic models, masking policies, and document intelligence require careful validation.

The plan is written in Jira-story style. Each item can become one Jira story or sub-task. Story IDs are suggested and can be adjusted in Jira.

Recommended sprint structure:

- Sprint 1: Days 1-5, project and Snowflake foundation.
- Sprint 2: Days 6-10, synthetic data and app shell.
- Sprint 3: Days 11-15, semantic model and Cortex Analyst integration.
- Sprint 4: Days 16-20, governance, privacy, and admin studio.
- Sprint 5: Days 21-25, document intelligence.
- Sprint 6: Days 26-30, evaluation, polish, and demo readiness.

---

## Sprint 1: Foundation and Environment Setup

### Day 1: Project Kickoff and Repository Setup

**Data/AI Engineer**

**JIRA-001: Define Snowflake POC environment plan**  
Create the Snowflake database, schema, warehouse, and role design on paper before implementation.

Acceptance criteria:

- Database name is finalized.
- Schema list is finalized.
- Role list is finalized.
- Warehouse size and auto-suspend policy are defined.

**Product/Frontend Engineer**

**JIRA-002: Create GitHub repository and project structure**  
Create the repository, initialize documentation folders, and define branch strategy.

Acceptance criteria:

- Repository exists.
- `main` and `develop` branch strategy is documented.
- `docs/` folder exists.
- Initial README exists.

---

### Day 2: Snowflake Free Trial and App Foundation

**Data/AI Engineer**

**JIRA-003: Create Snowflake trial account and base objects**  
Create the Snowflake account, database, schemas, warehouse, and resource monitor.

Acceptance criteria:

- Snowflake trial account is active.
- `CONTEXTGUARD_AI` database exists.
- Schemas exist: `RAW`, `CURATED`, `SEMANTIC`, `DOCS`, `APP`, `AUDIT`.
- XS warehouse is created with auto-suspend.
- Resource monitor is configured.

**Product/Frontend Engineer**

**JIRA-004: Scaffold Next.js application**  
Create the Next.js TypeScript app and prepare the base UI stack.

Acceptance criteria:

- Next.js app runs locally.
- TypeScript is configured.
- Tailwind CSS is configured.
- Basic app layout exists.

---

### Day 3: Roles, Permissions, and UI Navigation

**Data/AI Engineer**

**JIRA-005: Create Snowflake roles and initial grants**  
Create POC roles for admin, data steward, business user, and compliance user.

Acceptance criteria:

- Roles exist in Snowflake.
- Warehouse usage grants are assigned.
- Database/schema usage grants are assigned.
- Role design is documented.

**Product/Frontend Engineer**

**JIRA-006: Build initial navigation shell**  
Create the application shell with placeholder navigation for major product areas.

Acceptance criteria:

- Business Hub page route exists.
- Admin Studio page route exists.
- Documents page route exists.
- Evaluation page route exists.
- Settings page route exists.

---

### Day 4: Environment Configuration and SQL Folder Setup

**Data/AI Engineer**

**JIRA-007: Create Snowflake SQL script structure**  
Add organized SQL files for setup, raw tables, curated views, semantic layer, security, documents, and evaluation.

Acceptance criteria:

- `snowflake/00_setup` folder exists.
- `snowflake/01_raw_tables` folder exists.
- `snowflake/02_curated_views` folder exists.
- `snowflake/03_semantic` folder exists.
- `snowflake/04_security` folder exists.
- `snowflake/05_docs` folder exists.
- `snowflake/06_eval` folder exists.

**Product/Frontend Engineer**

**JIRA-008: Add environment variable template**  
Create `.env.example` and document required Snowflake/API variables.

Acceptance criteria:

- `.env.example` exists.
- Snowflake account, username, role, warehouse, database, schema variables are listed.
- No real secrets are committed.

---

### Day 5: Sprint 1 Review and Baseline Documentation

**Data/AI Engineer**

**JIRA-009: Document Snowflake foundation setup**  
Document current Snowflake account setup, roles, schemas, and credit-control settings.

Acceptance criteria:

- Snowflake setup notes are added to docs.
- Resource monitor details are included.
- Risks and open questions are listed.

**Product/Frontend Engineer**

**JIRA-010: Create first project demo screen**  
Create a basic home/dashboard screen that explains the POC modules without looking like a marketing landing page.

Acceptance criteria:

- App loads successfully.
- Navigation is usable.
- Placeholder pages are reachable.
- README includes local run instructions.

---

## Sprint 2: Synthetic Data and Dashboard Shell

### Day 6: Data Model Design and Dashboard Wireframe

**Data/AI Engineer**

**JIRA-011: Design synthetic enterprise data model**  
Design business tables for customers, orders, products, revenue, regions, and operational events.

Acceptance criteria:

- Entity list is documented.
- Table relationships are documented.
- Dirty data scenarios are listed.

**Product/Frontend Engineer**

**JIRA-012: Build Business Hub wireframe**  
Build the first Business Hub screen with question input, KPI area, chart area, and result area.

Acceptance criteria:

- Question input exists.
- KPI card area exists.
- Chart area exists.
- Result table area exists.

---

### Day 7: Synthetic Data Generation

**Data/AI Engineer**

**JIRA-013: Generate synthetic business data**  
Create synthetic data files for business entities.

Acceptance criteria:

- Customer data is generated.
- Product data is generated.
- Order/revenue data is generated.
- Region data is generated.
- Data is saved in a loadable format.

**Product/Frontend Engineer**

**JIRA-014: Create reusable dashboard components**  
Create reusable UI components for metric cards, result tables, and chart containers.

Acceptance criteria:

- Metric card component exists.
- Result table component exists.
- Chart panel component exists.
- Components work with mock data.

---

### Day 8: Dirty Data and Semi-Structured Data

**Data/AI Engineer**

**JIRA-015: Add dirty data and JSON event logs**  
Add nulls, duplicates, invalid dates, mixed currencies, inconsistent categories, and JSON operational logs.

Acceptance criteria:

- Dirty records are included.
- JSON event examples exist.
- Known data issues are documented.

**Product/Frontend Engineer**

**JIRA-016: Add persona switcher UI**  
Create persona selector for executive, sales, finance, operations, and compliance users.

Acceptance criteria:

- Persona selector exists.
- Persona changes update visible mock content.
- Persona state is represented in UI.

---

### Day 9: Load Data Into Snowflake

**Data/AI Engineer**

**JIRA-017: Load synthetic data into Snowflake RAW schema**  
Create raw tables and load generated datasets.

Acceptance criteria:

- Raw tables are created.
- CSV/JSON data is loaded.
- Row counts are validated.
- Load scripts are committed.

**Product/Frontend Engineer**

**JIRA-018: Build query history mock UI**  
Create a query history panel with mock questions, timestamps, personas, and status.

Acceptance criteria:

- Query history panel exists.
- Mock history records render correctly.
- Status badges exist.

---

### Day 10: Curated Views and Sprint 2 Review

**Data/AI Engineer**

**JIRA-019: Create curated business views**  
Create cleaned views that normalize common fields and exclude obvious bad records where appropriate.

Acceptance criteria:

- Curated views exist.
- Dirty data assumptions are documented.
- Basic validation queries pass.

**Product/Frontend Engineer**

**JIRA-020: Connect dashboard UI to mock API contract**  
Define the frontend data contract for question answers, SQL, chart type, sources, and confidence.

Acceptance criteria:

- Mock API response type is defined.
- UI renders based on contract.
- Loading and empty states exist.

---

## Sprint 3: Semantic Model and Cortex Analyst

### Day 11: Semantic Requirements

**Data/AI Engineer**

**JIRA-021: Define semantic entities, metrics, and dimensions**  
Create the first version of the semantic model requirements.

Acceptance criteria:

- Business entities are defined.
- Metrics are defined.
- Dimensions are defined.
- Synonyms are defined.

**Product/Frontend Engineer**

**JIRA-022: Create answer detail panel**  
Build UI to show SQL, sources, confidence, and explanation for an answer.

Acceptance criteria:

- SQL display exists.
- Sources display exists.
- Confidence display exists.
- Explanation area exists.

---

### Day 12: Cortex Analyst Setup

**Data/AI Engineer**

**JIRA-023: Configure Cortex Analyst semantic model**  
Create and test the initial semantic model for structured business questions.

Acceptance criteria:

- Semantic model exists.
- At least 10 test questions are defined.
- Cortex Analyst returns valid SQL for basic questions.

**Product/Frontend Engineer**

**JIRA-024: Build question submission API route**  
Create backend route placeholder for submitting natural-language questions.

Acceptance criteria:

- API route accepts question and persona.
- API route returns mock structured answer.
- Frontend uses the API route.

---

### Day 13: Snowflake API Integration

**Data/AI Engineer**

**JIRA-025: Document Cortex Analyst request/response behavior**  
Capture actual request and response examples from Cortex Analyst.

Acceptance criteria:

- Example request is documented.
- Example response is documented.
- Error cases are documented.

**Product/Frontend Engineer**

**JIRA-026: Connect API route to Snowflake service layer**  
Create a service abstraction for Snowflake/Cortex calls.

Acceptance criteria:

- Snowflake service module exists.
- Environment variables are used.
- Errors are handled safely.
- No secrets are exposed client-side.

---

### Day 14: Automatic Chart Detection

**Data/AI Engineer**

**JIRA-027: Define chart detection rules from query results**  
Define rules for KPI, table, line chart, bar chart, and pie chart.

Acceptance criteria:

- Time-series rule is defined.
- Categorical comparison rule is defined.
- Single-metric rule is defined.
- Fallback table rule is defined.

**Product/Frontend Engineer**

**JIRA-028: Implement automatic chart rendering**  
Render chart type based on result metadata or detected data shape.

Acceptance criteria:

- Line chart renders for time series.
- Bar chart renders for categorical comparison.
- KPI renders for single metric.
- Table renders as fallback.

---

### Day 15: Sprint 3 Integration Review

**Data/AI Engineer**

**JIRA-029: Test 25 structured questions**  
Run structured natural-language questions and document successes/failures.

Acceptance criteria:

- 25 questions are tested.
- SQL validity is recorded.
- Wrong or failed answers are categorized.

**Product/Frontend Engineer**

**JIRA-030: Polish structured question workflow**  
Improve loading, error, empty, success, and failed-query states.

Acceptance criteria:

- User sees clear loading state.
- Failed questions show useful message.
- Answer UI is stable.
- Demo questions are added.

---

## Sprint 4: Governance, Privacy, and Admin Studio

### Day 16: Sensitivity Model

**Data/AI Engineer**

**JIRA-031: Define PHI/PII sensitivity classification**  
Mark sensitive columns and define classification rules.

Acceptance criteria:

- PHI columns are listed.
- PII columns are listed.
- Confidential fields are listed.
- Classification logic is documented.

**Product/Frontend Engineer**

**JIRA-032: Build Admin Studio table catalog UI**  
Create table catalog page with table status and sensitivity summary.

Acceptance criteria:

- Table list renders.
- Status badges exist.
- Sensitivity summary exists.
- Search/filter UI exists.

---

### Day 17: Masking Policies

**Data/AI Engineer**

**JIRA-033: Implement Snowflake masking policies**  
Create masking policies for selected PHI/PII fields.

Acceptance criteria:

- Masking policies are created.
- Policies are applied to columns.
- Role-based masking behavior is tested.

**Product/Frontend Engineer**

**JIRA-034: Build column sensitivity UI**  
Show columns, data type, sensitivity label, and masking status.

Acceptance criteria:

- Column list renders.
- Sensitivity label is visible.
- Masking status is visible.
- Restricted fields are visually distinct.

---

### Day 18: Row Access Policies

**Data/AI Engineer**

**JIRA-035: Implement row access policies**  
Create role-based row filtering examples.

Acceptance criteria:

- Row access policy exists.
- Business user and compliance user see different results.
- Test queries are documented.

**Product/Frontend Engineer**

**JIRA-036: Build role simulator UI**  
Create a UI that shows how different personas see different access levels.

Acceptance criteria:

- Role selector exists.
- Access summary changes by role.
- Example restricted result is shown.

---

### Day 19: Audit Logging

**Data/AI Engineer**

**JIRA-037: Create query audit log model**  
Create tables or views for storing question, user role, SQL, status, and accessed resources.

Acceptance criteria:

- Audit table exists.
- Audit fields are documented.
- Sample audit rows are inserted.

**Product/Frontend Engineer**

**JIRA-038: Build audit log viewer**  
Create UI for viewing question/query audit events.

Acceptance criteria:

- Audit log table renders.
- Filters exist for persona, status, and sensitivity.
- Failed or blocked queries are visible.

---

### Day 20: Governance Sprint Review

**Data/AI Engineer**

**JIRA-039: Test safe refusal and restricted query behavior**  
Validate that unauthorized questions are blocked or masked appropriately.

Acceptance criteria:

- Restricted field question is tested.
- Unauthorized role behavior is tested.
- Safe refusal examples are documented.

**Product/Frontend Engineer**

**JIRA-040: Add governance status to answer UI**  
Show whether an answer used masked data, restricted data, or certified metrics.

Acceptance criteria:

- Governance status appears in answer panel.
- Masked/restricted/certified labels render.
- User-facing wording is clear.

---

## Sprint 5: Document Intelligence

### Day 21: Document Data Model

**Data/AI Engineer**

**JIRA-041: Design document ingestion model**  
Define document metadata, chunks, sensitivity labels, and source references.

Acceptance criteria:

- Document metadata fields are defined.
- Chunk model is defined.
- Citation/source model is defined.

**Product/Frontend Engineer**

**JIRA-042: Build document upload UI**  
Create upload screen for PDFs and document metadata.

Acceptance criteria:

- Upload UI exists.
- File metadata form exists.
- Upload state is represented.

---

### Day 22: Snowflake Stage Upload

**Data/AI Engineer**

**JIRA-043: Configure Snowflake Stage for documents**  
Create stage and test uploading sample files.

Acceptance criteria:

- Snowflake stage exists.
- Sample document is uploaded.
- Stage listing query works.

**Product/Frontend Engineer**

**JIRA-044: Connect upload UI to backend route**  
Create API route for document upload flow.

Acceptance criteria:

- Upload route exists.
- File validation exists.
- Upload errors are handled.

---

### Day 23: Extraction and Chunking

**Data/AI Engineer**

**JIRA-045: Extract and chunk document text**  
Use Snowflake AI functions or supporting parser to extract text and store chunks.

Acceptance criteria:

- Text extraction works for sample PDFs.
- Chunks are stored.
- Chunk metadata includes source document and page/reference.

**Product/Frontend Engineer**

**JIRA-046: Build document library UI**  
Show uploaded documents, status, type, sensitivity, and processing state.

Acceptance criteria:

- Document library renders.
- Processing status appears.
- Sensitivity label appears.

---

### Day 24: Cortex Search and Document Q&A

**Data/AI Engineer**

**JIRA-047: Configure Cortex Search over document chunks**  
Create search service and test semantic retrieval.

Acceptance criteria:

- Cortex Search service exists.
- Semantic search returns relevant chunks.
- Test queries are documented.

**Product/Frontend Engineer**

**JIRA-048: Build document search and Q&A UI**  
Create search input, answer panel, and citation display.

Acceptance criteria:

- Semantic search UI exists.
- Q&A panel exists.
- Citations render with document references.

---

### Day 25: Document Intelligence Review

**Data/AI Engineer**

**JIRA-049: Test document Q&A with 10 questions**  
Run document questions and record answer quality.

Acceptance criteria:

- 10 document questions are tested.
- Citations are validated.
- Failure cases are documented.

**Product/Frontend Engineer**

**JIRA-050: Polish document workflows**  
Improve upload, library, search, and Q&A states.

Acceptance criteria:

- Upload flow is clear.
- Empty states exist.
- Error states exist.
- Q&A citations are easy to inspect.

---

## Sprint 6: Evaluation, Polish, and Demo

### Day 26: Evaluation Dataset

**Data/AI Engineer**

**JIRA-051: Create verified question dataset**  
Create initial evaluation set for structured and document questions.

Acceptance criteria:

- 50 structured questions exist.
- 10 document questions exist.
- Expected SQL/result pattern is defined where possible.

**Product/Frontend Engineer**

**JIRA-052: Build evaluation dashboard shell**  
Create evaluation page for accuracy, pass/fail, and failure categories.

Acceptance criteria:

- Evaluation page exists.
- Summary cards exist.
- Results table exists.

---

### Day 27: Evaluation Execution

**Data/AI Engineer**

**JIRA-053: Implement evaluation runner**  
Create script or manual process to run verified questions and capture results.

Acceptance criteria:

- Evaluation runner exists.
- Results are stored.
- SQL validity is recorded.
- Failure reason is recorded.

**Product/Frontend Engineer**

**JIRA-054: Connect evaluation dashboard to results data**  
Display evaluation results from stored data or mock-to-real transition.

Acceptance criteria:

- Pass/fail counts render.
- Failure categories render.
- Question-level detail is visible.

---

### Day 28: Demo Data and UX Polish

**Data/AI Engineer**

**JIRA-055: Prepare final demo questions and datasets**  
Select stable demo questions for business, governance, and document flows.

Acceptance criteria:

- 10 business demo questions are selected.
- 5 governance demo questions are selected.
- 5 document demo questions are selected.
- All demo questions are tested.

**Product/Frontend Engineer**

**JIRA-056: Polish UI for demo readiness**  
Improve layout, spacing, labels, empty states, and responsive behavior.

Acceptance criteria:

- Main pages look demo-ready.
- Text does not overflow.
- Charts render correctly.
- Navigation is consistent.

---

### Day 29: Documentation and Presentation

**Data/AI Engineer**

**JIRA-057: Document Snowflake architecture and governance**  
Write final notes for Snowflake setup, semantic model, security policies, and credit controls.

Acceptance criteria:

- Snowflake architecture is documented.
- Governance behavior is documented.
- Credit-saving practices are documented.

**Product/Frontend Engineer**

**JIRA-058: Finalize README and demo script**  
Write project overview, setup instructions, feature list, and demo walkthrough.

Acceptance criteria:

- README is complete.
- Demo script is complete.
- Screenshots are added if available.

---

### Day 30: Final Review and Release

**Data/AI Engineer**

**JIRA-059: Run final end-to-end validation**  
Validate Snowflake queries, security behavior, document Q&A, and evaluation flow.

Acceptance criteria:

- Structured question flow works.
- Security demo works.
- Document Q&A works.
- Evaluation results are visible.

**Product/Frontend Engineer**

**JIRA-060: Prepare final POC release**  
Merge stable work, tag release, and prepare final project presentation.

Acceptance criteria:

- Final branch is merged.
- Release tag is created.
- Known limitations are documented.
- Final demo path is ready.

---

## Suggested Ownership Summary

| Area | Data/AI Engineer | Product/Frontend Engineer |
|---|---|---|
| Snowflake setup | Primary | Support |
| Synthetic data | Primary | Support for display needs |
| Semantic model | Primary | Support for UX labels |
| Cortex Analyst | Primary | API/UI integration |
| Business Hub | Support | Primary |
| Admin Studio | Data model support | Primary |
| Security policies | Primary | UI visibility |
| Document intelligence | Primary backend/data | Primary UI |
| Evaluation | Primary test logic | Primary dashboard |
| Documentation | Shared | Shared |

---

## Recommended Jira Labels

Use labels to keep the Jira board organized:

- `snowflake`
- `frontend`
- `backend`
- `semantic-layer`
- `security`
- `documents`
- `evaluation`
- `data-quality`
- `demo`
- `documentation`

---

## Recommended Definition of Done

A story is done only when:

- Code or SQL is committed.
- No secrets are committed.
- The work is tested locally or in Snowflake.
- The PR description explains the change.
- The other resource reviews or comments.
- Documentation is updated when relevant.
- Known limitations are listed if the story is incomplete by design.

