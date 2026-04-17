---
name: vtex-payments
description: Expert guidance for VTEX Payment Provider Protocol (PPP). Covers payment integration, gateway connectors, manifest.json for payments, PCI compliance, and transaction lifecycle. Trigger on any mention of "vtex payment", "payment provider", "ppp", "gateway connector", or "pci compliance".
---

# VTEX Payment Provider Protocol (PPP)

The **Payment Provider Protocol** is the interface used by VTEX to communicate with external payment gateways.

## 1. Interaction Flow
1. **Create Payment**: VTEX sends a POST with transaction details (value, currency, installments).
2. **Authorize**: Gateway responds with `authorized` or `denied`.
3. **Capture**: VTEX confirms the capture once the order is invoiced.
4. **Cancel/Refund**: For order cancellations or returns.

## 2. Setting Up a Provider
A payment provider is a VTEX IO app with the `payment-provider` builder.

### `manifest.json`
```json
{
  "builders": { "payment-provider": "1.x" },
  "billingOptions": { "type": "free" }
}
```

### Path Configuration (`service.json`)
You must implement these specific endpoints as defined in the protocol:
- `/payment`: Create & Authorize
- `/settle`: Capture
- `/cancel`: Cancel/Void
- `/refund`: Refund

## 3. PCI Compliance (Mandatory)
VTEX handles sensitive card data via its **Secure Proxy**.
- **Rule**: Your backend MUST NEVER touch raw card data.
- **Implementation**: VTEX sends a `cardToken`. You exchange this token for encrypted metadata via VTEX's secure infrastructure.

## 4. Key Implementation Rules
- **Idempotency**: All protocol calls must handle `X-VTEX-Idempotency-Key` to avoid double-charging.
- **Latency**: Responses must be fast (< 5s). Use asynchronous callbacks for slower gateways.
- **Status Mapping**: Map gateway statuses accurately to the VTEX transaction flow (`undefined`, `authorized`, `cancelled`, `captured`).

## 5. Testing & Debugging
- **Payment Gateway log**: Check VTEX Admin -> Payments -> Transactions for the detailed JSON exchange.
- **Postman Collection**: Use the official VTEX Payments Postman collection to simulate protocol calls.

---

## Common CLI Commands

```bash
vtex link
vtex publish
```
After publishing, the provider must be configured in **CloudFront** (Payments Configuration) in the VTEX Admin.
