# 依赖升级结果报告

**项目**: 深源弱电工程ERP系统
**日期**: 2026-02-15
**状态**: 全部完成，系统正常运行

---

## 升级总览

本次升级涵盖前后端全部依赖，共 6 个 git commit，涉及 25+ 个依赖包的版本更新，以及前端构建工具从 Create React App 迁移到 Vite 的架构级变更。

| 维度 | 数据 |
|------|------|
| 升级依赖总数 | 25+ |
| Git commits | 6 |
| 前端文件变更 | 16+ |
| 后端文件变更 | 3 |
| 测试通过率 | 100% (44/44) |
| 系统状态 | 正常运行 |

---

## 一、后端 Python 依赖升级

### 版本变更明细

| 包名 | 升级前 | 升级后 | 变化幅度 |
|------|--------|--------|---------|
| **fastapi** | 0.104.1 | 0.129.0 | +24 minor |
| **uvicorn[standard]** | 0.24.0 | 0.40.0 | +16 minor |
| **sqlalchemy** | 2.0.23 | 2.0.46 | +23 patch |
| **pydantic** | 2.5.0 | 2.12.5 | +7 minor |
| **pydantic-settings** | 2.1.0 | 2.13.0 | +12 minor |
| **python-jose[cryptography]** | 3.3.0 | 3.5.0 | +2 minor |
| **python-multipart** | 0.0.6 | 0.0.22 | +16 patch |
| **python-dotenv** | 1.0.0 | 1.2.1 | +2 minor |
| **pandas** | 2.1.4 | 2.3.3 | +2 minor |
| **openpyxl** | 3.1.2 | 3.1.5 | +3 patch |
| **pytest** | 7.4.3 | 8.4.2 | +1 major |
| **pytest-asyncio** | 0.21.1 | 0.25.3 | +4 minor |
| **passlib[bcrypt]** | 1.7.4 | 1.7.4 | 不变 |

### 清理项
- 移除 `pathlib2==2.3.7`（Python 3 内置 pathlib）
- 去重 `python-multipart`（原文件中重复出现）

### 代码适配修改
- `ext.declarative_base()` → `sqlalchemy.orm.declarative_base()`（SQLAlchemy 弃用 API）
- `regex=` → `pattern=`（FastAPI Query 参数弃用警告）

---

## 二、前端构建工具迁移

### 核心变更：react-scripts → Vite

| 项目 | 迁移前 | 迁移后 |
|------|--------|--------|
| 构建工具 | react-scripts 5.0.1 | Vite 7.3.1 |
| 开发服务器启动 | `npm start` | `npx vite` |
| 构建命令 | `react-scripts build` | `tsc --noEmit && vite build` |
| 输出目录 | `build/` | `dist/` |
| 环境变量前缀 | `REACT_APP_*` | `VITE_*` |
| 入口文件 | `src/index.tsx` | `src/main.tsx` |
| HTML 位置 | `public/index.html` | `index.html`（项目根目录） |
| API 代理 | `package.json proxy` | `vite.config.ts server.proxy` |

### 新增构建依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| vite | ^7.3.1 | 构建工具 |
| @vitejs/plugin-react | ^5.1.4 | React 支持插件 |
| vite-tsconfig-paths | ^6.1.1 | TypeScript 路径解析 |

### 移除的包
- `react-scripts` (5.0.1)
- `web-vitals` (^2.1.4)
- `d3-scale` (^4.0.2)
- `d3-shape` (^3.2.0)

---

## 三、前端框架依赖升级

| 包名 | 升级前 | 升级后 | 变化幅度 |
|------|--------|--------|---------|
| **typescript** | ^4.9.5 | ~5.7 | +1 major |
| **antd** | ^5.26.6 | ^5.29.3 | +3 minor |
| **@ant-design/icons** | ^6.0.0 | ^6.1.0 | +1 minor |
| **axios** | ^1.11.0 | ^1.13.5 | +2 minor |
| **react-router-dom** | ^7.7.1 | ^7.13.0 | +6 minor |
| **@types/jest** | ^27.5.2 | ^30.0.0 | +3 major |
| **@types/node** | ^16.18.126 | ^25.2.3 | +9 major |

### TypeScript 配置升级

| 配置项 | 升级前 | 升级后 |
|--------|--------|--------|
| target | ES5 | ES2020 |
| module | esnext | ESNext |
| moduleResolution | node | bundler |
| types | — | `["vite/client", "jest"]` |

### Ant Design 版本决策
- 初始升级至 v6.3.0
- 根据用户要求降级至 v5.29.3（v5 最新版本）
- 确保与现有组件代码完全兼容

---

## 四、升级后修复项

升级完成后发现并修复了以下问题：

### 1. AWS 公网 IP 变更
- **问题**: 实例重启后公网 IP 从 `18.219.25.24` 变为 `18.218.95.233`
- **影响**: 浏览器无法通过旧 IP 访问
- **修复**: 更新了全部配置文件、脚本、CORS 配置和文档（约 50 处）

### 2. Swagger UI CDN 不可访问
- **问题**: FastAPI 默认使用 `cdn.jsdelivr.net` 加载 Swagger UI，国内网络无法访问
- **影响**: `/docs` 页面白屏
- **修复**: 自定义 Swagger UI 端点，CDN 切换为 `unpkg.com`

---

## 五、验证结果

### 后端验证
- pytest 44/44 测试全部通过 (100%)
- API 健康检查正常：`{"status":"healthy","database":"connected"}`
- 登录认证正常（HttpOnly Cookie 机制）
- Swagger UI 文档页面正常加载

### 前端验证
- TypeScript 编译零错误
- Vite 开发服务器正常运行（HMR 热更新）
- 登录页面正常显示和交互
- API 代理功能正常（Vite proxy → localhost:8000）
- 生产构建正常生成 `dist/` 目录

### 系统集成验证
- 前端 http://18.218.95.233:3000 正常访问
- 后端 http://18.218.95.233:8000 正常访问
- API 文档 http://18.218.95.233:8000/docs 正常加载
- CORS 跨域配置正常
- 用户登录全流程正常

---

## 六、当前系统依赖全景

### 后端 (Python 3.12)
```
fastapi==0.129.0
uvicorn[standard]==0.40.0
sqlalchemy==2.0.46
pydantic==2.12.5
pydantic-settings==2.13.0
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.22
python-dotenv==1.2.1
pandas==2.3.3
openpyxl==3.1.5
pytest==8.4.2
pytest-asyncio==0.25.3
```

### 前端 (Node.js)
```json
{
  "dependencies": {
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "react-router-dom": "^7.13.0",
    "axios": "^1.13.5",
    "antd": "^5.29.3",
    "@ant-design/icons": "^6.1.0"
  },
  "devDependencies": {
    "typescript": "~5.7",
    "vite": "^7.3.1",
    "@vitejs/plugin-react": "^5.1.4",
    "vite-tsconfig-paths": "^6.1.1",
    "@types/node": "^25.2.3",
    "@types/jest": "^30.0.0"
  }
}
```

---

## 七、升级 Git 提交记录

| 提交 | 说明 |
|------|------|
| `cb048db` | chore: upgrade all Python dependencies to latest stable versions |
| `f12cceb` | feat: migrate frontend from react-scripts to Vite |
| `382b570` | chore: upgrade TypeScript 4.9→5.7, antd 5→6, axios, react-router-dom |
| `1270ff6` | fix: downgrade antd to v5 per user requirement |
| `19a4ca2` | chore: update startup scripts for Vite migration |
| *(待提交)* | fix: update IP address and Swagger CDN for accessibility |
