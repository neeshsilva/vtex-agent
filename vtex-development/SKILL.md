---
name: vtex-development
description: Comprehensive expert guidance for the VTEX platform. Covers VTEX IO, FastStore, Store Framework, and REST APIs. Use this skill for ANY VTEX-related task, including app development, storefront customization, API integrations (Catalog, OMS, Master Data), and platform architecture decisions. Trigger on "vtex", "vtex io", "faststore", "store framework", "manifest.json", "appkey", "apptoken", "vtex api", or when building any component or service for VTEX.
---

# VTEX Development Orchestrator

VTEX is a composable commerce platform with several distinct development paradigms. To provide the best assistance, this skill routes to specialized knowledge based on the project's technology stack.

## Choose Your Domain

Before writing code or providing deep technical advice, identify which VTEX technology is being used. If unsure, ask the user to provide their `manifest.json` or `package.json`.

| Technology | Indicators | Reference File |
| :--- | :--- | :--- |
| **FastStore** | `discovery.config.js`, `@faststore/core`, Next.js project | [faststore.md](file:///Users/tharushasilva/Desktop/personal/AI/create-skills/.agents/skills/vtex-development/references/faststore.md) |
| **VTEX IO (Backend/React)** | `manifest.json`, `node/`, `react/`, `graphql/` builders | [io-development.md](file:///Users/tharushasilva/Desktop/personal/AI/create-skills/.agents/skills/vtex-development/references/io-development.md) |
| **Store Framework** | `store/blocks/`, `vtex.css-handles`, block-based layouts | [store-framework.md](file:///Users/tharushasilva/Desktop/personal/AI/create-skills/.agents/skills/vtex-development/references/store-framework.md) |
| **REST APIs** | AppKey/AppToken, Catalog, OMS, Logistics, Master Data | [rest-apis.md](file:///Users/tharushasilva/Desktop/personal/AI/create-skills/.agents/skills/vtex-development/references/rest-apis.md) |

---

## Strategic Guidance

### 1. Choosing the Right Paradigm
*   **FastStore**: Best for performance-first, modern Jamstack storefronts (Next.js).
*   **Store Framework**: Best for low-code, CMS-heavy storefronts with pre-built blocks.
*   **VTEX IO**: The underlying platform for building custom apps, backend services, and React blocks for both SF and FastStore.

### 2. Implementation Workflow
1.  **Identify the domain** using the table above.
2.  **Read the corresponding reference file** in `references/` before proceeding with implementation.
3.  **Cross-reference** with [rest-apis.md](file:///Users/tharushasilva/Desktop/personal/AI/create-skills/.agents/skills/vtex-development/references/rest-apis.md) if you need specific endpoint schemas.

### 3. Core Constraints
*   **Never manage credentials manually**: Use VTEX IO `IOClients` for automatic auth whenever possible.
*   **Respect the "Never Edit Core" principle**: In FastStore, use the override system. In Store Framework, use `blockClass` and CSS handles.
*   **Security First**: Ensure all external calls are declared in `manifest.json` policies.

---

## VTEX Architecture at a Glance

```
                          ┌──────────────────────┐
                          │    VTEX IO Platform   │
                          └──────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
     ┌────────▼───────┐    ┌─────────▼──────┐    ┌─────────▼──────┐
     │ Node Builder   │    │ React Builder  │    │  GraphQL       │
     │ (services/API) │    │ (blocks/UI)    │    │  (schema +     │
     │                │    │                │    │   resolvers)   │
     └────────┬───────┘    └────────────────┘    └────────────────┘
              │
    ┌─────────▼──────────────────┐
    │         VTEX APIs          │
    │ Catalog · OMS · Pricing    │
    │ Checkout · Logistics · MDB │
    └────────────────────────────┘
```

### Storefront Options

| | **FastStore** | **Store Framework** |
|---|---|---|
| Technology | Next.js + TypeScript + GraphQL | VTEX IO React blocks + JSON |
| Customization | Code overrides in `/src` | JSON block composition |
| Performance | Excellent (built for CWV) | Good |
| CMS | VTEX Headless CMS | VTEX Site Editor |
| Best for | New projects, performance-critical | Existing stores, low-code teams |

---

## Common CLI Commands (Any VTEX Project)

```bash
vtex login myaccount           # Authenticate
vtex use my-workspace          # Switch workspace (always work in a workspace)
vtex link                      # Live dev mode
vtex publish                   # Publish a new version
vtex deploy myvendor.myapp@1.x # Make version stable
vtex workspace promote         # Promote workspace to production
```

---

## Key Resources

- [VTEX Developer Portal](https://developers.vtex.com)
- [FastStore Docs](https://developers.vtex.com/docs/guides/faststore)
- [Store Framework Docs](https://developers.vtex.com/docs/guides/store-framework)
- [VTEX IO App Development](https://developers.vtex.com/docs/app-development)
- [VTEX API Reference](https://developers.vtex.com/docs/api-reference)
- [VTEX IO Apps (pre-built)](https://developers.vtex.com/docs/vtex-io-apps)
- [VTEX Community](https://community.vtex.com)
