import React, { useState } from 'react';
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
  Col
} from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { createPurchaseRequest } from '../../services/purchase';
import { ItemType } from '../../types/purchase';

const { TextArea } = Input;
const { Option } = Select;

interface SimplePurchaseItem {
  id: string;
  item_name: string;
  specification: string;
  brand: string;
  unit: string;
  quantity: number;
  item_type: ItemType;
  supplier_name?: string;
  remarks?: string;
}

const SimplePurchaseForm: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<SimplePurchaseItem[]>([]);

  // 添加申购明细
  const addItem = () => {
    const newItem: SimplePurchaseItem = {
      id: Date.now().toString(),
      item_name: '',
      specification: '',
      brand: '',
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

  // 保存申购单
  const handleSave = async () => {
    if (items.length === 0) {
      message.warning('请至少添加一个申购明细');
      return;
    }

    try {
      const values = await form.validateFields();
      setLoading(true);

      // 构建请求数据
      const requestData = {
        project_id: 2, // 暂时使用固定的项目ID
        required_date: values.required_date?.toISOString(),
        remarks: values.remarks,
        items: items.map(item => ({
          item_name: item.item_name,
          specification: item.specification,
          brand: item.brand,
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
      render: (_: any, record: SimplePurchaseItem) => (
        <Select
          value={record.item_type}
          style={{ width: '100%' }}
          onChange={(value) => updateItem(record.id, 'item_type', value)}
        >
          <Option value={ItemType.MAIN_MATERIAL}>主材</Option>
          <Option value={ItemType.AUXILIARY_MATERIAL}>辅材</Option>
        </Select>
      )
    },
    {
      title: '物料名称',
      dataIndex: 'item_name',
      width: 200,
      render: (_: any, record: SimplePurchaseItem) => (
        <Input
          value={record.item_name}
          placeholder="请输入物料名称"
          onChange={(e) => updateItem(record.id, 'item_name', e.target.value)}
        />
      )
    },
    {
      title: '规格型号',
      dataIndex: 'specification',
      width: 150,
      render: (_: any, record: SimplePurchaseItem) => (
        <Input
          value={record.specification}
          placeholder="请输入规格型号"
          onChange={(e) => updateItem(record.id, 'specification', e.target.value)}
        />
      )
    },
    {
      title: '品牌',
      dataIndex: 'brand',
      width: 120,
      render: (_: any, record: SimplePurchaseItem) => (
        <Input
          value={record.brand}
          placeholder="请输入品牌"
          onChange={(e) => updateItem(record.id, 'brand', e.target.value)}
        />
      )
    },
    {
      title: '单位',
      dataIndex: 'unit',
      width: 80,
      render: (_: any, record: SimplePurchaseItem) => (
        <Input
          value={record.unit}
          placeholder="单位"
          onChange={(e) => updateItem(record.id, 'unit', e.target.value)}
        />
      )
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      width: 100,
      render: (_: any, record: SimplePurchaseItem) => (
        <InputNumber
          value={record.quantity}
          min={1}
          precision={2}
          style={{ width: '100%' }}
          onChange={(value) => updateItem(record.id, 'quantity', value || 1)}
        />
      )
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      width: 150,
      render: (_: any, record: SimplePurchaseItem) => (
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
      render: (_: any, record: SimplePurchaseItem) => (
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
        {/* 基本信息 */}
        <Card title="申购单基本信息" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="项目名称">
                <Input disabled value="娄山关路445弄综合弱电智能化" />
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
            <Button type="primary" icon={<PlusOutlined />} onClick={addItem}>
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
            scroll={{ x: 1000 }}
            locale={{ emptyText: '请点击"添加明细"按钮添加申购物料' }}
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

export default SimplePurchaseForm;