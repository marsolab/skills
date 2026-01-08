# Changelog

All notable changes to the System Architect skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-01-08

### Changed

- Restructured for fast decision-making: Reduced main SKILL.md from 1,409 lines to ~530 lines
- Moved detailed content to `references/` folder for easier navigation and maintenance
- Organized content by topic for better discoverability

### Added

- **references/distributed-systems.md** - CAP theorem, distributed transactions, fault tolerance, database sharding, consensus protocols
- **references/data-architecture.md** - Database comparison, polyglot persistence, caching strategies, replication, backups
- **references/cloud-infrastructure.md** - Kubernetes production checklist, service mesh comparison, container optimization, cloud platforms
- **references/api-design.md** - REST/GraphQL/gRPC comparison, versioning strategies, API gateway patterns, authentication flows
- **references/observability.md** - OpenTelemetry implementation, GitOps principles, production readiness checklist
- **references/security.md** - Authentication patterns (OAuth, JWT), authorization models (RBAC, ABAC), secrets management
- **references/disaster-recovery.md** - RPO/RTO analysis, multi-region failover, backup testing, DR runbooks
- Enhanced quick reference table linking decision trees to detailed guides
- Scenario-based architecture template with example (fintech application)

## [2.0.0] - 2026-01-08

### Added

- Comprehensive architecture patterns section covering microservices, DDD, event-driven architecture
- Quick decision trees for architecture style, database selection, consistency models, cloud providers, API styles, and scaling strategies
- Distributed systems section with CAP theorem application, distributed transactions (saga vs 2PC), fault tolerance strategies, and database sharding
- Data architecture section with database comparison matrix, polyglot persistence patterns, caching strategies, and replication patterns
- Cloud and infrastructure section with Kubernetes production checklist, service mesh comparison (Istio vs Linkerd), and container optimization
- API architecture section comparing REST, GraphQL, and gRPC with versioning strategies and API gateway patterns
- CI/CD and observability section with GitOps principles, OpenTelemetry observability stack, and production readiness checklist
- Security architecture section with API authentication/authorization patterns and secrets management
- Disaster recovery section with RPO/RTO analysis, multi-region failover patterns, and backup strategies
- Reference library with essential books, online resources, and curated tool recommendations
- Scenario-based reasoning template for systematic architecture evaluation
- Progressive competency levels from Foundation to Mastery
- Architecture Decision Records (ADR) template for documenting decisions

### Changed

- Evolved from minimal placeholder to production-grade comprehensive skill
- Structured content following proven skill format patterns
- Added trade-off analysis for every major architectural decision
- Included source attribution from 179+ authoritative resources

## [1.0.0] - 2025-01-01

### Added

- Initial minimal skill structure
- Basic description and placeholder content
