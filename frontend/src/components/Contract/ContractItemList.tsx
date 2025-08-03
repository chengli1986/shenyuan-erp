// frontend/src/components/Contract/ContractItemList.tsx
/**
 * 合同清单明细列表组件
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Card,
  Space,
  Button,
  Input,
  Select,
  Tag,
  Typography,
  Alert,
  message,
  Tooltip,
  Pagination,
  Row,
  Col
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  EyeOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

import {
  ContractItem,
  ContractFileVersion,
  SystemCategory,
  ItemType
} from '../../types/contract';
import {
  getContractItems,
  getSystemCategories,
  formatAmount
} from '../../services/contract';
import ContractItemDetail from './ContractItemDetail';
import ContractItemEdit from './ContractItemEdit';
import AdvancedItemFilter, { FilterValues } from './AdvancedItemFilter';

const { Search } = Input;
const { Option } = Select;
const { Text } = Typography;

interface ContractItemListProps {
  projectId: number;
  currentVersion?: ContractFileVersion;
  refreshKey?: number;
}

const ContractItemList: React.FC<ContractItemListProps> = ({
  projectId,
  currentVersion,
  refreshKey
}) => {
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<ContractItem[]>([]);
  const [categories, setCategories] = useState<SystemCategory[]>([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  });
  
  // 筛选条件
  const [filters, setFilters] = useState<FilterValues>({
    search: '',
    sort_field: 'total_price',
    sort_order: 'desc'
  });
  
  // 详情和编辑模态框状态
  const [detailItem, setDetailItem] = useState<ContractItem | null>(null);
  const [editItem, setEditItem] = useState<ContractItem | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [editVisible, setEditVisible] = useState(false);

  // 加载系统分类
  const loadCategories = useCallback(async () => {
    if (!currentVersion) return;
    
    try {
      const categoriesData = await getSystemCategories(projectId, currentVersion.id);
      setCategories(categoriesData);
    } catch (error) {
      console.error('加载系统分类失败:', error);
    }
  }, [currentVersion, projectId, refreshKey]);

  // 加载设备清单
  const loadItems = useCallback(async (page = 1, size = 20) => {
    console.log('=== loadItems调用 ===');
    console.log('currentVersion:', currentVersion);
    console.log('projectId:', projectId);
    console.log('page:', page, 'size:', size);
    console.log('currentVersion是否存在:', !!currentVersion);
    console.log('currentVersion.id:', currentVersion?.id);
    
    if (!currentVersion) {
      console.log('❌ currentVersion为空，无法加载设备清单');
      setItems([]);
      setPagination(prev => ({ ...prev, total: 0 }));
      return;
    }

    try {
      setLoading(true);
      console.log(`开始加载项目${projectId}版本${currentVersion.id}的设备清单...`);
      const response = await getContractItems(projectId, currentVersion.id, {
        ...filters,
        page,
        size
      });
      
      console.log('设备清单响应:', response);
      setItems(response.items);
      setPagination({
        current: response.page,
        pageSize: response.size,
        total: response.total
      });
    } catch (error) {
      console.error('加载设备清单失败:', error);
      message.error('加载设备清单失败');
    } finally {
      setLoading(false);
    }
  }, [currentVersion, projectId, filters, refreshKey]);

  // 处理筛选条件变更
  const handleFilterChange = (newFilters: FilterValues) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, current: 1 })); // 重置到第一页
    loadItems(1, pagination.pageSize);
  };

  // 重置筛选条件
  const handleFilterReset = () => {
    const resetFilters: FilterValues = {
      search: '',
      sort_field: 'total_price',
      sort_order: 'desc'
    };
    setFilters(resetFilters);
    setPagination(prev => ({ ...prev, current: 1 }));
    loadItems(1, pagination.pageSize);
  };

  // 处理分页变化
  const handlePaginationChange = (page: number, size?: number) => {
    console.log('=== 分页变化 ===');
    console.log('新页码:', page);
    console.log('每页数量:', size || pagination.pageSize);
    setPagination(prev => ({ ...prev, current: page, pageSize: size || prev.pageSize }));
    loadItems(page, size || pagination.pageSize);
  };

  // 刷新数据
  const handleRefresh = () => {
    loadCategories();
    loadItems(pagination.current, pagination.pageSize);
  };

  // 获取分类名称
  const getCategoryName = (categoryId?: number) => {
    if (!categoryId) return '-';
    const category = categories.find(cat => cat.id === categoryId);
    return category?.category_name || '-';
  };

  // 表格列定义
  const columns: ColumnsType<ContractItem> = [
    {
      title: '序号',
      dataIndex: 'serial_number',
      key: 'serial_number',
      width: 80,
      render: (value) => value || '-'
    },
    {
      title: '设备名称',
      dataIndex: 'item_name',
      key: 'item_name',
      width: 200,
      ellipsis: {
        showTitle: false
      },
      render: (value) => (
        <Tooltip title={value}>
          <Text strong>{value}</Text>
        </Tooltip>
      )
    },
    {
      title: '设备型号',
      dataIndex: 'brand_model',
      key: 'brand_model',
      width: 150,
      ellipsis: {
        showTitle: false
      },
      render: (value) => (
        <Tooltip title={value}>
          {value || '-'}
        </Tooltip>
      )
    },
    {
      title: '设备品牌',
      dataIndex: 'specification',
      key: 'specification',
      width: 150,
      ellipsis: {
        showTitle: false
      },
      render: (value) => (
        <Tooltip title={value}>
          {value || '待补充'}
        </Tooltip>
      )
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 60,
      render: (value) => value || '台'
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
      align: 'right',
      render: (value) => (
        <Text strong>{Number(value).toLocaleString()}</Text>
      )
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 100,
      align: 'right',
      render: (value) => value ? formatAmount(Number(value)) : '-'
    },
    {
      title: '总价',
      dataIndex: 'total_price',
      key: 'total_price',
      width: 120,
      align: 'right',
      render: (value) => (
        <Text strong type={value ? 'success' : undefined}>
          {value ? formatAmount(Number(value)) : '-'}
        </Text>
      )
    },
    {
      title: '系统分类',
      dataIndex: 'category_id',
      key: 'category_id',
      width: 120,
      render: (value) => (
        <Tag color="blue">{getCategoryName(value)}</Tag>
      )
    },
    {
      title: '物料类型',
      dataIndex: 'item_type',
      key: 'item_type',
      width: 80,
      render: (value) => (
        <Tag color={value === ItemType.PRIMARY ? 'green' : 'orange'}>
          {value || ItemType.PRIMARY}
        </Tag>
      )
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      width: 120,
      ellipsis: {
        showTitle: false
      },
      render: (value) => (
        <Tooltip title={value}>
          {value || '-'}
        </Tooltip>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button 
              size="small" 
              icon={<EyeOutlined />}
              onClick={() => {
                setDetailItem(record);
                setDetailVisible(true);
              }}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              size="small" 
              icon={<EditOutlined />}
              onClick={() => {
                setEditItem(record);
                setEditVisible(true);
              }}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  console.log('=== ContractItemList render ===');
  console.log('currentVersion in render:', currentVersion);
  console.log('items length:', items.length);
  console.log('pagination total:', pagination.total);
  
  if (!currentVersion) {
    console.log('❌ 渲染：currentVersion为空，显示警告');
    return (
      <Alert
        message="暂无合同清单版本"
        description="请先上传投标清单Excel文件"
        type="warning"
        showIcon
      />
    );
  }

  return (
    <div>
      {/* 高级筛选工具栏 */}
      <div style={{ marginBottom: 16 }}>
        <AdvancedItemFilter
          categories={categories}
          onFilterChange={handleFilterChange}
          onReset={handleFilterReset}
          loading={loading}
        />
      </div>

      {/* 数据统计 */}
      <Card style={{ marginBottom: 16 }}>
        <Space size="large">
          <Text>
            当前版本: <Text strong>v{currentVersion.version_number}</Text>
          </Text>
          <Text>
            设备总数: <Text strong>{pagination.total}</Text>
          </Text>
          <Text>
            系统分类: <Text strong>{categories.length}</Text>
          </Text>
        </Space>
      </Card>

      {/* 设备清单表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={items}
          rowKey="id"
          loading={loading}
          pagination={false}
          scroll={{ x: 1200 }}
          size="small"
        />
        
        {/* 分页 */}
        <div style={{ marginTop: 16, textAlign: 'right' }}>
          <Pagination
            current={pagination.current}
            pageSize={pagination.pageSize}
            total={pagination.total}
            showSizeChanger
            showQuickJumper
            showTotal={(total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`
            }
            onChange={handlePaginationChange}
            onShowSizeChange={handlePaginationChange}
          />
        </div>
      </Card>
      
      {/* 详情查看模态框 */}
      <ContractItemDetail
        item={detailItem}
        visible={detailVisible}
        onClose={() => {
          setDetailVisible(false);
          setDetailItem(null);
        }}
      />
      
      {/* 编辑模态框 */}
      <ContractItemEdit
        item={editItem}
        visible={editVisible}
        onClose={() => {
          setEditVisible(false);
          setEditItem(null);
        }}
        onSuccess={() => {
          // 编辑成功后刷新列表
          loadItems(pagination.current, pagination.pageSize);
          message.success('设备信息更新成功');
        }}
      />
    </div>
  );
};

export default ContractItemList;