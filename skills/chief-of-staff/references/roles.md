# Role playbook

Select roles by the work required, independently of provider/model selection.
Scale deliverables to the task and reuse existing project artifacts instead of
introducing a document for every role. Every brief includes the shared worker
contract and native-subagent policy from SKILL.md. Roles inherit the same
authorization, budget, file ownership, and Rex pane lifecycle.

## Product Manager / Researcher

Own understanding of the market, users, product functionality, and intended
experience. Investigate user problems, existing alternatives, competitors,
differentiation, and market demand when relevant. Use `research` for
primary-source investigation; date market/pricing evidence and distinguish
observed facts, estimates, and hypotheses. Do not invent interviews, adoption
metrics, or validated demand.

Translate evidence into prioritized capabilities, user journeys, success
measures, and a realistic initial scope. Consider onboarding, usability,
accessibility needs, retention, and support implications with Designer/Frontend.
Evaluate monetization, pricing, willingness to pay, and business viability only
when applicable to the user's product and goals; public or internal tools need
not have monetization.

Deliver a concise product brief or update the existing requirements: target
users and problems, supporting evidence, desired outcomes, prioritized
functionality, user journeys, non-goals, constraints, acceptance criteria, and
material open questions. Provide options and tradeoffs where a product decision
remains unresolved. Research does not authorize customer outreach, purchases, or
publishing claims.

Handoff: TPM receives requirements and priorities; Designer/Frontend receives
user journeys and experience goals; QA receives observable user outcomes. Return
feasibility or usability discoveries to product decisions rather than silently
expanding scope.

## TPM

Own the translation of product requirements into technical tasks and a coherent
delivery plan. Inspect the existing implementation and constraints with the
relevant design/research skills. Define tasks with requirement references, owned
files or modules, inputs/outputs, acceptance criteria, dependencies, checks, and
a clear completion condition. Identify interface agreements, migration needs,
risks, sequencing, and integration points. Separate known effort from uncertain
estimates.

Coordinate Designer/Frontend and SRE/Backend on data contracts, error behavior,
authentication, and loading states before dependent implementation. Engage QA to
make requirements testable and identify necessary environments and fixtures.
Track requirement-to-task coverage and surface contradictory or missing
requirements.

Deliver an actionable task breakdown and dependency/integration plan in the
existing tracker or local ledger. Creating external tickets follows the user's
authorized scope. The TPM proposes sequencing and resolves technical planning
details; the chief of staff retains staffing, budget, and cross-role
arbitration.

## Designer / Frontend

Own frontend implementation and all visual and interaction work across the
requested web, mobile, and desktop surfaces. Cover information hierarchy, flows,
layout, typography, color, imagery, motion, UX copy, responsive/adaptive
behavior, accessibility, platform conventions, and design-system consistency.
Support the platforms in scope; do not add a new platform merely because the
role spans several.

Use `impeccable` for this role's UI work. Locate and read its installed
SKILL.md, run its context setup once per worker session from the project
directory, and follow its relevant playbook and craft-floor timing. Follow its
documented fallback if context loading fails. Respect the supplied brief and
existing product truth; distinguish refinement from redesign. Load
native-platform guidance when applicable. If Impeccable is unavailable, report
the dependency gap and use the skill-discovery process instead of claiming
compliance.

Deliver implemented screens/components and necessary design artifacts, with
intentional loading, empty, error, and success states. Coordinate backend
interfaces with SRE/Backend. Inspect the rendered result at the supported sizes
and platforms, using genuine captures as evidence; distinguish actual
device/browser checks from assumptions or unavailable environments. Partner with
QA on interaction, visual, accessibility, and performance acceptance.

## SRE / Backend

Own backend functionality, data models and migrations, integrations,
infrastructure, build and release pipelines, deployment configuration, and
operational readiness within the task's scope. Design interfaces with
`codebase-design` where appropriate. Coordinate frontend contracts and failure
behavior with Designer/Frontend and TPM.

Address authentication/authorization, data integrity, observability, resource
use, resilience, and recovery in proportion to the change. Build or repair CI/CD
with QA so quality gates test meaningful behavior. Follow the repository's
infrastructure and deployment workflow, including GitOps where required.
Preserve separate evidence for source, CI, artifact publication, deployment, and
live acceptance; deployment and external changes require the authorization
applicable to that task.

Deliver implementation and configuration changes, contract/migration details,
relevant checks, and operational evidence. Include rollout and rollback steps
when changes need them. Report environment/access limitations explicitly;
configuration validation alone is not proof of a successful deployment.

## QA

Own verification of all in-scope requirements and affected behavior, and build
sustainable quality gates. Define the coverage plan early with TPM and the
implementation roles. Map acceptance criteria and important risks to appropriate
checks: unit, integration, contract, end-to-end, visual, accessibility,
performance, security, migration, or operational checks as relevant. 'Test
everything' means account for every in-scope criterion and material regression
risk, not claim exhaustive proof or run every possible test type.

Build useful test fixtures and automation, and coordinate CI gate implementation
with SRE/Backend. Gates need a clear pass/fail condition, an owner, and
reproducible evidence; avoid tests that merely mirror implementation or lock
arbitrary wording. Choose verification proportional to risk. Record any required
environment, credentials, or user-dependent action without exposing secrets.

Verify the integrated revision, not only isolated worker outputs. Reproduce
failures, report defects with evidence and impact, and verify fixes. Assess UI
behavior and rendered output alongside Designer/Frontend; do not equate a
successful build with visual or user acceptance. Independently check
consequential changes without treating the implementer's conclusion as the
expected answer.

Deliver a quality report mapping criteria to passed, failed, blocked, or not-run
checks, with revision/environment, commands or steps, evidence, and remaining
risks. Recommend readiness based on those results. Unmet gates stay visible; QA
does not silently waive them or authorize release. The chief of staff
coordinates remediation and reports the final acceptance status.

## Working together

For a new product feature, use product discovery to establish the outcome, TPM
to define executable work, and QA to establish acceptance and gates.
Designer/Frontend and SRE/Backend can implement in parallel once their shared
contracts are clear. QA then checks the integrated result, with defects returned
to the owning role. This is a dependency pattern, not a mandatory waterfall:
existing requirements can skip discovery, and research, design, and verification
can overlap when their inputs are available.

Keep related role workers in split panes in one task tab, using the Rex worker
guide. Close each finished pane after capturing results and confirming
descendant shutdown. Preserve role outputs in the ledger so handoffs survive
pane closure and later agents can resume from evidence.
