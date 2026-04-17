# VTEX Agent Suite - Track Registry

This repository follows the official VTEX modular skill architecture. Use the following table to identify the specialized agent (Track) for your development task.

| Agent Name | Skill ID | Core Focus | Reference File |
| :--- | :--- | :--- | :--- |
| **VTEX Orchestrator** | `vtex-development` | Router & Strategic Design | [SKILL.md](SKILL.md) |
| **FastStore Expert** | `vtex-faststore` | Performance, Next.js, WebOps | [references/faststore.md](references/faststore.md) |
| **IO Developer** | `vtex-io` | Backend, React Blocks, GraphQL | [references/io-development.md](references/io-development.md) |
| **Store Framework** | `vtex-legacy` | Blocks, JSON, Site Editor | [references/store-framework.md](references/store-framework.md) |
| **API Integrator** | `vtex-apis` | Catalog, OMS, Master Data | [references/rest-apis.md](references/rest-apis.md) |
| **Marketplace Pro** | `vtex-marketplace` | Sellers, Sync, Commissions | [references/marketplace.md](references/marketplace.md) |
| **Payment Architect** | `vtex-payments` | PPP, Gateway, PCI Compliance | [references/payments.md](references/payments.md) |

## Repository Structure

```text
vtex-agent/
├── SKILL.md                 # Main entry point (Orchestrator)
├── AGENTS.md                # This registry
├── references/              # Specialized domain knowledge
│   ├── faststore.md
│   ├── io-development.md
│   ├── rest-apis.md
│   ├── store-framework.md
│   ├── marketplace.md
│   └── payments.md
└── scripts/                 # Automation & utility scripts
```

## How to use
When starting a new task, tell the AI: *"I am working on [Domain], please use the VTEX [Domain] Expert track."*
The AI will then prioritize the instructions in the corresponding reference file.
