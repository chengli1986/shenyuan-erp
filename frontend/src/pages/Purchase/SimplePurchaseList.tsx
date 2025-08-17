import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Button,
  Card,
  message,
  Tag,
  Space,
  Modal,
  Popconfirm
} from 'antd';
import { PlusOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';
import { useNavigate, useLocation } from 'react-router-dom';
import SimplePurchaseDetail from './SimplePurchaseDetail';
import WorkflowStatus, { PurchaseStatus, WorkflowStep } from '../../components/Purchase/WorkflowStatus';
import api from '../../services/api';

// 申购单类型定义（支持工作流）
interface SimplePurchaseRequest {
  id: number;
  request_code: string;
  project_id: number;
  project_name?: string;
  request_date: string;
  status: PurchaseStatus;
  current_step?: WorkflowStep;
  current_approver_id?: number;
  system_category?: string;
  total_amount?: number;
  remarks?: string;
  items?: any[];
}

const SimplePurchaseList: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SimplePurchaseRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [detailVisible, setDetailVisible] = useState(false);
  const [currentDetail, setCurrentDetail] = useState<SimplePurchaseRequest | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // 加载申购单列表 - 支持分页
  const loadPurchaseRequests = useCallback(async (page = currentPage, size = pageSize, showMessage = false) => {
    setLoading(true);
    try {
      const response = await api.get(`purchases/`, {
        params: { page, size }
      });
      
      const result = response.data;
      setData(result.items || []);
      setTotal(result.total || 0);
      setCurrentPage(page);
      if (showMessage) {
        message.success(`加载成功，共${result.total || 0}条申购单，当前第${page}页`);
      }
      console.log('申购单数据已更新:', result.total || 0, '条记录，当前页:', result.items?.length || 0, '条');
    } catch (error) {
      console.error('加载申购单失败:', error);
      message.error('网络连接失败');
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize]);

  // 页面加载时获取数据
  useEffect(() => {
    loadPurchaseRequests();
  }, [loadPurchaseRequests]);

  // 监听 URL 参数变化，重新加载数据
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    if (searchParams.get('refresh')) {
      loadPurchaseRequests(currentPage, pageSize);
      // 清理 URL 参数
      navigate('/purchases', { replace: true });
    }
  }, [location.search, navigate, currentPage, pageSize, loadPurchaseRequests]);

  // 页面获得焦点时刷新数据
  useEffect(() => {
    const handleFocus = () => {
      loadPurchaseRequests(currentPage, pageSize);
    };

    window.addEventListener('focus', handleFocus);
    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, [currentPage, pageSize, loadPurchaseRequests]);

  // 查看申购单详情
  const viewPurchaseDetail = async (record: SimplePurchaseRequest) => {
    setDetailLoading(true);
    try {
      const response = await api.get(`purchases/${record.id}`);
      const detail = response.data;
      console.log('✅ 申购单详情加载成功:', detail);
      setCurrentDetail(detail);
      setDetailVisible(true);
    } catch (error) {
      console.error('加载申购单详情失败:', error);
      message.error('网络连接失败');
    } finally {
      setDetailLoading(false);
    }
  };

  // 删除单个申购单
  const deletePurchaseRequest = async (id: number, requestCode: string) => {
    setDeleteLoading(true);
    try {
      await api.delete(`purchases/${id}`);
      message.success(`申购单 ${requestCode} 删除成功`);
      loadPurchaseRequests(currentPage, pageSize);
      // 清除选中状态
      if (selectedRowKeys.includes(id)) {
        setSelectedRowKeys(selectedRowKeys.filter(key => key !== id));
      }
    } catch (error) {
      console.error('删除申购单失败:', error);
      message.error('网络连接失败');
    } finally {
      setDeleteLoading(false);
    }
  };

  // 批量删除申购单
  const batchDeletePurchaseRequests = async () => {
    // 关闭详情弹窗，避免状态冲突
    setDetailVisible(false);
    setCurrentDetail(null);

    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的申购单');
      return;
    }

    const draftRequests = data.filter(item => 
      selectedRowKeys.includes(item.id) && item.status === 'draft'
    );

    if (draftRequests.length === 0) {
      message.warning('只能删除草稿状态的申购单');
      return;
    }

    if (draftRequests.length < selectedRowKeys.length) {
      message.warning(`只能删除草稿状态的申购单，当前选中的 ${selectedRowKeys.length} 个申购单中有 ${draftRequests.length} 个是草稿状态`);
      return;
    }

    const idsToDelete = draftRequests.map(item => item.id);
    
    // 使用原生confirm确认删除（避免Modal.confirm的异步问题）
    const confirmMessage = `确定要删除选中的 ${draftRequests.length} 个草稿申购单吗？\n申购单编号：${draftRequests.map(r => r.request_code).join(', ')}\n\n此操作不可恢复！`;
    
    if (!window.confirm(confirmMessage)) {
      return;
    }

    setDeleteLoading(true);
    
    try {
      const response = await api.post('purchases/batch-delete', idsToDelete);
      message.success(`批量删除成功！删除了 ${response.data.deleted_count} 个申购单`);
      
      // 刷新数据和清除选中状态
      await loadPurchaseRequests(currentPage, pageSize);
      setSelectedRowKeys([]);
      
    } catch (error: any) {
      console.error('批量删除错误:', error);
      if (error.response?.data?.detail) {
        message.error(`批量删除失败: ${error.response.data.detail}`);
      } else {
        message.error('批量删除失败');
      }
    } finally {
      setDeleteLoading(false);
    }
  };

  // 行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys);
    },
    getCheckboxProps: (record: SimplePurchaseRequest) => ({
      disabled: record.status !== 'draft', // 只有草稿状态的申购单可以选择
    }),
  };

  // 简化的表格列定义
  const columns: ColumnsType<SimplePurchaseRequest> = [
    {
      title: '申购单号',
      dataIndex: 'request_code',
      key: 'request_code',
      width: 200
    },
    {
      title: '项目名称',
      dataIndex: 'project_name',
      key: 'project_name',
      width: 200,
      render: (value: string, record: SimplePurchaseRequest) => 
        value || `项目ID: ${record.project_id}`
    },
    {
      title: '申请日期',
      dataIndex: 'request_date',
      key: 'request_date',
      width: 150,
      render: (value: string) => new Date(value).toLocaleDateString('zh-CN')
    },
    {
      title: '工作流状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: PurchaseStatus, record: SimplePurchaseRequest) => (
        <WorkflowStatus 
          status={status} 
          currentStep={record.current_step}
          showSteps={false}
          size="small"
        />
      )
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 100,
      render: (amount: number) => {
        if (!amount) return '-';
        return `¥${amount.toLocaleString()}`;
      }
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      ellipsis: true,
      render: (value: string) => value || '-'
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button 
            type="text" 
            icon={<EyeOutlined />} 
            size="small"
            onClick={() => viewPurchaseDetail(record)}
            loading={detailLoading}
          >
            查看
          </Button>
          {record.status === 'draft' && (
            <Popconfirm
              title="删除确认"
              description={`确定要删除申购单 ${record.request_code} 吗？`}
              onConfirm={() => deletePurchaseRequest(record.id, record.request_code)}
              okText="确认删除"
              cancelText="取消"
              okType="danger"
            >
              <Button 
                type="text" 
                icon={<DeleteOutlined />} 
                size="small"
                danger
                loading={deleteLoading}
              >
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* 简单的标题和操作栏 */}
      <Card 
        title={
          <Space>
            <span>申购单管理 - 基础版本</span>
            {selectedRowKeys.length > 0 && (
              <span style={{ color: '#1890ff', fontSize: '14px' }}>
                已选择 {selectedRowKeys.length} 项
              </span>
            )}
          </Space>
        }
        extra={
          <Space>
            {selectedRowKeys.length > 0 && (
              <Button 
                danger
                icon={<DeleteOutlined />}
                onClick={batchDeletePurchaseRequests}
                loading={deleteLoading}
              >
                批量删除 ({selectedRowKeys.length})
              </Button>
            )}
            <Button 
              loading={loading}
              onClick={() => loadPurchaseRequests(currentPage, pageSize, true)}
            >
              刷新数据
            </Button>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => navigate('/purchases/create')}
            >
              新建申购单
            </Button>
          </Space>
        }
      >
        {/* 简单的申购单列表 */}
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1000 }}
          rowSelection={rowSelection}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条申购单`,
            showSizeChanger: true,
            showQuickJumper: true,
            onChange: (page, size) => {
              if (size !== pageSize) {
                setPageSize(size);
                loadPurchaseRequests(1, size);
              } else {
                loadPurchaseRequests(page, size);
              }
            },
            onShowSizeChange: (current, size) => {
              setPageSize(size);
              loadPurchaseRequests(1, size);
            }
          }}
          locale={{ 
            emptyText: '暂无申购单数据，请点击"新建申购单"创建' 
          }}
        />
      </Card>

      {/* 调试信息 */}
      {/* 工作流状态统计卡片 */}
      <Card 
        title="工作流统计" 
        style={{ marginTop: '16px' }}
        size="small"
      >
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          {[
            { status: 'draft', label: '草稿', color: '#faad14' },
            { status: 'submitted', label: '已提交', color: '#1890ff' },
            { status: 'price_quoted', label: '已询价', color: '#fa8c16' },
            { status: 'dept_approved', label: '部门已批', color: '#13c2c2' },
            { status: 'final_approved', label: '最终批准', color: '#52c41a' }
          ].map(({ status, label, color }) => {
            const count = data.filter(item => item.status === status).length;
            return (
              <div key={status} style={{ textAlign: 'center', minWidth: '80px' }}>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color }}>{count}</div>
                <div style={{ fontSize: '12px', color: '#666' }}>{label}</div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* 调试信息 */}
      <Card 
        title="调试信息" 
        style={{ marginTop: '16px' }}
        size="small"
      >
        <div style={{ fontSize: '12px', color: '#666' }}>
          <p>当前页数据：{data.length} 条</p>
          <p>总数据量：{total} 条</p>
          <p>当前页码：第 {currentPage} 页</p>
          <p>每页大小：{pageSize} 条</p>
          <p>API地址：/api/v1/purchases/?page={currentPage}&size={pageSize}</p>
          <p>加载状态：{loading ? '加载中...' : '已完成'}</p>
        </div>
      </Card>

      {/* 申购单详情对话框 */}
      <SimplePurchaseDetail
        visible={detailVisible}
        purchaseData={currentDetail}
        onClose={() => {
          setDetailVisible(false);
          setCurrentDetail(null);
        }}
        onRefresh={() => {
          loadPurchaseRequests(currentPage, pageSize);
        }}
      />
    </div>
  );
};

export default SimplePurchaseList;