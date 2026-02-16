# Design: Complete Purchase Module Split (Tasks 12-13)

**Date:** 2026-02-16
**Status:** Approved
**Context:** Tech debt remediation plan tasks 12 and 13 — the final two items.

## Problem

The purchase module split was started but never completed:
- 3 new backend files created (`purchase_query.py`, `purchase_utils.py`, `purchase_workflow.py`) — good code, but dead (not registered)
- 1 new frontend hook created (`usePurchaseEditForm.ts`) — good code, working
- **Original `purchases.py` still has all 1542 lines** — duplicates everything in the new files
- **Original `PurchaseEditForm.tsx` still monolithic** — hook not wired in
- New routers not registered in `__init__.py`

This is worse than the starting point: we have code duplication without any benefit.

## Design

### Task A: Backend — Complete `purchases.py` Split

**Goal:** `purchases.py` 1542 → ~500 lines (CRUD + suppliers only)

#### What stays in `purchases.py`:
- CRUD endpoints: `get_purchase_requests`, `get_purchase_request`, `create_purchase_request`, `update_purchase_request`, `delete_purchase_request`, `batch_delete_purchase_requests`
- Supplier endpoints: `get_suppliers`, `create_supplier`, `update_supplier`

#### What gets removed (already in split files):
| Lines in purchases.py | Destination | Content |
|----------------------|-------------|---------|
| 36-226 | purchase_query.py | Contract item / material / specification queries |
| 511-1109 | purchase_workflow.py | Submit / quote / approve / return / workflow-logs |
| 1350-1542 | purchase_query.py | Auxiliary recommend / system categories |

#### Inline utility replacement:
Replace inline permission-check / enrichment code in `purchases.py` with imports from `purchase_utils.py`.

#### Router registration (`__init__.py`):
```python
from . import purchase_query, purchase_workflow

api_router.include_router(purchase_query.router, prefix="/purchases", tags=["purchase-queries"])
api_router.include_router(purchase_workflow.router, prefix="/purchases", tags=["purchase-workflow"])
```

#### Verification:
1. `python -m pytest tests/ --ignore=tests/manual -q` — all tests pass
2. `curl` key endpoints (list, detail, submit, query) — confirm routing works
3. Check route count matches before/after

### Task B: Frontend — Complete `PurchaseEditForm.tsx` Split

**Goal:** `PurchaseEditForm.tsx` 1060 → ~200 lines (thin container)

#### New file: `PurchaseEditFormItems.tsx`
Extract the items table (column definitions, Table component, row-level event handlers).

#### Trim `PurchaseEditForm.tsx`:
- Import and use `usePurchaseEditForm` hook (already exists)
- Import and render `PurchaseEditFormItems` component
- Keep only: Card layout, form structure, submit button

#### Verification:
1. `npx tsc --noEmit` — zero errors
2. Visual check that edit form loads and functions correctly

### Commit Strategy

Two atomic commits:
1. `refactor: split purchases.py (1542→~500 lines) into 4 focused modules`
2. `refactor: split PurchaseEditForm.tsx (1060→~200 lines) into 3 focused files`

### Risks

| Risk | Mitigation |
|------|-----------|
| Router path conflicts (duplicate endpoints) | Remove duplicates from purchases.py BEFORE registering new routers |
| Missing imports after extraction | Run tests + TypeScript check after each step |
| Frontend state management breakage | Hook already exists and works; table extraction is purely presentational |
