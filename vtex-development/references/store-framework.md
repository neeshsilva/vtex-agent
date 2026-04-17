---
name: vtex-store-framework
description: Expert guidance for building and customizing VTEX Store Framework storefronts — the block-based, JSON-driven storefront system. Use this skill whenever the user is working with Store Framework blocks, store block JSON files, CSS handles, vtex.css-handles, store/blocks, store/interfaces.json, store/routes.json, product summary, shelf, search result layout, flex-layout, rich-text, slider-layout, blockClass, checkout-ui-custom, or customizing any block-based VTEX storefront. Trigger on any mention of "store framework", "store blocks", "css handles", "flex-layout", "product-summary", "store/blocks", or when building/debugging a block-based VTEX storefront theme.
---

# VTEX Store Framework

Store Framework is VTEX's block-based storefront system. Layouts are defined in JSON, not code — business users and developers compose pages by nesting reusable "blocks." It remains widely used in production and is the natural choice for teams who need CMS-friendly, low-code customization.

---

## Core Concepts

### How Blocks Compose

Every element on a page is a block. Blocks are nested hierarchically:

```
store.home
  └── flex-layout.row#main
      ├── slider-layout#hero
      │   └── image#slide1
      └── shelf#featured
          └── product-summary.shelf
              ├── product-summary-image
              ├── product-summary-name
              └── product-summary-price
```

### Block Naming with `#` IDs

Use `#my-id` suffix to create multiple independent instances of the same block:

```json
{
  "flex-layout.row#header-row": { "props": { "blockClass": "header" } },
  "flex-layout.row#footer-row": { "props": { "blockClass": "footer" } }
}
```

Without `#id`, you can only use one instance of a block per page.

### Key Files

| File | Purpose |
|---|---|
| `store/blocks/*.json` | Layout definitions per page |
| `store/routes.json` | URL path → block mapping |
| `store/interfaces.json` | Custom block type declarations |
| `styles/css/*.css` | Scoped CSS for each installed app |

---

## Built-in Layout Blocks

### `flex-layout.row` / `flex-layout.col`

The primary layout primitive — a flexbox row or column:

```json
{
  "flex-layout.row#promo": {
    "props": {
      "blockClass": "promoSection",
      "colSizing": "auto",
      "colGap": 4,
      "paddingTop": 6,
      "paddingBottom": 6,
      "fullWidth": true,
      "horizontalAlign": "center",
      "verticalAlign": "middle"
    },
    "children": ["flex-layout.col#left", "flex-layout.col#right"]
  },
  "flex-layout.col#left": {
    "props": { "width": "50%" },
    "children": ["rich-text#headline"]
  },
  "flex-layout.col#right": {
    "props": { "width": "50%" },
    "children": ["image#promo-img"]
  }
}
```

### `rich-text`

Rich text with markdown support:

```json
{
  "rich-text#headline": {
    "props": {
      "text": "## Welcome to *Our Store*\nDiscover our latest collection.",
      "textAlignment": "CENTER",
      "textPosition": "CENTER",
      "blockClass": "headline"
    }
  }
}
```

### `slider-layout`

Carousel/slider component:

```json
{
  "slider-layout#hero": {
    "props": {
      "itemsPerPage": { "desktop": 1, "tablet": 1, "phone": 1 },
      "showNavigationArrows": "always",
      "showPaginationDots": "always",
      "autoplay": true,
      "autoplayTimeout": 5000,
      "infinite": true
    },
    "children": ["image#slide1", "image#slide2", "image#slide3"]
  }
}
```

### `image`

```json
{
  "image#banner-summer": {
    "props": {
      "src": "https://cdn.mystore.com/summer.jpg",
      "alt": "Summer Collection",
      "width": "100%",
      "link": { "url": "/summer", "newTab": false }
    }
  }
}
```

---

## Routes & Pages

### `store/routes.json`

```json
{
  "store.home": { "path": "/" },
  "store.product": { "path": "/:slug/p" },
  "store.search": { "path": "/:term" },
  "store.custom#about": { "path": "/about" },
  "store.custom#sale": { "path": "/sale/:category" }
}
```

The route key (e.g., `store.custom#sale`) must match the block of the same name in your block files.

### Reading Route Params in a Component

```tsx
import { useRuntime } from 'vtex.render-runtime'

const SalePage = () => {
  const { route } = useRuntime()
  const { category } = route.params  // matches ":category"
  return <h1>Sale: {category}</h1>
}
```

---

## Declaring Custom Blocks

### `store/interfaces.json`

Declare your block so the platform knows it exists and what props it accepts:

```json
{
  "my-promo-card": {
    "component": "PromoCard",
    "allowed": ["*"],
    "props": {
      "title": {
        "type": "string",
        "title": "Card title",
        "default": "Promo"
      },
      "imageUrl": {
        "type": "string",
        "title": "Image URL"
      },
      "buttonLabel": {
        "type": "string",
        "title": "Button label",
        "default": "Shop Now"
      },
      "buttonUrl": {
        "type": "string",
        "title": "Button URL",
        "widget": { "ui:widget": "PageSelector" }
      }
    }
  }
}
```

### React Component (`react/PromoCard.tsx`)

```tsx
import React from 'react'
import { Link } from 'vtex.render-runtime'
import { useCssHandles } from 'vtex.css-handles'

const CSS_HANDLES = ['container', 'image', 'title', 'button'] as const

interface Props {
  title?: string
  imageUrl?: string
  buttonLabel?: string
  buttonUrl?: string
}

const PromoCard: React.FC<Props> = ({
  title = 'Promo',
  imageUrl,
  buttonLabel = 'Shop Now',
  buttonUrl = '/',
}) => {
  const { handles } = useCssHandles(CSS_HANDLES)

  return (
    <article className={handles.container}>
      {imageUrl && <img className={handles.image} src={imageUrl} alt={title} />}
      <h2 className={handles.title}>{title}</h2>
      <Link to={buttonUrl} className={handles.button}>
        {buttonLabel}
      </Link>
    </article>
  )
}

export default PromoCard
```

### Using the Custom Block in a Layout

```json
{
  "store.custom#landing": {
    "blocks": ["flex-layout.row#cards"]
  },
  "flex-layout.row#cards": {
    "children": ["my-promo-card#summer", "my-promo-card#winter"]
  },
  "my-promo-card#summer": {
    "props": {
      "title": "Summer Collection",
      "imageUrl": "https://cdn.mystore.com/summer.jpg",
      "buttonUrl": "/summer"
    }
  }
}
```

---

## CSS Handles & Styling

CSS handles give your components semantic, scoped class names that merchants can target in CSS overrides.

### Defining and Using Handles

```tsx
const CSS_HANDLES = ['container', 'title', 'badge'] as const

// Generates class names like:
// vtex-my-app-1-x-container
// vtex-my-app-1-x-title
// vtex-my-app-1-x-badge

const { handles } = useCssHandles(CSS_HANDLES)

return (
  <div className={handles.container}>
    <span className={handles.badge}>New</span>
  </div>
)
```

### `blockClass` for Per-Instance Styling

Any block can receive a `blockClass` prop. It appends a suffix to all handles in that block, letting you style one instance independently:

```json
{
  "rich-text#hero-message": {
    "props": { "blockClass": "hero" }
  }
}
```

Now target it in CSS: `.vtex-rich-text-0-x-wrapper--hero { ... }`

### Global CSS Overrides

Override styles from installed apps by creating CSS files in `styles/css/`:

```css
/* styles/css/vtex.rich-text.css */
.vtex-rich-text-0-x-wrapper {
  max-width: 1280px;
  margin: 0 auto;
}

.vtex-rich-text-0-x-wrapper--headline {
  text-align: center;
  padding: 40px 0;
  font-size: 2.5rem;
}
```

File naming convention: `{vendor}.{app-name}.css`

---

## Search & Shelf Customization

### Search Result Page

```json
{
  "store.search": {
    "blocks": ["search-result-layout"]
  },
  "search-result-layout": {
    "blocks": [
      "search-result-layout.desktop",
      "search-result-layout.mobile",
      "search-not-found-layout"
    ]
  },
  "search-result-layout.desktop": {
    "props": {
      "pagination": "show-more",
      "defaultGalleryLayout": "grid"
    },
    "children": [
      "flex-layout.row#search-breadcrumb",
      "search-result-layout.filterNavigator.v3",
      "gallery"
    ]
  }
}
```

### Product Summary (Shelf Item)

Customize what displays on each product card in any shelf or search results:

```json
{
  "product-summary.shelf": {
    "children": [
      "product-summary-image",
      "product-summary-name",
      "product-summary-rating",
      "product-summary-space",
      "product-summary-price",
      "product-summary-sku-selector",
      "product-summary-buy-button"
    ]
  },
  "product-summary-price": {
    "props": {
      "showListPrice": true,
      "showLabels": false,
      "showInstallments": true,
      "showDiscountValue": false
    }
  },
  "product-summary-image": {
    "props": {
      "showBadge": true,
      "badgeText": "Sale",
      "maxHeight": 300,
      "displayMode": "normal"
    }
  }
}
```

### Home Page Shelf

```json
{
  "shelf#featured": {
    "blocks": ["product-summary.shelf"],
    "props": {
      "category": 10,
      "orderBy": "OrderByBestDiscountDESC",
      "productList": {
        "maxItems": 8,
        "itemsPerPage": 4,
        "minItemsPerPage": 1
      }
    }
  }
}
```

---

## Checkout UI Customization

VTEX Checkout UI is customized via the `vtex.checkout-ui-custom` app.

```bash
vtex install vtex.checkout-ui-custom
```

Customizations live in a dedicated IO app using the `checkout-ui-custom` builder:

```css
/* checkout-ui-custom/css/checkout.css */

/* Layout */
.orderform-template-holder {
  max-width: 1200px;
  margin: 0 auto;
}

/* Cart summary */
.cart-sidebar .totalizers {
  background: #f9f9f9;
  padding: 16px;
  border-radius: 8px;
}

/* CTA button */
#checkout-confirmation-wrapper .btn-primary {
  background-color: #e31c58;
  border-color: #e31c58;
  border-radius: 4px;
  font-weight: 700;
}
```

---

## Admin Pages

Use the `admin` builder to add custom pages to VTEX Admin.

### `admin/navigation.json`

```json
{
  "section": "MY SECTION",
  "labelId": "admin/nav-my-section",
  "path": "/admin/my-app",
  "children": [
    {
      "labelId": "admin/nav-dashboard",
      "path": "/admin/my-app/dashboard"
    }
  ]
}
```

### `messages/en.json`

```json
{
  "admin/nav-my-section": "My App",
  "admin/nav-dashboard": "Dashboard"
}
```

### Admin React Page

```tsx
// admin/src/pages/Dashboard.tsx
import React from 'react'
import { Layout, PageBlock, PageHeader } from 'vtex.styleguide'

const Dashboard = () => (
  <Layout pageHeader={<PageHeader title="My Dashboard" />}>
    <div className="ph7-ns">
      <PageBlock variation="full">
        <p>Custom admin content here</p>
      </PageBlock>
    </div>
  </Layout>
)

export default Dashboard
```

---

## Common Pitfalls

1. **Missing `#id` suffix** — if you need two `flex-layout.row` on the same page, you *must* use unique IDs (`#header`, `#footer`). Without it, the second instance is silently ignored.
2. **`blockClass` does nothing without the CSS file** — adding `blockClass: "hero"` in JSON only creates the CSS class; you must also write the CSS in `styles/css/` to see any change.
3. **Editing native block CSS in the wrong file** — CSS for `vtex.shelf` goes in `styles/css/vtex.shelf.css`, not in your component's CSS file.
4. **`peerDependency` missing** — if your app's block expects `product-summary.shelf`, add `vtex.product-summary` to `peerDependencies` in `manifest.json`.
5. **Search filters not appearing** — filters come from the catalog facets configured in VTEX Admin, not from the block setup. Check that facets are enabled in the Catalog admin.
