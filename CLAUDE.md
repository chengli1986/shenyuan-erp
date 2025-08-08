# 项目开发记录

  ## 技术栈
  - 后端：FastAPI + SQLAlchemy + PostgreSQL
  - 前端：React + TypeScript + Ant Design

  ## 当前进度
  - [x] 项目基础管理模块
  - [x] 合同清单管理模块  
  - [x] 合同清单总览页面
  - [x] 系统测试管理模块
  - [x] 采购请购模块开发 (v1.0 简化版)

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

  ### 6. 版本管理功能问题 (2025-08-03)
  **问题**：合同清单版本管理中查看/下载按钮无响应
  **症状**：
  - 查看按钮点击无反应
  - 下载按钮无效果，浏览器提示"无法下载，没有文件"
  
  **根本原因**：
  1. Modal.info组件调用失败导致查看功能异常（环境兼容性问题）
  2. 缺少API代理配置导致跨域请求失败
  3. API路径不匹配导致404错误（前端使用/versions/，后端实际为/contract-versions/）
  4. 后端文件路径计算错误
  5. 文件下载需使用fetch+blob而非直接链接下载
  
  **解决方案**：
  1. **简化格式化函数**: 直接使用原生JavaScript方法替代复杂格式化
  2. **前端代理配置**: 在package.json中添加proxy配置
  3. **相对路径API调用**: 使用`/api/v1/...`替代绝对URL
  4. **修复API路径匹配**: 统一前后端使用`/contract-versions/`路径
  5. **后端路径修正**: 使用绝对路径计算文件位置
  6. **Modal兼容性修复**: 使用受控Modal替代Modal.info
  7. **下载方式优化**: 使用fetch+blob替代直接链接下载
  
  **技术细节**：
  ```typescript
  // 简化格式化
  render: (value) => new Date(value).toLocaleString()
  render: (value) => value ? `${(value / 1024).toFixed(1)} KB` : '-'
  ```
  ```json
  // package.json代理配置
  "proxy": "http://localhost:8000"
  ```
  ```typescript
  // API路径统一修正
  const downloadUrl = `/api/v1/contracts/projects/${projectId}/contract-versions/${version.id}/download`;
  
  // 受控Modal替代Modal.info
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<ContractFileVersion | null>(null);
  
  // fetch+blob下载方式
  const response = await fetch(downloadUrl);
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  ```
  ```python
  # 后端API路径统一
  @router.get("/projects/{project_id}/contract-versions/{version_id}/download")
  
  # 后端文件路径修正
  backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
  ```

  ### 7. 合同清单UI交互优化 (2025-08-04)
  **问题**：左侧菜单"合同清单"点击无响应，功能入口不清晰
  
  **解决方案**：实现层级导航设计
  - 创建ContractOverview总览页面
  - 保留双入口：菜单总览 + 项目快速访问
  - 统计卡片 + 列表视图 + 搜索筛选
  
  **技术要点**：
  - 并行获取项目合同信息提升性能
  - TypeScript类型安全处理
  - Badge组件状态展示
  - 响应式表格设计

  ## 采购请购模块开发记录 (2025-08-08)

  ### 开发背景和原则
  **用户需求**：开发采购请购模块，但要求采用"小步快跑、局部功能验证"的模式
  **开发原则**：
  - 从简单的局部功能开始
  - 每开发一个功能都验证测试
  - 适合编程初学者的学习节奏
  - 避免过度复杂的设计

  ### 技术架构设计
  **后端架构**：
  ```
  backend/app/models/purchase.py      # 数据模型定义
  backend/app/schemas/purchase.py     # API数据验证
  backend/app/api/v1/purchases.py     # RESTful API接口
  ```

  **前端架构**：
  ```
  frontend/src/types/purchase.ts      # TypeScript类型定义
  frontend/src/services/purchase.ts   # API调用封装
  frontend/src/pages/Purchase/        # UI组件
    ├── SimplePurchaseList.tsx       # 申购单列表页面
    ├── SimplePurchaseForm.tsx       # 申购单创建表单
    └── SimplePurchaseDetail.tsx     # 申购单详情弹窗
  ```

  ### 核心功能实现

  #### 1. 简化版数据模型
  **设计思路**：避免复杂的审批流程，专注核心CRUD功能
  ```python
  class SimplePurchaseRequest(Base):
      __tablename__ = "simple_purchase_requests"
      
      id = Column(Integer, primary_key=True, index=True)
      request_code = Column(String(50), unique=True, index=True, nullable=False)
      project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
      requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
      equipment_name = Column(String(200), nullable=False)
      brand_model = Column(String(200))
      quantity = Column(Integer, nullable=False)
      estimated_price = Column(Numeric(12, 2))
      urgency_level = Column(String(20), default="normal")
      reason = Column(Text)
      status = Column(String(20), default="pending")
      created_at = Column(DateTime, server_default=func.now())
  ```

  #### 2. API接口设计
  **RESTful设计**：遵循REST最佳实践
  ```python
  # 获取申购单列表（支持分页和筛选）
  @router.get("/", response_model=PaginatedSimplePurchaseResponse)

  # 创建新申购单
  @router.post("/", response_model=SimplePurchaseResponse)

  # 获取申购单详情
  @router.get("/{request_id}", response_model=SimplePurchaseResponse)

  # 更新申购单状态
  @router.put("/{request_id}", response_model=SimplePurchaseResponse)
  ```

  #### 3. 前端组件设计
  **组件职责清晰**：
  - **SimplePurchaseList**: 负责数据展示和分页
  - **SimplePurchaseForm**: 负责数据录入和验证
  - **SimplePurchaseDetail**: 负责详情展示和操作

  ### 开发过程中的问题解决

  #### 问题1：前端编译错误 (TypeScript类型问题)
  **错误现象**：
  ```typescript
  // 错误1：ContractItem类型字段不存在
  Property 'brand' does not exist on type 'ContractItem'

  // 错误2：Select组件filterOption类型不匹配
  Type '(input: string, option: any) => boolean' is not assignable

  // 错误3：disabled属性类型错误
  Type 'number' is not assignable to type 'boolean | undefined'

  // 错误4：接口继承类型冲突
  Types of property 'total_amount' are incompatible
  ```

  **解决方案**：
  ```typescript
  // 1. 修正字段名称（brand → brand_model）
  brand_model: contractItem.brand_model,

  // 2. 修复Select组件类型转换
  filterOption={(input, option) => 
    (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
  }

  // 3. 修复布尔类型转换
  disabled={!!selectedProject?.id}

  // 4. 使用Omit工具类型解决继承冲突
  export interface PurchaseRequestWithoutPrice extends Omit<PurchaseRequest, 'total_amount'> {
    total_amount?: null;
  }
  ```

  #### 问题2：申购单创建后无法查看
  **症状**：可以成功创建申购单，但列表页面不显示新数据
  **原因分析**：缺少数据刷新机制
  **解决方案**：
  ```typescript
  // 1. 创建成功后URL参数刷新
  navigate(`/purchases?refresh=${Date.now()}`);

  // 2. 监听URL参数变化
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    if (urlParams.get('refresh')) {
      loadPurchaseRequests();
    }
  }, [location.search, loadPurchaseRequests]);

  // 3. 页面焦点事件刷新
  useEffect(() => {
    const handleFocus = () => {
      loadPurchaseRequests();
    };
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [loadPurchaseRequests]);
  ```

  #### 问题3：查看按钮无响应
  **症状**：点击列表中的查看按钮没有任何反应
  **解决方案**：创建SimplePurchaseDetail组件
  ```typescript
  // 详情弹窗组件
  const SimplePurchaseDetail: React.FC<{
    visible: boolean;
    purchaseId: number;
    onClose: () => void;
  }> = ({ visible, purchaseId, onClose }) => {
    // 组件实现...
  };

  // 列表中绑定点击事件
  const viewDetail = (record: SimplePurchaseRequest) => {
    setSelectedPurchase(record);
    setDetailModalVisible(true);
  };
  ```

  #### 问题4：显示项目ID而非项目名称
  **症状**：列表显示"项目ID: 2"，用户希望看到实际项目名称
  **解决方案**：后端API返回关联数据
  ```python
  # backend/app/api/v1/purchases.py
  def get_purchase_requests(db: Session):
      # 获取项目名称
      project = db.query(Project).filter(Project.id == item.project_id).first()
      project_name = project.project_name if project else None
      
      # 获取申请人姓名
      requester = db.query(User).filter(User.id == item.requester_id).first()
      requester_name = requester.username if requester else None
      
      return {
          "project_name": project_name,
          "requester_name": requester_name,
          # 其他字段...
      }
  ```

  ### 系统测试页面修复 (2025-08-08)

  #### 问题描述
  **症状**：从网页端登录系统测试页面，不显示任何测试结果
  **验证过程**：
  ```bash
  # 1. 后端API正常返回数据
  curl http://localhost:8000/api/v1/tests/runs | jq '.total'
  # 输出: 27

  # 2. 前端代理也能正常访问
  curl http://localhost:3000/api/v1/tests/runs | jq '.total'
  # 输出: 27

  # 3. 前端页面却不显示数据
  ```

  #### 根本原因分析
  **技术细节**：FastAPI路由末尾斜杠处理机制
  ```python
  # FastAPI路由定义（无末尾斜杠）
  @router.get("/runs")  # 正确
  @router.get("/runs/") # 会自动重定向
  ```

  ```typescript
  // 前端API调用（有末尾斜杠）
  api.get('tests/runs/')  # 导致307重定向，数据丢失
  ```

  #### 解决方案
  **修复策略**：统一前后端API路径格式
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
  - 系统测试页面正常显示27条历史测试记录

  ### 技术总结和学习要点

  #### 开发流程总结
  1. **需求明确**：用户要求小步快跑的开发模式
  2. **架构简化**：避免复杂设计，专注核心功能
  3. **迭代验证**：每个功能完成后立即测试
  4. **问题修复**：及时解决编译和运行时问题
  5. **用户反馈**：根据用户体验优化界面显示

  #### 核心技术要点
  1. **TypeScript类型安全**：使用Omit、联合类型等工具类型
  2. **React Hooks最佳实践**：useCallback、useEffect依赖管理
  3. **API设计规范**：RESTful风格、统一路径格式
  4. **前后端协作**：代理配置、CORS处理
  5. **用户体验优化**：实时刷新、友好显示、响应式设计

  #### 调试技巧积累
  1. **API路径问题**：使用curl验证后端，检查前端路径格式
  2. **类型错误**：善用TypeScript工具类型解决继承冲突
  3. **数据刷新**：多种机制并存（URL参数、事件监听、手动刷新）
  4. **用户友好性**：显示有意义的信息而非技术ID

  ## 申购模块智能化升级 (2025-08-08)

  ### 项目需求和开发原则
  **核心需求**：申购模块与合同清单深度集成，确保主材采购严格符合合同约定
  **开发理念**：
  - "小步快跑"的迭代开发策略
  - 用户友好的智能化操作体验
  - 严格的业务规则约束和数据一致性保证
  - 编程学习者友好的代码结构和文档

  ### 智能化功能架构设计

  #### 1. 合同清单集成API体系
  **设计思路**：为申购表单提供智能选择数据源
  ```python
  # 后端API接口设计
  @router.get("/material-names/by-project/{project_id}")
  def get_material_names_by_project()  # 获取物料名称列表
  
  @router.get("/specifications/by-material")  
  def get_specifications_by_material()  # 根据物料名称联动查询规格
  
  @router.get("/contract-items/{item_id}/details")
  def get_contract_item_details()  # 获取物料详细信息和剩余数量
  ```

  #### 2. 智能表单组件设计
  **组件职责划分**：
  - `EnhancedPurchaseForm`：主表单容器，管理整体状态
  - 智能选择逻辑：物料名称 → 规格型号 → 品牌单位联动
  - 数量验证逻辑：实时计算剩余可申购数量并限制
  
  **状态管理策略**：
  ```typescript
  interface EnhancedPurchaseItem {
    // 基础信息
    item_name: string;
    specification: string;
    brand_model: string;
    unit: string;
    quantity: number;
    
    // 智能选择状态
    availableSpecifications?: SpecificationOption[];
    contract_item_id?: number;
    remaining_quantity?: number;
    
    // 业务约束
    max_quantity?: number;
    unit_price?: number;
  }
  ```

  ### 核心技术难题解决记录

  #### 难题1：React状态更新异步冲突
  **问题现象**：用户选择物料名称后，品牌、单位等字段不自动填充
  **原因分析**：多次连续调用updateItem导致状态更新被覆盖
  ```typescript
  // 问题代码：异步状态更新冲突
  const handleMaterialNameChange = async (itemId, materialName) => {
    const response = await getSpecificationsByMaterial(projectId, materialName);
    updateItem(itemId, 'item_name', materialName);           // 第1次更新
    updateItem(itemId, 'availableSpecifications', response); // 第2次更新
    updateItem(itemId, 'specification', spec.specification); // 第3次更新 - 可能被前面覆盖
    updateItem(itemId, 'brand_model', spec.brand_model);     // 第4次更新 - 可能丢失
  };
  ```
  
  **解决策略**：批量状态更新模式
  ```typescript
  // 解决方案：原子化批量更新
  const handleMaterialNameChange = async (itemId, materialName) => {
    const response = await getSpecificationsByMaterial(projectId, materialName);
    
    setItems(items => items.map(item => {
      if (item.id === itemId) {
        const updatedItem: EnhancedPurchaseItem = {
          ...item,
          item_name: materialName,
          availableSpecifications: response.specifications,
          // 如果只有一个规格，自动选择
          ...(response.specifications.length === 1 && {
            specification: response.specifications[0].specification,
            brand_model: response.specifications[0].brand_model,
            unit: response.specifications[0].unit,
            remaining_quantity: response.specifications[0].remaining_quantity
          })
        };
        return updatedItem;
      }
      return item;
    }));
  };
  ```

  **技术要点**：
  - 使用函数式setState确保状态更新的原子性
  - 避免多次独立的状态更新操作
  - 利用解构语法优雅处理条件赋值

  #### 难题2：TypeScript类型推断冲突
  **问题现象**：编译错误"Type 'number' is not assignable to type 'undefined'"
  **原因分析**：updatedItem对象初始化时字段为undefined，TypeScript推断为严格undefined类型
  ```typescript
  // 问题代码：类型推断过于严格
  const updatedItem = {
    ...item,
    specification: '',           // TypeScript推断为string
    max_quantity: undefined,     // TypeScript推断为undefined
    remaining_quantity: undefined // TypeScript推断为undefined
  };
  // 后续赋值失败
  updatedItem.max_quantity = spec.total_quantity; // Error: number不能赋值给undefined
  ```
  
  **解决策略**：显式类型注解
  ```typescript
  // 解决方案：明确类型契约
  const updatedItem: EnhancedPurchaseItem = {
    ...item,
    specification: '',
    max_quantity: undefined,     // 现在可以接受number类型
    remaining_quantity: undefined
  };
  updatedItem.max_quantity = spec.total_quantity; // ✓ 编译通过
  ```

  #### 难题3：数量验证和用户体验平衡
  **业务需求**：申购数量不能超过合同清单剩余数量，但用户输入体验要流畅
  **解决方案**：渐进式验证策略
  ```typescript
  const handleQuantityChange = (itemId: string, quantity: number) => {
    setItems(items => items.map(item => {
      if (item.id === itemId) {
        if (item.remaining_quantity !== undefined && quantity > item.remaining_quantity) {
          // 用户友好的提示和自动调整
          message.warning(`申购数量已调整为最大可申购数量 ${item.remaining_quantity}`);
          return { ...item, quantity: Math.max(1, item.remaining_quantity) };
        }
        return { ...item, quantity };
      }
      return item;
    }));
  };
  ```

  ### 合同清单显示修复实战 (2025-08-08)

  #### 问题发现和定位流程
  **用户反馈**：合同清单页面设备型号和品牌显示内容相反
  **初步假设**：可能是前端显示逻辑问题或数据库数据问题

  #### 系统化排查方法论
  
  **第1步：数据源验证**
  ```bash
  # 验证API返回的原始数据
  curl -X GET "http://localhost:8000/api/v1/purchases/contract-items/by-project/2" | \
    python3 -c "
    import sys, json
    data = json.load(sys.stdin)
    for item in data['items'][:2]:
        print(f'设备: {item[\"item_name\"]}')
        print(f'brand_model: {item[\"brand_model\"]}')      # 大华
        print(f'specification: {item[\"specification\"]}')  # DH-SH-HFS9541P-I
    "
  ```
  **结论**：数据库数据正确，brand_model存储品牌，specification存储型号

  **第2步：数据流追踪分析**
  ```
  Excel导入 → 字段解析 → 数据库存储 → API返回 → 前端显示
  设备品牌(大华) → brand_model字段 → ✓正确存储 → ✓正确返回 → ❌错误显示
  设备型号(DH-SH-HFS9541P-I) → specification字段 → ✓正确存储 → ✓正确返回 → ❌错误显示
  ```

  **第3步：前端代码审查**
  ```typescript
  // 发现问题：ContractItemList.tsx中列定义错误
  const columns = [
    {
      title: '设备型号',
      dataIndex: 'brand_model',    // ❌ 错误：应该是specification
    },
    {
      title: '设备品牌', 
      dataIndex: 'specification',  // ❌ 错误：应该是brand_model
    }
  ];
  ```

  **第4步：Excel解析逻辑确认**
  ```python
  # backend/app/utils/excel_parser.py
  HEADER_MAPPING = {
      '设备品牌': 'brand_model',     # ✓ 正确：Excel品牌列 → brand_model字段
      '设备型号': 'specification',   # ✓ 正确：Excel型号列 → specification字段
  }
  ```

  #### 根本原因总结
  **问题本质**：字段命名语义与实际用途不匹配导致的混淆
  - 数据库字段`brand_model`注释为"品牌型号"，容易误解为包含型号
  - 实际存储：`brand_model`只存品牌，`specification`存储型号
  - 前端开发时按字面意思理解字段含义，导致映射错误

  #### 修复和验证
  ```typescript
  // 修复：正确的字段映射
  {
    title: '设备型号',
    dataIndex: 'specification',    // ✓ 显示DH-SH-HFS9541P-I
  },
  {
    title: '设备品牌',
    dataIndex: 'brand_model',      // ✓ 显示大华
  }
  ```

  ### 技术债务和改进建议

  #### 1. 数据库字段命名优化建议
  **现状问题**：
  - `brand_model`字段名暗示包含型号，但实际只存品牌
  - `specification`字段名偏向规格描述，但实际存储具体型号

  **建议改进**：
  - `brand_model` → `brand` (品牌)
  - `specification` → `model_number` (具体型号)

  #### 2. 开发流程改进
  **字段映射验证清单**：
  - [ ] 新增字段时明确语义和用途
  - [ ] 前端组件开发前验证API数据结构
  - [ ] 使用TypeScript接口明确字段类型和含义
  - [ ] 添加单元测试验证数据映射正确性

  #### 3. 调试工具箱扩展
  **快速验证命令**：
  ```bash
  # API数据验证模板
  curl -s "http://localhost:8000/api/v1/endpoint" | \
    python3 -c "import sys,json; data=json.load(sys.stdin); print(json.dumps(data[:1], indent=2, ensure_ascii=False))"
  
  # 字段映射验证模板
  grep -r "dataIndex.*field_name" frontend/src/ # 查找字段使用
  grep -r "field_name.*comment" backend/app/models/ # 查找字段定义
  ```

  ## 核心调试技巧
  1. 使用curl测试API连接性
  2. 使用netstat检查端口占用
  3. 检查浏览器Network面板确认CORS问题
  4. 使用React useCallback防止不必要的重渲染
  5. 前端功能异常优先检查代理配置和API路径
  6. 文件下载问题首先验证后端文件路径计算
  7. API 404错误时检查前后端路径是否匹配（/versions/ vs /contract-versions/）

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
  - 开发新功能时重用已验证的组件，避免重复实现
  - 优先实现用户实际需要的功能，避免过度设计
  - 前端代理配置是开发环境的关键配置项，需要重启生效