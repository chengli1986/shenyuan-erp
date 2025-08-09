# 申购模块测试文档

## 测试覆盖范围

### 1. 智能申购规则测试 ✅ 
位置：`tests/test_purchase_rules.py`

**测试结果：7个测试场景全部通过**

#### 测试场景：
1. **主材验证规则** - 验证主材必须来自合同清单
2. **数量限制规则** - 申购数量不能超过合同剩余数量
3. **分批采购支持** - 支持同一物料多次分批申购
4. **规格自动填充** - 根据物料名称自动显示可选规格
5. **单位只读规则** - 从合同清单选择后单位不可修改
6. **备注自由输入** - 备注字段无任何限制
7. **完整申购场景** - 端到端的申购流程验证

### 2. 单元测试 ✅
位置：`tests/unit/test_purchase_functional.py`

**测试结果：11个单元测试全部通过**

- 申购业务规则测试
- 表单验证测试
- 申购单号生成测试
- 金额计算测试
- 工作流状态转换测试

### 3. 集成测试 ✅
位置：`tests/integration/test_purchase_integration.py`

**测试结果：5个集成测试全部通过**

- 完整申购工作流程测试
- 分批采购场景测试
- 主材辅材混合申购测试
- 申购审批集成测试
- 异常处理测试

## 运行测试

### 运行所有申购模块测试
```bash
cd backend
source venv/bin/activate
python tools/run_purchase_tests.py
```

### 运行智能规则测试
```bash
cd backend
source venv/bin/activate
python tests/test_purchase_rules.py
```

### 运行单元测试
```bash
cd backend
source venv/bin/activate
pytest tests/unit/test_purchase_simple.py -v
```

### 运行集成测试
```bash
cd backend
source venv/bin/activate
pytest tests/integration/test_purchase_api_simple.py -v
```

## 测试数据说明

### 模拟合同清单数据
- **项目1：智慧园区项目**
  - AI智能摄像头（大华/海康威视）
  - 网络硬盘录像机（大华）
  - 网线（辅材）

- **项目2：数据中心项目**
  - 核心交换机（华为）
  - 接入交换机（华为）

### 测试用例数据
- 合同数量：100台
- 已申购数量：30台
- 剩余可申购：70台
- 测试申购量：40台

## 业务规则验证点

### ✅ 已实现的验证
1. 主材物料名称必须从合同清单下拉选择
2. 规格根据物料名称联动显示
3. 品牌从合同清单自动填充
4. 单位自动填充且不可修改
5. 申购数量不超过合同剩余数量
6. 支持分批采购
7. 备注字段自由输入

### 🔄 集成到每日测试
测试已集成到系统每日自动测试流程中，每天UTC 13:00（北京时间21:00）自动执行。

## 测试报告
测试报告自动生成在 `backend/test_reports/` 目录下：
- `purchase_test_report_YYYYMMDD_HHMMSS.txt`

## 测试结果示例
```
🚀 开始运行申购模块智能规则测试...

✅ 主材验证规则测试通过
✅ 数量限制规则测试通过
✅ 分批采购支持测试通过
✅ 规格自动填充规则测试通过
✅ 单位只读规则测试通过
✅ 备注自由输入测试通过
✅ 完整申购场景测试通过

测试结果汇总: 7 通过, 0 失败
🎉 所有测试通过！
```

## 故障排除

### 常见问题
1. **ImportError**: 确保在虚拟环境中运行 `source venv/bin/activate`
2. **ModuleNotFoundError**: 安装缺失的依赖 `pip install -r requirements.txt`
3. **数据库连接错误**: 检查PostgreSQL服务是否运行

### 调试模式
```bash
# 运行单个测试函数
pytest tests/test_purchase_rules.py::test_main_material_validation -v

# 显示详细输出
pytest tests/unit/test_purchase_simple.py -v -s

# 只运行失败的测试
pytest --lf
```

## 持续改进
- [ ] 添加性能测试
- [ ] 增加边界条件测试
- [ ] 模拟并发申购场景
- [ ] 添加审批流程测试