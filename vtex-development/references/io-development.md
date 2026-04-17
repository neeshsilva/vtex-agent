---
name: vtex-io-development
description: Expert guidance for building VTEX IO apps — Node.js backend services, React storefront components, GraphQL APIs, and app lifecycle management. Use this skill whenever the user is working with manifest.json, vtex CLI, VTEX IO workspaces, Node builder services, React builder components, GraphQL resolvers, VTEX IO policies, VBASE storage, app events, settingsSchema, or deploying/publishing VTEX IO apps. Trigger on any mention of "vtex io", "manifest.json", "vtex link", "vtex publish", "vtex deploy", node builder, react builder, graphql builder, IO app, IOClients, or when building backend integrations or custom admin pages on VTEX.
---

# VTEX IO App Development

VTEX IO is the cloud-native development platform that powers all VTEX app customizations — from backend services and APIs to frontend React components and GraphQL layers. Every VTEX customization starts with a VTEX IO app.

---

## The `manifest.json` — Most Important File

Every VTEX IO app has a `manifest.json` at its root. This file defines everything the platform knows about your app.

```json
{
  "$schema": "https://raw.githubusercontent.com/vtex/node-vtex-api/master/gen/manifest.schema",
  "vendor": "myaccount",
  "name": "my-app",
  "version": "1.0.0",
  "title": "My App",
  "description": "What this app does",
  "builders": {
    "react": "3.x",
    "node": "6.x",
    "graphql": "1.x",
    "docs": "0.x"
  },
  "dependencies": {
    "vtex.styleguide": "9.x"
  },
  "peerDependencies": {
    "vtex.store": "2.x"
  },
  "policies": [
    {
      "name": "outbound-access",
      "attrs": { "host": "api.external-service.com" }
    }
  ],
  "settingsSchema": {
    "title": "App Settings",
    "type": "object",
    "properties": {
      "apiKey": { "title": "API Key", "type": "string" }
    }
  }
}
```

**Key rules:**
- `vendor` = your VTEX account name (kebab-case)
- `name` = unique app name (kebab-case)
- `version` = Semantic Versioning (`major.minor.patch`)
- `builders` declares what your app does; each maps to a directory
- `dependencies` are auto-installed; `peerDependencies` must already exist in the merchant's account
- Any external HTTP call needs an `outbound-access` policy entry

### Builders → Directories

| Builder | Directory | Purpose |
|---|---|---|
| `node` | `/node` | Backend services & REST handlers |
| `react` | `/react` | Frontend React blocks |
| `graphql` | `/graphql` | GraphQL schema & resolvers |
| `store` | `/store` | Block declarations and routes |
| `styles` | `/styles` | Global CSS variables |
| `admin` | `/admin` | Admin panel pages |
| `docs` | `/docs` | Documentation |

---

## CLI Workflow

```bash
# Authenticate
vtex login myaccount

# Never work on master — create a workspace first
vtex use my-feature-workspace

# Live development — mounts your local code into the workspace
vtex link

# Bump version (patch/minor/major) and create a release commit
vtex release patch stable

# Publish to the VTEX registry
vtex publish

# Install in a production workspace for validation
vtex use my-test --production
vtex install myaccount.my-app@1.0.1

# Make this version the stable candidate for all accounts
vtex deploy myaccount.my-app@1.0.1
```

**When to bump what:**
- `patch` — Bug fixes, no API changes
- `minor` — New features, backwards compatible
- `major` — Breaking changes (renamed blocks, removed settings)

### Workspace Management

```bash
vtex workspace list
vtex workspace create my-feature
vtex workspace reset my-feature    # Removes linked apps
vtex workspace promote              # Promotes to production traffic
vtex workspace delete my-feature
```

> Development workspaces handle no real traffic. Use `--production` flag to create a production workspace for final validation before promoting.

---

## Node Builder (Backend Services)

```
node/
├── clients/
│   ├── index.ts          # Exports your Clients class
│   └── myClient.ts       # Custom typed HTTP clients
├── middlewares/
│   └── myHandler.ts      # Route handler functions
├── resolvers/
│   └── index.ts          # GraphQL resolvers
├── index.ts              # Service definition
└── package.json
```

### `node/index.ts` — Service Definition

```typescript
import { Service, ParamsContext, RecorderState } from '@vtex/api'
import { Clients } from './clients'
import { myHandler } from './middlewares/myHandler'
import { onOrderCreated } from './middlewares/eventHandler'

export default new Service<Clients, RecorderState, ParamsContext>({
  clients: {
    implementation: Clients,
    options: {
      default: { retries: 2, timeout: 10000 },
    },
  },
  routes: {
    myRoute: myHandler,            // maps to a path in service.json
  },
  events: {
    onOrderCreated,                // listens for broadcast events
  },
})
```

### `node/service.json` — Route Declarations

```json
{
  "memory": 256,
  "timeout": 10,
  "minReplicas": 2,
  "maxReplicas": 10,
  "routes": {
    "myRoute": {
      "path": "/_v/app/my-endpoint/:id",
      "public": true
    },
    "privateRoute": {
      "path": "/_v/app/private",
      "public": false
    }
  }
}
```

`public: true` allows unauthenticated calls. Private routes require a `VtexIdclientAutCookie` token.

### Handler Pattern

```typescript
// node/middlewares/myHandler.ts
import { ServiceContext } from '@vtex/api'
import { Clients } from '../clients'

type Context = ServiceContext<Clients>

export const myHandler = async (ctx: Context, next: () => Promise<any>) => {
  const { id } = ctx.vtex.route.params

  try {
    const result = await ctx.clients.myClient.getById(id)
    ctx.status = 200
    ctx.body = result
  } catch (e) {
    ctx.status = 500
    ctx.body = { error: e.message }
  }

  await next()
}
```

### Typed HTTP Clients

Always wrap external API calls in a typed client class — never use raw `fetch`. This gives you automatic retry, timeout, and auth injection:

```typescript
// node/clients/myClient.ts
import { ExternalClient, InstanceOptions, IOContext } from '@vtex/api'

export class MyClient extends ExternalClient {
  constructor(ctx: IOContext, options?: InstanceOptions) {
    super('https://api.external-service.com', ctx, {
      ...options,
      headers: {
        ...(options?.headers),
        Authorization: `Bearer ${ctx.authToken}`,
      },
    })
  }

  getById(id: string) {
    return this.http.get(`/items/${id}`, { metric: 'my-client-get' })
  }

  create(data: unknown) {
    return this.http.post('/items', data, { metric: 'my-client-create' })
  }
}
```

```typescript
// node/clients/index.ts
import { IOClients } from '@vtex/api'
import { MyClient } from './myClient'

export class Clients extends IOClients {
  public get myClient() {
    return this.getOrSet('myClient', MyClient)
  }
}
```

---

## React Builder (Frontend Components)

```
react/
├── MyComponent.tsx        # Component name = block name
├── typings/vtex.d.ts      # Type declarations for vtex packages
└── package.json
```

### Component with CSS Handles and Context Hooks

```tsx
import React from 'react'
import { useCssHandles } from 'vtex.css-handles'
import { useProduct } from 'vtex.product-context'

const CSS_HANDLES = ['wrapper', 'title', 'badge'] as const

const ProductHighlight: React.FC = () => {
  const { handles } = useCssHandles(CSS_HANDLES)
  const productContext = useProduct()

  if (!productContext?.product) return null

  return (
    <div className={handles.wrapper}>
      <h2 className={handles.title}>{productContext.product.productName}</h2>
      <span className={handles.badge}>New</span>
    </div>
  )
}

export default ProductHighlight
```

### Props Schema (`store/interfaces.json`)

```json
{
  "my-block": {
    "component": "MyComponent",
    "props": {
      "title": { "type": "string", "title": "Title", "default": "Hello" },
      "showBadge": { "type": "boolean", "title": "Show badge", "default": true }
    }
  }
}
```

---

## GraphQL Builder

```
graphql/
└── schema.graphql       # Type and Query definitions

node/
└── resolvers/
    └── index.ts         # Resolver implementations
```

```graphql
# graphql/schema.graphql
type MyData {
  id: String!
  value: String
}

type Query {
  myData(id: String!): MyData
}
```

```typescript
// node/resolvers/index.ts
export const resolvers = {
  Query: {
    myData: async (_: any, { id }: { id: string }, ctx: any) => {
      return ctx.clients.myClient.getById(id)
    },
  },
}
```

Connect resolvers in `node/index.ts`:
```typescript
export default new Service({ clients: {...}, routes: {...}, graphql: { resolvers } })
```

---

## App Settings

`settingsSchema` in `manifest.json` auto-generates a config UI in VTEX Admin:

```json
"settingsSchema": {
  "title": "My App",
  "type": "object",
  "properties": {
    "apiKey": { "title": "API Key", "type": "string" },
    "enabled": { "title": "Enabled", "type": "boolean", "default": true },
    "maxItems": { "title": "Max Items", "type": "integer", "default": 10 }
  }
}
```

Read settings in a handler:
```typescript
const settings = await ctx.clients.apps.getAppSettings(
  `${vendor}.${name}@${major}.x`
)
const { apiKey, enabled } = settings
```

---

## VBASE Storage

VBASE is a workspace-scoped key-value store. Use it for caching and lightweight state:

```typescript
const BUCKET = 'my-cache'

// Write
await ctx.clients.vbase.saveJSON(BUCKET, 'my-key', { data: 'value' })

// Read
const data = await ctx.clients.vbase.getJSON<MyType>(BUCKET, 'my-key')

// Delete
await ctx.clients.vbase.delete(BUCKET, 'my-key')
```

> VBASE is workspace-scoped — data in a dev workspace is not visible on master.

---

## Events (Pub/Sub)

```typescript
// Emit
await ctx.clients.events.sendEvent('', 'my-event', { payload: 'value' })

// Listen — register in node/index.ts
events: {
  'vtex.orders-broadcast:order-created': handleOrderCreated,
}
```

Add the event policy to `manifest.json`:
```json
"policies": [{ "name": "vtex.orders-broadcast:order-created" }]
```

---

## Common Pitfalls

1. **Forgetting `outbound-access` policy** — every external HTTP call needs it in `manifest.json`, or the request will be blocked by the platform.
2. **Developing on master workspace** — always use `vtex use my-workspace` first.
3. **Raw fetch in Node handlers** — use `IOClients` instead; raw fetches bypass retries, timeouts, and auth injection.
4. **Major version bumps breaking merchants** — a major bump stops automatic updates for accounts using your app. Make sure to communicate breaking changes.
5. **Missing peerDependencies** — if your React component uses hooks from `vtex.product-context`, it must be a `peerDependency`.
