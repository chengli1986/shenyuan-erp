# 依赖升级设计文档

日期：2026-02-15

## 目标

前后端依赖全面升级，包括 react-scripts 迁移到 Vite。解决审计报告中标记的严重过时依赖问题。

## 后端 Python 依赖升级

### 删除

| 包 | 原因 |
|---|------|
| `pathlib2` | Python 3 内置 pathlib，完全多余 |
| `python-multipart`（重复行） | requirements.txt 中重复列出 |

### 升级

| 包 | 当前版本 | 目标 | 说明 |
|---|---------|------|------|
| `fastapi` | 0.104.1 | 最新稳定版 | 核心框架 |
| `uvicorn` | 0.24.0 | 最新稳定版 | ASGI 服务器 |
| `sqlalchemy` | 2.0.23 | 2.0.x 最新 | 补丁升级 |
| `pydantic` | 2.5.0 | 2.x 最新 | 次版本升级 |
| `pydantic-settings` | 2.1.0 | 最新 | 配套升级 |
| `python-jose` | 3.3.0 | 3.x 最新 | JWT 库 |
| `pytest` | 7.4.3 | 8.x 最新 | 测试框架 |
| `pandas` | 2.1.4 | 2.x 最新 | 不升3.0（breaking changes） |
| `openpyxl` | 3.1.2 | 3.x 最新 | Excel处理 |

### 暂不处理

| 包 | 原因 |
|---|------|
| `passlib` | 功能正常，替换为 bcrypt 直接调用是独立任务 |

## 前端依赖升级

### 阶段A：react-scripts → Vite 迁移

1. 安装 `vite`、`@vitejs/plugin-react`、`vite-tsconfig-paths`
2. 创建 `vite.config.ts`，配置 API 代理（替代 package.json proxy）
3. 移动 `index.html` 到项目根目录
4. 环境变量前缀 `REACT_APP_*` → `VITE_*`
5. 更新 `tsconfig.json` 添加 Vite 类型
6. 更新 npm scripts
7. 删除 react-scripts 和 CRA 相关包

### 阶段B：其他依赖升级

| 包 | 当前 | 目标 |
|---|------|------|
| `typescript` | ^4.9.5 | ^5.7.x |
| `antd` | ^5.26.6 | ^5.x 最新 |
| `react-router-dom` | ^7.7.1 | ^7.x 最新 |
| `axios` | ^1.11.0 | ^1.x 最新 |
| `@types/node` | ^16 | ^22 |
| `@types/jest` | ^27 | ^29 |

### 删除

| 包 | 原因 |
|---|------|
| `web-vitals` | 未使用 |
| `d3-scale` / `d3-shape` | 确认未直接使用后删除 |

### 启动脚本更新

- `start-erp-dev.sh`：适配 Vite dev server
- `start-erp-prod.sh`：适配 Vite build 输出（dist 目录）

## 执行顺序

1. 后端清理（删除无用包）
2. 后端升级（逐个升级 + 测试验证）
3. 前端 Vite 迁移
4. 前端依赖升级
5. 清理无用前端依赖
6. 启动脚本更新
7. 全面验证

## 验证标准

- 后端：pytest 全部通过 + uvicorn 启动无错误 + 登录 API 正常
- 前端 Vite：vite build 无错误 + 开发服务器启动 + 页面加载正常
- 前端依赖：TypeScript 编译无错误 + 核心页面功能正常

## 回滚策略

每个阶段完成后 git commit，出问题可以 git revert 回退。
