import React, { useState, useEffect, useCallback } from 'react';
import {
  Form,
  Input,
  Button,
  Card,
  Table,
  Space,
  message,
  InputNumber,
  Select,
  DatePicker,
  Row,
  Col,
  Alert,
  Tooltip
} from 'antd';
import { PlusOutlined, DeleteOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { createPurchaseRequest, getMaterialNamesByProject, getSpecificationsByMaterial } from '../../services/purchase';
import { ItemType } from '../../types/purchase';
import { ProjectService } from '../../services/project';
import { Project } from '../../types/project';

const { TextArea } = Input;
const { Option } = Select;

interface EnhancedPurchaseItem {
  id: string;
  item_type: ItemType;
  contract_item_id?: number; // 合同清单项ID（主材必须有）
  item_name: string;
  specification: string;
  brand_model: string;
  unit: string;
  quantity: number;
  max_quantity?: number; // 最大可申购数量（来自合同清单）
  remaining_quantity?: number; // 剩余可申购数量
  unit_price?: number; // 单价（来自合同清单）
  remarks?: string;
  // 选择状态
  availableSpecifications?: {
    contract_item_id: number;
    specification: string;
    brand_model: string;
    unit: string;
    total_quantity: number;
    purchased_quantity: number;
    remaining_quantity: number;
    unit_price?: number;
  }[];
}

const EnhancedPurchaseForm: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<EnhancedPurchaseItem[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [materialNames, setMaterialNames] = useState<string[]>([]);

  // 加载项目列表
  const loadProjects = useCallback(async () => {
    try {
      const response = await ProjectService.getProjects(1, 100); // 获取所有项目
      setProjects(response.items || []);
    } catch (error) {
      console.error('获取项目列表失败:', error);
      message.error('获取项目列表失败');
    }
  }, []);

  // 加载项目的物料名称列表
  const loadMaterialNames = useCallback(async () => {
    if (!selectedProjectId) {
      setMaterialNames([]);
      return;
    }
    
    try {
      const response = await getMaterialNamesByProject(selectedProjectId, '主材');
      setMaterialNames(response.material_names);
    } catch (error) {
      console.error('获取物料名称失败:', error);
      message.error('获取物料名称失败');
    }
  }, [selectedProjectId]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  useEffect(() => {
    loadMaterialNames();
  }, [loadMaterialNames]);

  // 添加申购明细
  const addItem = () => {
    const newItem: EnhancedPurchaseItem = {
      id: Date.now().toString(),
      item_type: ItemType.MAIN_MATERIAL,
      item_name: '',
      specification: '',
      brand_model: '',
      unit: '',
      quantity: 1,
      remarks: ''
    };
    setItems([...items, newItem]);
  };

  // 删除申购明细
  const removeItem = (id: string) => {
    setItems(items.filter(item => item.id !== id));
  };

  // 更新申购明细
  const updateItem = (id: string, field: string, value: any) => {
    setItems(items.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    ));
  };

  // 物料名称选择变化 - 触发规格型号联动查询
  const handleMaterialNameChange = async (itemId: string, materialName: string) => {
    if (!materialName) {
      // 清空相关字段
      setItems(items => items.map(item => 
        item.id === itemId ? {
          ...item,
          item_name: '',
          availableSpecifications: [],
          specification: '',
          brand_model: '',
          unit: '',
          contract_item_id: undefined,
          max_quantity: undefined,
          remaining_quantity: undefined,
          unit_price: undefined
        } : item
      ));
      return;
    }

    try {
      const response = await getSpecificationsByMaterial(selectedProjectId!, materialName);
      
      // 批量更新item状态
      setItems(items => items.map(item => {
        if (item.id === itemId) {
          const updatedItem: EnhancedPurchaseItem = {
            ...item,
            item_name: materialName,
            availableSpecifications: response.specifications,
            specification: '',
            brand_model: '',
            unit: '',
            contract_item_id: undefined,
            max_quantity: undefined,
            remaining_quantity: undefined,
            unit_price: undefined
          };
          
          // 如果只有一个规格选项，自动选择
          if (response.specifications.length === 1) {
            const spec = response.specifications[0];
            updatedItem.contract_item_id = spec.contract_item_id;
            updatedItem.specification = spec.specification;
            updatedItem.brand_model = spec.brand_model;
            updatedItem.unit = spec.unit;
            updatedItem.max_quantity = spec.total_quantity;
            updatedItem.remaining_quantity = spec.remaining_quantity;
            updatedItem.unit_price = spec.unit_price;
            
            // 如果当前数量超过剩余可申购数量，调整数量
            if (updatedItem.quantity > spec.remaining_quantity) {
              updatedItem.quantity = Math.max(1, spec.remaining_quantity);
              message.warning(`申购数量已调整为最大可申购数量 ${spec.remaining_quantity}`);
            }
          }
          
          return updatedItem;
        }
        return item;
      }));
      
    } catch (error) {
      console.error('获取规格型号失败:', error);
      message.error('获取规格型号失败');
    }
  };

  // 规格型号选择变化 - 自动填充相关信息
  const handleSpecificationChange = (itemId: string, contractItemId: number) => {
    setItems(items => items.map(item => {
      if (item.id === itemId && item.availableSpecifications) {
        const selectedSpec = item.availableSpecifications.find(spec => spec.contract_item_id === contractItemId);
        if (selectedSpec) {
          
          const updatedItem: EnhancedPurchaseItem = {
            ...item,
            contract_item_id: selectedSpec.contract_item_id,
            specification: selectedSpec.specification,
            brand_model: selectedSpec.brand_model,
            unit: selectedSpec.unit,
            max_quantity: selectedSpec.total_quantity,
            remaining_quantity: selectedSpec.remaining_quantity,
            unit_price: selectedSpec.unit_price
          };
          
          // 数量不能超过剩余可申购数量
          if (item.quantity > selectedSpec.remaining_quantity) {
            updatedItem.quantity = Math.max(1, selectedSpec.remaining_quantity);
            message.warning(`申购数量已调整为最大可申购数量 ${selectedSpec.remaining_quantity}`);
          }
          
          return updatedItem;
        }
      }
      return item;
    }));
  };

  // 数量变化验证
  const handleQuantityChange = (itemId: string, quantity: number) => {
    setItems(items => items.map(item => {
      if (item.id === itemId) {
        if (item.remaining_quantity !== undefined && quantity > item.remaining_quantity) {
          message.warning(`申购数量不能超过剩余可申购数量 ${item.remaining_quantity}`);
          return { ...item, quantity: Math.max(1, item.remaining_quantity) };
        } else {
          return { ...item, quantity: quantity };
        }
      }
      return item;
    }));
  };

  // 物料类型变化处理
  const handleItemTypeChange = (itemId: string, itemType: ItemType) => {
    setItems(items => items.map(item => {
      if (item.id === itemId) {
        const updatedItem = { ...item, item_type: itemType };
        
        // 如果切换到辅材，清空合同清单相关限制
        if (itemType === ItemType.AUXILIARY_MATERIAL) {
          updatedItem.contract_item_id = undefined;
          updatedItem.availableSpecifications = [];
          updatedItem.max_quantity = undefined;
          updatedItem.remaining_quantity = undefined;
          updatedItem.unit_price = undefined;
        }
        
        return updatedItem;
      }
      return item;
    }));
  };

  // 保存申购单
  const handleSave = async () => {
    if (!selectedProjectId) {
      message.warning('请先选择项目');
      return;
    }
    
    if (items.length === 0) {
      message.warning('请至少添加一个申购明细');
      return;
    }

    // 验证主材必须从合同清单选择
    const invalidMainMaterials = items.filter(
      item => item.item_type === ItemType.MAIN_MATERIAL && !item.contract_item_id
    );
    
    if (invalidMainMaterials.length > 0) {
      message.error('主材必须从合同清单中选择，请检查物料名称和规格型号');
      return;
    }

    try {
      const values = await form.validateFields();
      setLoading(true);

      // 构建请求数据
      const requestData = {
        project_id: selectedProjectId!,
        required_date: values.required_date?.toISOString(),
        remarks: values.remarks,
        items: items.map(item => ({
          contract_item_id: item.contract_item_id,
          item_name: item.item_name,
          specification: item.specification,
          brand: item.brand_model, // 后端使用brand字段
          unit: item.unit,
          quantity: item.quantity,
          item_type: item.item_type,
          remarks: item.remarks
        }))
      };

      const response = await createPurchaseRequest(requestData);
      message.success(`申购单创建成功！编号：${response.request_code}`);
      
      // 返回列表页，添加时间戳强制刷新
      navigate(`/purchases?refresh=${Date.now()}`);
    } catch (error: any) {
      console.error('创建申购单失败:', error);
      message.error(error.message || '创建申购单失败');
    } finally {
      setLoading(false);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '序号',
      width: 60,
      render: (_: any, __: any, index: number) => index + 1
    },
    {
      title: '类型',
      dataIndex: 'item_type',
      width: 100,
      render: (_: any, record: EnhancedPurchaseItem) => (
        <Select
          value={record.item_type}
          style={{ width: '100%' }}
          onChange={(value) => handleItemTypeChange(record.id, value)}
        >
          <Option value={ItemType.MAIN_MATERIAL}>主材</Option>
          <Option value={ItemType.AUXILIARY_MATERIAL}>辅材</Option>
        </Select>
      )
    },
    {
      title: (
        <span>
          物料名称
          <Tooltip title="主材必须从合同清单中选择，辅材可以自由输入">
            <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
          </Tooltip>
        </span>
      ),
      dataIndex: 'item_name',
      width: 200,
      render: (_: any, record: EnhancedPurchaseItem) => {
        if (record.item_type === ItemType.MAIN_MATERIAL) {
          // 主材：从合同清单下拉选择
          return (
            <Select
              value={record.item_name || undefined}
              placeholder="请选择物料名称"
              style={{ width: '100%' }}
              showSearch
              filterOption={(input, option) =>
                (option?.label as string)?.toLowerCase().includes(input.toLowerCase()) ||
                (option?.value as string)?.toLowerCase().includes(input.toLowerCase())
              }
              onChange={(value) => handleMaterialNameChange(record.id, value)}
              allowClear
            >
              {materialNames.map(name => (
                <Option key={name} value={name}>{name}</Option>
              ))}
            </Select>
          );
        } else {
          // 辅材：自由输入
          return (
            <Input
              value={record.item_name}
              placeholder="请输入物料名称"
              onChange={(e) => updateItem(record.id, 'item_name', e.target.value)}
            />
          );
        }
      }
    },
    {
      title: (
        <span>
          规格型号
          <Tooltip title="主材会根据物料名称自动显示可选规格">
            <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
          </Tooltip>
        </span>
      ),
      dataIndex: 'specification',
      width: 200,
      render: (_: any, record: EnhancedPurchaseItem) => {
        if (record.item_type === ItemType.MAIN_MATERIAL && record.availableSpecifications) {
          // 主材且有可选规格：下拉选择
          return (
            <Select
              value={record.contract_item_id}
              placeholder="请选择规格型号"
              style={{ width: '100%' }}
              onChange={(value) => handleSpecificationChange(record.id, value)}
              allowClear
            >
              {record.availableSpecifications.map(spec => (
                <Option key={spec.contract_item_id} value={spec.contract_item_id}>
                  <div>
                    <div>{spec.specification}</div>
                    <div style={{ fontSize: '12px', color: '#999' }}>
                      剩余: {spec.remaining_quantity}/{spec.total_quantity} {spec.unit}
                    </div>
                  </div>
                </Option>
              ))}
            </Select>
          );
        } else {
          // 辅材或主材无可选规格：显示文本
          return (
            <Input
              value={record.specification}
              placeholder="规格型号"
              disabled={record.item_type === ItemType.MAIN_MATERIAL}
              onChange={(e) => updateItem(record.id, 'specification', e.target.value)}
            />
          );
        }
      }
    },
    {
      title: '品牌型号',
      dataIndex: 'brand_model',
      width: 150,
      render: (_: any, record: EnhancedPurchaseItem) => (
        <Input
          value={record.brand_model}
          placeholder="品牌型号"
          disabled={record.item_type === ItemType.MAIN_MATERIAL && !!record.contract_item_id}
          onChange={(e) => updateItem(record.id, 'brand_model', e.target.value)}
        />
      )
    },
    {
      title: '单位',
      dataIndex: 'unit',
      width: 80,
      render: (_: any, record: EnhancedPurchaseItem) => (
        <Input
          value={record.unit}
          placeholder="单位"
          disabled={record.item_type === ItemType.MAIN_MATERIAL && !!record.contract_item_id}
          onChange={(e) => updateItem(record.id, 'unit', e.target.value)}
        />
      )
    },
    {
      title: (
        <span>
          数量
          <Tooltip title="主材数量不能超过合同清单剩余数量">
            <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
          </Tooltip>
        </span>
      ),
      dataIndex: 'quantity',
      width: 120,
      render: (_: any, record: EnhancedPurchaseItem) => (
        <div>
          <InputNumber
            value={record.quantity}
            min={1}
            max={record.remaining_quantity}
            precision={2}
            style={{ width: '100%' }}
            onChange={(value) => handleQuantityChange(record.id, value || 1)}
          />
          {record.remaining_quantity !== undefined && (
            <div style={{ fontSize: '10px', color: '#999' }}>
              最多: {record.remaining_quantity}
            </div>
          )}
        </div>
      )
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      width: 150,
      render: (_: any, record: EnhancedPurchaseItem) => (
        <Input
          value={record.remarks}
          placeholder="备注"
          onChange={(e) => updateItem(record.id, 'remarks', e.target.value)}
        />
      )
    },
    {
      title: '操作',
      width: 60,
      render: (_: any, record: EnhancedPurchaseItem) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => removeItem(record.id)}
        />
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Form form={form} layout="vertical">
        {/* 功能说明 */}
        <Alert
          message="智能申购功能说明"
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              <li>主材必须从合同清单中选择，确保申购物料与合同一致</li>
              <li>选择物料名称后，系统自动显示可选的规格型号</li>
              <li>品牌、单位等信息会根据合同清单自动填充</li>
              <li>申购数量不能超过合同清单的剩余可申购数量</li>
              <li>辅材可以自由填写，不受合同清单限制</li>
            </ul>
          }
          type="info"
          style={{ marginBottom: 16 }}
        />

        {/* 基本信息 */}
        <Card title="申购单基本信息" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                label="项目名称" 
                required
                tooltip="请选择要申购物料的项目"
              >
                <Select
                  value={selectedProjectId}
                  placeholder="请选择项目"
                  style={{ width: '100%' }}
                  showSearch
                  filterOption={(input, option) =>
                    (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
                  }
                  onChange={(value) => {
                    setSelectedProjectId(value);
                    // 清空现有的申购明细
                    setItems([]);
                    setMaterialNames([]);
                  }}
                >
                  {projects.map(project => (
                    <Option key={project.id} value={project.id} label={project.project_name}>
                      <div>
                        <div>{project.project_name}</div>
                        <div style={{ fontSize: '12px', color: '#999' }}>
                          {project.project_code} | {project.status === 'in_progress' ? '进行中' : project.status}
                        </div>
                      </div>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="需求日期" name="required_date">
                <DatePicker style={{ width: '100%' }} placeholder="选择需求日期" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item label="申购说明" name="remarks">
                <TextArea rows={2} placeholder="请输入申购说明或备注" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 申购明细 */}
        <Card 
          title="申购明细" 
          extra={
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={addItem}
              disabled={!selectedProjectId}
              title={!selectedProjectId ? "请先选择项目" : "添加申购明细"}
            >
              添加明细
            </Button>
          }
          style={{ marginBottom: 16 }}
        >
          <Table
            columns={columns}
            dataSource={items}
            rowKey="id"
            pagination={false}
            scroll={{ x: 1200 }}
            locale={{ 
              emptyText: selectedProjectId 
                ? '请点击"添加明细"按钮添加申购物料' 
                : '请先选择项目，然后添加申购明细'
            }}
            size="small"
          />
        </Card>

        {/* 操作按钮 */}
        <Card>
          <Space>
            <Button onClick={() => navigate('/purchases')}>
              返回
            </Button>
            <Button 
              type="primary"
              loading={loading}
              onClick={handleSave}
            >
              保存申购单
            </Button>
          </Space>
        </Card>
      </Form>
    </div>
  );
};

export default EnhancedPurchaseForm;