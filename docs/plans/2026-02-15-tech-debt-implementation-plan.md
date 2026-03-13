# 技术债务修复实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 修复代码审计中发现的所有 P0 安全问题、P1 代码质量问题和 P2 架构债务。

**方案:** 从最安全的改动（P0 配置变更）到最高风险的改动（P2 文件拆分）依次执行。每个任务一个 git commit。后端任务用 pytest 验证，前端任务用 `npx tsc --noEmit` 验证。

**技术栈:** Python/FastAPI 后端, React/TypeScript/Vite 前端, SQLAlchemy ORM, Ant Design UI

---

## 任务 1: P0 — 修复硬编码的 debug 模式

**涉及文件:**
- 修改: `backend/app/core/config.py:7`

**步骤 1: 将默认值改为 False**

在 `backend/app/core/config.py` 中，修改第 7 行：

```python
# 修改前
debug: bool = True

# 修改后
debug: bool = False
```

`.env` 文件中已有 `DEBUG=True`，pydantic-settings 会自动读取。生产环境如果没有 `.env` 则默认为 `False`。

**步骤 2: 验证后端可启动**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -c "from app.core.config import settings; print(f'debug={settings.debug}')"`
预期输出: `debug=True`（从 `.env` 读取）

**步骤 3: 运行测试**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -m pytest tests/ --ignore=tests/disabled --ignore=tests/manual -q`
预期: 全部测试通过

**步骤 4: 提交**

```bash
git add backend/app/core/config.py
git commit -m "fix(security): read debug mode from env, default False"
```

---

## 任务 2: P0 — 收紧 CORS 请求头配置

**涉及文件:**
- 修改: `backend/app/main.py:78-79`

**步骤 1: 替换通配符请求头**

在 `backend/app/main.py` 中，修改 CORS 中间件配置：

```python
# 修改前
    allow_headers=["*"],
    expose_headers=["*"],

# 修改后
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Length"],
```

**步骤 2: 验证后端可启动**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -c "from app.main import app; print('OK')"`
预期输出: `OK`

**步骤 3: 运行测试**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -m pytest tests/ --ignore=tests/disabled --ignore=tests/manual -q`
预期: 全部测试通过

**步骤 4: 提交**

```bash
git add backend/app/main.py
git commit -m "fix(security): restrict CORS allow/expose headers"
```

---

## 任务 3: P0 — 修复裸 except 语句

**涉及文件:**
- 修改: `backend/app/api/v1/file_upload.py:254`

**步骤 1: 替换裸 except**

在 `backend/app/api/v1/file_upload.py` 中，修改第 254 行：

```python
# 修改前
        except:
            pass

# 修改后
        except (OSError, IOError):
            pass
```

**步骤 2: 运行测试**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -m pytest tests/ --ignore=tests/disabled --ignore=tests/manual -q`
预期: 全部测试通过

**步骤 3: 提交**

```bash
git add backend/app/api/v1/file_upload.py
git commit -m "fix(security): replace bare except with specific exception types"
```

---

## 任务 4: P1 — 将 main.py 中的 print() 替换为 logging

**涉及文件:**
- 修改: `backend/app/main.py`

**步骤 1: 添加 logger 并替换 print**

在 `backend/app/main.py` 顶部添加 `import logging` 并创建 logger。替换 `lifespan` 函数中的 4 处 `print()` 调用：

```python
# 在已有 import 之后添加
import logging

logger = logging.getLogger(__name__)

# 在 lifespan 函数中替换:
#   print("正在创建数据库表...")    → logger.info("正在创建数据库表...")
#   print("数据库表创建完成！")     → logger.info("数据库表创建完成！")
#   print("启动测试调度器...")      → logger.info("启动测试调度器...")
#   print("正在关闭测试调度器...")  → logger.info("正在关闭测试调度器...")
```

**步骤 2: 运行测试**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -m pytest tests/ --ignore=tests/disabled --ignore=tests/manual -q`
预期: 全部测试通过

**步骤 3: 提交**

```bash
git add backend/app/main.py
git commit -m "refactor: replace print() with logging in main.py"
```

---

## 任务 5: P1 — 将 purchase.ts 中的 fetch() 迁移为 axios

**涉及文件:**
- 修改: `frontend/src/services/purchase.ts`

**步骤 1: 删除 API_BASE 和 handleResponse，转换所有 fetch 调用**

文件已导入 `api`。删除 `API_BASE` 常量（第 26 行）和 `handleResponse` 函数（第 29-35 行）。转换每个 `fetch()` 调用：

**需要转换的函数（13 处 fetch 调用）：**

| 函数名 | 方法 | 路径 |
|--------|------|------|
| `getContractItemDetails` | GET | `purchases/contract-items/${itemId}/details` |
| `getPurchaseRequests` | GET | `purchases/?${queryString}` |
| `getPurchaseRequest` | GET | `purchases/${requestId}` |
| `updatePurchaseRequest` | PUT | `purchases/${requestId}` |
| `submitPurchaseRequest` | POST | `purchases/${requestId}/submit` |
| `quotePurchaseRequest` | POST | `purchases/${requestId}/quote` |
| `approvePurchaseRequest` | POST | `purchases/${requestId}/approve` |
| `deletePurchaseRequest` | DELETE | `purchases/${requestId}` |
| `getSuppliers` | GET | `purchases/suppliers/?${queryString}` |
| `createSupplier` | POST | `purchases/suppliers/` |
| `updateSupplier` | PUT | `purchases/suppliers/${supplierId}` |
| `getAuxiliaryRecommendations` | GET | `purchases/auxiliary/recommend?...` |
| `createAuxiliaryTemplate` | POST | `purchases/auxiliary/templates/` |

**转换模式：**

```typescript
// GET: fetch → api.get
// 修改前:
const response = await fetch(`${API_BASE}/purchases/${requestId}`);
return handleResponse<PurchaseRequestWithItems>(response);
// 修改后:
const response = await api.get(`purchases/${requestId}`);
return response.data;

// POST + body: fetch → api.post
// 修改前:
const response = await fetch(`${API_BASE}/purchases/${requestId}/quote`, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(quoteData),
});
return handleResponse<PurchaseRequest>(response);
// 修改后:
const response = await api.post(`purchases/${requestId}/quote`, quoteData);
return response.data;

// PUT: fetch → api.put
// 修改前:
const response = await fetch(`${API_BASE}/purchases/${requestId}`, {
  method: 'PUT', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(updateData),
});
return handleResponse<PurchaseRequest>(response);
// 修改后:
const response = await api.put(`purchases/${requestId}`, updateData);
return response.data;

// DELETE: fetch → api.delete
// 修改前:
const response = await fetch(`${API_BASE}/purchases/${requestId}`, { method: 'DELETE' });
return handleResponse<{ detail: string }>(response);
// 修改后:
const response = await api.delete(`purchases/${requestId}`);
return response.data;
```

**步骤 2: 验证 TypeScript 编译**

运行: `cd /home/ubuntu/shenyuan-erp/frontend && npx tsc --noEmit`
预期: 零错误

**步骤 3: 提交**

```bash
git add frontend/src/services/purchase.ts
git commit -m "refactor: migrate all fetch() to axios api service in purchase.ts"
```

---

## 任务 6: P1 — 将 contract.ts 中的 fetch() 迁移为 axios

**涉及文件:**
- 修改: `frontend/src/services/contract.ts`

**步骤 1: 添加 api 导入，删除 API_BASE/handleResponse，转换 fetch 调用，删除硬编码数据**

在顶部添加 `import api from './api';`。

删除 `API_BASE` 常量（第 22 行）和 `handleResponse` 函数（第 25-31 行）。

删除 `getSystemCategories` 中的硬编码静态数据块（第 82-106 行）——用 API 调用替换整个函数体。

**需要转换的函数（13 处 fetch 调用）：**

| 函数名 | 方法 | 路径 |
|--------|------|------|
| `getContractVersions` | GET | `contracts/projects/${projectId}/contract-versions` |
| `getCurrentContractVersion` | GET | `contracts/projects/${projectId}/contract-versions/current` |
| `createContractVersion` | POST | `contracts/projects/${projectId}/contract-versions` |
| `getSystemCategories` | GET | `contracts/projects/${projectId}/versions/${versionId}/categories-working` |
| `createSystemCategory` | POST | `contracts/projects/${projectId}/versions/${versionId}/categories` |
| `getContractItems` | GET | `contracts/projects/${projectId}/versions/${versionId}/items?${query}` |
| `getContractItem` | GET | `contracts/projects/${projectId}/versions/${versionId}/items/${itemId}` |
| `createContractItem` | POST | `contracts/projects/${projectId}/versions/${versionId}/items` |
| `updateContractItem` | PUT | `contracts/projects/${projectId}/versions/${versionId}/items/${itemId}` |
| `getContractSummary` | GET | `contracts/projects/${projectId}/contract-summary` |
| `uploadContractExcel` | POST | `upload/projects/${projectId}/upload-contract-excel`（FormData） |
| `getContractFiles` | GET | `upload/projects/${projectId}/contract-files` |
| `deleteContractFile` | DELETE | `upload/projects/${projectId}/contract-files/${versionId}` |

**特殊情况 — `uploadContractExcel` 使用 FormData：**

```typescript
// 修改前:
const response = await fetch(`${API_BASE}/upload/projects/${projectId}/upload-contract-excel`, {
  method: 'POST', body: uploadFormData,
});
return handleResponse<ExcelUploadResponse>(response);

// 修改后:
const response = await api.post(
  `upload/projects/${projectId}/upload-contract-excel`,
  uploadFormData,
  { headers: { 'Content-Type': 'multipart/form-data' } }
);
return response.data;
```

**特殊情况 — `getSystemCategories` 删除硬编码数据：**

```typescript
// 修改后: 干净的实现，无硬编码数据
export async function getSystemCategories(
  projectId: number,
  versionId: number
): Promise<SystemCategory[]> {
  try {
    const response = await api.get(
      `contracts/projects/${projectId}/versions/${versionId}/categories-working`
    );
    return response.data;
  } catch {
    return [];
  }
}
```

**步骤 2: 验证 TypeScript 编译**

运行: `cd /home/ubuntu/shenyuan-erp/frontend && npx tsc --noEmit`
预期: 零错误

**步骤 3: 提交**

```bash
git add frontend/src/services/contract.ts
git commit -m "refactor: migrate all fetch() to axios api service in contract.ts

Remove hardcoded static data in getSystemCategories."
```

---

## 任务 7: P1 — 删除所有 console.log 语句

**涉及文件（11 个文件，42 处）：**
- `frontend/src/components/Contract/ContractItemList.tsx`（17 处）
- `frontend/src/pages/Contract/ContractManagement.tsx`（6 处）
- `frontend/src/pages/Purchase/SimplePurchaseDetail.tsx`（6 处）
- `frontend/src/components/Contract/ContractVersionList.tsx`（3 处）
- `frontend/src/pages/Purchase/SimplePurchaseList.tsx`（2 处）
- `frontend/src/components/Purchase/PurchaseQuoteForm.tsx`（2 处）
- `frontend/src/pages/SystemTest/SystemTestDashboard.tsx`（2 处）
- `frontend/src/App.tsx`（1 处）
- `frontend/src/components/CreateProjectModal.tsx`（1 处）
- `frontend/src/components/EditProjectModal.tsx`（1 处）
- `frontend/src/components/ProjectFileManager.tsx`（1 处）

**不要修改:** `frontend/src/services/api.ts` — 其中的 `console.error` 是有意保留的 API 错误日志。

**步骤 1: 删除所有 console.log 行**

删除上述 11 个文件中所有包含 `console.log(` 的行。如发现 `console.warn(` 也一并删除。

对于 `App.tsx` 第 130 行的 console.log，直接删除即可：

```typescript
// 修改前
console.log(`${key} 功能开发中...`);

// 修改后: 删除这一行，菜单点击本身已不会执行任何操作
```

**步骤 2: 验证 TypeScript 编译**

运行: `cd /home/ubuntu/shenyuan-erp/frontend && npx tsc --noEmit`
预期: 零错误

**步骤 3: 提交**

```bash
git add -A frontend/src/
git commit -m "cleanup: remove 42 console.log debug statements from frontend"
```

---

## 任务 8: P1 — 修复 TypeScript `any` 类型

**涉及文件（15 个文件，26 处）：**
- `frontend/src/services/projectFile.ts`（5 处）
- `frontend/src/pages/Purchase/SimplePurchaseList.tsx`（5 处）
- `frontend/src/components/ProjectFileManager.tsx`（2 处）
- `frontend/src/components/Purchase/WorkflowHistory.tsx`（2 处）
- `frontend/src/services/purchase.ts`（2 处）
- 其他 10 个文件各 1 处

**每种模式的修复策略：**

1. **`catch (error: any)`** → `catch (error: unknown)` + 类型守卫：
```typescript
// 修改前
} catch (error: any) {
  message.error(error.message || '操作失败');
}

// 修改后
} catch (error: unknown) {
  const msg = error instanceof Error ? error.message : '操作失败';
  message.error(msg);
}
```

2. **`items: any[]`** → 使用已有类型或 `Record<string, unknown>[]`

3. **函数参数 `(value: any, record: any)`** → 使用组件的行类型或 `Record<string, unknown>`

**步骤 1: 修复全部 26 处**

对每个文件应用上述模式。对于表格 render 函数中类型复杂且不值得定义的 record，使用 `Record<string, unknown>` 代替 `any`。

**步骤 2: 验证 TypeScript 编译**

运行: `cd /home/ubuntu/shenyuan-erp/frontend && npx tsc --noEmit`
预期: 零错误

**步骤 3: 提交**

```bash
git add -A frontend/src/
git commit -m "refactor: replace 26 TypeScript 'any' types with proper types"
```

---

## 任务 9: P2 — 删除残留的 .bak 和 disabled 测试文件

**需要删除的文件：**
- `backend/tests/unit/test_purchase_simple_broken.py.bak`
- `backend/tests/unit/test_purchase_broken.py.bak`
- `backend/tests/integration/test_purchase_api_broken.py.bak`
- `backend/tests/integration/test_purchase_api_simple_broken.py.bak`
- `backend/tests/disabled/` 目录下全部 11 个文件

**步骤 1: 删除文件**

```bash
rm backend/tests/unit/*.bak
rm backend/tests/integration/*.bak
rm -rf backend/tests/disabled/
```

**步骤 2: 运行测试确认无影响**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -m pytest tests/ --ignore=tests/manual -q`
预期: 全部测试通过（这些文件本来就被忽略/禁用）

**步骤 3: 提交**

```bash
git add -A backend/tests/
git commit -m "cleanup: remove .bak files and disabled test directory"
```

---

## 任务 10: P2 — 完善数据库驱动配置

**涉及文件:**
- 修改: `backend/app/core/config.py`
- 修改: `backend/app/core/database.py`

**步骤 1: 在 Settings 中添加 effective_database_url 属性**

在 `backend/app/core/config.py` 的 `model_config` 之前添加计算属性：

```python
    @property
    def effective_database_url(self) -> str:
        if self.database_driver == "postgresql":
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        return self.database_url  # 默认 SQLite
```

**步骤 2: 在 database.py 中使用 effective_database_url**

在 `backend/app/core/database.py` 中，修改第 12 行：

```python
# 修改前
DATABASE_URL = settings.database_url

# 修改后
DATABASE_URL = settings.effective_database_url
```

**步骤 3: 验证 SQLite 仍然正常工作**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -c "from app.core.database import DATABASE_URL; print(DATABASE_URL)"`
预期输出: `sqlite:///./erp_test.db`（因为 `.env` 中是 `DATABASE_DRIVER=sqlite`）

**步骤 4: 运行测试**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -m pytest tests/ --ignore=tests/disabled --ignore=tests/manual -q`
预期: 全部测试通过

**步骤 5: 提交**

```bash
git add backend/app/core/config.py backend/app/core/database.py
git commit -m "feat: wire up DATABASE_DRIVER env var to auto-build database URL"
```

---

## 任务 11: P2 — 添加 React Error Boundary

**涉及文件:**
- 新建: `frontend/src/components/ErrorBoundary.tsx`
- 修改: `frontend/src/App.tsx`

**步骤 1: 创建 ErrorBoundary 组件**

创建 `frontend/src/components/ErrorBoundary.tsx`：

```tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button, Result } from 'antd';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Result
          status="error"
          title="页面出现错误"
          subTitle={this.state.error?.message || '发生了未知错误'}
          extra={
            <Button type="primary" onClick={() => window.location.reload()}>
              刷新页面
            </Button>
          }
        />
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
```

**步骤 2: 在 App 根组件中包裹 ErrorBoundary**

在 `frontend/src/App.tsx` 中导入并包裹：

```tsx
// 添加导入
import ErrorBoundary from './components/ErrorBoundary';

// 在 App 函数中包裹:
function App() {
  return (
    <ErrorBoundary>
      <ConfigProvider locale={zhCN}>
        <ConnectionProvider>
          <Router>
            <AppContent />
          </Router>
        </ConnectionProvider>
      </ConfigProvider>
    </ErrorBoundary>
  );
}
```

**步骤 3: 验证 TypeScript 编译**

运行: `cd /home/ubuntu/shenyuan-erp/frontend && npx tsc --noEmit`
预期: 零错误

**步骤 4: 提交**

```bash
git add frontend/src/components/ErrorBoundary.tsx frontend/src/App.tsx
git commit -m "feat: add React ErrorBoundary for graceful crash handling"
```

---

## 任务 12: P2 — 拆分 purchases.py（1542 行 → 4 个文件）

**涉及文件:**
- 修改: `backend/app/api/v1/purchases.py`（保留 CRUD，约 400 行）
- 新建: `backend/app/api/v1/purchase_workflow.py`（工作流操作，约 400 行）
- 新建: `backend/app/api/v1/purchase_query.py`（合同清单查询，约 400 行）
- 新建: `backend/app/api/v1/purchase_utils.py`（共享工具函数，约 300 行）
- 修改: `backend/app/api/v1/__init__.py`（注册新路由）

**步骤 1: 阅读当前 purchases.py 并确定函数边界**

阅读完整文件，确定哪些函数属于哪个模块：

- **purchase_utils.py**: 跨模块使用的工具函数 — 权限检查、分页辅助、价格脱敏、`get_purchase_item_dict`、响应格式化。这些不是路由端点。
- **purchase_query.py**: 只读查询端点 — `get_contract_items_by_project`、`get_material_names`、`get_specifications`、`get_contract_item_details`、`get_system_categories_by_project`、`get_system_categories_by_material`。全部是 GET 请求。
- **purchase_workflow.py**: 状态变更的工作流端点 — `submit_purchase_request`、`quote_purchase_request`、`approve_purchase_request`、`return_purchase_request`、`get_workflow_logs`。这些会修改申购单状态。
- **purchases.py**（保留）: 核心 CRUD — `get_purchase_requests`（列表）、`get_purchase_request`（详情）、`create_purchase_request`、`update_purchase_request`、`delete_purchase_request`、`batch_delete_purchase_requests`。

**步骤 2: 创建 purchase_utils.py**

提取所有非路由工具函数。该模块没有 router。

```python
# backend/app/api/v1/purchase_utils.py
"""采购模块工具函数"""

from sqlalchemy.orm import Session
from app.models.project import Project
# ... 按需导入

def get_managed_project_ids(db: Session, user) -> list[int] | None:
    """获取项目经理负责的项目ID列表。其他角色返回 None。"""
    ...

def get_purchase_item_dict(item, db: Session, include_price: bool = True) -> dict:
    """将 PurchaseRequestItem 转换为包含关联数据的字典。"""
    ...

# ... 其他工具函数
```

**步骤 3: 创建 purchase_query.py**

提取查询端点，创建独立 router：

```python
# backend/app/api/v1/purchase_query.py
"""采购模块 - 合同清单查询/物料查询/系统分类 API"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
# ... 其他导入

router = APIRouter()

@router.get("/contract-items/by-project/{project_id}")
def get_contract_items_by_project(...):
    ...

# ... 其他查询端点
```

**步骤 4: 创建 purchase_workflow.py**

提取工作流端点，创建独立 router：

```python
# backend/app/api/v1/purchase_workflow.py
"""采购模块 - 工作流操作：提交/询价/审批/退回"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
# ... 其他导入

router = APIRouter()

@router.post("/{request_id}/submit")
def submit_purchase_request(...):
    ...

# ... 其他工作流端点
```

**步骤 5: 更新 __init__.py 注册新路由**

在 `backend/app/api/v1/__init__.py` 中添加导入和注册：

```python
from . import purchases, purchase_workflow, purchase_query, auth
# ... 现有导入

# 注册采购子路由（全部在 /purchases 前缀下）
api_router.include_router(
    purchases.router,
    prefix="/purchases",
    tags=["purchases"]
)
api_router.include_router(
    purchase_workflow.router,
    prefix="/purchases",
    tags=["purchase-workflow"]
)
api_router.include_router(
    purchase_query.router,
    prefix="/purchases",
    tags=["purchase-queries"]
)
```

**步骤 6: 运行测试**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -m pytest tests/ --ignore=tests/disabled --ignore=tests/manual -v`
预期: 全部测试通过。API 路径不变。

**步骤 7: 验证 API 端点仍然可用**

运行: `cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -c "from app.main import app; routes = [r.path for r in app.routes]; print(f'{len(routes)} routes registered'); assert '/api/v1/purchases/' in str(routes)"`

**步骤 8: 提交**

```bash
git add backend/app/api/v1/purchases.py backend/app/api/v1/purchase_workflow.py backend/app/api/v1/purchase_query.py backend/app/api/v1/purchase_utils.py backend/app/api/v1/__init__.py
git commit -m "refactor: split purchases.py (1542 lines) into 4 focused modules

- purchases.py: CRUD operations (~400 lines)
- purchase_workflow.py: submit/quote/approve/return (~400 lines)
- purchase_query.py: contract/material/category queries (~400 lines)
- purchase_utils.py: shared helpers (~300 lines)

All API paths unchanged."
```

---

## 任务 13: P2 — 拆分 PurchaseEditForm.tsx（1060 行 → 3 个文件）

**涉及文件:**
- 修改: `frontend/src/pages/Purchase/PurchaseEditForm.tsx`（保留为容器组件，约 200 行）
- 新建: `frontend/src/pages/Purchase/PurchaseEditFormItems.tsx`（明细项表格，约 400 行）
- 新建: `frontend/src/pages/Purchase/hooks/usePurchaseEditForm.ts`（状态管理 hook，约 400 行）

**步骤 1: 阅读完整文件确定边界**

阅读 `PurchaseEditForm.tsx`，确定：
- 状态变量和数据获取逻辑 → `usePurchaseEditForm.ts`
- 明细项表格渲染和行级事件处理 → `PurchaseEditFormItems.tsx`
- 整体布局、表单结构、提交按钮 → 保留在 `PurchaseEditForm.tsx`

**步骤 2: 创建自定义 hook**

将所有 `useState`、`useEffect`、数据获取函数和处理函数提取到 `hooks/usePurchaseEditForm.ts`。hook 返回组件需要的所有状态和处理函数。

```typescript
// frontend/src/pages/Purchase/hooks/usePurchaseEditForm.ts
import { useState, useEffect, useCallback } from 'react';
import { message } from 'antd';
import api from '../../../services/api';
// ... 其他导入

export function usePurchaseEditForm(purchaseId: number) {
  // 所有状态声明移到这里
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<EditItem[]>([]);
  // ... 所有其他状态

  // 所有数据获取和处理函数移到这里
  const loadPurchaseData = useCallback(async () => { ... }, [purchaseId]);
  const handleSave = useCallback(async () => { ... }, [items]);
  // ... 所有其他处理函数

  return {
    loading, items, setItems,
    handleSave, loadPurchaseData,
    // ... 所有其他导出的状态/处理函数
  };
}
```

**步骤 3: 创建 PurchaseEditFormItems 组件**

将明细项表格（列定义 + Table 组件）提取为独立组件：

```typescript
// frontend/src/pages/Purchase/PurchaseEditFormItems.tsx
import React from 'react';
import { Table, Select, InputNumber, Input } from 'antd';
// ... 其他导入

interface PurchaseEditFormItemsProps {
  items: EditItem[];
  onItemChange: (id: string, field: string, value: unknown) => void;
  // ... 其他需要的 props
}

const PurchaseEditFormItems: React.FC<PurchaseEditFormItemsProps> = ({
  items, onItemChange, ...
}) => {
  const columns = [ ... ];  // 从父组件移来
  return <Table dataSource={items} columns={columns} ... />;
};

export default PurchaseEditFormItems;
```

**步骤 4: 简化 PurchaseEditForm.tsx**

父组件变成薄壳：

```typescript
// frontend/src/pages/Purchase/PurchaseEditForm.tsx
import React from 'react';
import { Card, Button, Space } from 'antd';
import { usePurchaseEditForm } from './hooks/usePurchaseEditForm';
import PurchaseEditFormItems from './PurchaseEditFormItems';

const PurchaseEditForm: React.FC<Props> = ({ purchaseId, ... }) => {
  const { loading, items, handleSave, ... } = usePurchaseEditForm(purchaseId);

  return (
    <Card title="编辑申购单" extra={<Button onClick={handleSave}>保存</Button>}>
      <PurchaseEditFormItems items={items} onItemChange={...} />
    </Card>
  );
};
```

**步骤 5: 验证 TypeScript 编译**

运行: `cd /home/ubuntu/shenyuan-erp/frontend && npx tsc --noEmit`
预期: 零错误

**步骤 6: 提交**

```bash
git add frontend/src/pages/Purchase/PurchaseEditForm.tsx frontend/src/pages/Purchase/PurchaseEditFormItems.tsx frontend/src/pages/Purchase/hooks/usePurchaseEditForm.ts
git commit -m "refactor: split PurchaseEditForm.tsx (1060 lines) into 3 focused files

- PurchaseEditForm.tsx: container component (~200 lines)
- PurchaseEditFormItems.tsx: items table (~400 lines)
- hooks/usePurchaseEditForm.ts: state management hook (~400 lines)"
```

---

## 最终验证

全部 13 个任务完成后：

**后端验证：**
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate
python -m pytest tests/ --ignore=tests/manual -v
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
curl -s http://localhost:8000/health | python -m json.tool
```

**前端验证：**
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npx tsc --noEmit
npx vite build
```

**集成验证：**
```bash
# 登录测试
curl -s -X POST http://localhost:8000/api/v1/auth/login -d "username=admin&password=admin123" | python -m json.tool

# 申购单 API 测试
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -d "username=admin&password=admin123" | python -m json.tool | grep access_token | cut -d'"' -f4)
curl -s http://localhost:8000/api/v1/purchases/ -H "Authorization: Bearer $TOKEN" | python -m json.tool
```
