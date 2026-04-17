---
name: vtex-rest-apis
description: Expert guidance for integrating with VTEX REST APIs — Catalog, Pricing, Orders (OMS), Checkout, Logistics, Master Data, and platform authentication. Use this skill whenever the user is working with VTEX API authentication (AppKey/AppToken), Catalog API, OMS API, Checkout API, Pricing API, Logistics API, Master Data API, VTEX IO typed clients (IOClients), API rate limiting, or building third-party integrations with VTEX. Trigger on any mention of "vtex api", "appkey", "apptoken", "vtex catalog api", "vtex oms", "master data", "vtex checkout api", "vtex logistics api", "vtex pricing api", IOClients, or when building integrations, ERPs, WMS connectors, or any service that calls VTEX REST endpoints.
---

# VTEX REST APIs

VTEX exposes REST APIs for every core commerce capability — Catalog, Pricing, Orders, Checkout, Logistics, and more. This skill covers authentication patterns, key endpoint references, and the VTEX IO typed client pattern for building integrations.

---

## Authentication

### AppKey + AppToken (Server-to-Server)

The standard auth method for backend integrations:

```http
X-VTEX-API-AppKey: vtexappkey-myaccount-XXXXXX
X-VTEX-API-AppToken: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Create keys in VTEX Admin: **Account Settings → Account Management → App Keys**.

**Security best practices:**
- Create separate keys per integration (not one shared key)
- Grant only the roles the integration actually needs
- Rotate keys regularly
- Never expose keys client-side

### User Token (Frontend Calls)

For calls made on behalf of a logged-in shoppper, use the `VtexIdclientAutCookie` cookie — set automatically by VTEX's login flow:

```
Cookie: VtexIdclientAutCookie={token}
```

### VTEX IO — Never Manage Credentials Manually

In VTEX IO Node apps, authentication is handled automatically through the request context. Never hardcode or pass credentials manually:

```typescript
// ✅ Correct — ctx.clients handles auth injection
const product = await ctx.clients.catalog.getProduct(id)

// ❌ Wrong — don't manually manage tokens
const token = process.env.VTEX_APP_TOKEN // never do this
```

---

## VTEX IO Typed Clients (Best Practice)

In IO Node apps, wrap all API calls in typed client classes for automatic retry, timeout, and auth injection:

```typescript
// node/clients/catalog.ts
import { ExternalClient, InstanceOptions, IOContext } from '@vtex/api'

interface Product {
  Id: number
  Name: string
  IsActive: boolean
  CategoryId: number
}

export class CatalogClient extends ExternalClient {
  constructor(ctx: IOContext, options?: InstanceOptions) {
    super(
      'http://portal.vtexcommercestable.com.br/api/catalog',
      ctx,
      {
        ...options,
        headers: {
          ...(options?.headers),
          VtexIdclientAutCookie: ctx.authToken,
        },
      }
    )
  }

  getProduct(id: string): Promise<Product> {
    return this.http.get(`/pvt/product/${id}`, { metric: 'catalog-get' })
  }

  searchProducts(term: string): Promise<Product[]> {
    return this.http.get(
      `/../../catalog_system/pub/products/search/${term}`,
      { metric: 'catalog-search' }
    )
  }
}
```

```typescript
// node/clients/index.ts
import { IOClients } from '@vtex/api'
import { CatalogClient } from './catalog'

export class Clients extends IOClients {
  public get catalog() {
    return this.getOrSet('catalog', CatalogClient)
  }
}
```

---

## Catalog API

**Base URL:** `https://{account}.vtexcommercestable.com.br/api/catalog`

### Get Product

```http
GET /pvt/product/{productId}
```

```json
{
  "Id": 1234,
  "Name": "Classic T-Shirt",
  "IsActive": true,
  "CategoryId": 10,
  "BrandId": 200,
  "RefId": "TSHIRT-001",
  "Description": "..."
}
```

### Create Product

```http
POST /pvt/product
Content-Type: application/json

{
  "Name": "New Product",
  "CategoryId": 10,
  "BrandId": 200,
  "RefId": "NEW-001",
  "IsVisible": true,
  "IsActive": true,
  "MetaTagDescription": "SEO description",
  "Title": "New Product | My Store"
}
```

### Get SKUs by Product

```http
GET /pvt/product/{productId}/skus
```

### Create SKU

```http
POST /pvt/stockkeepingunit
Content-Type: application/json

{
  "ProductId": 1234,
  "Name": "Classic T-Shirt - Blue M",
  "RefId": "TSHIRT-BLUE-M",
  "IsActive": true,
  "Height": 1.0,
  "Width": 20.0,
  "Length": 20.0,
  "WeightKg": 0.2
}
```

### Public Product Search

```http
GET /api/catalog_system/pub/products/search/{term}?_from=0&_to=49&O={sortOrder}
```

Sort options (`O=`): `OrderByScoreDESC` · `OrderByPriceASC` · `OrderByPriceDESC` · `OrderByNameASC` · `OrderByBestDiscountDESC`

### Categories Tree

```http
GET /api/catalog_system/pub/category/tree/{depth}
```

Use `depth=3` for up to 3 levels.

---

## Pricing API

**Base URL:** `https://api.vtex.com/{account}/pricing`

### Get Price for a SKU

```http
GET /prices/{skuId}
```

```json
{
  "itemId": "12345",
  "listPrice": 99.99,
  "costPrice": 45.00,
  "tradePolicies": {
    "1": {
      "listPrice": 99.99,
      "sellingPrice": 89.99,
      "priceValidUntil": "2025-12-31T00:00:00Z"
    }
  }
}
```

### Create or Update a Price

```http
PUT /prices/{skuId}
Content-Type: application/json

{
  "listPrice": 99.99,
  "costPrice": 45.00,
  "basePrice": 89.99
}
```

### Fixed Prices (Price Tables)

```http
PUT /prices/{skuId}/fixed/{tradePolicyId}
Content-Type: application/json

{
  "tradePolicyId": 1,
  "rules": [
    { "value": 79.99, "minQuantity": 1 },
    { "value": 69.99, "minQuantity": 5 }
  ]
}
```

---

## Orders Management (OMS)

**Base URL:** `https://api.vtex.com/{account}/oms`

### Get Order by ID

```http
GET /pvt/orders/{orderId}
```

Key response fields: `orderId`, `status`, `items[]`, `shippingData`, `paymentData`, `totals[]`, `clientProfileData`.

### List Orders

```http
GET /pvt/orders?q={term}&f_status={status}&page=1&per_page=15&f_creationDate=creationDate:[{from} TO {to}]
```

Common `f_status` values:

| Status | Meaning |
|---|---|
| `payment-pending` | Awaiting payment confirmation |
| `ready-for-handling` | Approved, awaiting fulfillment |
| `handling` | Being prepared / picked |
| `invoiced` | Invoice issued, shipped |
| `canceled` | Order cancelled |

### Update Status

```http
POST /pvt/orders/{orderId}/start-handling
POST /pvt/orders/{orderId}/cancel
```

### Add Invoice & Tracking

```http
POST /pvt/orders/{orderId}/invoice
Content-Type: application/json

{
  "type": "Output",
  "invoiceNumber": "NF-1234",
  "invoiceValue": 8999,
  "issuanceDate": "2024-11-01T00:00:00",
  "trackingNumber": "BR123456789BR",
  "trackingUrl": "https://carrier.com/track/BR123456789BR",
  "courier": "FedEx",
  "items": [{ "id": "sku-id", "price": 8999, "quantity": 1 }]
}
```

---

## Checkout API

**Base URL:** `https://{account}.vtexcommercestable.com.br/api/checkout`

The `orderFormId` is stored in the `checkout.vtex.com` cookie.

### Get Current Cart

```http
GET /pub/orderForm/{orderFormId}
```

### Add Item to Cart

```http
POST /pub/orderForm/{orderFormId}/items
Content-Type: application/json

{
  "orderItems": [
    { "id": "12345", "quantity": 1, "seller": "1" }
  ]
}
```

### Set Shipping Address

```http
POST /pub/orderForm/{orderFormId}/attachments/shippingData

{
  "selectedAddresses": [{
    "addressType": "residential",
    "country": "USA",
    "postalCode": "10001",
    "city": "New York",
    "state": "NY",
    "street": "123 Main St",
    "number": ""
  }]
}
```

### Place Order

```http
POST /pub/orders?sc={salesChannelId}

{ "orderFormId": "{orderFormId}" }
```

---

## Logistics API

**Base URL:** `https://logistics.vtex.com/api`

### Get Inventory by SKU

```http
GET /logistics/pvt/inventory/skus/{skuId}
```

```json
{
  "skuId": "12345",
  "balance": [{
    "warehouseId": "principal",
    "warehouseName": "Main Warehouse",
    "totalQuantity": 150,
    "reservedQuantity": 12,
    "hasUnlimitedQuantity": false
  }]
}
```

### Update Inventory

```http
PUT /logistics/pvt/inventory/skus/{skuId}/warehouses/{warehouseId}

{
  "unlimitedQuantity": false,
  "quantity": 200
}
```

### Calculate Shipping

```http
POST /logistics/pub/shipping/calculate

{
  "logisticsInfo": [{ "itemIndex": 0, "quantity": 1 }],
  "shippingData": {
    "address": { "postalCode": "10001", "country": "USA" }
  },
  "items": [{ "id": "12345", "requestIndex": 0, "quantity": 1, "price": 8999 }]
}
```

---

## Master Data API (v2)

**Base URL:** `https://api.vtex.com/{account}/dataentities`

Master Data is VTEX's platform CRM and custom document store.

### Create a Document

```http
POST /dataentities/{entity}/documents
Content-Type: application/json

{
  "email": "customer@example.com",
  "firstName": "John",
  "subscribed": true
}
```

**Response:** `201 Created` with `{ "Id": "CL-abc123", "Href": "..." }`

### Search Documents

```http
GET /dataentities/{entity}/search?_where=email=customer@example.com&_fields=id,email,firstName,subscribed&_sort=createdIn DESC&_size=10
```

Always specify `_fields` — fetching all fields is expensive and slow.

### Update a Document (PATCH)

```http
PATCH /dataentities/{entity}/documents/{documentId}

{ "subscribed": false }
```

### Delete a Document

```http
DELETE /dataentities/{entity}/documents/{documentId}
```

---

## Rate Limits & Throttling

| API | Approximate Limit |
|---|---|
| Catalog (read) | 200 req/min |
| Catalog (write) | 10 req/min |
| OMS | 400 req/min |
| Pricing | 200 req/min |
| Master Data | 5,000 req/min |

**Best practices:**

1. **Cache aggressively.** Product data rarely changes. Cache with a TTL using VBASE (if in IO) or Redis (if external).
2. **Batch where possible.** Use bulk endpoints when updating prices or inventory for many SKUs.
3. **Handle 429 gracefully.** Implement exponential backoff. `@vtex/api` clients retry automatically when `retries` is set.
4. **Specify `_fields` in Master Data.** Never fetch all fields. Specify exactly what you need.
5. **Use conditional requests.** Pass `If-None-Match` with an ETag to avoid redundant payloads on GET endpoints that support it.

```typescript
// Configure retries in your IO client
export class MyServiceClient extends ExternalClient {
  constructor(ctx: IOContext, options?: InstanceOptions) {
    super('https://api.external.com', ctx, {
      ...options,
      retries: 3,           // auto-retry on 5xx and network errors
      timeout: 8000,        // fail fast if slow — better UX
    })
  }
}
```
