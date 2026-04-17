---
name: vtex-faststore
description: Expert guidance for building high-performance VTEX storefronts with FastStore — VTEX's modern Jamstack toolkit built on Next.js, TypeScript, and GraphQL. Use this skill whenever the user is working with FastStore, @faststore/core, getOverriddenSection, FastStore component overrides, FastStore API extensions, FastStore GraphQL, Headless CMS (VTEX CMS), FastStore themes, design tokens, FastStore CLI, discovery.config.js, faststore.config.js, FastStore WebOps, or deploying a Next.js-based VTEX storefront. Trigger on any mention of "faststore", "getOverriddenSection", "@faststore/core", "FastStore WebOps", "headless cms vtex", or building/customizing a high-performance VTEX storefront.
---

# VTEX FastStore

FastStore is VTEX's modern storefront toolkit. It's built on **Next.js + TypeScript + GraphQL** using a Jamstack architecture. It's the recommended choice for new VTEX storefronts because of its excellent Core Web Vitals performance.

**Official Golden Path**: Never edit `@faststore/core` directly. All customizations live in `/src` via the override system. Every custom section must be exported in `src/components/index.tsx`.

### 1. Framework Isolation (Crucial)
To maintain long-term scalability and leverage FastStore WebOps optimizations, you MUST NOT use native Next.js components directly.
- **❌ DO NOT USE**: `next/link`, `next/image`, `next/router`.
- **✅ USE**: `Link`, `Image`, `useRouter` from `@faststore/ui` or `@faststore/core`.
  - *Reason*: `@faststore/ui` components are optimized for VTEX WebOps and handle analytics/performance automatically.

---

## Project Structure

```
my-store/
├── @faststore/core/          # Read-only core — do NOT edit
├── src/                      # All YOUR work goes here
│   ├── components/
│   │   ├── sections/         # Section overrides
│   │   ├── ui/               # Custom UI components
│   │   └── index.tsx         # REQUIRED: export all overrides here
│   ├── fonts/                # Custom web fonts
│   ├── pages/                # Custom Next.js pages (use sparingly)
│   ├── themes/               # CSS design tokens
│   └── customizations.scss   # Global style entry point
├── cms/faststore/            # Headless CMS schema definitions
├── discovery.config.js       # Store URLs, account, locale
└── faststore.config.js       # FastStore feature flags
```

### `discovery.config.js`

```js
module.exports = {
  account: 'mystore',
  storeUrl: 'https://www.mystore.com',
  secureSubdomain: 'https://secure.mystore.com',
  checkoutUrl: 'https://www.mystore.com/checkout',
  loginUrl: 'https://www.mystore.com/login',
  accountUrl: 'https://www.mystore.com/account',
  locale: 'en-US',
  currency: 'USD',
  // Enforces Lighthouse score in CI
  lighthouseScore: { performance: 0.9 },
}
```

### Local Development

```bash
yarn install
yarn dev        # http://localhost:3000
yarn build      # Production build
yarn faststore  # FastStore CLI
```

---

## Component Overrides & Atomic Design

FastStore follows an atomic design hierarchy:
1. **Atoms (`@faststore/ui`)**: Low-level elements (Button, Input). Zero styling logic.
2. **Molecules (`@faststore/components`)**: Composed UI (SearchInput, ProductCard).
3. **Organisms/Sections (`@faststore/core`)**: Headless CMS-ready modules (Hero, Shelf).

### The Override Rule
Sections are top-level layout components managed via Headless CMS. You can customize them without touching the core.

### Pattern 1: Override Component Props

Change prop values of a sub-component inside a native section:

```tsx
// src/components/sections/CustomProductDetails.tsx
import {
  ProductDetailsSection,
  getOverriddenSection,
} from '@faststore/core'
import type { SectionOverrideDefinitionV1 } from '@faststore/core'

const OVERRIDE: SectionOverrideDefinitionV1<'ProductDetails'> = {
  Section: ProductDetailsSection,
  components: {
    // Modify props of the native ProductTitle component
    ProductTitle: {
      props: { titleTag: 'h1' },
    },
    DiscountBadge: {
      props: { size: 'big' },
    },
  },
}

export default getOverriddenSection(OVERRIDE)
```

### Pattern 2: Replace a Sub-Component Entirely

Swap a native sub-component with your own implementation:

```tsx
// src/components/ui/CustomBuyButton.tsx
import React from 'react'
import { Button } from '@faststore/ui'

const CustomBuyButton = ({ disabled, onClick, ...props }: any) => (
  <Button
    variant="primary"
    disabled={disabled}
    onClick={onClick}
    data-testid="buy-button"
    {...props}
  >
    Add to Cart 🛒
  </Button>
)

export default CustomBuyButton
```

```tsx
// src/components/sections/CustomProductDetails.tsx
import { ProductDetailsSection, getOverriddenSection } from '@faststore/core'
import CustomBuyButton from '../ui/CustomBuyButton'

export default getOverriddenSection({
  Section: ProductDetailsSection,
  components: {
    BuyButton: { Component: CustomBuyButton },
  },
})
```

### Registering ALL Overrides

Every override must be exported from `src/components/index.tsx`. This is non-negotiable — if it's not exported here, it won't be applied:

```tsx
// src/components/index.tsx
export { default as ProductDetails } from './sections/CustomProductDetails'
export { default as Hero } from './sections/CustomHero'
export { default as ProductShelf } from './sections/CustomShelf'
```

The export key (`ProductDetails`, `Hero`) **must exactly match** the native section name.

---

## API Extensions (GraphQL)

FastStore's GraphQL API can be extended to pull in additional product or third-party data.

### Directory Structure

```
src/
└── graphql/
    ├── vtex/
    │   └── fragments/
    │       └── ProductFragment.graphql   # Extend existing VTEX queries
    └── thirdParty/
        ├── schema.graphql               # New types and queries
        └── resolvers/
            └── index.ts                 # Resolver implementations
```

### Extending an Existing VTEX Query

Add extra fields to the native `StoreProduct` type:

```graphql
# src/graphql/vtex/fragments/ProductFragment.graphql
fragment ServerProduct on StoreProduct {
  releaseDate
  unitMultiplier
  brand {
    name
    brandId
  }
}
```

### Adding a Brand-New Query (Third-Party Data)

```graphql
# src/graphql/thirdParty/schema.graphql
type StoreReview {
  rating: Float!
  comment: String!
  author: String!
}

type Query {
  productReviews(productId: String!): [StoreReview!]!
}
```

```typescript
// src/graphql/thirdParty/resolvers/index.ts
const resolvers = {
  Query: {
    productReviews: async (_: any, { productId }: { productId: string }) => {
      const res = await fetch(`https://api.reviews.io/products/${productId}`)
      return res.json()
    },
  },
}
export default resolvers
```

### Using Custom Data in a Component

```tsx
import { gql } from '@faststore/core'
import { useQuery } from '@faststore/graphql-utils'

const REVIEWS_QUERY = gql`
  query ProductReviews($productId: String!) {
    productReviews(productId: $productId) {
      rating
      comment
      author
    }
  }
`

const ReviewSection = ({ productId }: { productId: string }) => {
  const { data, loading } = useQuery(REVIEWS_QUERY, {
    variables: { productId },
  })
  if (loading) return <div>Loading reviews...</div>
  return (
    <ul>
      {data?.productReviews.map((r, i) => (
        <li key={i}>⭐ {r.rating} — {r.comment}</li>
      ))}
    </ul>
  )
}
```

---

## Headless CMS Integration

The Headless CMS lets business users manage page content without code changes. Register your sections so they appear in the CMS editor.

### Registering a Section

```json
// cms/faststore/content-types.json
[
  {
    "id": "promo-banner",
    "name": "Promo Banner",
    "configurationSchemaSets": [
      {
        "name": "Settings",
        "configurations": [
          {
            "name": "title",
            "schema": {
              "title": "Title",
              "type": "string",
              "default": "Summer Sale"
            }
          },
          {
            "name": "ctaUrl",
            "schema": {
              "title": "CTA URL",
              "type": "string"
            }
          }
        ]
      }
    ]
  }
]
```

Sync schemas to the CMS:
```bash
vtex cms sync
```

---

## Theming & Design Tokens

FastStore uses CSS custom properties as design tokens. Always start visual customizations here before reaching for overrides.

### Common Token Categories

| Category | Example Token | Purpose |
|---|---|---|
| Colors | `--fs-color-primary-bkg` | Primary brand color |
| Typography | `--fs-text-face-body` | Body font family |
| Spacing | `--fs-spacing-4` | Spacing scale unit |
| Border | `--fs-border-radius` | Corner rounding |
| Shadow | `--fs-shadow` | Box shadow |

### Custom Theme File

```scss
// src/themes/custom-theme.scss
[data-store-theme] {
  // Brand colors
  --fs-color-primary-bkg: #e31c58;
  --fs-color-primary-text: #ffffff;
  --fs-color-secondary-bkg: #f4f4f4;

  // Typography
  --fs-text-face-body: 'Inter', sans-serif;
  --fs-text-face-title: 'Inter', sans-serif;
  --fs-text-size-base: 16px;

  // Shape
  --fs-border-radius: 8px;
  --fs-border-radius-pill: 99px;
}
```

Import in `src/customizations.scss`:
```scss
@import 'themes/custom-theme';
```

### Styling Specific Components

Use FastStore's data attributes to target components without class name guessing:

```scss
[data-fs-button][data-fs-button-variant="primary"] {
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

[data-fs-product-card] {
  border: 1px solid var(--fs-color-neutral-3);
  border-radius: var(--fs-border-radius);
}
```

---

## Custom Sections

Create pages-level sections that content editors can add/remove in Headless CMS:

```tsx
// src/components/sections/PromoBanner.tsx
interface Props {
  title: string
  ctaLabel: string
  ctaUrl: string
}

const PromoBanner = ({ title, ctaLabel, ctaUrl }: Props) => (
  <section data-fs-promo-banner>
    <h2>{title}</h2>
    <a href={ctaUrl}>{ctaLabel}</a>
  </section>
)

export default PromoBanner
```

Export it from `src/components/index.tsx` and register it in `cms/faststore/content-types.json`.

---

## Analytics

FastStore uses GA4-compatible events. When overriding components that fire events (like `ProductCard`, `BuyButton`), you must manually re-fire those events or analytics will break:

```tsx
import { useAnalyticsEvent } from '@faststore/sdk'

const MyProductCard = ({ product }: { product: any }) => {
  const { sendAnalyticsEvent } = useAnalyticsEvent()

  const handleClick = () => {
    sendAnalyticsEvent({
      name: 'select_item',
      params: {
        items: [{ item_id: product.sku, item_name: product.name, price: product.price }],
      },
    })
  }

### Required GA4 Parameters
- `select_item`: `item_id`, `item_name`, `price`, `item_brand`.
- `add_to_cart`: `value`, `currency`, `items[]`.
- `view_item`: `value`, `currency`, `items[]`.

> [!CAUTION]
> If you create a custom `BuyButton` or `ProductCard` and forget to fire these events, the store's conversion tracking will be broken.
```

---

## Performance Best Practices

1. **Minimize overrides** — every replaced component adds JS bundle weight. Override only what you must.
2. **use `loading="eager"` only for above-the-fold images.** All others stay lazy (default).
3. **Prefer CSS tokens** over inline styles — zero JS runtime overhead.
4. **Server-side GraphQL** — fetch data in server queries, not client-side. Reduces waterfalls.
5. **Enforce Lighthouse CI** — set thresholds in `discovery.config.js`. FastStore WebOps blocks deploys that fall below them.

```tsx
// Use FastStore's Image component — handles lazy load, responsive, format optimization
import { Image } from '@faststore/ui'

<Image
  src="/hero.jpg"
  alt="Summer Sale"
  width={1280}
  height={432}
  loading="eager"   // only for hero images
/>
```
