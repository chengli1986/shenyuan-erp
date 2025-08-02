# 项目开发记录

  ## 技术栈
  - 后端：FastAPI + SQLAlchemy + PostgreSQL
  - 前端：React + TypeScript + Ant Design

  ## 当前进度
  - [x] 项目基础管理模块
  - [x] 合同清单管理模块  
  - [x] 系统测试管理模块
  - [ ] 系统分类管理优化

  ## 重要决策
  - 按照v62版本开发文档进行开发
  - 采用最小单位提交策略

  ## 系统测试模块功能
  - [x] 测试结果数据模型和API
  - [x] 系统测试仪表板界面
  - [x] 手动触发测试功能（单元/集成/全部）
  - [x] 测试历史记录和统计
  - [x] 每日自动测试调度
  - [x] 测试状态实时监控
  
  ## 下次重启后需要验证
  - [ ] 测试触发按钮功能正常
  - [ ] 前端状态显示正确

  ## 开发环境设置
  
  ### 开发模式 (start-erp-dev.sh)
  - 前端：React开发服务器，端口3000，支持热重载
  - API地址：http://localhost:8000 (本地连接)
  - 使用场景：VSCode Remote SSH开发
  - 访问：http://18.219.25.24:3000
  
  ### 生产模式 (start-erp-prod.sh)  
  - 前端：serve静态文件服务器，端口8080，性能优化
  - API地址：http://18.219.25.24:8000 (公网连接)
  - 使用场景：生产部署、演示展示
  - 访问：http://18.219.25.24:8080
  
  ### 脚本管理
  - 启动：./scripts/start-erp-dev.sh 或 ./scripts/start-erp-prod.sh
  - 停止：./scripts/stop-erp.sh (统一停止)
  - 监控：./scripts/check-erp.sh (状态检查)
  - 详细文档：scripts/README.md

  ## 重要问题解决记录

  ### 1. IP地址更新 (18.219.25.24)
  升级AWS实例后，所有脚本和配置需要更新IP地址：
  - 更新所有启动脚本中的IP地址
  - 更新前端环境变量文件
  - 更新CORS配置

  ### 2. 前端连接状态"未连接"问题
  **问题**：前端显示后端未连接，但API可以正常访问
  **原因**：CORS配置不包含前端端口
  **解决**：在backend/app/main.py的CORS middleware中添加前端端口

  ### 3. 端口占用问题
  **问题**：wetty占用3000端口
  **解决**：完全移除wetty服务，不影响Claude Code使用
  
  ### 4. 前端公网访问问题
  **问题**：serve监听IPv6而非IPv4
  **解决**：使用tcp://0.0.0.0:8080参数

  ### 5. ESLint警告清理
  **问题**：多个React组件存在ESLint警告
  **解决**：使用useCallback模式，修复useEffect依赖数组

  ## 核心调试技巧
  1. 使用curl测试API连接性
  2. 使用netstat检查端口占用
  3. 检查浏览器Network面板确认CORS问题
  4. 使用React useCallback防止不必要的重渲染

  ## 代码规范
  - React组件使用useCallback包装函数避免useEffect依赖问题
  - 清理所有未使用的import
  - 前端环境变量必须在npm start前设置
  - CORS配置必须包含所有前端访问端口