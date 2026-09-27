# Review Intelligence Platform — Product Requirements Document

**Document:** Product Requirements Document (PRD)
**Product:** Review Intelligence Platform
**Repository:** binesheb/google-review-autoreply
**Authoritative branch:** main
**Version:** 1.0
**Status:** Product baseline / active development
**Last updated:** 2026-09-27

---

## 1. Product Summary

Review Intelligence Platform is a self-hosted, local-first platform for organisations that receive customer reviews and need a controlled system to monitor, understand, draft, review, approve, modify, publish and learn from responses.

The platform is generic. No company name, location, credential, policy, brand voice or customer-specific fact may be hard-coded into the core product.

The first major integration target is Google Business Profile reviews. The architecture must support additional review and messaging sources without redesigning the core review workflow.

The product combines:

- review ingestion and historical import;
- review reconciliation;
- classification and risk detection;
- verified organisation knowledge retrieval;
- local AI response generation;
- deterministic safety controls;
- human approval;
- editing and regeneration;
- controlled publishing;
- complaint and case management;
- audit history;
- analytics;
- controlled learning datasets;
- administration and deployment management.

---

## 2. Vision

Build a trustworthy review operations platform in which:

> AI proposes. Evidence informs. Rules protect. Humans control. The system remembers.

A new organisation should be able to deploy the platform on supported Linux infrastructure with one primary installation command, configure its business, connect a review source, import historical reviews, test AI responses, and progressively enable automation.

This is a review intelligence and response operations system, not merely an auto-responder.

---

## 3. Product Principles

1. **Generic core** — no customer-specific business logic or credentials in source code.
2. **Installer-first** — fresh supported Linux deployment without manually installing Python, PostgreSQL, Qdrant or the AI runtime.
3. **Configuration separation** — infrastructure configuration belongs to installation; business behaviour belongs in the application.
4. **Local-first AI** — local inference is the initial deployment model; AI providers are replaceable.
5. **Knowledge is not model training** — business facts normally change through the knowledge layer, not model retraining.
6. **AI drafts; rules govern publishing** — deterministic controls remain outside the model.
7. **Fail closed** — critical safety or infrastructure uncertainty stops automatic publishing.
8. **Human control** — approve, deny, edit, regenerate, hold, escalate, publish and global pause are first-class actions.
9. **Audit everything important** — preserve review, drafts, edits, decisions and publication history.
10. **Upgrade-safe** — schema changes use migrations and persistent data survives application upgrades.

---

## 4. Target Users

### Platform Administrator
Installation, infrastructure, authentication, integrations, backup and security.

### Organisation Administrator
Organisation, locations, policies, AI instructions, knowledge and automation.

### Review Operator
Review queue, response editing, approval, denial, regeneration and escalation.

### Reviewer / Approver
Final approval for configured categories or risk levels.

### Manager
Escalations, complaints, sensitive reviews and workflow oversight.

### Analyst
Review trends, topics, sentiment and operational reporting.

---

## 5. Core Journey

~~~text
Review Source
    ↓
Ingestion + Reconciliation
    ↓
Review Ledger
    ↓
Classification + Risk
    ↓
Verified Knowledge Retrieval
    ↓
Local AI Draft
    ↓
Deterministic Safety Gate
    ↓
Workflow Policy
    ↓
Approval OR Controlled Auto-Publish
    ↓
Publication + Verification
    ↓
Audit + Analytics + Learning Candidate
~~~

---

## 6. Review Lifecycle

Recommended states:

- NEW
- SYNCED
- CLASSIFIED
- DRAFTING
- DRAFT_READY
- SAFETY_REVIEW
- PENDING_APPROVAL
- EDITED
- REGENERATION_REQUESTED
- REGENERATED
- APPROVED
- DENIED
- HELD
- ESCALATED
- PUBLISHING
- PUBLISHED
- PUBLISH_FAILED
- CLOSED
- PAUSED

Every transition must be validated. UI actions must not silently bypass workflow rules.

---

## 7. Review Ingestion

### Sources

Version 1 priority:

- Google Business Profile reviews.

Future source abstraction:

- other review platforms;
- messaging channels;
- social platforms;
- web forms;
- internal complaint systems.

### Historical Import

The platform must support importing existing reviews with:

- pagination;
- source identifiers;
- timestamps;
- deduplication;
- import status;
- retries;
- safe default of no automatic publishing.

### Continuous Synchronization

Scheduled synchronization must:

- fetch new reviews;
- detect updated reviews;
- reconcile external state;
- record last successful sync;
- expose errors;
- retry transient failures.

---

## 8. Review Data

Where available, retain:

- source;
- external review ID;
- organisation;
- location;
- reviewer display name;
- rating;
- review text;
- language;
- source creation/update timestamps;
- ingestion timestamp;
- classification;
- sentiment;
- topics;
- risk;
- workflow state;
- current draft;
- published reply;
- escalation/case references;
- audit references.

Original source content must be immutable in history.

---

## 9. AI Response Generation

The model receives controlled context:

1. system instructions;
2. organisation instructions;
3. location context;
4. review text;
5. verified retrieved knowledge;
6. applicable response policy;
7. response constraints;
8. regeneration instructions, when supplied.

AI output is always a draft until workflow authorization allows publication.

---

## 10. Response Operations

Operators must be able to:

- approve;
- deny;
- edit;
- regenerate;
- regenerate with custom instructions;
- hold;
- resume;
- escalate;
- publish where authorized;
- assign;
- compare versions.

### Regeneration

Regeneration may use quick controls such as:

- shorter;
- warmer;
- more professional;
- more empathetic;
- more concise;
- address complaint;
- remove promotion;
- focus on appreciation.

It must also support free-text instructions.

Every regeneration creates a new version and preserves previous versions.

### Tone

Configurable styles may include:

- professional;
- warm;
- concise;
- empathetic;
- premium;
- apologetic;
- neutral;
- organisation-defined.

### Length

Organisation policy may specify:

- minimum;
- maximum;
- preferred length;
- sentence limits.

---

## 11. Response Versioning

Every generated or edited response is a version.

Example:

~~~text
Review
 ├── Draft 1 — AI
 ├── Draft 2 — AI regeneration
 ├── Draft 3 — regeneration with instruction
 ├── Draft 4 — human edit
 └── Draft 5 — final approved
~~~

A response version records, where applicable:

- version;
- source type;
- actor;
- model;
- model parameters;
- instruction version;
- knowledge references;
- safety result;
- timestamp;
- superseded status.

Previous drafts must never be silently overwritten.

---

## 12. Approval Workflow

Actions:

- Approve;
- Deny;
- Edit;
- Regenerate;
- Regenerate with instruction;
- Hold;
- Escalate;
- Publish;
- Cancel.

Policies may depend on:

- rating;
- sentiment;
- risk;
- topic;
- complaint category;
- location;
- user role;
- AI confidence;
- unsupported claims;
- sensitive subjects.

Example policy:

~~~text
Low-risk positive review
→ may be eligible for auto-publish

Very low rating
→ human approval

Legal allegation
→ escalation

Safety issue
→ escalation

Unsupported factual claim
→ approval required
~~~

These are configurable examples, not hard-coded business policy.

---

## 13. Denial and Hold

When denied:

- no publication;
- denial reason captured;
- draft preserved;
- review remains actionable;
- regeneration/editing remains available;
- escalation may be created.

When held:

- reason captured;
- review appears in a dedicated queue;
- no automatic publication;
- resume requires an authorized action.

---

## 14. Escalation and Case Management

A review may create an internal case.

Case categories include:

- complaint;
- refund request;
- service issue;
- staff issue;
- product issue;
- safety issue;
- legal concern;
- fraud allegation;
- privacy concern;
- operational issue;
- other.

Cases support:

- owner;
- department/team;
- priority;
- status;
- notes;
- internal comments;
- attachments where supported;
- due date;
- resolution;
- related review;
- audit history.

Internal case information must never leak into a public response.

---

## 15. Safety Engine

Deterministic checks should detect/prevent:

- unsupported promises;
- fabricated facts;
- fabricated compensation;
- invented policies;
- confidential information;
- personal data;
- internal employee information;
- unsafe advice;
- legal conclusions;
- medical claims;
- discriminatory content;
- abusive responses;
- threats;
- accidental disclosure;
- prohibited promotional claims.

Safety result:

- PASS;
- WARN;
- BLOCK;
- ESCALATE.

BLOCK and required ESCALATE prevent normal automatic publishing.

---

## 16. Knowledge Base

The knowledge base stores verified business information such as:

- organisation information;
- location details;
- hours;
- services;
- parking;
- returns/exchanges;
- delivery;
- contact information;
- policies;
- FAQs;
- approved response guidance;
- escalation instructions.

Each item supports, where applicable:

- title;
- content;
- organisation;
- location scope;
- category;
- source;
- effective/expiry dates;
- version;
- status;
- author;
- verification state.

---

## 17. RAG / Semantic Retrieval

The retrieval pipeline is:

~~~text
Document
 ↓
Chunk
 ↓
Embedding
 ↓
Vector Store
 ↓
Similarity Search
 ↓
Relevant Context
 ↓
Prompt
 ↓
AI
~~~

Initial vector store: Qdrant.

The embedding provider must be replaceable.

Requirements:

- organisation isolation;
- location filtering;
- version references;
- stale vector cleanup;
- re-indexing;
- retrieval diagnostics.

If vector retrieval is unavailable, the platform may use a safe fallback where appropriate, but must not invent missing knowledge.

---

## 18. AI Provider Abstraction

The application must not depend directly on one model vendor.

Provider interface should support:

- generation;
- embeddings;
- health checks;
- model metadata;
- parameters;
- timeouts;
- retries;
- structured errors.

Initial local provider: Ollama.

Future providers may include other local runtimes, hosted APIs and organisation-specific inference servers.

---

## 19. AI Configuration

Administrators may configure:

- response model;
- embedding model;
- temperature;
- output limits;
- context limits where supported;
- timeout;
- retry policy;
- default tone;
- default language;
- system instructions.

AI configuration changes must be audited.

---

## 20. Master Instructions

The organisation instruction set defines:

- brand voice;
- prohibited claims;
- greetings/closings;
- language policy;
- escalation rules;
- response length;
- customer-care guidance;
- factual constraints.

Instruction sets are versioned and responses must reference the version used.

---

## 21. Controlled Learning

Learning candidates may come from:

- human edits;
- rejected drafts;
- regenerated drafts;
- approval patterns;
- corrected facts;
- recurring complaints;
- operator feedback.

The production model must not silently retrain itself.

Learning flow:

~~~text
Human Feedback
 ↓
Learning Candidate
 ↓
Review
 ↓
Approved Knowledge / Rule / Dataset
 ↓
Benchmark
 ↓
Optional Model Update
~~~

---

## 22. Golden Benchmark

Maintain representative benchmark cases containing:

- review;
- expected response characteristics;
- prohibited content;
- required factual context;
- risk level;
- approved reference response;
- scoring criteria.

Major changes to model, instructions, knowledge or safety rules should be benchmarked before automation expansion.

---

## 23. Shadow Mode

Shadow mode generates and evaluates responses without publishing them.

It is required before broad automatic publishing.

---

## 24. Automation Controls

Configurable controls:

- global pause;
- organisation pause;
- location pause;
- source pause;
- schedule;
- daily publishing limit;
- rating thresholds;
- risk thresholds;
- approval requirements;
- retry limits;
- failure behaviour.

Emergency global stop is mandatory.

Recommended progression:

~~~text
Install
 ↓
Configure
 ↓
Historical Dry Run
 ↓
Golden Benchmark
 ↓
Shadow Mode
 ↓
Human Approval
 ↓
Limited Automation
 ↓
Expanded Automation
~~~

---

## 25. Publishing

Publishing is separate from generation.

Before publishing:

1. authenticate;
2. verify current review state;
3. verify response version;
4. run safety;
5. evaluate workflow policy;
6. publish;
7. record external result;
8. verify where possible;
9. record retry/error information.

Stale drafts must not overwrite newer versions without explicit authorization.

---

## 26. Publishing Failure

On failure:

- preserve approved response;
- record error;
- classify retryable/non-retryable;
- retry according to policy;
- notify when required;
- prevent duplicate publication.

Use idempotency or equivalent safeguards where supported by the external source.

---

## 27. Dashboard

### Overview

Show:

- pending reviews;
- approvals;
- escalations;
- failed publishing;
- synchronization health;
- AI health;
- automation state;
- recent activity.

### Review Queue

Filters:

- location;
- rating;
- sentiment;
- risk;
- topic;
- workflow state;
- age;
- source;
- assignee;
- case status.

### Review Detail

Show:

- original review;
- metadata;
- classification;
- risk;
- retrieved knowledge;
- current response;
- response history;
- safety result;
- audit trail;
- case information.

Actions:

- approve;
- edit;
- regenerate;
- regenerate with instruction;
- deny;
- hold;
- escalate;
- publish where permitted.

---

## 28. Bulk Operations

Where permissions allow:

- bulk approve;
- bulk deny;
- bulk hold;
- bulk assign;
- bulk regenerate;
- bulk export.

Bulk publish requires explicit confirmation and still runs per-review safety/workflow rules.

---

## 29. Search

Search should support:

- review text;
- reviewer name where available;
- external review ID;
- response text;
- case ID;
- knowledge items;
- audit events.

Semantic review search may be added later.

---

## 30. Notifications

Potential channels:

- in-app;
- email;
- webhook;
- future messaging integrations.

Events:

- high-risk review;
- escalation;
- publishing failure;
- Google authentication failure;
- AI failure;
- database health issue;
- backup failure;
- automation pause;
- overdue approval.

---

## 31. Analytics

Provide:

- review volume;
- rating distribution/trend;
- response rate;
- response time;
- approval rate;
- rejection rate;
- regeneration rate;
- human edit rate;
- auto-publish rate;
- publishing failure rate;
- topic trends;
- sentiment trends;
- location comparisons;
- complaint categories;
- unresolved cases.

Clearly distinguish source facts from AI-derived classifications.

---

## 32. Multi-Location

Each location may have:

- source account/profile;
- address;
- timezone;
- hours;
- policies;
- instructions;
- knowledge scope;
- automation policy;
- users;
- escalation rules.

Organisation defaults may be overridden at location level.

---

## 33. Multi-Tenant Readiness

The architecture must be organisation-aware even when each installation initially serves one organisation.

All organisation-owned records must be scoped by organisation.

Cross-organisation access must be impossible through normal application paths.

Future SaaS multi-tenancy is optional and not required for the first self-hosted release.

---

## 34. Authentication and Authorization

Minimum:

- secure password hashing;
- signed expiring sessions;
- HTTP-only cookies;
- CSRF protection where applicable;
- secure secret handling;
- logout;
- password change;
- session invalidation.

Roles:

- Platform Admin;
- Organisation Admin;
- Manager;
- Reviewer;
- Operator;
- Analyst;
- Read Only.

Future:

- 2FA;
- SSO;
- OIDC;
- LDAP/enterprise identity.

High-risk actions require appropriate permissions.

---

## 35. Audit Log

Audit events include:

- login/logout;
- configuration changes;
- knowledge changes;
- instruction changes;
- AI setting changes;
- assignment;
- generation;
- regeneration;
- edit;
- approval;
- denial;
- escalation;
- publication;
- publication failure;
- automation changes;
- integration changes;
- user/role changes.

Audit records should include actor, action, object, timestamp, correlation ID and previous/new values where appropriate.

---

## 36. Data Protection

Apply data minimisation.

Sensitive data should not be unnecessarily copied into logs, prompts, analytics or telemetry.

Secrets must never be committed to GitHub.

Logs must redact credentials and tokens.

Backups must be protected.

---

## 37. Deployment

First-class targets:

- Ubuntu;
- Debian.

Required:

- one-command bootstrap;
- Docker Engine;
- Docker Compose;
- PostgreSQL;
- Qdrant;
- Ollama;
- persistent volumes;
- environment configuration;
- health checks;
- migrations;
- restart policy.

Installer must be idempotent.

Re-running it must not destroy customer data.

---

## 38. Installation-Time Configuration

May include:

- product name;
- administrator username/password;
- web port;
- timezone;
- installation directory;
- AI response model;
- embedding model;
- initial automation policy.

Advanced deployments must support non-interactive configuration.

Secrets must not be printed.

---

## 39. Runtime Business Configuration

Managed from the application:

- organisation;
- locations;
- review sources;
- AI instructions;
- knowledge;
- safety rules;
- approval policies;
- automation;
- notifications;
- integrations.

Infrastructure settings and business settings must remain separate.

---

## 40. Upgrade Strategy

An upgrade must:

1. identify application version;
2. verify configuration;
3. run migrations;
4. validate services;
5. start new version;
6. run health checks;
7. report status.

Rollback should be supported where practical.

Backups must be taken before destructive migrations.

---

## 41. Backup and Recovery

Support:

- PostgreSQL backup;
- Qdrant backup/export strategy;
- configuration backup;
- restore procedure;
- backup verification;
- retention policy.

Production deployments must periodically test restoration.

---

## 42. Observability

Expose:

- health endpoint;
- readiness endpoint;
- service status;
- application logs;
- audit logs;
- sync status;
- AI status;
- vector status;
- database status;
- job status.

Future monitoring may use Prometheus, Grafana and alerting.

---

## 43. Background Jobs

Long-running work should run outside request/response traffic.

Jobs include:

- review synchronization;
- historical import;
- classification;
- embedding;
- knowledge indexing;
- generation;
- publishing;
- retries;
- notifications;
- analytics aggregation;
- backups.

Job requirements:

- retry;
- timeout;
- idempotency;
- status;
- failure/dead-letter handling;
- observability.

---

## 44. API

Documented API areas:

- authentication;
- organisations;
- locations;
- reviews;
- response drafts;
- response actions;
- knowledge;
- instructions;
- cases;
- users;
- settings;
- integrations;
- health;
- analytics.

OpenAPI remains available in development.

---

## 45. Google Integration

Requirements:

- OAuth authorization;
- account discovery;
- location discovery;
- review listing;
- pagination;
- historical synchronization;
- reconciliation;
- owner reply publishing;
- token refresh;
- error handling;
- rate-limit handling;
- connection health.

Publishing must verify the target review/location state.

---

## 46. Internationalisation

Support:

- multiple languages;
- organisation language preference;
- location language preference;
- review language detection;
- multilingual knowledge.

Response language should follow configured policy and/or review language.

---

## 47. Accessibility

Dashboard should provide:

- keyboard navigation;
- readable contrast;
- semantic controls;
- screen-reader support;
- responsive layouts;
- clear status indicators.

---

## 48. Performance

Initial targets:

- normal local dashboard operations under 2 seconds;
- indexed review list queries under 1 second under normal workloads;
- AI generation time displayed and measured rather than assumed;
- background synchronization must not block interactive requests.

---

## 49. Reliability

The system should:

- restart after recoverable failures;
- retry transient external failures;
- preserve queued work;
- prevent duplicate publication;
- preserve audit events;
- expose service health.

---

## 50. Core Data Model

Core entities:

- Organisation;
- Location;
- User;
- Role;
- ReviewSource;
- Review;
- ReviewVersion;
- Classification;
- ResponseDraft;
- ResponseVersion;
- Approval;
- Publication;
- KnowledgeItem;
- KnowledgeVersion;
- InstructionSet;
- InstructionVersion;
- Case;
- Assignment;
- AuditLog;
- Notification;
- Integration;
- Job;
- SystemSetting;
- BenchmarkCase;
- LearningCandidate.

All schema changes use migration management.

---

## 51. Non-Goals for Initial Release

The initial release does not require:

- automatic model retraining;
- autonomous business decisions;
- fully autonomous complaint resolution;
- unrestricted internet-facing deployment;
- guaranteed cross-platform review support;
- managed SaaS billing;
- custom model training for every customer.

These may become future features.

---

## 52. Roadmap

### Phase 0 — Engineering Foundation

- generic repository;
- installer;
- Docker;
- PostgreSQL;
- Qdrant;
- Ollama;
- migrations;
- CI;
- baseline dashboard.

### Phase 1 — Review Operations

- ingestion;
- historical import;
- reconciliation;
- review queue;
- drafts;
- approval;
- denial;
- editing;
- regeneration;
- audit.

### Phase 2 — Knowledge Intelligence

- knowledge management;
- embeddings;
- RAG;
- organisation/location scoping;
- instruction versioning;
- benchmark.

### Phase 3 — Google Production Integration

- OAuth;
- location discovery;
- review sync;
- reply publishing;
- reconciliation;
- retries.

### Phase 4 — Enterprise Controls

- RBAC;
- 2FA;
- credential protection;
- backups;
- monitoring;
- TLS;
- reverse proxy.

### Phase 5 — Intelligence

- complaint analytics;
- topic trends;
- anomaly detection;
- response quality analytics;
- learning candidates.

### Phase 6 — Multi-Source Platform

- additional review platforms;
- messaging channels;
- CRM;
- webhooks;
- enterprise integrations.

### Phase 7 — Optional SaaS

- multi-tenant hosted mode;
- billing;
- tenant provisioning;
- central management.

---

## 53. Acceptance Criteria

A first controlled production release requires:

1. Clean supported Linux installation works using the documented one-command installer.
2. Required configuration can be collected securely.
3. Application starts and authenticates.
4. PostgreSQL persists through restart and upgrade.
5. Qdrant persists indexed knowledge.
6. Ollama persists required models.
7. Database migrations execute successfully.
8. Organisation can be configured without source changes.
9. Locations can be configured without source changes.
10. Historical reviews can be imported.
11. New reviews can be synchronized.
12. Local AI can generate a draft.
13. Knowledge can be retrieved and shown as context.
14. Safety checks run before publication.
15. Users can edit responses.
16. Users can regenerate responses.
17. Users can regenerate with custom instructions.
18. Response versions remain accessible.
19. Users can approve responses.
20. Users can deny responses.
21. Users can hold responses.
22. Users can escalate responses.
23. Approved responses can be published through the configured integration.
24. Publication failures are recorded and recoverable.
25. Critical workflow actions are audited.
26. Automation can be globally paused.
27. Dry-run and shadow modes work.
28. Automated tests pass.
29. CI passes.
30. Production Docker build passes.
31. Backup and restore are tested.
32. Required security controls are enabled.
33. Google authentication and publishing are verified in a controlled environment.

---

## 54. Definition of Done

A feature is complete only when:

~~~text
Requirement defined
 ↓
Implementation
 ↓
Tests
 ↓
UI/API verification
 ↓
Failure-path verification
 ↓
Security review
 ↓
Audit verification
 ↓
Documentation
 ↓
CI green
 ↓
Deployment impact checked
~~~

---

## 55. Success Metrics

Measure:

- synchronization success;
- review-to-draft time;
- review-to-response time;
- approval rate;
- edit rate;
- regeneration rate;
- denial rate;
- escalation rate;
- safety-block rate;
- auto-publish rate;
- publishing success rate;
- duplicate-publication rate;
- AI factual correction rate;
- human acceptance rate;
- knowledge retrieval success;
- automation failure rate.

Metrics inform operators and system improvement; they do not replace human judgment.

---

## 56. Architecture Decision Rule

For every significant feature, ask:

1. Is it generic?
2. Is it infrastructure, application configuration, business data or integration logic?
3. Does it require auditability?
4. Does it affect safety?
5. Does it require a migration?
6. Does it require a permission?
7. Does it require a background job?
8. What happens if its dependency fails?
9. How is it tested?
10. Can an organisation use it without source-code modification?

---

## 57. Product Positioning

**Full description:**

> Review Intelligence Platform is a self-hosted AI-powered review operations platform that helps organisations monitor customer reviews, retrieve verified business knowledge, generate controlled responses, route complaints, manage human approvals, publish safely and learn from operator feedback.

**Short description:**

> AI-powered review management with human control, verified knowledge and safe automation.

---

## 58. Jayalakshmi Deployment

Jayalakshmi Silks may be the first production deployment and can configure its organisation, locations, business instructions, brand voice, knowledge, escalation rules, Google Business Profiles, response policies and approval users.

These values must remain deployment configuration/data, not generic product source code.

---

## 59. Build-and-Learn Requirement

This project is also an engineering learning project.

For significant architecture decisions, documentation should explain:

- what the component is;
- why it is required;
- alternatives considered;
- why the selected approach was chosen;
- how it works;
- how it fails;
- how it is tested;
- how it is deployed.

The objective is both a working product and an understandable system that its owners can operate, extend and repair.

---

**End of PRD**
