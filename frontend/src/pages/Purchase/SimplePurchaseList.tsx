import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Button,
  Card,
  message,
  Tag,
  Space
} from 'antd';
import { PlusOutlined, EyeOutlined } from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';
import { useNavigate, useLocation } from 'react-router-dom';
import SimplePurchaseDetail from './SimplePurchaseDetail';

// 简化的类型定义
interface SimplePurchaseRequest {
  id: number;
  request_code: string;
  project_id: number;
  project_name?: string;
  request_date: string;
  status: string;
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

  // 加载申购单列表 - 支持分页
  const loadPurchaseRequests = useCallback(async (page = currentPage, size = pageSize, showMessage = false) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/purchases/?page=${page}&size=${size}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const result = await response.json();
        setData(result.items || []);
        setTotal(result.total || 0);
        setCurrentPage(page);
        if (showMessage) {
          message.success(`加载成功，共${result.total || 0}条申购单，当前第${page}页`);
        }
        console.log('申购单数据已更新:', result.total || 0, '条记录，当前页:', result.items?.length || 0, '条');
      } else if (response.status === 401) {
        message.error('请重新登录');
        localStorage.removeItem('access_token');
        localStorage.removeItem('currentUser');
        window.location.reload();
      } else {
        message.error('加载申购单失败');
      }
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
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/purchases/${record.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const detail = await response.json();
        console.log('✅ 申购单详情加载成功:', detail);
        setCurrentDetail(detail);
        setDetailVisible(true);
      } else if (response.status === 401) {
        message.error('请重新登录');
        localStorage.removeItem('access_token');
        localStorage.removeItem('currentUser');
        window.location.reload();
      } else {
        const errorText = await response.text();
        console.error('API错误:', response.status, errorText);
        message.error(`加载申购单详情失败: ${response.status}`);
      }
    } catch (error) {
      console.error('加载申购单详情失败:', error);
      message.error('网络连接失败');
    } finally {
      setDetailLoading(false);
    }
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
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'draft' ? 'orange' : 'blue'}>
          {status === 'draft' ? '草稿' : status}
        </Tag>
      )
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
      width: 150,
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
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* 简单的标题和操作栏 */}
      <Card 
        title="申购单管理 - 基础版本" 
        extra={
          <Space>
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
      />
    </div>
  );
};

export default SimplePurchaseList;