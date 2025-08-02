# 深源ERP系统

一个专为工程项目管理而设计的企业资源规划(ERP)系统，提供项目管理、合同清单管理、文件管理和系统测试等核心功能。

## 目录

- [技术栈](#技术栈)
- [功能模块](#功能模块)
- [快速开始](#快速开始)
- [开发指南](#开发指南)
- [部署指南](#部署指南)
- [故障排除](#故障排除)
- [开发最佳实践](#开发最佳实践)

## 技术栈

### 后端
- **FastAPI** - 现代高性能Python Web框架
- **SQLAlchemy** - Python SQL工具包和ORM
- **PostgreSQL/SQLite** - 数据库
- **Uvicorn** - ASGI服务器

### 前端
- **React 19** - 用户界面库
- **TypeScript** - 类型安全的JavaScript
- **Ant Design** - 企业级UI组件库
- **Axios** - HTTP客户端
- **React Router** - 路由管理

## 功能模块

- ✅ **项目基础管理** - 项目创建、编辑、状态管理
- ✅ **合同清单管理** - Excel导入、清单解析、设备管理
- ✅ **系统测试管理** - 自动化测试、结果监控、统计分析
- 🚧 **系统分类管理** - 设备分类体系优化

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- NPM 8+

### 一键启动脚本

#### 🔵 开发模式
```bash
./scripts/start-erp-dev.sh
```
- **前端**：React开发服务器 (端口3000，热重载)
- **API连接**：localhost:8000 (本地)
- **适用**：VSCode Remote SSH开发
- **访问**：http://18.219.25.24:3000

#### 🟠 生产模式  
```bash
./scripts/start-erp-prod.sh
```
- **前端**：serve静态服务器 (端口8080，性能优化)
- **API连接**：18.219.25.24:8000 (公网)
- **适用**：生产部署、演示展示
- **访问**：http://18.219.25.24:8080

#### 🛑 统一停止
```bash
./scripts/stop-erp.sh
```
- 同时停止开发和生产模式的所有服务

> 📁 **详细脚本文档**：查看 [scripts/README.md](scripts/README.md) 了解所有脚本的详细用法

#### 📊 模式对比

| 特性 | 开发模式 (dev) | 生产模式 (prod) |
|------|---------------|----------------|
| **前端服务器** | React开发服务器 | serve静态服务器 |
| **端口** | 3000 | 8080 |
| **API连接** | localhost:8000 | 18.219.25.24:8000 |
| **构建** | 无需构建 | npm run build |
| **热重载** | ✅ 支持 | ❌ 不支持 |
| **性能** | 开发优化 | 生产优化 |
| **使用场景** | 代码开发调试 | 生产部署演示 |

### 手动启动

#### 后端启动
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端启动
```bash
cd frontend
npm install
export REACT_APP_API_BASE_URL=http://localhost:8000
npm start
```

## 开发指南

### 推荐开发方式

1. **VSCode + Remote SSH** (推荐)
   - 使用VSCode Remote SSH连接服务器
   - 前端访问: `http://localhost:3000`
   - 后端API文档: `http://localhost:8000/docs`

2. **环境变量配置**
   ```bash
   # 开发环境
   export HOST=0.0.0.0
   export PORT=3000
   export REACT_APP_API_BASE_URL=http://localhost:8000
   ```

3. **代码质量**
   - ESLint配置自动检查代码质量
   - TypeScript严格模式
   - React最佳实践遵循useCallback, useEffect等规范

### 项目结构
```
shenyuan-erp/
├── backend/          # FastAPI后端
│   ├── app/         
│   │   ├── api/     # API路由
│   │   ├── models/  # 数据库模型
│   │   ├── schemas/ # Pydantic模型
│   │   └── utils/   # 工具函数
│   └── tests/       # 单元测试
├── frontend/         # React前端
│   ├── src/
│   │   ├── components/ # 组件
│   │   ├── pages/     # 页面
│   │   ├── services/  # API调用
│   │   └── types/     # TypeScript类型
└── scripts/          # 部署脚本
```

## 部署指南

### 开发环境部署
```bash
./scripts/start-erp-dev.sh
```
**特点**：React热重载开发服务器，本地API连接，适合开发调试

### 生产环境部署
```bash
./scripts/start-erp-prod.sh
```
**特点**：静态文件优化服务器，公网API连接，适合生产展示

### 服务监控
- 查看日志：`tail -f backend/backend.log` 或 `tail -f frontend/frontend.log`
- 健康检查：`curl http://localhost:8000/health`
- 停止服务：`./stop-erp.sh`

## 故障排除

### 常见问题解决

#### 1. 前端显示"后端未连接"

**症状**：前端页面正常显示但连接状态显示"未连接"

**可能原因**：
- CORS配置问题
- 网络连接问题
- API端点配置错误

**解决步骤**：
```bash
# 1. 检查后端健康状态
curl http://localhost:8000/health

# 2. 检查前端到后端CORS
curl -H "Origin: http://localhost:3000" http://localhost:8000/health

# 3. 检查端口占用
sudo netstat -tlnp | grep :3000
sudo netstat -tlnp | grep :8000

# 4. 检查CORS配置（backend/app/main.py中）
# 确保allow_origins包含前端地址
```

**最终解决**：
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", ...],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

#### 2. 端口占用（wetty占用3000端口）

**症状**：`Something is already running on port 3000`

**解决方案**：
```bash
# 查找端口占用
sudo netstat -tlnp | grep :3000

# 删除wetty服务（安全，不影响Claude Code）
sudo systemctl stop wetty
sudo systemctl disable wetty
sudo rm /etc/systemd/system/wetty.service
sudo systemctl daemon-reload
npm uninstall -g wetty
```

#### 3. ESLint警告清理

**常见警告类型**：
- 未使用的imports
- useEffect依赖缺失
- 未使用的变量

**解决方案**：
```typescript
// 1. 清理未使用的imports
// 错误：import { Space, Button } from 'antd'; // Space未使用
// 正确：import { Button } from 'antd';

// 2. 修复useEffect依赖
// 错误：useEffect(() => { fetchData(); }, []);
// 正确：
const fetchData = useCallback(async () => {
  // 数据获取逻辑
}, [dependency1, dependency2]);

useEffect(() => {
  fetchData();
}, [fetchData]);
```

#### 4. API返回307重定向

**症状**：后端返回: `307 Temporary Redirect`

**原因**：FastAPI路由末尾斜杠问题

**解决方案**：
```typescript
// 前端API调用确保路径正确
// 错误：/api/v1/projects
// 正确：/api/v1/projects/
```

#### 5. 环境变量设置

**症状**：前端无法连接API地址

**解决方案**：
```bash
# 确保在npm start前设置环境变量
export REACT_APP_API_BASE_URL=http://localhost:8000
npm start

# 或在package.json的scripts中配置
"start": "REACT_APP_API_BASE_URL=http://localhost:8000 react-scripts start"
```

## 开发最佳实践

### 调试技巧排序

1. **网络连接调试**：
   - 使用`curl`测试API连通性
   - 检查浏览器Network面板
   - 确认CORS配置正确

2. **服务状态检查**：
   - `ps aux | grep uvicorn` - 检查后端进程
   - `ps aux | grep node` - 检查前端进程
   - `sudo netstat -tlnp` - 检查端口占用

3. **日志分析**：
   - 后端：`tail -f backend/backend.log`
   - 前端：`tail -f frontend/frontend.log`
   - 浏览器Console查看JavaScript错误

4. **CORS调试**：
   ```bash
   # 测试CORS配置是否正确
   curl -I -X OPTIONS http://localhost:8000/health \
     -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET"
   ```

### 开发流程

1. **开发环境**：
   - 使用VSCode Remote SSH
   - 前端localhost:3000，后端localhost:8000
   - 保持前后端端口一致性

2. **代码质量**：
   - 及时修复ESLint警告
   - 使用TypeScript严格模式
   - 正确使用React Hooks规范

3. **部署流程**：
   - 开发环境使用start-erp-dev.sh
   - 生产环境通过nginx反向代理
   - 定期备份数据库

4. **调试原则**：
   - 使用浏览器开发者工具
   - 检查网络配置
   - 使用服务器端日志排查

## AWS部署注意事项

### 安全组配置
确保EC2实例安全组开放以下端口：

| 端口 | 用途 | 来源 |
|------|------|------|
| 22 | SSH访问 | 您的IP |
| 8000 | 后端API | 0.0.0.0/0 |
| 3000 | 前端(开发) | 0.0.0.0/0 |
| 8080 | 前端(生产) | 0.0.0.0/0 |

### 配置步骤
1. 登录AWS控制台
2. 进入EC2 → 实例 → 选择实例
3. 安全标签 → 点击安全组
4. 编辑入站规则 → 添加上述端口
5. 保存更改

## 常见操作

遇到问题时的检查清单：
1. 查看[故障排除](#故障排除)部分
2. 检查服务状态
3. 使用诊断脚本：`./scripts/diagnose-frontend.sh`
4. 确认AWS安全组配置正确

## 📚 学习资源

### 技术文档
- [网络访问原理学习指南](docs/网络访问原理学习指南.md) - 深入理解前后端网络通信原理
- [脚本使用说明](scripts/README.md) - 详细的部署脚本文档

### 开发记录
- [CLAUDE.md](CLAUDE.md) - 项目开发记录和问题解决历史

## 文档信息

**最后更新**：2025-08-02  
**版本**：1.0.0