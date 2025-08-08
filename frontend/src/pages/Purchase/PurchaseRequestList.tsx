import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  DatePicker,
  Modal,
  message,
  Card,
  Row,
  Col,
  Statistic,
  Tooltip,
  Popconfirm
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckOutlined,
  DollarOutlined,
  AuditOutlined
} from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';
import {
  PurchaseRequestWithItems,
  PurchaseStatus,
  PurchaseRequestQueryParams
} from '../../types/purchase';
import {
  getPurchaseRequests,
  deletePurchaseRequest,
  submitPurchaseRequest,
  formatPurchaseStatus,
  getPurchaseStatusColor
} from '../../services/purchase';

const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface PurchaseRequestListProps {
  projectId?: number;
  onCreateRequest?: () => void;
  onEditRequest?: (requestId: number) => void;
}

const PurchaseRequestList: React.FC<PurchaseRequestListProps> = ({ 
  projectId, 
  onCreateRequest, 
  onEditRequest 
}) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PurchaseRequestWithItems[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  
  // 查询条件
  const [queryParams, setQueryParams] = useState<PurchaseRequestQueryParams>({
    project_id: projectId
  });
  
  // 统计信息
  const [statistics, setStatistics] = useState({
    total_requests: 0,
    pending_approval: 0,
    approved: 0,
    total_amount: 0
  });

  // 加载申购单列表
  const loadPurchaseRequests = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getPurchaseRequests({
        ...queryParams,
        page: currentPage,
        size: pageSize
      });
      
      setData(response.items);
      setTotal(response.total);
      
      // 计算统计信息
      const stats = {
        total_requests: response.total,
        pending_approval: response.items.filter(item => 
          ['submitted', 'price_quoted'].includes(item.status)
        ).length,
        approved: response.items.filter(item => 
          ['final_approved', 'completed'].includes(item.status)
        ).length,
        total_amount: response.items
          .filter(item => item.total_amount)
          .reduce((sum, item) => sum + (item.total_amount || 0), 0)
      };
      setStatistics(stats);
      
    } catch (error) {
      console.error('加载申购单列表失败:', error);
      message.error('加载申购单列表失败');
    } finally {
      setLoading(false);
    }
  }, [queryParams, currentPage, pageSize]);

  useEffect(() => {
    loadPurchaseRequests();
  }, [loadPurchaseRequests]);

  // 搜索处理
  const handleSearch = (value: string) => {
    setQueryParams(prev => ({ ...prev, search: value }));
    setCurrentPage(1);
  };

  // 状态筛选
  const handleStatusFilter = (status: string) => {
    setQueryParams(prev => ({ 
      ...prev, 
      status: status === 'all' ? undefined : status as PurchaseStatus 
    }));
    setCurrentPage(1);
  };

  // 提交申购单
  const handleSubmit = async (requestId: number) => {
    try {
      await submitPurchaseRequest(requestId);
      message.success('申购单提交成功');
      loadPurchaseRequests();
    } catch (error) {
      console.error('提交申购单失败:', error);
      message.error('提交申购单失败');
    }
  };

  // 删除申购单
  const handleDelete = async (requestId: number) => {
    try {
      await deletePurchaseRequest(requestId);
      message.success('申购单删除成功');
      loadPurchaseRequests();
    } catch (error) {
      console.error('删除申购单失败:', error);
      message.error('删除申购单失败');
    }
  };

  // 表格列定义
  const columns: ColumnsType<PurchaseRequestWithItems> = [
    {
      title: '申购单号',
      dataIndex: 'request_code',
      key: 'request_code',
      width: 150,
      fixed: 'left'
    },
    {
      title: '项目名称',
      dataIndex: 'project_name',
      key: 'project_name',
      width: 200,
      ellipsis: true
    },
    {
      title: '申请人',
      dataIndex: 'requester_name',
      key: 'requester_name',
      width: 100
    },
    {
      title: '申请日期',
      dataIndex: 'request_date',
      key: 'request_date',
      width: 120,
      render: (value: string) => new Date(value).toLocaleDateString()
    },
    {
      title: '需求日期',
      dataIndex: 'required_date',
      key: 'required_date',
      width: 120,
      render: (value: string) => value ? new Date(value).toLocaleDateString() : '-'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: PurchaseStatus) => (
        <Tag color={getPurchaseStatusColor(status)}>
          {formatPurchaseStatus(status)}
        </Tag>
      )
    },
    {
      title: '申购金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 120,
      align: 'right',
      render: (amount: number) => amount ? `¥${amount.toLocaleString()}` : '-'
    },
    {
      title: '申购项数',
      key: 'items_count',
      width: 100,
      align: 'center',
      render: (_, record) => record.items?.length || 0
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              size="small"
              onClick={() => {/* TODO: 查看详情 */}}
            />
          </Tooltip>
          
          {record.status === PurchaseStatus.DRAFT && (
            <>
              <Tooltip title="编辑">
                <Button 
                  type="text" 
                  icon={<EditOutlined />} 
                  size="small"
                  onClick={() => onEditRequest?.(record.id)}
                />
              </Tooltip>
              <Tooltip title="提交">
                <Button 
                  type="text" 
                  icon={<CheckOutlined />} 
                  size="small"
                  onClick={() => handleSubmit(record.id)}
                />
              </Tooltip>
              <Popconfirm
                title="确定删除此申购单吗？"
                onConfirm={() => handleDelete(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Tooltip title="删除">
                  <Button 
                    type="text" 
                    icon={<DeleteOutlined />} 
                    size="small"
                    danger
                  />
                </Tooltip>
              </Popconfirm>
            </>
          )}
          
          {record.status === PurchaseStatus.SUBMITTED && (
            <Tooltip title="询价">
              <Button 
                type="text" 
                icon={<DollarOutlined />} 
                size="small"
                onClick={() => {/* TODO: 询价 */}}
              />
            </Tooltip>
          )}
          
          {['price_quoted', 'dept_approved'].includes(record.status) && (
            <Tooltip title="审批">
              <Button 
                type="text" 
                icon={<AuditOutlined />} 
                size="small"
                onClick={() => {/* TODO: 审批 */}}
              />
            </Tooltip>
          )}
        </Space>
      )
    }
  ];

  return (
    <div>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总申购单数" 
              value={statistics.total_requests} 
              prefix={<PlusOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="待审批" 
              value={statistics.pending_approval} 
              prefix={<AuditOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已审批" 
              value={statistics.approved} 
              prefix={<CheckOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总金额" 
              value={statistics.total_amount} 
              prefix={<DollarOutlined />}
              precision={2}
              suffix="元"
            />
          </Card>
        </Col>
      </Row>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Space size="middle">
              <Search
                placeholder="搜索申购单号或备注"
                allowClear
                style={{ width: 300 }}
                onSearch={handleSearch}
              />
              
              <Select
                placeholder="筛选状态"
                allowClear
                style={{ width: 150 }}
                onChange={handleStatusFilter}
              >
                <Option value="all">全部状态</Option>
                <Option value="draft">草稿</Option>
                <Option value="submitted">已提交</Option>
                <Option value="price_quoted">已询价</Option>
                <Option value="dept_approved">部门审批</Option>
                <Option value="final_approved">最终审批</Option>
                <Option value="completed">已完成</Option>
                <Option value="rejected">已拒绝</Option>
              </Select>
            </Space>
          </Col>
          
          <Col>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => onCreateRequest?.()}
            >
              新建申购单
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 申购单列表 */}
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
    </div>
  );
};

export default PurchaseRequestList;