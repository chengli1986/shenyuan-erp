# 深源ERP系统 - 部署脚本集

本目录包含深源ERP系统的所有部署和管理脚本。

## 📋 脚本清单

### 🚀 启动脚本

#### `start-erp-dev.sh` - 开发环境启动
```bash
./scripts/start-erp-dev.sh
```

**功能**：
- 启动React开发服务器（端口3000，支持热重载）
- API连接localhost:8000（本地开发）
- 适用于VSCode Remote SSH开发

**特点**：
- ✅ 热重载支持
- ✅ 开发调试优化
- ✅ 本地API连接
- ✅ 详细启动日志

#### `start-erp-prod.sh` - 生产环境启动
```bash
./scripts/start-erp-prod.sh
```

**功能**：
- 构建生产版本（npm run build）
- 启动serve静态服务器（端口8080）
- API连接18.219.25.24:8000（公网）
- 适用于生产部署和演示

**特点**：
- ✅ 生产优化构建
- ✅ 静态文件服务
- ✅ 公网API连接
- ✅ 性能优化

### 🛑 管理脚本

#### `stop-erp.sh` - 服务停止
```bash
./scripts/stop-erp.sh
```

**功能**：
- 停止所有后端服务（uvicorn进程）
- 停止所有前端服务（serve和npm start进程）
- 清理残留进程
- 统一停止开发和生产模式

#### `check-erp.sh` - 状态检查
```bash
./scripts/check-erp.sh
```

**功能**：
- 检查后端服务运行状态
- 检查前端服务运行状态
- 测试API响应
- 测试前端页面访问
- 显示访问地址和端口信息

### 🔧 诊断脚本

#### `diagnose-frontend.sh` - 前端问题诊断
```bash
./scripts/diagnose-frontend.sh
```

**功能**：
- 检查网络接口配置
- 检查防火墙状态
- 检查端口监听情况
- 测试本地和公网访问
- AWS安全组检查提醒

## 🎯 使用场景

### 日常开发
```bash
# 启动开发环境
./scripts/start-erp-dev.sh

# 检查运行状态
./scripts/check-erp.sh

# 停止服务
./scripts/stop-erp.sh
```

### 生产部署
```bash
# 启动生产环境
./scripts/start-erp-prod.sh

# 检查运行状态
./scripts/check-erp.sh

# 停止服务
./scripts/stop-erp.sh
```

### 问题排查
```bash
# 检查系统状态
./scripts/check-erp.sh

# 前端问题诊断
./scripts/diagnose-frontend.sh

# 查看日志
tail -f backend/backend.log
tail -f frontend/frontend.log
```

## 📊 脚本对比

| 脚本 | 用途 | 前端服务器 | 端口 | API连接 | 使用场景 |
|------|------|-----------|------|---------|----------|
| `start-erp-dev.sh` | 开发启动 | React开发服务器 | 3000 | localhost:8000 | 开发调试 |
| `start-erp-prod.sh` | 生产启动 | serve静态服务器 | 8080 | 18.219.25.24:8000 | 生产演示 |
| `stop-erp.sh` | 服务停止 | - | - | - | 统一停止 |
| `check-erp.sh` | 状态检查 | - | - | - | 运维监控 |
| `diagnose-frontend.sh` | 问题诊断 | - | - | - | 故障排查 |

## 🔐 权限要求

所有脚本需要执行权限：
```bash
chmod +x scripts/*.sh
```

## 📝 日志文件

脚本执行后的日志文件位置：
- **后端日志**：`backend/backend.log`
- **前端日志**：`frontend/frontend.log`

## ⚠️ 注意事项

1. **AWS安全组**：确保开放端口3000、8000、8080
2. **环境变量**：脚本会自动设置必要的环境变量
3. **进程管理**：使用`stop-erp.sh`统一停止，避免手动kill进程
4. **端口冲突**：如遇端口占用，先运行`stop-erp.sh`清理

## 🚀 快速上手

1. **首次使用**：
   ```bash
   chmod +x scripts/*.sh
   ./scripts/start-erp-dev.sh
   ```

2. **访问系统**：
   - 开发模式：http://18.219.25.24:3000
   - 生产模式：http://18.219.25.24:8080
   - API文档：http://18.219.25.24:8000/docs

3. **停止服务**：
   ```bash
   ./scripts/stop-erp.sh
   ```

---

**维护者**：深源ERP开发团队  
**最后更新**：2025-08-02