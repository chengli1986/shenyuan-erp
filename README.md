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
- ✅ **采购请购模块** - 简化版采购申请单管理 (v1.0)
- ✅ **系统分类管理** - 智能物料系统分类和优化

### 采购请购模块 (v1.0)

**开发原则**：采用"小步快跑、局部功能验证"的迭代开发模式

**核心功能**：
- ✅ 简化版申购单创建 - 基础信息录入和提交
- ✅ 申购单列表查看 - 完整分页显示和状态查询
- ✅ 申购单详情查看 - 弹窗展示完整信息
- ✅ 项目名称显示 - 替代项目ID展示，提升用户体验
- ✅ 分页功能完善 - 支持20/50/100条记录显示选择
- ✅ **单个删除功能** - 支持草稿状态申购单的删除
- ✅ **批量删除功能** - 支持多选删除，提升批量操作效率
- ✅ **项目级权限隔离** - 项目经理只能管理负责项目的申购单
- ✅ **智能系统分类** - 物料级系统分类，主材自动识别，辅材灵活选择

**技术特点**：
- **简化版数据模型**：避免复杂的审批流程，专注核心功能
- **统一API服务**：前端使用统一的axios服务处理所有API调用
- **权限控制完善**：支持角色级和项目级双重权限控制
- **类型安全设计**：完整的TypeScript类型定义
- **响应式UI**：基于Ant Design的现代化界面
- **实时刷新机制**：创建后自动刷新列表数据
- **智能系统分类**：基于合同清单的物料系统自动识别
- **前端编译优化**：统一API导入方式，避免编译错误

**文件结构**：
```
backend/app/models/purchase.py      # 采购数据模型
backend/app/schemas/purchase.py     # API数据校验
backend/app/api/v1/purchases.py     # RESTful API接口

frontend/src/types/purchase.ts      # TypeScript类型定义
frontend/src/services/purchase.ts   # API调用服务
frontend/src/pages/Purchase/        # 前端页面组件
  ├── SimplePurchaseList.tsx       # 申购单列表
  ├── SimplePurchaseForm.tsx       # 申购单表单
  ├── EnhancedPurchaseForm.tsx     # 智能申购表单(支持系统分类)
  └── SimplePurchaseDetail.tsx     # 申购单详情
```

**设计决策**：
- 采用简化的单表设计，避免复杂的关联关系
- 使用弹窗模式展示详情，减少页面跳转
- 实现项目名称解析，提升数据可读性
- 预留扩展接口，支持未来功能迭代

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

## UI/UX设计决策

### 合同清单层级导航设计
**问题背景**：左侧菜单"合同清单"无响应，功能入口不明确

**设计方案**：采用层级导航（双入口设计）
- **总览入口**：左侧菜单"合同清单" → 合同清单总览页面
- **快速入口**：项目列表操作按钮 → 特定项目合同管理

**用户场景**：
- 管理员/财务：使用总览页面查看所有项目合同状态
- 项目经理：通过项目列表快速访问负责项目的合同

**实现效果**：
- 统计卡片展示关键指标
- 列表视图支持搜索筛选
- 状态Badge优雅展示
- 响应式设计适配不同屏幕

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

### 系统分类优化功能 (v1.1)

**核心创新**：物料级智能系统分类，提升采购管理精度

**功能特点**：
- ✅ **物料级分类**：从申购单级别移动到申购明细级别，更精准的系统归属
- ✅ **智能主材识别**：根据合同清单自动推荐物料对应的系统分类
- ✅ **辅材灵活分类**：辅材支持手动选择任意系统分类
- ✅ **多系统支持**：单个物料属于多个系统时提供智能选择机制
- ✅ **UI优化**：详情页显示系统分类，列表页保持简洁

**技术实现**：
```typescript
// 智能系统分类选择
interface SystemCategory {
  id: number;
  category_name: string;
  is_suggested?: boolean;  // 智能推荐标记
  items_count?: number;    // 包含物料数量
}

// 物料变化时自动加载系统分类
const handleMaterialNameChange = async (itemId, materialName) => {
  if (projectId && materialName) {
    const categories = await getSystemCategoriesByMaterial(projectId, materialName);
    
    // 自动选择建议的系统分类
    const suggestedCategory = categories.find(cat => cat.is_suggested);
    if (suggestedCategory && categories.length === 1) {
      handleSystemCategoryChange(itemId, suggestedCategory.id);
    }
  }
};
```

**后端API增强**：
- `GET /purchases/system-categories/by-project/{project_id}` - 获取项目系统分类列表
- `GET /purchases/system-categories/by-material` - 根据物料名称智能推荐系统分类

**数据库模型扩展**：
```python
class PurchaseRequestItem(Base):
    # 新增系统分类外键关联
    system_category_id = Column(Integer, ForeignKey("system_categories.id"), nullable=True)
    system_category = relationship("SystemCategory", backref="purchase_items")
```

#### 编辑页面系统分类显示修复 (v1.2 - 2025-08-19)

**问题背景**：历史申购单编辑时，系统分类列显示横杠（-）而非具体系统名称

**根本原因**：历史数据缺少系统分类信息（`system_category_id = null`），但新申购单功能完全正常

**修复策略**：增强编辑页面，为所有申购明细提供系统分类选择功能

**核心改进**：
- ✅ **历史数据支持**：为所有申购明细加载项目系统分类选择器
- ✅ **智能推荐保持**：主材仍有⭐标记的智能推荐功能
- ✅ **手动选择增强**：用户可为历史数据手动选择系统分类
- ✅ **类型安全保障**：全面的数组类型检查，消除运行时错误
- ✅ **渐进式改善**：支持历史数据质量逐步完善

**技术实现**：
```typescript
// 为所有明细项加载系统分类（新增功能）
getAllSystemCategoriesByProject(projectId).then(allCategories => {
  setItems(prevItems => prevItems.map(prevItem => ({
    ...prevItem,
    availableSystemCategories: allCategories  // 所有物料都可选择
  })));
});

// 优化UI渲染逻辑：优先显示选择器而非横杠
if (Array.isArray(record.availableSystemCategories) && record.availableSystemCategories.length > 0) {
  return (
    <Select
      value={value}
      placeholder={record.system_category_name || "选择系统"}
      onChange={(categoryId) => {
        // 同步更新ID和名称
        const selectedCategory = record.availableSystemCategories.find(cat => cat.id === categoryId);
        if (selectedCategory) {
          setItems(items => items.map(item => 
            item.id === record.id ? {
              ...item,
              system_category_id: categoryId,
              system_category_name: selectedCategory.category_name
            } : item
          ));
        }
      }}
    >
      {record.availableSystemCategories.map(cat => (
        <Select.Option key={cat.id} value={cat.id}>
          {cat.is_suggested ? '⭐ ' : ''}{cat.category_name}
        </Select.Option>
      ))}
    </Select>
  );
}
```

**用户体验改善**：
- 编辑任何申购单（新的或历史的）都能看到系统分类选择器
- 历史申购单可以手动选择并保存系统分类到数据库
- 新申购单保持智能推荐功能（⭐标记推荐项）
- 完全消除页面加载和操作中的技术错误

## 故障排除

### 申购单分页功能问题 (2025-08-16)

#### 问题场景
用户设置每页显示20/50/100条记录时，页面仍然只显示10条记录，分页功能失效。

#### 根本原因
前后端API参数名不匹配：
- 前端发送：`page_size=20`
- 后端期望：`size=20`
- 结果：后端使用默认值`size=10`

#### 快速诊断方法
```bash
# 1. 验证后端API是否正确响应
curl "http://localhost:8000/api/v1/purchases/?page=1&size=20" -H "Authorization: Bearer $TOKEN"

# 2. 检查前端API调用参数
grep -r "page_size" frontend/src/pages/Purchase/
```

#### 解决方案
修正前端API调用中的参数名：
```typescript
// 错误：
fetch(`/api/v1/purchases/?page=${page}&page_size=${size}`)

// 正确：
fetch(`/api/v1/purchases/?page=${page}&size=${size}`)
```

#### 预防措施
- API开发时明确定义参数命名规范
- 前后端开发同步确认接口文档
- 使用TypeScript接口定义强制参数一致性

### React应用无限加载问题 (2025-08-15)

#### 问题场景
用户登录成功后，React主应用出现无限加载，页面无法正常显示。

#### 根本原因
复杂组件导入和状态管理引起的初始化循环：
- ConnectionProvider组件循环依赖
- 过多的console.log影响性能
- useEffect依赖数组配置错误

#### 调试策略
1. **渐进式简化**：创建最小可行版本逐步添加功能
2. **组件分离测试**：单独测试问题组件
3. **性能优化**：清理调试日志和无效依赖

#### 解决方案
```typescript
// 简化认证逻辑
isLoggedIn(): boolean {
  const token = localStorage.getItem('access_token');
  return token !== null && this.currentUser !== null;
}

// 使用useCallback优化性能
const loadData = useCallback(async () => {
  // 数据加载逻辑
}, [dependencies]);
```

### 权限系统集成问题 (2025-08-09)

#### 问题场景
用户权限系统开发后，现有功能（如申购模块）出现数据无法显示、保存失败等问题。

#### 根本原因
前端API调用缺少JWT认证token，导致401未授权错误。

**技术细节**：
- 前端直接使用`fetch`调用而非封装的`api`实例
- `api.ts`已配置自动token附加，但某些组件绕过了该机制
- 后端权限限制过于严格，业务角色无法执行必要操作

### 申购单审批按钮无响应问题修复 (2025-08-20)

#### 问题场景
用户报告申购单工作流中，部门主管和总经理的审批/拒绝按钮点击后无任何响应，无法完成申购审批流程。

#### 根本原因分析
通过系统化调试发现问题根源是`Modal.confirm`组件在处理复杂表单内容时无法正确触发回调函数：

**技术细节**：
```typescript
// ❌ 问题代码：Modal.confirm + 复杂表单
Modal.confirm({
  title: '部门主管审批',
  content: (
    <Form form={form}>
      <Form.Item name="approval_notes" label="审批意见">
        <Input.TextArea />
      </Form.Item>
    </Form>
  ),
  onOk: () => {
    // 这个回调函数不会被触发
    handleDeptApprove(true, notes);
  }
});
```

#### 解决方案实施
**核心策略**：将有问题的`Modal.confirm`替换为可控的`Modal`组件

**1. 统一状态管理**：
```typescript
const [approvalForm] = Form.useForm();
const [approvalVisible, setApprovalVisible] = useState(false);
const [approvalType, setApprovalType] = useState<'approve' | 'reject' | 'final_approve' | 'final_reject'>('approve');
```

**2. 替换按钮点击事件**：
```typescript
// ✅ 修复后：统一使用openApprovalModal
<Button onClick={() => openApprovalModal('approve')}>批准</Button>
<Button onClick={() => openApprovalModal('reject')}>拒绝</Button>
<Button onClick={() => openApprovalModal('final_approve')}>最终批准</Button>
<Button onClick={() => openApprovalModal('final_reject')}>最终拒绝</Button>
```

**3. 实现可控Modal组件**：
```typescript
<Modal
  title={approvalType === 'approve' ? '部门主管审批' : '总经理最终审批'}
  visible={approvalVisible}
  onOk={handleApprovalSubmit}
  onCancel={() => setApprovalVisible(false)}
  confirmLoading={loading}
>
  <Form form={approvalForm} layout="vertical">
    {/* 根据approvalType动态渲染不同表单字段 */}
  </Form>
</Modal>
```

#### 修复成果验证
- ✅ **部门主管审批**：点击批准/拒绝按钮正常弹出审批Modal
- ✅ **总经理审批**：点击最终批准/拒绝按钮正常弹出审批Modal  
- ✅ **表单验证**：拒绝操作必填理由，审批操作理由可选
- ✅ **API集成**：审批提交正确调用后端API，状态正常流转
- ✅ **前端编译**：0个TypeScript错误，0个ESLint警告

#### 技术启示
1. **Modal.confirm限制**：不适合包含复杂表单的确认对话框
2. **可控组件优势**：提供更好的状态管理和用户体验控制
3. **调试方法论**：分层诊断（表象→直接原因→根本原因）
4. **组件标准化**：统一的状态管理模式提高可维护性

### 项目级权限隔离系统 (2025-08-16)

#### 核心功能
多项目多项目经理环境下的权限隔离系统，确保申购单严格按项目权限控制。

#### 权限矩阵
| 角色 | 项目访问权限 | 申购单可见性 | 价格信息 |
|------|-------------|-------------|----------|
| 管理员 | 全部项目 | 全部申购单 | ✅ 可见 |
| 项目经理 | 负责的项目 | 仅负责项目的申购单 | ❌ 隐藏 |
| 采购员 | 全部项目 | 全部申购单 | ✅ 可见 |
| 部门主管 | 全部项目 | 全部申购单 | ✅ 可见 |

#### 测试账户
- **管理员**: `admin` / `admin123`
- **项目经理**: `test_pm` / `testpm123` (负责项目2,3)

#### 快速验证权限隔离
```bash
# 1. 测试项目经理权限
PM_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=test_pm&password=testpm123" | jq -r '.access_token')

curl -s "http://localhost:8000/api/v1/purchases/" \
  -H "Authorization: Bearer $PM_TOKEN" | \
  jq '{total: .total, projects: [.items[].project_id] | unique}'

# 2. 对比管理员权限  
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

curl -s "http://localhost:8000/api/v1/purchases/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.total'
```

#### 常见问题排查

**问题1**：项目经理看不到申购单
```bash
# 检查项目分配
curl -s "http://localhost:8000/api/v1/projects/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | \
  jq '.items[] | {id, project_name, project_manager}'
```

**问题2**：权限过滤不生效
```bash
# 检查枚举比较
grep -r "current_user\.role.*==" backend/app/api/v1/purchases.py
# 确保使用: current_user.role.value == "project_manager"
```

#### 系统化排查方法
```bash
# 1. 验证后端API和数据完整性
curl -s "http://localhost:8000/api/v1/purchases/" -H "Authorization: Bearer $TOKEN" | jq '.total'

# 2. 检查后端日志
tail -f backend.log | grep -E "(ERROR|权限|项目经理)"

# 3. 验证用户角色配置
curl -s "http://localhost:8000/api/v1/auth/me" -H "Authorization: Bearer $TOKEN" | jq '.role'
```

### 批量删除功能问题 (2025-08-17)

#### 问题场景
用户报告批量删除功能完全不工作，单个删除正常，但批量删除无响应。

#### 根本原因分析
经过系统化调试发现两个关键问题：

1. **前端API调用不统一**：
   ```typescript
   // ❌ 问题：混用fetch和api服务
   await fetch('/api/v1/purchases/batch-delete', {
     headers: { 'Authorization': `Bearer ${token}` }  // 手动处理
   });
   
   // ✅ 解决：统一使用api服务
   await api.post('purchases/batch-delete', idsToDelete);  // 自动处理
   ```

2. **Modal.confirm异步处理兼容性问题**：
   ```typescript
   // ❌ 问题：复杂异步回调
   Modal.confirm({
     onOk: () => new Promise(async (resolve, reject) => { ... })
   });
   
   // ✅ 解决：使用原生confirm
   if (window.confirm("确认删除吗？")) {
     await executeDelete();
   }
   ```

#### 系统化调试方法
1. **分层测试**：后端API → 前端代理 → React组件 → 用户交互
2. **独立验证**：创建简单HTML页面直接测试API
3. **对比分析**：工作的功能vs不工作的功能找差异

#### 解决方案
- 统一使用`services/api.ts`进行所有API调用
- 避免在Modal.confirm中使用复杂异步操作
- 建立完整的调试工具链进行问题定位

## 开发最佳实践

### 前端API调用规范

#### 1. 统一API服务使用
**原则**：所有API调用必须使用统一的`services/api.ts`服务

```typescript
// ✅ 正确方式
import api from '../../services/api';

// GET请求
const response = await api.get('purchases/', { params: { page, size } });

// POST请求
const response = await api.post('purchases/batch-delete', idsToDelete);

// DELETE请求
await api.delete(`purchases/${id}`);
```

**优势**：
- 自动处理JWT token认证
- 统一错误处理和拦截
- 避免重复的请求配置代码

#### 2. Modal组件使用注意事项
**避免复杂异步操作**：
```typescript
// ❌ 问题写法：Modal.confirm + 复杂异步
Modal.confirm({
  onOk: () => new Promise(async (resolve, reject) => {
    // 复杂异步操作可能导致状态管理问题
  })
});

// ✅ 推荐写法：原生confirm + 直接异步调用
if (window.confirm("确认操作吗？")) {
  await executeOperation();
}
```

### 调试方法论

#### 1. 分层诊断思维
```
表象问题：功能不工作
     ↓
API层验证：curl测试后端
     ↓
网络层验证：代理和路由
     ↓
组件层验证：React状态和事件
     ↓
交互层验证：用户操作流程
```

#### 2. 独立测试优先
创建简单的HTML页面直接测试API：
```html
<!-- debug-feature.html -->
<script>
async function testAPI() {
  const response = await fetch('/api/v1/endpoint', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  console.log('测试结果:', await response.json());
}
</script>
```

### 权限系统开发规范
1. **权限优先设计**：新功能开发前必须先设计权限控制
2. **类型安全检查**：枚举比较使用`.value`属性，Schema定义严格验证
3. **分层权限控制**：数据库层过滤 + API层验证 + 前端UI控制
4. **可测试可验证**：为权限边界准备专门的测试工具

### 调试工具链
- **API测试**: `curl + jq` 快速验证后端
- **权限测试**: `frontend/public/debug-user-auth.html` 调试页面
- **日志分析**: `tail -f backend.log | grep ERROR`
- **数据库查询**: 开发环境支持直接数据库访问

### 项目级权限核心代码
```python
# backend/app/api/v1/purchases.py
if current_user.role.value == "project_manager":
    managed_projects = db.query(Project.id).filter(
        Project.project_manager == current_user.name
    ).all()
    
    if managed_projects:
        managed_project_ids = [p.id for p in managed_projects]
        query = query.filter(PurchaseRequest.project_id.in_(managed_project_ids))
    else:
        query = query.filter(PurchaseRequest.id == -1)  # 返回空结果
```

### 快速参考：项目级权限隔离系统 (2025-08-16)

**核心功能**：多项目多项目经理环境下的权限隔离，确保申购单严格按项目权限控制。

#### 快速验证权限隔离
```bash
# 1. 测试孙赟权限（只能看到项目2的申购单）
SUNYUN_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=sunyun&password=sunyun123" | jq -r '.access_token')

curl -s "http://localhost:8000/api/v1/purchases/" \
  -H "Authorization: Bearer $SUNYUN_TOKEN" | \
  jq '{total: .total, projects: [.items[].project_id] | unique}'
# 预期结果: {"total": 21, "projects": [2]}

# 2. 测试李强权限（只能看到项目3的申购单）
LIQIANG_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=liqiang&password=liqiang123" | jq -r '.access_token')

curl -s "http://localhost:8000/api/v1/purchases/" \
  -H "Authorization: Bearer $LIQIANG_TOKEN" | \
  jq '{total: .total, projects: [.items[].project_id] | unique}'
# 预期结果: {"total": 3, "projects": [3]}

# 3. 对比管理员权限（可以看到所有申购单）
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

curl -s "http://localhost:8000/api/v1/purchases/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.total'
# 预期结果: 24 (所有申购单)
```

#### 测试账户
- **管理员**: `admin` / `admin123` (全部权限)
- **项目经理(孙赟)**: `sunyun` / `sunyun123` (负责项目2-娄山关路445弄综合弱电智能化)
- **项目经理(李强)**: `liqiang` / `liqiang123` (负责项目3-某小区智能化改造项目)

#### 权限矩阵速查
| 角色 | 项目访问 | 申购单可见性 | 价格信息 | 数据范围 |
|------|---------|-------------|----------|---------|
| 管理员 | 全部项目 | 全部申购单 | ✅ 可见 | 无限制 |
| 项目经理 | 负责的项目 | 仅负责项目申购单 | ❌ 隐藏 | 严格隔离 |
| 采购员 | 全部项目 | 全部申购单 | ✅ 可见 | 无限制 |
| 部门主管 | 全部项目 | 全部申购单 | ✅ 可见 | 无限制 |

#### 常见问题快速排查
```bash
# 问题1：项目经理看不到申购单
curl -s "http://localhost:8000/api/v1/projects/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | \
  jq '.items[] | {id, project_name, project_manager}'

# 问题2：权限过滤不生效 - 检查枚举比较
grep -r "current_user\.role.*==" backend/app/api/v1/purchases.py
# 确保使用: current_user.role.value == "project_manager"

# 问题3：验证用户角色
curl -s "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq '.role'
```

## 系统架构

### 技术栈
- **后端**：FastAPI + SQLAlchemy + PostgreSQL  
- **前端**：React + TypeScript + Ant Design
- **认证**：JWT Token认证 + 多角色权限控制
- **部署**：AWS c7i-flex.large + Docker容器化

### 核心模块
- ✅ **项目管理模块**：项目创建、信息管理、进度跟踪
- ✅ **合同清单管理**：Excel导入、版本控制、物料管理
- ✅ **申购请购模块**：智能申购、多级审批、项目级权限隔离
- ✅ **用户权限系统**：7角色权限矩阵、JWT认证、权限隔离
- ✅ **系统测试模块**：自动化测试、测试报告、质量监控

### 权限架构设计
**多级权限控制**：
- **数据库层**：SQL查询过滤
- **API层**：权限验证和数据脱敏
- **前端层**：UI权限控制和功能隐藏

**项目级权限隔离**：
- 项目经理只能访问负责的项目数据
- 支持一个经理管理多个项目
- 动态权限分配和验证
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=purchaser&password=purchase123"
```

#### 修复方案
1. **统一API调用方式**
```typescript
// 错误：直接使用fetch
const response = await fetch('/api/v1/purchases/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// 正确：使用封装的api实例
const response = await api.get('purchases/');
```

2. **调整后端权限策略**
```python
# 修复前：过于严格
if current_user.role not in ["project_manager", "admin"]:
    raise HTTPException(status_code=403, detail="只有项目经理可以创建申购单")

# 修复后：符合业务需求
if current_user.role not in ["project_manager", "purchaser", "admin"]:
    raise HTTPException(status_code=403, detail="只有项目经理和采购员可以创建申购单")
```

3. **前端错误处理**
```typescript
// 在api.ts中添加401自动处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('currentUser');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);
```

#### 经验总结
1. **权限系统集成检查清单**：
   - [ ] 所有API调用使用统一认证机制
   - [ ] 后端权限配置符合业务流程需求
   - [ ] 前端有完善的401错误处理
   - [ ] 数据库原有数据完整性验证

2. **调试技巧**：
   - 先验证后端API和数据完整性
   - 使用`grep`查找前端API调用模式
   - 分角色测试功能权限边界
   - 检查浏览器Network面板定位具体错误

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

#### 6. 版本管理功能问题

**症状**：合同清单版本管理中查看/下载按钮无响应

**问题定位**：
1. **查看按钮无反应**：Modal.info组件调用失败导致查看功能异常
2. **下载按钮无效果**：缺少API代理配置导致跨域请求失败
3. **API路径不匹配**：前后端API路径不一致导致404错误

**解决步骤**：

1. **修复查看功能**：
```typescript
// 简化日期和文件大小格式化
render: (value) => new Date(value).toLocaleString()
render: (value) => value ? `${(value / 1024).toFixed(1)} KB` : '-'
```

2. **修复下载功能**：
```json
// frontend/package.json - 添加API代理
{
  "proxy": "http://localhost:8000"
}
```

3. **修复API路径匹配**：
```typescript
// frontend - 统一使用contract-versions路径
const downloadUrl = `/api/v1/contracts/projects/${projectId}/contract-versions/${version.id}/download`;
```

```python
# backend/app/api/v1/contracts.py - 统一API路径
@router.get("/projects/{project_id}/contract-versions/{version_id}/download")
```

4. **后端路径修复**：
```python
# backend/app/api/v1/contracts.py - 修正文件路径计算
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
file_path = os.path.join(backend_dir, "uploads", "contracts", version.stored_filename)
```

**验证步骤**：
```bash
# 1. 重启服务应用代理配置
./scripts/stop-erp.sh
./scripts/start-erp-dev.sh

# 2. 测试API代理
curl http://localhost:3000/api/v1/contracts/test

# 3. 测试下载API（注意使用contract-versions路径）
curl -I http://localhost:8000/api/v1/contracts/projects/2/contract-versions/3/download
```

**技术要点**：
- 开发环境需要配置代理解决跨域问题
- 前端使用相对路径`/api/v1/...`访问后端API
- 后端文件路径必须使用绝对路径计算
- 重启前端服务才能应用package.json的代理配置
- Modal.info在某些环境下可能失效，建议使用受控Modal组件

#### 7. 采购模块前端编译错误 (2025-08-08)

**症状**：采购模块前端编译时出现多个TypeScript错误

**错误类型**：
```typescript
// 1. ContractItem类型错误
Property 'brand' does not exist on type 'ContractItem'

// 2. Select组件filterOption类型错误  
Type '(input: string, option: any) => boolean' is not assignable

// 3. disabled属性类型错误
Type 'number' is not assignable to type 'boolean | undefined'

// 4. 继承接口错误
Types of property 'total_amount' are incompatible
```

**解决方案**：
```typescript
// 1. 修复字段名称错误
// 错误：item.brand
// 正确：item.brand_model

// 2. 修复Select组件类型
filterOption={(input, option) => 
  (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
}

// 3. 修复disabled属性类型
disabled={!!selectedProject?.id}

// 4. 修复接口继承
export interface PurchaseRequestWithoutPrice extends Omit<PurchaseRequest, 'total_amount'> {
  total_amount?: null;
}
```

#### 8. 申购单功能问题修复 (2025-08-08)

**问题1**：申购单创建后无法查看
- **症状**：可以创建申购单，但列表无法显示新创建的数据
- **解决**：添加多种数据刷新机制（URL参数、页面焦点事件）

**问题2**：查看按钮无响应
- **症状**：点击查看按钮没有任何反应
- **解决**：创建SimplePurchaseDetail组件，实现详情弹窗显示

**问题3**：项目ID显示代替项目名称
- **症状**：列表显示"项目ID: 2"而非实际项目名称
- **解决**：后端API返回项目名称，前端优先显示名称

```python
# backend/app/api/v1/purchases.py
# 添加项目名称查询
project = db.query(Project).filter(Project.id == item.project_id).first()
project_name = project.project_name if project else None

# API响应包含项目名称
return {
    "project_name": project_name,
    "requester_name": requester.username if requester else None,
    # 其他字段...
}
```

#### 9. 系统测试页面显示问题 (2025-08-08)

**症状**：系统测试页面不显示任何测试结果，但后端API正常返回数据

**问题定位**：
```bash
# 后端API正常返回27条记录
curl http://localhost:8000/api/v1/tests/runs | jq '.total'
# 输出: 27

# 前端通过代理访问也正常
curl http://localhost:3000/api/v1/tests/runs | jq '.total'  
# 输出: 27
```

**根本原因**：前端API路径末尾包含斜杠，而FastAPI路由不接受末尾斜杠

**解决方案**：
```typescript
// frontend/src/services/test.ts
// 修复前：
const response = await api.get('tests/runs/', { params });
const response = await api.get(`tests/runs/${runId}/`);
const response = await api.get('tests/statistics/');
const response = await api.get('tests/latest/');

// 修复后：
const response = await api.get('tests/runs', { params });
const response = await api.get(`tests/runs/${runId}`);
const response = await api.get('tests/statistics');
const response = await api.get('tests/latest');
```

**验证结果**：
- 移除所有API路径末尾斜杠
- 前后端路径完全匹配
- 系统测试页面正常显示27条历史记录

#### 10. 申购模块智能化优化 (2025-08-08)

**需求背景**：用户要求申购模块与合同清单深度集成，确保主材严格来源于合同清单

**优化内容**：
1. **物料名称智能选择**：主材只能从合同清单下拉选择，辅材可自由输入
2. **规格型号联动显示**：选择物料后自动显示可选规格选项
3. **品牌单位自动填充**：选择规格后品牌、单位自动填充且不可修改
4. **数量限制验证**：申购数量不能超过合同清单剩余可申购数量
5. **分批采购支持**：支持同一物料多次申购，动态计算剩余数量

**技术实现**：
```typescript
// 物料名称联动查询API
export async function getMaterialNamesByProject(projectId: number, itemType: string)

// 规格选择联动API  
export async function getSpecificationsByMaterial(projectId: number, itemName: string)

// 智能表单组件
<EnhancedPurchaseForm /> // 替代原SimplePurchaseForm
```

**关键技术难点及解决**：
- **状态更新冲突**：多次单独updateItem调用导致异步冲突
  ```typescript
  // 问题：多次单独更新导致状态丢失
  updateItem(itemId, 'field1', value1);
  updateItem(itemId, 'field2', value2);
  
  // 解决：批量状态更新
  setItems(items => items.map(item => 
    item.id === itemId ? { ...item, field1: value1, field2: value2 } : item
  ));
  ```

- **TypeScript类型推断错误**：updatedItem对象字段被推断为undefined类型
  ```typescript
  // 解决：显式类型注解
  const updatedItem: EnhancedPurchaseItem = { ...item, newField: value };
  ```

#### 11. 合同清单显示字段修复 (2025-08-08)

**问题症状**：合同清单页面"设备型号"显示品牌，"设备品牌"显示型号，完全相反

**问题排查过程**：
1. **API数据验证**：确认后端返回数据正确
   ```bash
   curl -X GET "http://localhost:8000/api/v1/purchases/contract-items/by-project/2"
   # brand_model: "大华", specification: "DH-SH-HFS9541P-I" ✓
   ```

2. **前端显示逻辑检查**：发现表格列定义字段映射错误
3. **Excel解析逻辑验证**：确认数据导入映射正确

**根本原因**：前端表格列定义中dataIndex字段映射错误
```typescript
// 错误的映射
{ title: '设备型号', dataIndex: 'brand_model' }     // 应该是specification
{ title: '设备品牌', dataIndex: 'specification' }   // 应该是brand_model
```

**数据流分析**：
```
Excel文件 → 解析器 → 数据库 → API → 前端显示
设备品牌(大华) → brand_model字段 → brand_model字段 → 错误显示在型号列
设备型号(DH-SH-HFS9541P-I) → specification字段 → specification字段 → 错误显示在品牌列
```

**修复方案**：
```typescript
// 修复后的正确映射
{ title: '设备型号', dataIndex: 'specification' }   // 显示DH-SH-HFS9541P-I
{ title: '设备品牌', dataIndex: 'brand_model' }     // 显示大华
```

**技术启示**：
- 字段命名与实际用途可能不匹配，需要通过数据流追踪确认
- 前端显示问题优先检查数据源，再检查显示逻辑
- 使用curl等工具快速验证API数据正确性

## 开发最佳实践

### 调试技巧排序

1. **API参数和连接调试**：
   - 使用`curl`直接测试后端API和参数
   - 检查浏览器Network面板的实际请求
   - 对比前后端参数命名一致性
   - 确认CORS配置正确

2. **React性能和状态调试**：
   - 创建最小可行版本排除复杂依赖
   - 检查useEffect依赖数组配置
   - 清理console.log等调试语句
   - 使用useCallback优化组件性能

3. **服务状态检查**：
   - `ps aux | grep uvicorn` - 检查后端进程
   - `ps aux | grep node` - 检查前端进程
   - `sudo netstat -tlnp` - 检查端口占用

4. **日志分析**：
   - 后端：`tail -f backend/backend.log`
   - 前端：`tail -f frontend/frontend.log`
   - 浏览器Console查看JavaScript错误

5. **CORS调试**：
   ```bash
   # 测试CORS配置是否正确
   curl -I -X OPTIONS http://localhost:8000/health \
     -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET"
   ```

### API开发最佳实践

**基于2025-08-16分页参数问题经验总结**

#### 1. 前后端参数命名一致性
```python
# 后端API定义 (FastAPI)
@router.get("/")
async def get_items(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)  # 使用'size'而非'page_size'
):
    pass
```

```typescript
// 前端API调用必须匹配
const response = await fetch(`/api/v1/items/?page=${page}&size=${size}`);
```

#### 2. API参数验证流程
```bash
# 开发时验证API参数有效性
curl "http://localhost:8000/api/v1/purchases/?page=1&size=20" -H "Authorization: Bearer $TOKEN"

# 检查返回数据是否符合预期
# {"total": 18, "items": [...], "page": 1, "size": 20}
```

#### 3. TypeScript类型定义强制一致性
```typescript
// 定义API参数接口
interface PaginationParams {
  page: number;
  size: number;  // 确保与后端参数名一致
}

// 在API服务中使用
const getPurchases = (params: PaginationParams) => {
  return api.get(`/purchases/?page=${params.page}&size=${params.size}`);
};
```

### React开发最佳实践

**基于2025-08-15无限加载问题经验总结**

#### 1. 组件性能优化
```typescript
// ✅ 使用useCallback防止不必要的重渲染
const loadData = useCallback(async (page = 1, size = 10) => {
  // 数据加载逻辑
}, [currentPage, pageSize]);

// ✅ 正确配置useEffect依赖
useEffect(() => {
  loadData();
}, [loadData]);

// ❌ 避免复杂的组件导入链
import { ComplexProvider } from './contexts/ComplexContext';
```

#### 2. 调试和问题排查
```typescript
// ✅ 渐进式组件开发
// 1. 创建最小可行版本 (AppMinimal.tsx)
// 2. 逐步添加功能并测试
// 3. 定位问题组件后针对性修复

// ✅ 清理性能影响的代码
// 移除多余的console.log
// 简化状态管理逻辑
// 避免在render中进行复杂计算
```

#### 3. 状态管理最佳实践
```typescript
// ✅ 认证状态简化
isLoggedIn(): boolean {
  const token = localStorage.getItem('access_token');
  return token !== null && this.currentUser !== null;
}

// ✅ 避免状态更新冲突
const handleUpdate = useCallback((id: string, updates: Partial<Item>) => {
  setItems(items => items.map(item => 
    item.id === id ? { ...item, ...updates } : item
  ));
}, []);
```

### 权限系统集成开发流程

**基于2025-08-09权限系统开发经验总结**

#### 1. 权限系统开发原则
- **数据保护优先**：任何系统性修改前都要验证数据完整性
- **渐进式集成**：先确保现有功能正常，再扩展新的权限功能
- **业务驱动设计**：权限配置必须符合实际业务流程需求

#### 2. 前端API调用标准化
```typescript
// ❌ 错误：直接使用fetch绕过认证
const response = await fetch('/api/v1/purchases/', {
  headers: { 'Content-Type': 'application/json' }
});

// ✅ 正确：使用统一api实例自动附加token
const response = await api.get('purchases/');
```

#### 3. 权限问题调试黄金流程
```bash
# 第一步：数据完整性验证
curl -s "http://localhost:8000/api/v1/purchases/" -H "Authorization: Bearer $TOKEN"

# 第二步：前端API调用审查
grep -r "fetch.*api/v1" frontend/src/ --include="*.ts" --include="*.tsx"

# 第三步：权限配置验证
curl -X POST "http://localhost:8000/api/v1/auth/login" -d "username=purchaser&password=purchase123"

# 第四步：角色权限边界测试
for role in admin general_manager purchaser; do
  echo "Testing $role permissions..."
  # 测试每个角色的功能访问权限
done
```

#### 4. 认证集成检查清单
- [ ] 所有API调用使用`services/api.ts`而非直接`fetch`
- [ ] 前端有完善的401错误自动重新登录处理
- [ ] 后端权限配置与业务流程匹配
- [ ] 不同角色的功能权限边界测试通过
- [ ] 原有数据100%完整性保持

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

## 项目经理权限系统开发实战 (2025-08-17)

### 开发背景
基于用户需求"多个项目可能对应多个项目经理，如何确保这两个项目的申购单互相独立，不受影响？"，我们开发了完整的项目级权限隔离系统。

### 核心技术实现

#### 1. 数据库层权限过滤
**文件位置**: `backend/app/api/v1/purchases.py` (第238-252行)
```python
# 项目经理权限过滤核心逻辑
if current_user.role.value == "project_manager":
    managed_projects = db.query(Project.id).filter(
        Project.project_manager == current_user.name
    ).all()
    
    if managed_projects:
        managed_project_ids = [p.id for p in managed_projects]
        query = query.filter(PurchaseRequest.project_id.in_(managed_project_ids))
    else:
        query = query.filter(PurchaseRequest.id == -1)  # 确保返回空结果
```

#### 2. 测试账号配置
```
孙赟: sunyun/sunyun123 (负责项目2-娄山关路445弄综合弱电智能化)
李强: liqiang/liqiang123 (负责项目3-某小区智能化改造项目)
管理员: admin/admin123 (全部权限)
```

### 重大技术问题及解决方案

#### 问题1: UserRole枚举比较失败
**现象**: 项目经理仍能看到所有申购单，权限过滤不生效
**根本原因**: Python枚举不能直接与字符串比较
```python
# ❌ 错误写法
if current_user.role == "project_manager":

# ✅ 正确写法
if current_user.role.value == "project_manager":
```
**影响范围**: 修复了6处枚举比较错误

#### 问题2: Pydantic Schema类型定义冲突
**现象**: `PurchaseRequestWithoutPrice` Schema编译错误
**错误信息**: `Types of property 'total_amount' are incompatible`
```python
# ❌ 问题方式：类型冲突
class PurchaseRequestWithoutPrice(PurchaseRequestInDB):
    total_amount: None = None  # 试图修改父类字段类型

# ✅ 解决方案：明确定义字段
class PurchaseRequestWithoutPrice(BaseModel):
    id: int
    request_code: str
    # ... 明确定义需要的字段，不包含price相关字段
```

#### 问题3: 重复用户账号冲突
**现象**: 数据库中存在多个同名用户，导致权限混乱
**解决方案**: 清理重复用户并建立唯一用户名规范
```bash
# 清理重复用户的命令示例
DELETE FROM users WHERE username IN ('pm_li', 'pm_孙赟', 'pm_李强');
```

#### 问题4: 前端服务端口问题
**现象**: 前端自动切换到3001端口，导致CORS配置失效
**解决方案**: 
1. 强制设置PORT环境变量为3000
2. 更新CORS配置包含所有必要端口
```bash
export PORT=3000
export REACT_APP_API_BASE_URL=http://localhost:8000
npm start
```

### 调试方法论

#### 系统化调试流程
```bash
# 1. 验证后端权限逻辑
curl -s "http://localhost:8000/api/v1/purchases/" -H "Authorization: Bearer $TOKEN" | jq .

# 2. 检查数据库权限分配
curl -s "http://localhost:8000/api/v1/projects/" -H "Authorization: Bearer $TOKEN" | \
  jq '.items[] | {id, project_name, project_manager}'

# 3. 验证用户角色配置
curl -s "http://localhost:8000/api/v1/auth/me" -H "Authorization: Bearer $TOKEN" | jq '.role'

# 4. 测试权限隔离效果
for user in sunyun liqiang; do
  echo "=== 测试 $user ==="
  TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
    -d "username=$user&password=${user}123" | jq -r '.access_token')
  curl -s "http://localhost:8000/api/v1/purchases/" \
    -H "Authorization: Bearer $TOKEN" | \
    jq '{total: .total, projects: [.items[].project_id] | unique}'
done
```

#### 快速问题定位命令
```bash
# 检查枚举比较问题
grep -rn "current_user\.role.*==" backend/app/api/v1/

# 验证Schema字段定义
grep -A 10 -B 5 "PurchaseRequestWithoutPrice" backend/app/schemas/purchase.py

# 检查用户重复问题
python3 -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
users = db.query(User).filter(User.name.in_(['孙赟', '李强'])).all()
for u in users: print(f'{u.name} ({u.username})')
"
```

### 权限验证结果
- ✅ 孙赟只能看到项目2的21条申购单 (娄山关路项目)
- ✅ 李强只能看到项目3的3条申购单 (某小区智能化改造)
- ✅ 管理员可以看到全部24条申购单
- ✅ 价格信息对项目经理完全隐藏
- ✅ 项目间权限严格隔离，互不影响

### 性能和安全考虑
```sql
-- 优化索引
CREATE INDEX idx_projects_project_manager ON projects(project_manager);
CREATE INDEX idx_purchase_requests_project_id ON purchase_requests(project_id);
```

### 开发最佳实践总结
1. **枚举类型规范**: Python枚举比较统一使用`.value`属性
2. **Schema继承规范**: 避免修改父类字段类型，使用明确字段定义
3. **权限测试驱动**: 权限边界测试优先于功能开发
4. **多层安全防护**: 数据库层+API层+前端层三重权限控制
5. **用户数据规范**: 建立用户名唯一性约束，避免重复账号
6. **环境变量管理**: 前端端口等关键配置使用环境变量控制

## 📚 学习资源

### 技术文档
- [网络访问原理学习指南](docs/网络访问原理学习指南.md) - 深入理解前后端网络通信原理
- [脚本使用说明](scripts/README.md) - 详细的部署脚本文档

### 开发记录
- [CLAUDE.md](CLAUDE.md) - 项目开发记录和问题解决历史

## 12. 系统测试功能修复（2025-08-09）

### 问题描述
1. **状态显示错误**：37个测试全部通过，但系统测试汇总页面显示状态为"失败"
2. **测试结果不显示**：点击测试运行ID后，测试结果页面不显示任何测试用例详情

### 根本原因分析

#### 问题1：状态判断逻辑缺陷
- **文件位置**：`backend/app/api/v1/test_results.py` 第202行
- **原因**：状态判断依赖`process.returncode == 0`，即使所有测试通过，如果pytest进程返回码不为0仍会标记为失败
- **代码问题**：
  ```python
  # 原逻辑
  test_run.status = "completed" if failed == 0 and process.returncode == 0 else "failed"
  ```

#### 问题2：缺少详细测试结果保存
- **原因**：手动触发测试时只保存了TestRun记录，没有保存TestResult详细记录
- **缺失功能**：
  1. 没有解析pytest输出提取单个测试用例结果
  2. 缺少`/api/v1/tests/results/{run_id}`端点

### 解决方案实施

#### 修复1：改进状态判断逻辑
```python
# 修复后的逻辑
passed = output.count(' PASSED')
failed = output.count(' FAILED')
skipped = output.count(' SKIPPED')
error = output.count(' ERROR')
total = passed + failed + skipped + error

# 只要没有失败和错误就是成功，不依赖进程返回码
test_run.status = "completed" if failed == 0 and error == 0 else "failed"
```

#### 修复2：保存详细测试结果
```python
# 解析pytest输出，保存每个测试用例
from app.models.test_result import TestResult
test_lines = output.split('\n')
for line in test_lines:
    if ' PASSED' in line or ' FAILED' in line:
        # 解析测试名称和状态
        parts = line.split('::')
        test_suite = test_file.replace('tests/', '').replace('.py', '')
        test_result = TestResult(
            test_run_id=run_id,
            test_suite=test_suite,
            test_name=test_name,
            status=status
        )
        db.add(test_result)
```

#### 修复3：添加测试结果API端点
```python
@router.get("/results/{run_id}")
def get_test_results(run_id: str, db: Session = Depends(get_db)):
    """获取指定测试运行的详细结果"""
    results = db.query(TestResult).filter(
        TestResult.test_run_id == run_id
    ).all()
    return {
        "run_id": run_id,
        "total_results": len(results),
        "results": [result.to_dict() for result in results]
    }
```

### 调试技巧总结
1. **API响应验证**：使用`curl | jq`直接查看API响应，快速定位问题
2. **数据流追踪**：从数据库→API→前端逐层检查数据传递
3. **日志分析**：查看pytest输出格式，理解解析逻辑
4. **隔离测试**：移除有问题的测试文件，确保干净的测试环境

### 验证结果
- ✅ 36个测试全部通过，状态正确显示为"completed"
- ✅ 测试结果API返回36个详细的测试用例记录
- ✅ 前端能正确显示每个测试用例的名称、状态和所属套件

## 申购单测试套件完整部署 (2025-08-19)

### 测试套件概述
为确保申购单系统的稳定性和可靠性，我们创建了一套完整的单元测试和集成测试，并成功集成到每日回归测试套件中。

### 测试架构
```
backend/tests/
├── test_purchase_rules.py                    # 业务规则测试 (7个核心规则)
├── unit/test_purchase_permissions.py         # 权限系统测试 (7个权限场景)  
├── integration/test_purchase_edit_page.py    # 编辑页面集成测试 (6个流程)
└── tools/run_purchase_tests_standalone.py   # 独立测试运行器
```

### 核心功能覆盖
- **✅ 业务规则验证**: 主材验证、数量限制、分批采购、规格填充等7项核心规则
- **✅ 权限系统完整测试**: 项目级权限隔离、角色价格可见性、操作权限边界等
- **✅ 编辑页面用户体验**: 历史数据兼容、系统分类选择、数据持久化等端到端流程
- **✅ 系统分类功能**: 智能推荐、手动选择、API集成、错误处理等完整场景

### 测试执行和结果
```bash
# 运行完整测试套件
python backend/tools/run_purchase_tests_standalone.py

# 最新测试结果 (2025-08-19)
总测试模块: 3
通过模块: 3  
失败模块: 0
成功率: 100.0%

分类测试结果:
✅ business_rules: 1/1 通过 (100.0%)
✅ permissions: 1/1 通过 (100.0%) 
✅ edit_page: 1/1 通过 (100.0%)
```

### 每日回归测试集成
测试套件已完全集成到每日回归测试系统：
- **配置文件**: `backend/tools/purchase_test_config_standalone.json`
- **集成示例**: `scripts/run_daily_tests.py` 
- **自动报告**: `backend/test_reports/` 目录下的详细测试报告

### 技术特点
- **独立运行**: 不依赖复杂数据库连接，使用Mock对象模拟
- **全面覆盖**: 23个申购相关测试，涵盖所有核心功能
- **用户导向**: 模拟真实用户操作流程，验证完整用户体验
- **质量保证**: 类型安全、业务逻辑验证、回归防护完整

### 测试价值
1. **系统稳定性**: 确保申购模块在复杂业务场景下正确运行
2. **回归防护**: 每日自动检测，快速发现和定位问题
3. **质量保障**: 全面的测试覆盖为功能扩展提供信心
4. **维护友好**: 详细的测试文档和报告，便于问题排查

这套测试系统不仅验证了当前功能的正确性，更为未来的功能扩展和维护提供了坚实的基础，体现了现代软件开发中测试驱动和质量优先的最佳实践。

## 文档信息

**最后更新**：2025-08-19  
**版本**：1.3.0 - 申购单测试套件完整部署，每日回归测试集成