import React from 'react';
import { Table, Select, Input, InputNumber, Button, Tooltip } from 'antd';
import { DeleteOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { ItemType } from '../../types/purchase';

const { Option } = Select;

interface SystemCategory {
  id: number;
  category_name: string;
  category_code?: string;
  description?: string;
  is_suggested?: boolean;
  items_count?: number;
}

interface EnhancedPurchaseItem {
  id: string;
  item_type: ItemType;
  contract_item_id?: number;
  system_category_id?: number;
  item_name: string;
  specification: string;
  brand_model: string;
  unit: string;
  quantity: number;
  max_quantity?: number;
  remaining_quantity?: number;
  unit_price?: number;
  remarks?: string;
  availableSpecifications?: {
    contract_item_id: number;
    specification: string;
    brand_model: string;
    unit: string;
    total_quantity: number;
    purchased_quantity: number;
    remaining_quantity: number;
    unit_price?: number;
  }[];
  availableSystemCategories?: SystemCategory[];
  systemCategoryMessage?: string;
  autoSelectedSystem?: SystemCategory;
}

interface EnhancedPurchaseFormItemsProps {
  items: EnhancedPurchaseItem[];
  materialNames: string[];
  selectedProjectId: number | null;
  onItemTypeChange: (itemId: string, type: ItemType) => void;
  onMaterialNameChange: (itemId: string, name: string) => void;
  onSpecificationChange: (itemId: string, contractItemId: number) => void;
  onSystemCategoryChange: (itemId: string, categoryId: number) => void;
  onAuxiliarySystemCategory: (itemId: string) => void;
  onQuantityChange: (itemId: string, quantity: number) => void;
  onUpdateItem: (itemId: string, field: string, value: string | number | boolean | undefined | null) => void;
  onRemoveItem: (itemId: string) => void;
}

const EnhancedPurchaseFormItems: React.FC<EnhancedPurchaseFormItemsProps> = ({
  items,
  materialNames,
  selectedProjectId,
  onItemTypeChange,
  onMaterialNameChange,
  onSpecificationChange,
  onSystemCategoryChange,
  onAuxiliarySystemCategory,
  onQuantityChange,
  onUpdateItem,
  onRemoveItem,
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
      render: (_: unknown, record: EnhancedPurchaseItem) => (
        <Select
          value={record.item_type}
          style={{ width: '100%' }}
          onChange={(value: ItemType) => onItemTypeChange(record.id, value)}
        >
          <Option value={ItemType.MAIN_MATERIAL}>主材</Option>
          <Option value={ItemType.AUXILIARY_MATERIAL}>辅材</Option>
        </Select>
      )
    },
    {
      title: (
        <span>
          物料名称
          <Tooltip title="主材必须从合同清单中选择，辅材可以自由输入">
            <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
          </Tooltip>
        </span>
      ),
      dataIndex: 'item_name',
      width: 200,
      render: (_: unknown, record: EnhancedPurchaseItem) => {
        if (record.item_type === ItemType.MAIN_MATERIAL) {
          return (
            <Select
              value={record.item_name || undefined}
              placeholder="请选择物料名称"
              style={{ width: '100%' }}
              showSearch
              filterOption={(input, option) =>
                (option?.label as string)?.toLowerCase().includes(input.toLowerCase()) ||
                (option?.value as string)?.toLowerCase().includes(input.toLowerCase())
              }
              onChange={(value: string) => onMaterialNameChange(record.id, value)}
              allowClear
            >
              {materialNames.map(name => (
                <Option key={name} value={name}>{name}</Option>
              ))}
            </Select>
          );
        } else {
          return (
            <Input
              value={record.item_name}
              placeholder="请输入物料名称"
              onChange={(e) => onUpdateItem(record.id, 'item_name', e.target.value)}
            />
          );
        }
      }
    },
    {
      title: (
        <span>
          规格型号
          <Tooltip title="主材会根据物料名称自动显示可选规格">
            <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
          </Tooltip>
        </span>
      ),
      dataIndex: 'specification',
      width: 200,
      render: (_: unknown, record: EnhancedPurchaseItem) => {
        if (record.item_type === ItemType.MAIN_MATERIAL && record.availableSpecifications) {
          return (
            <Select
              value={record.contract_item_id}
              placeholder="请选择规格型号"
              style={{ width: '100%' }}
              onChange={(value: number) => onSpecificationChange(record.id, value)}
              allowClear
            >
              {record.availableSpecifications.map(spec => (
                <Option key={spec.contract_item_id} value={spec.contract_item_id}>
                  <div>
                    <div>{spec.specification}</div>
                    <div style={{ fontSize: '12px', color: '#999' }}>
                      剩余: {spec.remaining_quantity}/{spec.total_quantity} {spec.unit}
                    </div>
                  </div>
                </Option>
              ))}
            </Select>
          );
        } else {
          return (
            <Input
              value={record.specification}
              placeholder="规格型号"
              disabled={record.item_type === ItemType.MAIN_MATERIAL}
              onChange={(e) => onUpdateItem(record.id, 'specification', e.target.value)}
            />
          );
        }
      }
    },
    {
      title: '品牌型号',
      dataIndex: 'brand_model',
      width: 150,
      render: (_: unknown, record: EnhancedPurchaseItem) => (
        <Input
          value={record.brand_model}
          placeholder="品牌型号"
          disabled={record.item_type === ItemType.MAIN_MATERIAL && !!record.contract_item_id}
          onChange={(e) => onUpdateItem(record.id, 'brand_model', e.target.value)}
        />
      )
    },
    {
      title: (
        <span>
          所属系统
          <Tooltip title="主材会根据合同清单自动选择系统，辅材可手动选择">
            <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
          </Tooltip>
        </span>
      ),
      dataIndex: 'system_category_id',
      width: 150,
      render: (_: unknown, record: EnhancedPurchaseItem) => {
        if (record.autoSelectedSystem) {
          return (
            <div>
              <div style={{ color: '#52c41a', fontSize: '12px' }}>
                已自动选择
              </div>
              <div>{record.autoSelectedSystem.category_name}</div>
            </div>
          );
        } else if (record.availableSystemCategories && record.availableSystemCategories.length > 0) {
          return (
            <div>
              {record.systemCategoryMessage && (
                <div style={{ fontSize: '12px', color: '#666', marginBottom: 4 }}>
                  {record.systemCategoryMessage}
                </div>
              )}
              <Select
                value={record.system_category_id}
                placeholder="选择系统"
                style={{ width: '100%' }}
                onChange={(value: number) => onSystemCategoryChange(record.id, value)}
                allowClear
              >
                {record.availableSystemCategories.map(cat => (
                  <Option key={cat.id} value={cat.id}>
                    <div>
                      <div>{cat.category_name}</div>
                      {cat.is_suggested && (
                        <div style={{ fontSize: '10px', color: '#1890ff' }}>
                          建议选择 ({cat.items_count}个物料)
                        </div>
                      )}
                    </div>
                  </Option>
                ))}
              </Select>
            </div>
          );
        } else if (record.item_type === ItemType.AUXILIARY_MATERIAL && record.item_name) {
          return (
            <Button
              size="small"
              onClick={() => onAuxiliarySystemCategory(record.id)}
              style={{ width: '100%' }}
            >
              选择系统
            </Button>
          );
        } else {
          return <span style={{ color: '#ccc' }}>-</span>;
        }
      }
    },
    {
      title: '单位',
      dataIndex: 'unit',
      width: 80,
      render: (_: unknown, record: EnhancedPurchaseItem) => (
        <Input
          value={record.unit}
          placeholder="单位"
          disabled={record.item_type === ItemType.MAIN_MATERIAL && !!record.contract_item_id}
          onChange={(e) => onUpdateItem(record.id, 'unit', e.target.value)}
        />
      )
    },
    {
      title: (
        <span>
          数量
          <Tooltip title="主材数量不能超过合同清单剩余数量">
            <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
          </Tooltip>
        </span>
      ),
      dataIndex: 'quantity',
      width: 120,
      render: (_: unknown, record: EnhancedPurchaseItem) => (
        <div>
          <InputNumber
            value={record.quantity}
            min={1}
            max={record.remaining_quantity}
            precision={2}
            style={{ width: '100%' }}
            onChange={(value) => onQuantityChange(record.id, value || 1)}
          />
          {record.remaining_quantity !== undefined && (
            <div style={{ fontSize: '10px', color: '#999' }}>
              最多: {record.remaining_quantity}
            </div>
          )}
        </div>
      )
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      width: 150,
      render: (_: unknown, record: EnhancedPurchaseItem) => (
        <Input
          value={record.remarks}
          placeholder="备注"
          onChange={(e) => onUpdateItem(record.id, 'remarks', e.target.value)}
        />
      )
    },
    {
      title: '操作',
      width: 60,
      render: (_: unknown, record: EnhancedPurchaseItem) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => onRemoveItem(record.id)}
        />
      )
    }
  ];

  return (
    <Table
      columns={columns}
      dataSource={items}
      rowKey="id"
      pagination={false}
      scroll={{ x: 1200 }}
      locale={{
        emptyText: selectedProjectId
          ? '请点击"添加明细"按钮添加申购物料'
          : '请先选择项目，然后添加申购明细'
      }}
      size="small"
    />
  );
};

export default EnhancedPurchaseFormItems;
