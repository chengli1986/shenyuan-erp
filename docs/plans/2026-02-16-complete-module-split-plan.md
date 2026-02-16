# Complete Purchase Module Split — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Finish the partially-completed file splits for `purchases.py` (1542→~500 lines) and `PurchaseEditForm.tsx` (1060→~200 lines), eliminating all code duplication.

**Architecture:** The new split files (`purchase_query.py`, `purchase_workflow.py`, `purchase_utils.py`, `usePurchaseEditForm.ts`) already exist and contain correct code. The work is to wire them in and remove the duplicated code from the original monolithic files. No new logic is written — only code deletion and import rewiring.

**Tech Stack:** Python/FastAPI backend, React/TypeScript/Vite frontend, SQLAlchemy ORM, Ant Design UI

**Baseline:** 44 backend tests passing, 24 purchase API routes registered.

---

## Task 1: Register new routers in `__init__.py`

**Files:**
- Modify: `backend/app/api/v1/__init__.py`

**Step 1: Add imports and router registrations**

In `backend/app/api/v1/__init__.py`, add the two new module imports and register their routers. The key constraint is that all three routers share the `/purchases` prefix.

Change line 9 from:
```python
from . import projects, project_files, contracts, file_upload, test_results, purchases, auth
```
to:
```python
from . import projects, project_files, contracts, file_upload, test_results, purchases, purchase_query, purchase_workflow, auth
```

After the existing purchases router block (after line 55), add:

```python
# 注册采购查询相关的API路由
api_router.include_router(
    purchase_query.router,
    prefix="/purchases",
    tags=["purchase-queries"]
)

# 注册采购工作流相关的API路由
api_router.include_router(
    purchase_workflow.router,
    prefix="/purchases",
    tags=["purchase-workflow"]
)
```

**Step 2: Verify routes are registered (expect duplicates temporarily)**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -c "
from app.main import app
routes = [r.path for r in app.routes if '/purchases' in str(getattr(r, 'path', ''))]
print(f'Purchase routes: {len(routes)}')
"
```
Expected: Route count > 24 (duplicates exist because purchases.py still has the old endpoints). This is expected and will be resolved in Task 2.

**Step 3: Run tests**

Run: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -m pytest tests/ --ignore=tests/manual -q`
Expected: 44 passed

---

## Task 2: Remove duplicate endpoints from `purchases.py`

**Files:**
- Modify: `backend/app/api/v1/purchases.py`

This is the critical step. Remove the sections that are duplicated in the split files. **Work from bottom to top** to preserve line numbers for earlier deletions.

**Step 1: Remove system categories section (lines 1383-1543)**

Delete from line 1383 (`# ========== 系统分类相关API ==========`) through line 1543 (end of file).

These endpoints are already in `purchase_query.py` lines 251-409:
- `GET /system-categories/by-project/{project_id}`
- `GET /system-categories/by-material`

**Step 2: Remove auxiliary recommend section (lines 1348-1381)**

Delete from line 1348 (`# ========== 辅材智能推荐 ==========`) through line 1381.

These endpoints are already in `purchase_query.py` lines 216-248:
- `GET /auxiliary/recommend`
- `POST /auxiliary/templates/`

**Step 3: Remove workflow endpoints section (lines 511-1109)**

Delete from line 511 (`@router.post("/{request_id}/submit"`) through line 1109 (end of `get_workflow_logs` function, just before line 1110 `@router.delete`).

These endpoints are already in `purchase_workflow.py`:
- `POST /{request_id}/submit`
- `POST /{request_id}/quote`
- `POST /{request_id}/return`
- `POST /{request_id}/dept-approve`
- `POST /{request_id}/final-approve`
- `POST /{request_id}/approve`
- `GET /{request_id}/workflow-logs`

**Step 4: Remove query endpoints section (lines 36-226)**

Delete from line 36 (`# ========== 合同清单物料查询 ==========`) through line 226 (end of `get_specifications_by_material`, just before line 227 `# ========== 申购单管理 ==========`).

These endpoints are already in `purchase_query.py` lines 23-213:
- `GET /contract-items/by-project/{project_id}`
- `GET /contract-items/{item_id}/details`
- `GET /material-names/by-project/{project_id}`
- `GET /specifications/by-material`

**Step 5: Clean up unused imports**

After removing the code, many imports in `purchases.py` will be unused. The remaining file only needs imports for CRUD + suppliers + delete/batch-delete. Update the import block (lines 1-33) to only what's needed:

```python
"""
采购请购API接口 - CRUD和供应商管理
"""

from typing import List, Optional, Any
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.api import deps
from app.core.database import get_db
from app.models.purchase import (
    PurchaseRequest, PurchaseRequestItem, PurchaseApproval,
    Supplier, PurchaseStatus, ItemType, ApprovalStatus
)
from app.models.project import Project
from app.models.contract import ContractItem
from app.models.user import User, UserRole
from app.schemas.purchase import (
    PurchaseRequestCreate, PurchaseRequestUpdate, PurchaseRequestInDB,
    PurchaseRequestWithItems, PurchaseRequestWithoutPrice,
    SupplierCreate, SupplierUpdate, SupplierInDB,
    PurchaseRequestListResponse, SupplierListResponse
)
from app.services.purchase_service import PurchaseService
from app.api.v1.purchase_utils import (
    get_managed_project_ids,
    check_project_manager_access,
    enrich_purchase_item_details,
    get_project_and_requester_names
)

router = APIRouter()
```

**Step 6: Replace inline utility code with imports from purchase_utils**

In the remaining CRUD functions, find any inline code that duplicates `purchase_utils.py` functions and replace with the imported versions. Specifically:

In `get_purchase_request` (detail endpoint), find the inline code that enriches item details (adds system_category_name, remaining_quantity) and replace with:
```python
enrich_purchase_item_details(db, result)
```

In `get_purchase_requests` (list endpoint), find the inline code that gets managed project IDs and replace with:
```python
managed_project_ids = get_managed_project_ids(db, current_user)
```

In `get_purchase_request`, find inline project/requester name lookups and replace with:
```python
project_name, requester_name = get_project_and_requester_names(db, request)
```

**Step 7: Verify exact 24 routes**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -c "
from app.main import app
routes = [(r.path, list(r.methods) if hasattr(r, 'methods') else []) for r in app.routes if '/purchases' in str(getattr(r, 'path', ''))]
for path, methods in sorted(routes):
    print(f'{methods} {path}')
print(f'\nTotal: {len(routes)}')
"
```
Expected: Exactly 24 routes (same as before).

**Step 8: Run tests**

Run: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -m pytest tests/ --ignore=tests/manual -q`
Expected: 44 passed

**Step 9: Verify file size**

Run: `wc -l backend/app/api/v1/purchases.py`
Expected: ~500 lines (down from 1542)

**Step 10: Commit**

```bash
git add backend/app/api/v1/purchases.py backend/app/api/v1/purchase_query.py backend/app/api/v1/purchase_utils.py backend/app/api/v1/purchase_workflow.py backend/app/api/v1/__init__.py
git commit -m "refactor: split purchases.py (1542 lines) into 4 focused modules

- purchases.py: CRUD + suppliers (~500 lines)
- purchase_workflow.py: submit/quote/approve/return (624 lines)
- purchase_query.py: contract/material/category queries (409 lines)
- purchase_utils.py: shared helpers (103 lines)

All 24 API paths unchanged. 44/44 tests passing."
```

---

## Task 3: Wire `PurchaseEditForm.tsx` to use the existing hook

**Files:**
- Modify: `frontend/src/pages/Purchase/PurchaseEditForm.tsx`

The hook `hooks/usePurchaseEditForm.ts` (618 lines) already exists with all state management, handlers, and API calls. Currently `PurchaseEditForm.tsx` has all of this inline — duplicating the hook.

**Step 1: Replace inline state/logic with hook import**

At the top of `PurchaseEditForm.tsx`, replace the inline state declarations and handler functions with:

```typescript
import { usePurchaseEditForm } from './hooks/usePurchaseEditForm';
import type { PurchaseEditItem, SpecificationOption, SystemCategory } from './hooks/usePurchaseEditForm';
```

Remove from `PurchaseEditForm.tsx`:
- The duplicate interface definitions (Project, SystemCategory, SpecificationOption, PurchaseEditItem) — lines 31-96
- The `generateId` function — line 29
- All `useState` declarations inside the component (they come from the hook)
- All `useEffect` hooks (they're in the hook)
- All handler functions: `handleMaterialNameChange`, `handleSpecificationChange`, `handleSystemCategoryChange`, `handleQuantityChange`, `handlePriceChange`, `handleItemTypeChange`, `handleAuxiliarySystemCategory`, `addItem`, `removeItem`, `updateItem`, `handleSave`

Replace with a single hook call at the top of the component:
```typescript
const {
  form,
  loading,
  projects,
  items,
  setItems,
  materialNames,
  isProjectManager,
  handleMaterialNameChange,
  handleSpecificationChange,
  handleSystemCategoryChange,
  handleQuantityChange,
  handlePriceChange,
  handleItemTypeChange,
  handleAuxiliarySystemCategory,
  addItem,
  removeItem,
  updateItem,
  handleSave,
} = usePurchaseEditForm(purchaseData?.id ?? 0);
```

Keep: the `columns` definition, the JSX return (Modal + Card + Table), the component props interface.

**Step 2: Verify TypeScript compilation**

Run: `cd /home/ubuntu/shenyuan-erp/frontend && npx tsc --noEmit`
Expected: zero errors

**Step 3: Verify line count**

Run: `wc -l frontend/src/pages/Purchase/PurchaseEditForm.tsx`
Expected: ~400-500 lines (columns + JSX remain, state/logic removed)

---

## Task 4: Extract items table to `PurchaseEditFormItems.tsx`

**Files:**
- Create: `frontend/src/pages/Purchase/PurchaseEditFormItems.tsx`
- Modify: `frontend/src/pages/Purchase/PurchaseEditForm.tsx`

**Step 1: Create `PurchaseEditFormItems.tsx`**

Extract the `columns` array definition and the `<Table>` component into a new file. This component receives all data and handlers as props.

```typescript
// frontend/src/pages/Purchase/PurchaseEditFormItems.tsx
import React from 'react';
import { Table, Select, InputNumber, Input, Popconfirm, Button } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import type { PurchaseEditItem, SpecificationOption, SystemCategory } from './hooks/usePurchaseEditForm';

interface PurchaseEditFormItemsProps {
  items: PurchaseEditItem[];
  materialNames: string[];
  isProjectManager: boolean;
  onMaterialNameChange: (itemId: string, name: string) => void;
  onSpecificationChange: (itemId: string, spec: string) => void;
  onSystemCategoryChange: (itemId: string, categoryId: number) => void;
  onQuantityChange: (itemId: string, qty: number) => void;
  onPriceChange: (itemId: string, price: number) => void;
  onItemTypeChange: (itemId: string, type: string) => void;
  onAuxiliarySystemCategory: (itemId: string, projectId: number) => void;
  onRemoveItem: (itemId: string) => void;
  onUpdateItem: (itemId: string, field: string, value: unknown) => void;
}

const PurchaseEditFormItems: React.FC<PurchaseEditFormItemsProps> = ({ ... }) => {
  const columns = [ /* move columns array here */ ];

  return (
    <Table
      columns={columns}
      dataSource={items}
      rowKey="id"
      pagination={false}
      scroll={{ x: 1000 }}
      size="small"
      bordered
    />
  );
};

export default PurchaseEditFormItems;
```

**Step 2: Update `PurchaseEditForm.tsx` to use the new component**

Replace the inline `columns` definition and `<Table>` with:

```typescript
import PurchaseEditFormItems from './PurchaseEditFormItems';

// In the JSX, replace the <Table> with:
<PurchaseEditFormItems
  items={items}
  materialNames={materialNames}
  isProjectManager={isProjectManager}
  onMaterialNameChange={handleMaterialNameChange}
  onSpecificationChange={handleSpecificationChange}
  onSystemCategoryChange={handleSystemCategoryChange}
  onQuantityChange={handleQuantityChange}
  onPriceChange={handlePriceChange}
  onItemTypeChange={handleItemTypeChange}
  onAuxiliarySystemCategory={handleAuxiliarySystemCategory}
  onRemoveItem={removeItem}
  onUpdateItem={updateItem}
/>
```

**Step 3: Verify TypeScript compilation**

Run: `cd /home/ubuntu/shenyuan-erp/frontend && npx tsc --noEmit`
Expected: zero errors

**Step 4: Verify final line counts**

Run:
```bash
wc -l frontend/src/pages/Purchase/PurchaseEditForm.tsx frontend/src/pages/Purchase/PurchaseEditFormItems.tsx frontend/src/pages/Purchase/hooks/usePurchaseEditForm.ts
```
Expected:
- `PurchaseEditForm.tsx`: ~150-200 lines (thin container)
- `PurchaseEditFormItems.tsx`: ~300-400 lines (table + columns)
- `usePurchaseEditForm.ts`: 618 lines (unchanged)

**Step 5: Commit**

```bash
git add frontend/src/pages/Purchase/PurchaseEditForm.tsx frontend/src/pages/Purchase/PurchaseEditFormItems.tsx frontend/src/pages/Purchase/hooks/usePurchaseEditForm.ts
git commit -m "refactor: split PurchaseEditForm.tsx (1060 lines) into 3 focused files

- PurchaseEditForm.tsx: container component (~200 lines)
- PurchaseEditFormItems.tsx: items table + columns (~350 lines)
- hooks/usePurchaseEditForm.ts: state management hook (618 lines)"
```

---

## Final Verification

After both commits:

**Backend:**
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate
python -m pytest tests/ --ignore=tests/manual -v
```
Expected: 44 passed

**Frontend:**
```bash
cd /home/ubuntu/shenyuan-erp/frontend && npx tsc --noEmit
```
Expected: zero errors

**File sizes:**
```bash
wc -l backend/app/api/v1/purchases.py backend/app/api/v1/purchase_query.py backend/app/api/v1/purchase_workflow.py backend/app/api/v1/purchase_utils.py frontend/src/pages/Purchase/PurchaseEditForm.tsx frontend/src/pages/Purchase/PurchaseEditFormItems.tsx frontend/src/pages/Purchase/hooks/usePurchaseEditForm.ts
```
Expected: No file > 650 lines (down from 1542 and 1060).

**Route count:**
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -c "
from app.main import app
routes = [r.path for r in app.routes if '/purchases' in str(getattr(r, 'path', ''))]
print(f'Purchase routes: {len(routes)}')
"
```
Expected: Exactly 24 routes.
