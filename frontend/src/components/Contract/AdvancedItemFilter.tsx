// frontend/src/components/Contract/AdvancedItemFilter.tsx
/**
 * 高级设备筛选组件
 * 提供更强大的搜索、筛选和排序功能
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Space,
  Input,
  Select,
  Button,
  InputNumber,
  DatePicker,
  Checkbox,
  Tag,
  Row,
  Col,
  Collapse,
  Typography,
  Tooltip,
  Badge
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  ClearOutlined,
  ReloadOutlined,
  DownOutlined,
  UpOutlined
} from '@ant-design/icons';

import { SystemCategory, ItemType } from '../../types/contract';

const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { Panel } = Collapse;
const { Text } = Typography;

export interface FilterValues {
  search: string;
  category_id?: number;
  item_type?: string;
  price_range?: [number, number];
  quantity_range?: [number, number];
  has_specification?: boolean;
  is_key_equipment?: boolean;
  is_optimized?: boolean;
  sort_field?: string;
  sort_order?: 'asc' | 'desc';
}

interface AdvancedItemFilterProps {
  categories: SystemCategory[];
  onFilterChange: (filters: FilterValues) => void;
  onReset: () => void;
  loading?: boolean;
}

const AdvancedItemFilter: React.FC<AdvancedItemFilterProps> = ({
  categories,
  onFilterChange,
  onReset,
  loading = false
}) => {
  const [expanded, setExpanded] = useState(false);
  const [filters, setFilters] = useState<FilterValues>({
    search: '',
    sort_field: 'total_price',
    sort_order: 'desc'
  });
  const [activeFilters, setActiveFilters] = useState<string[]>([]);

  // 更新筛选条件
  const updateFilter = (key: keyof FilterValues, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
    
    // 更新活跃筛选器列表
    updateActiveFilters(newFilters);
  };

  // 更新活跃筛选器列表
  const updateActiveFilters = (currentFilters: FilterValues) => {
    const active: string[] = [];
    
    if (currentFilters.search) active.push('关键词搜索');
    if (currentFilters.category_id) active.push('系统分类');
    if (currentFilters.item_type) active.push('物料类型');
    if (currentFilters.price_range) active.push('价格范围');
    if (currentFilters.quantity_range) active.push('数量范围');
    if (currentFilters.has_specification) active.push('有规格说明');
    if (currentFilters.is_key_equipment) active.push('关键设备');
    if (currentFilters.is_optimized) active.push('优化项目');
    
    setActiveFilters(active);
  };

  // 重置筛选条件
  const handleReset = () => {
    const resetFilters: FilterValues = {
      search: '',
      sort_field: 'total_price',
      sort_order: 'desc'
    };
    setFilters(resetFilters);
    setActiveFilters([]);
    onReset();
  };

  // 快速筛选按钮
  const quickFilters = [
    {
      label: '高价值设备',
      action: () => updateFilter('price_range', [10000, Number.MAX_SAFE_INTEGER])
    },
    {
      label: '关键设备',
      action: () => updateFilter('is_key_equipment', true)
    },
    {
      label: '优化项目',
      action: () => updateFilter('is_optimized', true)
    },
    {
      label: '主要材料',
      action: () => updateFilter('item_type', ItemType.PRIMARY)
    }
  ];

  // 排序选项
  const sortOptions = [
    { label: '总价从高到低', value: 'total_price:desc' },
    { label: '总价从低到高', value: 'total_price:asc' },
    { label: '数量从多到少', value: 'quantity:desc' },
    { label: '数量从少到多', value: 'quantity:asc' },
    { label: '单价从高到低', value: 'unit_price:desc' },
    { label: '单价从低到高', value: 'unit_price:asc' },
    { label: '设备名称A-Z', value: 'item_name:asc' },
    { label: '设备名称Z-A', value: 'item_name:desc' }
  ];

  const handleSortChange = (value: string) => {
    const [field, order] = value.split(':');
    updateFilter('sort_field', field);
    updateFilter('sort_order', order);
  };

  const getSortValue = () => {
    return `${filters.sort_field}:${filters.sort_order}`;
  };

  useEffect(() => {
    updateActiveFilters(filters);
  }, []);

  return (
    <Card>
      {/* 基础筛选行 */}
      <Row gutter={[16, 16]} align="middle">
        <Col xs={24} sm={24} md={8}>
          <Search
            placeholder="搜索设备名称、型号、规格、备注"
            allowClear
            value={filters.search}
            onChange={(e) => updateFilter('search', e.target.value)}
            onSearch={(value) => updateFilter('search', value)}
            enterButton={<SearchOutlined />}
            loading={loading}
          />
        </Col>

        <Col xs={8} sm={6} md={3}>
          <Select
            placeholder="系统分类"
            allowClear
            style={{ width: '100%' }}
            value={filters.category_id}
            onChange={(value) => updateFilter('category_id', value)}
            showSearch
            optionFilterProp="children"
          >
            {categories.map(category => (
              <Option key={category.id} value={category.id}>
                {category.category_name}
              </Option>
            ))}
          </Select>
        </Col>

        <Col xs={8} sm={6} md={3}>
          <Select
            placeholder="物料类型"
            allowClear
            style={{ width: '100%' }}
            value={filters.item_type}
            onChange={(value) => updateFilter('item_type', value)}
          >
            <Option value={ItemType.PRIMARY}>{ItemType.PRIMARY}</Option>
            <Option value={ItemType.AUXILIARY}>{ItemType.AUXILIARY}</Option>
          </Select>
        </Col>

        <Col xs={8} sm={6} md={3}>
          <Select
            placeholder="排序方式"
            style={{ width: '100%' }}
            value={getSortValue()}
            onChange={handleSortChange}
          >
            {sortOptions.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        </Col>

        <Col xs={24} sm={6} md={5}>
          <Space wrap>
            <Button
              icon={expanded ? <UpOutlined /> : <DownOutlined />}
              onClick={() => setExpanded(!expanded)}
              size="small"
            >
              高级筛选
              {activeFilters.length > 0 && (
                <Badge count={activeFilters.length} size="small" />
              )}
            </Button>
            <Button
              icon={<ClearOutlined />}
              onClick={handleReset}
              disabled={activeFilters.length === 0}
              size="small"
            >
              重置
            </Button>
            <Button
              icon={<ReloadOutlined />}
              loading={loading}
              onClick={() => onFilterChange(filters)}
              size="small"
            >
              刷新
            </Button>
          </Space>
        </Col>
      </Row>

      {/* 活跃筛选器标签 */}
      {activeFilters.length > 0 && (
        <Row style={{ marginTop: 12 }}>
          <Col span={24}>
            <Space wrap>
              <Text type="secondary">已应用筛选：</Text>
              {activeFilters.map(filter => (
                <Tag key={filter} color="blue" closable={false}>
                  {filter}
                </Tag>
              ))}
            </Space>
          </Col>
        </Row>
      )}

      {/* 高级筛选面板 */}
      {expanded && (
        <div style={{ marginTop: 16, borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong>价格范围（元）</Text>
                <Space.Compact style={{ width: '100%' }}>
                  <InputNumber
                    placeholder="最低价"
                    min={0}
                    style={{ width: '50%' }}
                    value={filters.price_range?.[0]}
                    onChange={(value) => {
                      const range = filters.price_range || [0, 0];
                      updateFilter('price_range', [value || 0, range[1]]);
                    }}
                  />
                  <InputNumber
                    placeholder="最高价"
                    min={0}
                    style={{ width: '50%' }}
                    value={filters.price_range?.[1]}
                    onChange={(value) => {
                      const range = filters.price_range || [0, 0];
                      updateFilter('price_range', [range[0], value || Number.MAX_SAFE_INTEGER]);
                    }}
                  />
                </Space.Compact>
              </Space>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong>数量范围</Text>
                <Space.Compact style={{ width: '100%' }}>
                  <InputNumber
                    placeholder="最少数量"
                    min={0}
                    style={{ width: '50%' }}
                    value={filters.quantity_range?.[0]}
                    onChange={(value) => {
                      const range = filters.quantity_range || [0, 0];
                      updateFilter('quantity_range', [value || 0, range[1]]);
                    }}
                  />
                  <InputNumber
                    placeholder="最多数量"
                    min={0}
                    style={{ width: '50%' }}
                    value={filters.quantity_range?.[1]}
                    onChange={(value) => {
                      const range = filters.quantity_range || [0, 0];
                      updateFilter('quantity_range', [range[0], value || Number.MAX_SAFE_INTEGER]);
                    }}
                  />
                </Space.Compact>
              </Space>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Space direction="vertical">
                <Text strong>设备特性</Text>
                <Space direction="vertical">
                  <Checkbox
                    checked={filters.has_specification}
                    onChange={(e) => updateFilter('has_specification', e.target.checked)}
                  >
                    有规格说明
                  </Checkbox>
                  <Checkbox
                    checked={filters.is_key_equipment}
                    onChange={(e) => updateFilter('is_key_equipment', e.target.checked)}
                  >
                    关键设备
                  </Checkbox>
                  <Checkbox
                    checked={filters.is_optimized}
                    onChange={(e) => updateFilter('is_optimized', e.target.checked)}
                  >
                    优化项目
                  </Checkbox>
                </Space>
              </Space>
            </Col>
          </Row>

          {/* 快速筛选按钮 */}
          <Row style={{ marginTop: 16 }}>
            <Col span={24}>
              <Space>
                <Text strong>快速筛选：</Text>
                {quickFilters.map(filter => (
                  <Button
                    key={filter.label}
                    size="small"
                    onClick={filter.action}
                  >
                    {filter.label}
                  </Button>
                ))}
              </Space>
            </Col>
          </Row>
        </div>
      )}
    </Card>
  );
};

export default AdvancedItemFilter;