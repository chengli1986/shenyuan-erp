# 申购单功能测试套件说明

本文档说明最近开发的申购单核心功能的单元测试和集成测试使用方法。

## 📋 测试覆盖功能

### 单元测试（Unit Tests）
1. **申购单验证弹窗功能** (`test_purchase_validation.py`)
   - 主材数量限制验证
   - 辅材自由输入验证  
   - 错误消息格式化
   - 性能优化测试

2. **系统分类智能推荐** (`test_system_category_intelligence.py`)
   - 单系统自动推荐
   - 多系统用户选择
   - 历史数据兼容性
   - 推荐算法准确性

3. **剩余数量计算逻辑** (`test_remaining_quantity_calculation.py`)
   - 优化后的状态包含逻辑（只统计final_approved/completed）
   - 批量计算性能
   - 实时更新准确性
   - 边界条件处理

4. **批量操作功能** (`test_batch_operations.py`)
   - 批量删除权限验证
   - 事务安全性
   - 审计日志记录
   - 性能优化

5. **工作流审批功能** (`test_workflow_approval.py`)
   - 完整审批流程：提交→询价→部门审批→最终审批
   - 工作流退回功能
   - 角色权限验证
   - 状态转换一致性

### 集成测试（Integration Tests）
1. **工作流集成测试** (`test_purchase_workflow_integration.py`)
   - 端到端工作流生命周期
   - 智能系统分类API集成
   - 实时数量计算集成
   - 跨组件数据一致性

2. **前后端UI集成测试** (`test_purchase_ui_backend_integration.py`)
   - 表单提交与数据验证集成
   - 权限控制前后端一致性
   - 错误处理协调
   - 工作流UI状态显示

## 🚀 快速使用

### 运行所有测试
```bash
# 使用统一测试运行器
cd /home/ubuntu/shenyuan-erp/backend/tests
python test_suite_runner.py

# 或使用pytest直接运行
cd /home/ubuntu/shenyuan-erp/backend
python -m pytest tests/unit/test_purchase_*.py tests/integration/test_purchase_*.py -v
```

### 分类运行测试
```bash
# 只运行单元测试
python test_suite_runner.py --type unit

# 只运行集成测试  
python test_suite_runner.py --type integration

# 详细输出模式
python test_suite_runner.py --verbose

# 生成测试报告
python test_suite_runner.py --report
```

### 运行单个测试文件
```bash
# 运行申购单验证测试
python -m pytest tests/unit/test_purchase_validation.py -v

# 运行工作流集成测试
python -m pytest tests/integration/test_purchase_workflow_integration.py -v
```

## 📊 测试报告

### 测试运行器输出示例
```
============================================================
申购单功能测试套件 - 2025-01-28 15:30:00
============================================================

🔧 运行单元测试...
  🔍 运行: unit/test_purchase_validation.py
    ✅ 通过
  🔍 运行: unit/test_system_category_intelligence.py
    ✅ 通过
  🔍 运行: unit/test_remaining_quantity_calculation.py
    ✅ 通过
  🔍 运行: unit/test_batch_operations.py
    ✅ 通过
  🔍 运行: unit/test_workflow_approval.py
    ✅ 通过

🔗 运行集成测试...
  🔍 运行: integration/test_purchase_workflow_integration.py
    ✅ 通过
  🔍 运行: integration/test_purchase_ui_backend_integration.py
    ✅ 通过

============================================================
测试结果汇总
============================================================
总测试文件: 7
通过文件: 7
失败文件: 0
成功率: 100.0%
运行时间: 12.45秒

分类详情:
  ✅ unit: 5/5 (100.0%)
  ✅ integration: 2/2 (100.0%)

🎉 所有测试通过！
```

## 🛠️ 开发指南

### 添加新测试
1. 单元测试：添加到 `tests/unit/` 目录
2. 集成测试：添加到 `tests/integration/` 目录  
3. 文件命名：使用 `test_purchase_*.py` 格式
4. 更新 `test_suite_runner.py` 中的测试文件列表

### 测试编写规范
- 使用 pytest 框架
- Mock 外部依赖（数据库、API等）
- 包含正常场景和边界条件
- 添加清晰的测试文档字符串
- 使用描述性的断言消息

### Mock 对象使用
```python
from unittest.mock import Mock, patch

def test_example():
    with patch('app.services.purchase_service.PurchaseService') as mock_service:
        mock_service.create_purchase_request.return_value = {'id': 1}
        # 测试代码...
```

## 📁 测试文件结构

```
backend/tests/
├── unit/
│   ├── test_purchase_validation.py           # 申购单验证测试
│   ├── test_system_category_intelligence.py  # 智能分类测试
│   ├── test_remaining_quantity_calculation.py # 剩余数量计算测试
│   ├── test_batch_operations.py              # 批量操作测试
│   └── test_workflow_approval.py             # 工作流审批测试
├── integration/
│   ├── test_purchase_workflow_integration.py     # 工作流集成测试
│   └── test_purchase_ui_backend_integration.py   # UI后端集成测试
├── test_suite_runner.py                      # 统一测试运行器
├── pytest_purchase_features.ini              # pytest配置文件
└── README_purchase_features_tests.md         # 本说明文档
```

## 🔧 CI/CD 集成

### GitHub Actions 示例
```yaml
name: Purchase Features Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest
    - name: Run Purchase Features Tests
      run: |
        cd backend/tests
        python test_suite_runner.py --report
```

### Jenkins Pipeline 示例
```groovy
pipeline {
    agent any
    stages {
        stage('Test Purchase Features') {
            steps {
                sh '''
                    cd backend/tests
                    python test_suite_runner.py --type all --verbose --report
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'backend/tests/test_report_*.json'
                }
            }
        }
    }
}
```

## 📈 测试指标

### 覆盖的业务场景
- ✅ 申购单创建到最终审批的完整流程
- ✅ 主材合同清单集成和辅材自由录入
- ✅ 智能系统分类推荐和手动选择
- ✅ 剩余数量实时计算和验证
- ✅ 批量操作的权限控制和事务安全
- ✅ 多角色工作流权限矩阵验证
- ✅ 前后端数据格式兼容性
- ✅ 错误处理和用户体验一致性

### 测试类型分布
- **单元测试**: 5个文件，专注业务逻辑验证
- **集成测试**: 2个文件，关注组件间交互
- **总覆盖**: 7个测试文件，20+个测试场景

## 🤝 贡献指南

1. 添加新功能时，同时添加对应的单元测试
2. 修改现有功能时，更新相关测试用例
3. 集成测试重点验证跨组件交互
4. 保持测试的独立性，避免测试间依赖
5. 定期运行完整测试套件确保回归质量

---
**创建时间**: 2025-01-28  
**维护者**: Claude Code  
**最后更新**: 测试套件创建完成