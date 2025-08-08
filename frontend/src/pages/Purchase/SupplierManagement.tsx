import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Input,
  Modal,
  Form,
  message,
  Card,
  Row,
  Col,
  Switch,
  Rate,
  Popconfirm
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';
import {
  Supplier,
  SupplierCreate,
  SupplierUpdate,
  SupplierQueryParams
} from '../../types/purchase';
import {
  getSuppliers,
  createSupplier,
  updateSupplier
} from '../../services/purchase';

const { Search } = Input;
const { TextArea } = Input;

const SupplierManagement: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Supplier[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  
  // 查询条件
  const [queryParams, setQueryParams] = useState<SupplierQueryParams>({});
  
  // 弹窗状态
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [form] = Form.useForm();

  // 加载供应商列表
  const loadSuppliers = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getSuppliers({
        ...queryParams,
        page: currentPage,
        size: pageSize
      });
      
      setData(response.items);
      setTotal(response.total);
      
    } catch (error) {
      console.error('加载供应商列表失败:', error);
      message.error('加载供应商列表失败');
    } finally {
      setLoading(false);
    }
  }, [queryParams, currentPage, pageSize]);

  useEffect(() => {
    loadSuppliers();
  }, [loadSuppliers]);

  // 搜索处理
  const handleSearch = (value: string) => {
    setQueryParams(prev => ({ ...prev, search: value }));
    setCurrentPage(1);
  };

  // 新建供应商
  const handleCreate = () => {
    setEditingSupplier(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 编辑供应商
  const handleEdit = (supplier: Supplier) => {
    setEditingSupplier(supplier);
    form.setFieldsValue(supplier);
    setModalVisible(true);
  };

  // 保存供应商
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingSupplier) {
        // 更新
        await updateSupplier(editingSupplier.id, values);
        message.success('供应商更新成功');
      } else {
        // 创建
        await createSupplier(values);
        message.success('供应商创建成功');
      }
      
      setModalVisible(false);
      loadSuppliers();
    } catch (error: any) {
      console.error('保存供应商失败:', error);
      message.error(error.message || '保存供应商失败');
    }
  };

  // 表格列定义
  const columns: ColumnsType<Supplier> = [
    {
      title: '供应商编码',
      dataIndex: 'supplier_code',
      key: 'supplier_code',
      width: 120
    },
    {
      title: '供应商名称',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      width: 200,
      ellipsis: true
    },
    {
      title: '联系人',
      dataIndex: 'contact_person',
      key: 'contact_person',
      width: 100
    },
    {
      title: '联系电话',
      dataIndex: 'phone',
      key: 'phone',
      width: 120
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 150,
      ellipsis: true
    },
    {
      title: '地址',
      dataIndex: 'address',
      key: 'address',
      width: 200,
      ellipsis: true
    },
    {
      title: '评级',
      dataIndex: 'rating',
      key: 'rating',
      width: 120,
      render: (rating: number) => (
        <Rate disabled value={rating} style={{ fontSize: 16 }} />
      )
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (value: string) => new Date(value).toLocaleDateString()
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="text" 
            icon={<EditOutlined />} 
            size="small"
            onClick={() => handleEdit(record)}
          />
        </Space>
      )
    }
  ];

  return (
    <div>
      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Search
              placeholder="搜索供应商名称、编码或联系人"
              allowClear
              style={{ width: 300 }}
              onSearch={handleSearch}
            />
          </Col>
          
          <Col>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              新建供应商
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 供应商列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条/共 ${total} 条`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size || 10);
            }
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 供应商表单弹窗 */}
      <Modal
        title={editingSupplier ? '编辑供应商' : '新建供应商'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={800}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            rating: 3,
            is_active: true
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="供应商名称"
                name="supplier_name"
                rules={[{ required: true, message: '请输入供应商名称' }]}
              >
                <Input placeholder="请输入供应商名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="供应商编码"
                name="supplier_code"
              >
                <Input placeholder="留空自动生成" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="联系人"
                name="contact_person"
              >
                <Input placeholder="请输入联系人姓名" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="联系电话"
                name="phone"
              >
                <Input placeholder="请输入联系电话" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="邮箱"
                name="email"
                rules={[{ type: 'email', message: '请输入有效的邮箱地址' }]}
              >
                <Input placeholder="请输入邮箱地址" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="供应商评级"
                name="rating"
              >
                <Rate />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="地址"
            name="address"
          >
            <Input placeholder="请输入详细地址" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="营业执照号"
                name="business_license"
              >
                <Input placeholder="请输入营业执照号" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="税号"
                name="tax_number"
              >
                <Input placeholder="请输入税号" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="银行账户"
            name="bank_account"
          >
            <Input placeholder="请输入银行账户信息" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="状态"
                name="is_active"
                valuePropName="checked"
              >
                <Switch checkedChildren="启用" unCheckedChildren="禁用" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="备注"
            name="remarks"
          >
            <TextArea rows={3} placeholder="请输入备注信息" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SupplierManagement;