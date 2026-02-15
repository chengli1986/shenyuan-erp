# 技术债务修复设计文档

**日期**: 2026-02-15
**范围**: P0 安全修复 + P1 代码质量 + P2 架构优化

---

## P0 - 安全修复（3 项）

### 1. debug 模式从环境变量读取

**当前**: `backend/app/core/config.py:7` 硬编码 `debug: bool = True`
**修改**: 改为从 `.env` 读取，默认 `False`
```python
debug: bool = False  # 由 .env 中 DEBUG=True 覆盖
```
影响范围：仅 `config.py` 一个文件。

### 2. 收紧 CORS 配置

**当前**: `allow_headers=["*"]`, `expose_headers=["*"]`
**修改**: 限定为实际使用的 header
```python
allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
expose_headers=["Content-Length"],
```
影响范围：仅 `main.py`。

### 3. 修复裸 except

**当前**: `backend/app/api/v1/file_upload.py:254` 使用 `except: pass`
**修改**: 改为 `except (OSError, IOError): pass`
影响范围：仅 `file_upload.py`。

---

## P1 - 代码质量（4 项）

### 4. 统一 fetch() → axios api 服务

**当前**: `services/purchase.ts` 和 `services/contract.ts` 中有 26 处原生 `fetch()` 调用，绕过了 `api` 服务的认证和错误处理。

**修改方案**:
- 删除两个文件中的 `API_BASE` 常量和 `handleResponse` 函数
- 所有 `fetch()` 调用改为 `api.get()` / `api.post()` / `api.put()` / `api.delete()`
- `contract.ts` 中第 82-94 行的硬编码静态数据一并清除，改为实际 API 调用

**示例**:
```typescript
// 修复前
const response = await fetch(`${API_BASE}/purchases/contract-items/${itemId}/details`);
return handleResponse(response);

// 修复后
const response = await api.get(`purchases/contract-items/${itemId}/details`);
return response.data;
```

影响范围：`services/purchase.ts`, `services/contract.ts`, `components/Contract/ContractVersionList.tsx`

### 5. 清除 console.log（105 处）

**策略**:
- 删除所有 `console.log` 调试语句
- 保留 `services/api.ts` 中的 `console.error`（唯一的 API 错误日志点）
- 不引入新的日志框架（YAGNI，当前规模不需要）

影响范围：约 15 个前端文件。

### 6. 修复 TypeScript `any` 类型（26 处）

**策略**:
- `catch (error: any)` → `catch (error: unknown)` + 类型守卫
- 函数参数和返回值中的 `any` → 定义具体 interface
- API 响应中的 `items: any[]` → 使用已有的类型定义

影响范围：约 10 个前端文件。

### 7. 后端 print() → logging

**修改**: `main.py` 中 4 处 `print()` 改为 `logging.getLogger(__name__).info()`
影响范围：仅 `main.py`。

---

## P2 - 架构优化（5 项）

### 8. 拆分超大后端文件

**目标文件**: `backend/app/api/v1/purchases.py` (1542 行)

**拆分方案**:
```
purchases.py (1542行) → 拆为:
├── purchases.py         # 申购单 CRUD（~400行）
├── purchase_workflow.py  # 工作流操作：提交/询价/审批/退回（~400行）
├── purchase_query.py     # 合同清单查询/物料查询/系统分类 API（~400行）
└── purchase_utils.py     # 权限检查/分页/价格脱敏等工具函数（~300行）
```

**路由注册**: 各子模块创建自己的 `router`，在 `__init__.py` 中统一合并注册，对外 API 路径不变。

### 9. 添加 React Error Boundary

**修改**: 创建 `frontend/src/components/ErrorBoundary.tsx`，在 `App.tsx` 中包裹根组件。崩溃时显示友好的错误提示页面而非白屏。

### 10. 清理残留文件

- 删除 4 个 `.bak` 测试文件
- 清理 `tests/disabled/` 中无用的测试文件（已有 `tests/unit/` 和 `tests/integration/` 覆盖）

### 11. 数据库配置完善

**当前问题**: `config.py` 有 `database_driver` 和 PostgreSQL 配置字段，但 `database.py` 完全没用到它们，永远使用 `database_url`（默认 SQLite）。

**修改**: 让 `config.py` 根据 `DATABASE_DRIVER` 环境变量自动构建正确的 `database_url`：
```python
@property
def effective_database_url(self) -> str:
    if self.database_driver == "postgresql":
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    return self.database_url  # 默认 SQLite
```

注意：不安装 Alembic，因为当前仍使用 SQLite 开发，数据库迁移工具留到正式切换 PostgreSQL 时再引入。

### 12. 拆分超大前端文件

**目标文件**: `PurchaseEditForm.tsx` (1060 行)

**拆分方案**:
```
PurchaseEditForm.tsx (1060行) → 拆为:
├── PurchaseEditForm.tsx          # 主容器组件（~200行）
├── PurchaseEditFormItems.tsx     # 明细项表格和编辑逻辑（~400行）
└── hooks/usePurchaseEditForm.ts  # 表单状态管理 hook（~400行）
```

其他 >500 行的文件（`EnhancedPurchaseForm.tsx` 844 行、`SimplePurchaseDetail.tsx` 745 行）采用相同模式：抽取自定义 hook + 拆分子组件。

---

## 执行顺序

| 步骤 | 内容 | 风险 | 预计改动量 |
|------|------|------|-----------|
| 1 | P0 安全修复（3项） | 低 | ~20 行 |
| 2 | P1-7 后端 print→logging | 低 | ~10 行 |
| 3 | P1-4 统一 fetch→axios | 中 | ~200 行 |
| 4 | P1-5 清除 console.log | 低 | 删除 ~105 行 |
| 5 | P1-6 修复 any 类型 | 低 | ~50 行 |
| 6 | P2-10 清理残留文件 | 低 | 删除文件 |
| 7 | P2-11 数据库配置完善 | 低 | ~15 行 |
| 8 | P2-9 Error Boundary | 低 | 新增 ~50 行 |
| 9 | P2-8 拆分后端大文件 | 中 | 重构 ~1500 行 |
| 10 | P2-12 拆分前端大文件 | 高 | 重构 ~2600 行 |

每个步骤完成后 git commit，出问题可以单独 revert。

## 验证标准

- 后端：pytest 全部通过 + uvicorn 启动无错误
- 前端：TypeScript 编译零错误 + 页面功能正常
- API：登录 + 申购单 CRUD + 工作流全流程正常
