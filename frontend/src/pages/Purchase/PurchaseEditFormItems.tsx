import React from 'react';
import {
  Table,
  Select,
  Input,
  InputNumber,
  Popconfirm,
  Button,
} from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import type { PurchaseEditItem } from './hooks/usePurchaseEditForm';

export interface PurchaseEditFormItemsProps {
  items: PurchaseEditItem[];
  materialNames: string[];
  isProjectManager: boolean;
  onMaterialNameChange: (itemId: string, name: string) => void;
  onSpecificationChange: (itemId: string, spec: string) => void;
  onSystemCategoryWithName: (itemId: string, categoryId: number, categoryName: string) => void;
  onQuantityChange: (itemId: string, qty: number) => void;
  onPriceChange: (itemId: string, price: number) => void;
  onItemTypeChange: (itemId: string, type: 'main' | 'auxiliary') => void;
  onRemoveItem: (itemId: string) => void;
  onUpdateItem: (itemId: string, field: keyof PurchaseEditItem, value: string | number | boolean | undefined | null) => void;
}

const PurchaseEditFormItems: React.FC<PurchaseEditFormItemsProps> = ({
  items,
  materialNames,
  isProjectManager,
  onMaterialNameChange,
  onSpecificationChange,
  onSystemCategoryWithName,
  onQuantityChange,
  onPriceChange,
  onItemTypeChange,
  onRemoveItem,
  onUpdateItem,
}) => {
  const columns = [
    {
      title: '序号',
      width: 60,
      render: (_: unknown, __: unknown, index: number) => index + 1
    },
    {
      title: '类型',
      dataIndex: 'item_type',
      width: 100,
      render: (value: 'main' | 'auxiliary', record: PurchaseEditItem) => (
        <Select
          value={value}
          style={{ width: '100%' }}
          onChange={(itemType: 'main' | 'auxiliary') => onItemTypeChange(record.id, itemType)}
        >
          <Select.Option value="main">主材</Select.Option>
          <Select.Option value="auxiliary">辅材</Select.Option>
        </Select>
      )
    },
    {
      title: '物料名称',
      dataIndex: 'item_name',
      width: 180,
      render: (value: string, record: PurchaseEditItem) => {
        if (record.item_type === 'main') {
          return (
            <Select
              value={value}
              onChange={(materialName: string) => onMaterialNameChange(record.id, materialName)}
              placeholder="请选择物料名称"
              style={{ width: '100%' }}
              showSearch
              filterOption={(input, option: { children?: string } | undefined) =>
                (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
              }
              allowClear
            >
              {materialNames.map(name => (
                <Select.Option key={name} value={name}>{name}</Select.Option>
              ))}
            </Select>
          );
        } else {
          return (
            <Input
              value={value}
              placeholder="请输入物料名称"
              onChange={(e) => onUpdateItem(record.id, 'item_name', e.target.value)}
            />
          );
        }
      }
    },
    {
      title: '规格型号',
      dataIndex: 'specification',
      width: 160,
      render: (value: string, record: PurchaseEditItem) => {
        if (record.item_type === 'main' && record.availableSpecifications?.length) {
          return (
            <Select
              value={value}
              placeholder="请选择规格型号"
              style={{ width: '100%' }}
              onChange={(specification: string) => onSpecificationChange(record.id, specification)}
              allowClear
            >
              {record.availableSpecifications.map((spec, index) => (
                <Select.Option key={index} value={spec.specification}>
                  <div>
                    <div>{spec.specification}</div>
                    <div style={{ fontSize: '12px', color: '#999' }}>
                      剩余: {spec.remaining_quantity}/{spec.total_quantity} {spec.unit}
                    </div>
                  </div>
                </Select.Option>
              ))}
            </Select>
          );
        } else {
          return (
            <Input
              value={value || ''}
              placeholder="规格型号"
              disabled={!!(record.item_type === 'main' && record.item_name && !record.availableSpecifications?.length)}
              onChange={(e) => onUpdateItem(record.id, 'specification', e.target.value)}
            />
          );
        }
      }
    },
    {
      title: '品牌',
      dataIndex: 'brand',
      width: 120,
      render: (value: string, record: PurchaseEditItem) => (
        <Input
          value={value || ''}
          onChange={(e) => onUpdateItem(record.id, 'brand', e.target.value)}
          placeholder="品牌"
          disabled={record.item_type === 'main'}
          style={record.item_type === 'main' ? { backgroundColor: '#f5f5f5', color: '#999' } : {}}
        />
      )
    },
    {
      title: '所属系统',
      dataIndex: 'system_category_id',
      width: 140,
      render: (value: number, record: PurchaseEditItem) => {
        if (Array.isArray(record.availableSystemCategories) && record.availableSystemCategories.length > 0) {
          return (
            <Select
              value={value}
              placeholder={record.system_category_name ? record.system_category_name : "选择系统"}
              style={{ width: '100%' }}
              onChange={(categoryId: number) => {
                const selectedCategory = Array.isArray(record.availableSystemCategories)
                  ? record.availableSystemCategories.find(cat => cat.id === categoryId)
                  : null;
                if (selectedCategory) {
                  onSystemCategoryWithName(record.id, categoryId, selectedCategory.category_name);
                }
              }}
              allowClear
              showSearch
              filterOption={(input, option: { children?: string } | undefined) =>
                (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {record.availableSystemCategories.map(cat => (
                <Select.Option key={cat.id} value={cat.id}>
                  {cat.is_suggested ? '⭐ ' : ''}{cat.category_name}
                </Select.Option>
              ))}
            </Select>
          );
        }

        if (record.system_category_name) {
          return (
            <span style={{ color: '#1890ff' }}>
              {record.system_category_name}
            </span>
          );
        }

        return <span style={{ color: '#ccc' }}>-</span>;
      }
    },
    {
      title: '单位',
      dataIndex: 'unit',
      width: 80,
      render: (value: string, record: PurchaseEditItem) => {
        if (record.item_type === 'main') {
          return (
            <Input
              value={value || ''}
              disabled
              style={{ backgroundColor: '#f5f5f5', color: '#999' }}
              placeholder="自动填充"
            />
          );
        } else {
          return (
            <Select
              value={value}
              onChange={(unit: string) => onUpdateItem(record.id, 'unit', unit)}
              style={{ width: '100%' }}
            >
              <Select.Option value="个">个</Select.Option>
              <Select.Option value="台">台</Select.Option>
              <Select.Option value="套">套</Select.Option>
              <Select.Option value="米">米</Select.Option>
              <Select.Option value="公斤">公斤</Select.Option>
              <Select.Option value="箱">箱</Select.Option>
              <Select.Option value="包">包</Select.Option>
            </Select>
          );
        }
      }
    },
    {
      title: '申购数量',
      dataIndex: 'quantity',
      width: 100,
      render: (value: number, record: PurchaseEditItem) => {
        const maxQuantity = record.remaining_quantity;
        const hasLimit = record.item_type === 'main' && maxQuantity !== undefined;

        return (
          <div>
            <InputNumber
              value={value}
              onChange={(quantity) => onQuantityChange(record.id, quantity || 1)}
              min={1}
              max={hasLimit ? maxQuantity : undefined}
              style={{ width: '100%' }}
              placeholder="数量"
            />
            {record.item_type === 'main' && record.contract_item_id && hasLimit && (
              <div style={{ fontSize: '10px', color: '#999', marginTop: '2px' }}>
                上限: {maxQuantity}
              </div>
            )}
            {record.item_type === 'main' && !record.contract_item_id && (
              <div style={{ fontSize: '10px', color: '#ff7875', marginTop: '2px' }}>
                请选择物料和规格关联合同清单
              </div>
            )}
          </div>
        );
      }
    },
    // Price column: hidden from project managers
    ...(isProjectManager ? [] : [{
      title: '单价',
      dataIndex: 'unit_price',
      width: 100,
      render: (value: number, record: PurchaseEditItem) => (
        <InputNumber
          value={value}
          onChange={(price) => onPriceChange(record.id, price || 0)}
          min={0}
          precision={2}
          style={{ width: '100%' }}
          placeholder="单价"
        />
      )
    }]),
    {
      title: '备注',
      dataIndex: 'remarks',
      width: 120,
      render: (value: string, record: PurchaseEditItem) => (
        <Input
          value={value}
          onChange={(e) => onUpdateItem(record.id, 'remarks', e.target.value)}
          placeholder="备注"
        />
      )
    },
    {
      title: '操作',
      width: 80,
      render: (_: unknown, record: PurchaseEditItem) => (
        <Popconfirm
          title="确定删除这一项吗？"
          onConfirm={() => onRemoveItem(record.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button
            type="text"
            icon={<DeleteOutlined />}
            size="small"
            danger
          />
        </Popconfirm>
      )
    }
  ];

  return (
    <Table
      columns={columns}
      dataSource={items}
      rowKey="id"
      pagination={false}
      scroll={{ x: 1000 }}
      size="small"
      bordered
    />
  );
};

export default PurchaseEditFormItems;
