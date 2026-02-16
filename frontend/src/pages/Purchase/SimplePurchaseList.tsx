import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Button,
  Card,
  message,
  Space,
} from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import SimplePurchaseDetail from './SimplePurchaseDetail';
import PurchaseEditForm from './PurchaseEditForm';
import { getPurchaseListColumns, WorkflowStatsCard } from './PurchaseListColumns';
import type { SimplePurchaseRequest } from './PurchaseListColumns';
import api from '../../services/api';
import type { PurchaseDetailData } from '../../types/purchase';

const SimplePurchaseList: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SimplePurchaseRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [detailVisible, setDetailVisible] = useState(false);
  const [currentDetail, setCurrentDetail] = useState<PurchaseDetailData | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [editVisible, setEditVisible] = useState(false);
  const [currentEdit, setCurrentEdit] = useState<PurchaseDetailData | null>(null);
  const [editLoading, setEditLoading] = useState(false);

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

    } catch (error: unknown) {
      console.error('批量删除错误:', error);
      message.error(error instanceof Error ? error.message : '批量删除失败');
    } finally {
      setDeleteLoading(false);
    }
  };

  // 编辑申购单
  const editPurchaseRequest = async (record: SimplePurchaseRequest | PurchaseDetailData) => {
    setEditLoading(true);
    try {
      const response = await api.get(`purchases/${record.id}`);
      const detail = response.data;
      setCurrentEdit(detail);
      setEditVisible(true);
    } catch (error: unknown) {
      console.error('获取申购单详情失败:', error);
      message.error(error instanceof Error ? error.message : '获取申购单详情失败');
    } finally {
      setEditLoading(false);
    }
  };

  // 保存编辑
  const handleEditSave = async (editData: Record<string, unknown>) => {
    if (!currentEdit) return;

    try {
      await api.put(`purchases/${currentEdit.id}`, editData);
      await loadPurchaseRequests(currentPage, pageSize);
      setEditVisible(false);
      setCurrentEdit(null);
    } catch (error: unknown) {
      console.error('更新申购单失败:', error);
      throw error; // 让编辑组件处理错误显示
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

  // 表格列定义
  const columns = getPurchaseListColumns({
    onView: viewPurchaseDetail,
    onEdit: editPurchaseRequest,
    onDelete: deletePurchaseRequest,
    detailLoading,
    editLoading,
    deleteLoading,
  });

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

      {/* 工作流状态统计卡片 */}
      <WorkflowStatsCard data={data} />

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
        onEdit={(purchaseData) => {
          // 从详情页跳转到编辑页
          setDetailVisible(false);
          setCurrentDetail(null);
          editPurchaseRequest(purchaseData);
        }}
      />

      {/* 申购单编辑对话框 */}
      <PurchaseEditForm
        visible={editVisible}
        purchaseData={currentEdit}
        onCancel={() => {
          setEditVisible(false);
          setCurrentEdit(null);
        }}
        onSave={handleEditSave}
      />
    </div>
  );
};

export default SimplePurchaseList;
