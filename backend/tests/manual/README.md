# 手动测试脚本目录

本目录包含各种手动测试脚本，用于验证特定功能和场景。这些脚本通常用于：

- 开发阶段的功能验证
- 复杂业务场景的端到端测试
- 故障排查和调试
- 性能测试和压力测试

## 文件说明

### 工作流测试
- `test_complete_workflow.py` - 申购单完整工作流测试（项目经理→采购员→部门主管→总经理）
- `test_workflow.py` - 申购单工作流API测试脚本

### 功能验证测试
- `test_edit_functionality.py` - 申购单编辑功能测试
- `validate_edit_functionality.py` - 编辑功能完整性验证

### 系统分类测试
- `test_system_category_api.py` - 系统分类API测试
- `test_system_category_creation.py` - 系统分类创建测试
- `verify_system_category_fix.py` - 系统分类修复验证

### 特定问题修复测试
- `test_array_fix.py` - 数组处理问题修复测试
- `test_quote_fix.py` - 询价功能修复测试

## 使用方法

这些脚本大多是独立运行的，使用前请确保：

1. 后端服务正在运行 (`http://localhost:8000`)
2. 数据库包含必要的测试数据
3. 具备相应的用户权限（部分脚本需要管理员权限）

## 运行示例

```bash
# 进入backend目录
cd /home/ubuntu/shenyuan-erp/backend

# 运行完整工作流测试
python tests/manual/test_complete_workflow.py

# 运行系统分类测试
python tests/manual/test_system_category_api.py
```

## 注意事项

- 这些脚本可能会修改数据库数据，建议在开发环境运行
- 部分脚本包含硬编码的测试数据，根据实际情况调整
- 脚本执行时间可能较长，请耐心等待结果