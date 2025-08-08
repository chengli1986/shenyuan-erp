import React, { useState, useEffect, useCallback } from 'react';
import {
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Card,
  Table,
  Space,
  Modal,
  message,
  Row,
  Col,
  InputNumber,
  Tooltip,
  Tag,
  Divider
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  BulbOutlined,
  SaveOutlined,
  SendOutlined
} from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import {
  PurchaseRequestCreate,
  PurchaseItemCreate,
  ItemType,
  AuxiliaryRecommendation
} from '../../types/purchase';
import { ContractItem } from '../../types/contract';
import {
  createPurchaseRequest,
  updatePurchaseRequest,
  submitPurchaseRequest,
  getAuxiliaryRecommendations,
  formatItemType
} from '../../services/purchase';
import { getContractItems } from '../../services/contract';

const { Option } = Select;
const { TextArea } = Input;

interface PurchaseRequestFormProps {
  projectId: number;
  requestId?: number;
  onClose: () => void;
  onSuccess: () => void;
}

interface PurchaseItemFormData extends PurchaseItemCreate {
  id?: string; // 临时ID用于表格
}

const PurchaseRequestForm: React.FC<PurchaseRequestFormProps> = ({
  projectId,
  requestId,
  onClose,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  
  // 申购明细列表
  const [items, setItems] = useState<PurchaseItemFormData[]>([]);
  
  // 合同清单项选项
  const [contractItems, setContractItems] = useState<ContractItem[]>([]);
  const [contractItemsLoading, setContractItemsLoading] = useState(false);
  
  // 辅材推荐
  const [recommendationVisible, setRecommendationVisible] = useState(false);
  const [recommendations, setRecommendations] = useState<AuxiliaryRecommendation[]>([]);
  const [selectedMainMaterial, setSelectedMainMaterial] = useState<number | null>(null);

  // 加载合同清单项
  const loadContractItems = useCallback(async () => {
    setContractItemsLoading(true);
    try {
      // 需要获取项目的当前合同清单版本
      // 这里暂时使用项目ID，实际应该获取当前版本ID
      const response = await getContractItems(projectId, 1, { 
        size: 1000 // 获取所有项目
      });
      setContractItems(response.items);
    } catch (error) {
      console.error('加载合同清单失败:', error);
      message.warning('无法加载合同清单，主材选择功能受限');
    } finally {
      setContractItemsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadContractItems();
  }, [loadContractItems]);

  // 添加申购明细
  const addItem = () => {
    const newItem: PurchaseItemFormData = {
      id: Date.now().toString(),
      item_name: '',
      unit: '',
      quantity: 1,
      item_type: ItemType.MAIN_MATERIAL
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

  // 处理合同清单项选择
  const handleContractItemSelect = (itemId: string, contractItemId: number) => {
    const contractItem = contractItems.find(item => item.id === contractItemId);
    if (contractItem) {
      updateItem(itemId, 'contract_item_id', contractItemId);
      updateItem(itemId, 'item_name', contractItem.item_name);
      updateItem(itemId, 'specification', contractItem.specification);
      updateItem(itemId, 'brand', contractItem.brand_model);
      updateItem(itemId, 'unit', contractItem.unit);
    }
  };

  // 获取辅材推荐
  const getRecommendations = async (mainMaterialId: number) => {
    try {
      const recs = await getAuxiliaryRecommendations(mainMaterialId);
      setRecommendations(recs);
      setSelectedMainMaterial(mainMaterialId);
      setRecommendationVisible(true);
    } catch (error) {
      console.error('获取辅材推荐失败:', error);
      message.error('获取辅材推荐失败');
    }
  };

  // 应用辅材推荐
  const applyRecommendation = (recommendation: AuxiliaryRecommendation) => {
    const newItem: PurchaseItemFormData = {
      id: Date.now().toString(),
      item_name: recommendation.item_name,
      specification: recommendation.specification,
      brand: recommendation.brand,
      unit: recommendation.unit || '个',
      quantity: recommendation.avg_quantity || 1,
      item_type: ItemType.AUXILIARY_MATERIAL,
      remarks: `来源: ${recommendation.source}, 置信度: ${(recommendation.confidence * 100).toFixed(0)}%`
    };
    setItems([...items, newItem]);
    message.success('已添加推荐辅材');
  };

  // 保存申购单
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      const requestData: PurchaseRequestCreate = {
        project_id: projectId,
        required_date: values.required_date ? values.required_date.toISOString() : undefined,
        remarks: values.remarks,
        items: items.map(item => ({
          contract_item_id: item.contract_item_id,
          item_name: item.item_name,
          specification: item.specification,
          brand: item.brand,
          unit: item.unit,
          quantity: item.quantity,
          item_type: item.item_type,
          remarks: item.remarks
        }))
      };

      if (requestId) {
        await updatePurchaseRequest(requestId, {
          required_date: requestData.required_date,
          remarks: requestData.remarks
        });
      } else {
        await createPurchaseRequest(requestData);
      }

      message.success('申购单保存成功');
      onSuccess();
    } catch (error: any) {
      console.error('保存申购单失败:', error);
      message.error(error.message || '保存申购单失败');
    } finally {
      setLoading(false);
    }
  };

  // 提交申购单
  const handleSubmit = async () => {
    try {
      await handleSave();
      if (requestId) {
        setSubmitLoading(true);
        await submitPurchaseRequest(requestId);
        message.success('申购单提交成功');
        onSuccess();
      }
    } catch (error: any) {
      console.error('提交申购单失败:', error);
      message.error(error.message || '提交申购单失败');
    } finally {
      setSubmitLoading(false);
    }
  };

  // 申购明细表格列定义
  const itemColumns: ColumnsType<PurchaseItemFormData> = [
    {
      title: '类型',
      dataIndex: 'item_type',
      width: 80,
      render: (_, record) => (
        <Select
          value={record.item_type}
          style={{ width: '100%' }}
          onChange={(value) => {
            updateItem(record.id!, 'item_type', value);
            if (value === ItemType.AUXILIARY_MATERIAL) {
              updateItem(record.id!, 'contract_item_id', undefined);
            }
          }}
        >
          <Option value={ItemType.MAIN_MATERIAL}>主材</Option>
          <Option value={ItemType.AUXILIARY_MATERIAL}>辅材</Option>
        </Select>
      )
    },
    {
      title: '合同清单项',
      dataIndex: 'contract_item_id',
      width: 200,
      render: (_, record) => (
        record.item_type === ItemType.MAIN_MATERIAL ? (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Select
              value={record.contract_item_id}
              placeholder="选择合同清单项"
              style={{ width: '100%' }}
              loading={contractItemsLoading}
              showSearch
              filterOption={(input, option) => {
                const label = option?.label || option?.value || '';
                return String(label).toLowerCase().includes(input.toLowerCase());
              }}
              onChange={(value) => handleContractItemSelect(record.id!, value)}
            >
              {contractItems.map(item => (
                <Option key={item.id} value={item.id}>
                  {item.item_name} - {item.specification}
                </Option>
              ))}
            </Select>
            {record.contract_item_id && (
              <Button
                type="link"
                size="small"
                icon={<BulbOutlined />}
                onClick={() => getRecommendations(record.contract_item_id!)}
              >
                推荐辅材
              </Button>
            )}
          </Space>
        ) : (
          <span style={{ color: '#999' }}>辅材无需选择</span>
        )
      )
    },
    {
      title: '物料名称',
      dataIndex: 'item_name',
      width: 150,
      render: (_, record) => (
        <Input
          value={record.item_name}
          placeholder="请输入物料名称"
          onChange={(e) => updateItem(record.id!, 'item_name', e.target.value)}
          disabled={record.item_type === ItemType.MAIN_MATERIAL && !!record.contract_item_id}
        />
      )
    },
    {
      title: '规格型号',
      dataIndex: 'specification',
      width: 150,
      render: (_, record) => (
        <Input
          value={record.specification}
          placeholder="请输入规格型号"
          onChange={(e) => updateItem(record.id!, 'specification', e.target.value)}
        />
      )
    },
    {
      title: '品牌',
      dataIndex: 'brand',
      width: 120,
      render: (_, record) => (
        <Input
          value={record.brand}
          placeholder="请输入品牌"
          onChange={(e) => updateItem(record.id!, 'brand', e.target.value)}
        />
      )
    },
    {
      title: '单位',
      dataIndex: 'unit',
      width: 80,
      render: (_, record) => (
        <Input
          value={record.unit}
          placeholder="单位"
          onChange={(e) => updateItem(record.id!, 'unit', e.target.value)}
          disabled={record.item_type === ItemType.MAIN_MATERIAL && !!record.contract_item_id}
        />
      )
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      width: 100,
      render: (_, record) => (
        <InputNumber
          value={record.quantity}
          min={1}
          precision={2}
          style={{ width: '100%' }}
          onChange={(value) => updateItem(record.id!, 'quantity', value || 1)}
        />
      )
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      width: 150,
      render: (_, record) => (
        <Input
          value={record.remarks}
          placeholder="备注"
          onChange={(e) => updateItem(record.id!, 'remarks', e.target.value)}
        />
      )
    },
    {
      title: '操作',
      width: 80,
      render: (_, record) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => removeItem(record.id!)}
        />
      )
    }
  ];

  return (
    <div>
      <Form form={form} layout="vertical">
        <Card title="基本信息" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="需求日期"
                name="required_date"
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="申购备注"
                name="remarks"
              >
                <TextArea rows={3} placeholder="请输入申购说明或备注" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        <Card 
          title="申购明细" 
          extra={
            <Button type="primary" icon={<PlusOutlined />} onClick={addItem}>
              添加明细
            </Button>
          }
          style={{ marginBottom: 16 }}
        >
          <Table
            columns={itemColumns}
            dataSource={items}
            rowKey="id"
            pagination={false}
            scroll={{ x: 1200 }}
            locale={{ emptyText: '暂无申购明细，请点击"添加明细"按钮添加' }}
          />
        </Card>

        <Card>
          <Space>
            <Button onClick={onClose}>
              取消
            </Button>
            <Button 
              type="default" 
              icon={<SaveOutlined />}
              loading={loading}
              onClick={handleSave}
            >
              保存草稿
            </Button>
            <Button 
              type="primary" 
              icon={<SendOutlined />}
              loading={submitLoading}
              onClick={handleSubmit}
              disabled={items.length === 0}
            >
              保存并提交
            </Button>
          </Space>
        </Card>
      </Form>

      {/* 辅材推荐弹窗 */}
      <Modal
        title="辅材智能推荐"
        open={recommendationVisible}
        onCancel={() => setRecommendationVisible(false)}
        footer={null}
        width={800}
      >
        <Table
          dataSource={recommendations}
          rowKey="item_name"
          pagination={false}
          size="small"
          columns={[
            {
              title: '推荐物料',
              dataIndex: 'item_name',
              render: (text, record) => (
                <div>
                  <div><strong>{text}</strong></div>
                  {record.specification && (
                    <div style={{ fontSize: 12, color: '#666' }}>
                      {record.specification}
                    </div>
                  )}
                </div>
              )
            },
            {
              title: '单位',
              dataIndex: 'unit',
              width: 80
            },
            {
              title: '建议数量',
              dataIndex: 'avg_quantity',
              width: 100,
              render: (value) => value ? value.toFixed(2) : '-'
            },
            {
              title: '置信度',
              dataIndex: 'confidence',
              width: 100,
              render: (value) => (
                <Tag color={value > 0.8 ? 'green' : value > 0.5 ? 'orange' : 'default'}>
                  {(value * 100).toFixed(0)}%
                </Tag>
              )
            },
            {
              title: '推荐来源',
              dataIndex: 'source',
              width: 120
            },
            {
              title: '操作',
              width: 80,
              render: (_, record) => (
                <Button
                  type="link"
                  size="small"
                  onClick={() => applyRecommendation(record)}
                >
                  添加
                </Button>
              )
            }
          ]}
        />
      </Modal>
    </div>
  );
};

export default PurchaseRequestForm;