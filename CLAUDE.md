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

  ## 重要技术突破 (2025-08-02)

  ### AWS c7i-flex.large环境成功配置
  - 服务器配置升级至c7i-flex.large，完全支持Claude Code编译环境
  - VSCode Remote SSH稳定运行，实现云端开发环境
  - 公网IP: 18.219.25.24，支持多种访问方式

  ### 开发生产环境完全分离
  - **开发模式**(scripts/start-erp-dev.sh): React热重载 + localhost API连接
  - **生产模式**(scripts/start-erp-prod.sh): 静态优化服务器 + 公网API连接
  - 完美支持VSCode Remote SSH + Claude Code开发工作流

  ### 网络访问机制理解
  - 服务绑定0.0.0.0同时支持localhost和公网IP访问
  - localhost:8000/3000 - 开发调试最优选择
  - 18.219.25.24:8000/3000 - 远程访问和演示
  - 前后端通信: React(浏览器) → localhost:8000 → FastAPI(服务器)

  ### 关键问题解决模式
  1. **端口冲突处理**: 先停止服务./scripts/stop-erp.sh，强制清理残留进程
  2. **服务启动失败**: 检查端口占用 `sudo netstat -tlnp | grep :端口`
  3. **前端连接失败**: 验证CORS配置包含所有前端访问端口
  4. **进程管理**: 使用scripts/目录统一管理，避免手动kill进程

  ## 项目文档体系
  - README.md: 项目总览和快速开始
  - scripts/README.md: 详细脚本使用文档  
  - docs/网络访问原理学习指南.md: 深度技术学习资料
  - CLAUDE.md: 开发记录和问题解决历史

  ## 未来开发要点
  - 使用./scripts/start-erp-dev.sh启动开发环境
  - 遇到问题先查看故障排除文档和学习指南
  - 新功能开发前先阅读网络访问原理理解前后端通信
  - 定期备份重要配置和数据库文件