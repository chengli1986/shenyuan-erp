import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Button,
  Table,
  message,
  Divider,
  Space,
  Typography,
  Card,
  Row,
  Col
} from 'antd';
import { DollarOutlined } from '@ant-design/icons';
import api from '../../services/api';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface PurchaseItem {
  id: number;
  item_name: string;
  specification: string;
  brand: string;
  unit: string;
  quantity: number;
  unit_price?: number;
  total_price?: number;
  supplier_name?: string;
  supplier_contact?: string;
  supplier_contact_person?: string;  // 新增：供应商联系人全名
  payment_method?: string;  // 新增：物料级付款方式
  estimated_delivery?: string;
}

interface PurchaseQuoteFormProps {
  visible: boolean;
  purchaseData: any;
  onClose: () => void;
  onSuccess: () => void;
}

interface QuoteFormData {
  quote_notes?: string;
  items: Array<{
    item_id: number;
    unit_price: number;
    supplier_name: string;
    supplier_contact?: string;
    supplier_contact_person?: string;  // 新增
    payment_method?: string;  // 新增
    estimated_delivery?: string;
  }>;
}

const PurchaseQuoteForm: React.FC<PurchaseQuoteFormProps> = ({
  visible,
  purchaseData,
  onClose,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<PurchaseItem[]>([]);

  useEffect(() => {
    if (visible && purchaseData?.items) {
      setItems(purchaseData.items);
      // 重置表单
      form.resetFields();
    }
  }, [visible, purchaseData, form]);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      console.log('📝 [React] 开始表单验证...');
      const values = await form.validateFields();
      console.log('✅ [React] 表单验证通过，获取到的values:', values);
      
      // 构建询价数据
      const quoteData: QuoteFormData = {
        quote_notes: values.quote_notes,
        items: items.map(item => ({
          item_id: item.id,
          unit_price: values[`unit_price_${item.id}`] || 0,
          supplier_name: values[`supplier_name_${item.id}`] || '',
          supplier_contact: values[`supplier_contact_${item.id}`] || '',
          supplier_contact_person: values[`supplier_contact_person_${item.id}`] || '',
          payment_method: values[`payment_method_${item.id}`] || '',
          estimated_delivery: values[`estimated_delivery_${item.id}`] 
            ? values[`estimated_delivery_${item.id}`].format('YYYY-MM-DD') + 'T00:00:00' 
            : undefined
        }))
      };

      // 验证所有必填项
      for (const item of quoteData.items) {
        const itemName = items.find(i => i.id === item.item_id)?.item_name;
        
        if (!item.unit_price || item.unit_price <= 0) {
          message.error(`请填写 ${itemName} 的单价`);
          return;
        }
        if (!item.supplier_name) {
          message.error(`请填写 ${itemName} 的供应商`);
          return;
        }
        if (!item.supplier_contact_person) {
          message.error(`请填写 ${itemName} 的联系人`);
          return;
        }
        if (!item.supplier_contact) {
          message.error(`请填写 ${itemName} 的联系方式`);
          return;
        }
        if (!item.payment_method) {
          message.error(`请选择 ${itemName} 的付款方式`);
          return;
        }
      }

      console.log('🚀 [React] 开始提交询价数据:', JSON.stringify(quoteData, null, 2));
      console.log('🔗 [React] API调用地址:', `purchases/${purchaseData.id}/quote`);
      console.log('🔑 [React] 当前token存在:', !!localStorage.getItem('access_token'));
      await api.post(`purchases/${purchaseData.id}/quote`, quoteData);
      message.success('询价完成，已提交部门主管审批');
      onSuccess();
      onClose();
    } catch (error: any) {
      console.error('💥 [React] 询价失败:', error);
      console.error('🔍 [React] 错误详情:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        stack: error.stack,
        config: error.config
      });
      
      // 分析错误类型
      if (error.response) {
        console.error(`🌐 [React] HTTP错误 ${error.response.status}: ${error.response.statusText}`);
        console.error('📋 [React] 服务器响应:', error.response.data);
      } else if (error.request) {
        console.error('🚫 [React] 网络错误: 请求已发送但没有收到响应');
        console.error('📡 [React] 请求详情:', error.request);
      } else {
        console.error('⚙️ [React] 配置错误:', error.message);
      }
      
      message.error(error.response?.data?.detail || error.message || '询价提交失败');
    } finally {
      setLoading(false);
    }
  };

  const calculateTotal = (itemId: number, unitPrice: number) => {
    const item = items.find(i => i.id === itemId);
    return item ? (unitPrice * item.quantity).toFixed(2) : '0.00';
  };

  const getTotalAmount = () => {
    let total = 0;
    items.forEach(item => {
      const unitPrice = form.getFieldValue(`unit_price_${item.id}`) || 0;
      total += unitPrice * item.quantity;
    });
    return total.toFixed(2);
  };

  const columns = [
    {
      title: '物料名称',
      dataIndex: 'item_name',
      width: 200,
      render: (text: string, record: PurchaseItem) => (
        <div>
          <Text strong>{text}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {record.specification}
          </Text>
        </div>
      )
    },
    {
      title: '品牌',
      dataIndex: 'brand',
      width: 100
    },
    {
      title: '数量',
      width: 80,
      render: (record: PurchaseItem) => `${record.quantity} ${record.unit}`
    },
    {
      title: '单价(元)',
      width: 120,
      render: (record: PurchaseItem) => (
        <Form.Item
          name={`unit_price_${record.id}`}
          style={{ margin: 0 }}
          rules={[
            { required: true, message: '请填写单价' },
            { type: 'number', min: 0.01, message: '单价必须大于0' }
          ]}
        >
          <InputNumber
            placeholder="单价"
            style={{ width: '100%' }}
            min={0.01}
            precision={2}
            onChange={() => form.validateFields()}
          />
        </Form.Item>
      )
    },
    {
      title: '总价(元)',
      width: 120,
      render: (record: PurchaseItem) => {
        const unitPrice = form.getFieldValue(`unit_price_${record.id}`) || 0;
        return (
          <Text strong style={{ color: '#1890ff' }}>
            ¥{calculateTotal(record.id, unitPrice)}
          </Text>
        );
      }
    },
    {
      title: '供应商',
      width: 150,
      render: (record: PurchaseItem) => (
        <Form.Item
          name={`supplier_name_${record.id}`}
          style={{ margin: 0 }}
          rules={[{ required: true, message: '请填写供应商' }]}
        >
          <Input placeholder="供应商名称" />
        </Form.Item>
      )
    },
    {
      title: '联系人',
      width: 100,
      render: (record: PurchaseItem) => (
        <Form.Item
          name={`supplier_contact_person_${record.id}`}
          style={{ margin: 0 }}
          rules={[{ required: true, message: '请填写联系人' }]}
        >
          <Input placeholder="联系人姓名" />
        </Form.Item>
      )
    },
    {
      title: '联系方式',
      width: 120,
      render: (record: PurchaseItem) => (
        <Form.Item
          name={`supplier_contact_${record.id}`}
          style={{ margin: 0 }}
          rules={[{ required: true, message: '请填写联系方式' }]}
        >
          <Input placeholder="联系电话" />
        </Form.Item>
      )
    },
    {
      title: '付款方式',
      width: 120,
      render: (record: PurchaseItem) => (
        <Form.Item
          name={`payment_method_${record.id}`}
          style={{ margin: 0 }}
          rules={[{ required: true, message: '请填写付款方式' }]}
        >
          <Input placeholder="如：月结30天" />
        </Form.Item>
      )
    },
    {
      title: '预计到货',
      width: 130,
      render: (record: PurchaseItem) => (
        <Form.Item
          name={`estimated_delivery_${record.id}`}
          style={{ margin: 0 }}
        >
          <DatePicker 
            placeholder="选择日期"
            style={{ width: '100%' }}
            disabledDate={(current) => current && current < dayjs().startOf('day')}
          />
        </Form.Item>
      )
    }
  ];

  return (
    <Modal
      title={
        <Space>
          <DollarOutlined />
          <span>申购单询价 - {purchaseData?.request_code}</span>
        </Space>
      }
      visible={visible}
      onCancel={onClose}
      width={1400}
      footer={[
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={handleSubmit}>
          提交询价
        </Button>
      ]}
    >
      <Form
        form={form}
        layout="vertical"
        onValuesChange={() => {
          // 触发总价重新计算
        }}
      >
        {/* 申购单基本信息 */}
        <Card size="small" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Text strong>申购单号：</Text>
              <Text>{purchaseData?.request_code}</Text>
            </Col>
            <Col span={6}>
              <Text strong>项目：</Text>
              <Text>{purchaseData?.project_name}</Text>
            </Col>
            <Col span={6}>
              <Text strong>申请人：</Text>
              <Text>{purchaseData?.requester_name}</Text>
            </Col>
            <Col span={6}>
              <Text strong>申请日期：</Text>
              <Text>{dayjs(purchaseData?.request_date).format('YYYY-MM-DD')}</Text>
            </Col>
          </Row>
        </Card>

        {/* 申购明细表格 */}
        <div style={{ marginBottom: 16 }}>
          <Title level={5}>申购明细</Title>
          <Table
            columns={columns}
            dataSource={items}
            rowKey="id"
            pagination={false}
            scroll={{ x: 1300 }}
            size="small"
            bordered
          />
        </div>

        {/* 总价显示 */}
        <Card size="small" style={{ marginBottom: 16, backgroundColor: '#f0f2f5' }}>
          <Row justify="end">
            <Col>
              <Text strong style={{ fontSize: '16px', color: '#1890ff' }}>
                <DollarOutlined /> 总金额：¥{getTotalAmount()}
              </Text>
            </Col>
          </Row>
        </Card>

        <Divider />

        <Form.Item
          label="询价备注"
          name="quote_notes"
        >
          <TextArea
            placeholder="请填写询价备注信息..."
            rows={3}
            maxLength={500}
            showCount
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default PurchaseQuoteForm;