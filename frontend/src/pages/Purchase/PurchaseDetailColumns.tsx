import React from 'react';
import { Tag } from 'antd';
import { formatItemType } from '../../services/purchase';
import { PurchaseDetailData, PurchaseDetailItem } from '../../types/purchase';

interface CurrentUser {
  role: string;
  name: string;
}

export const getPurchaseDetailColumns = (
  currentUser: CurrentUser | null,
  purchaseData: PurchaseDetailData
) => [
  {
    title: '序号',
    width: 60,
    render: (_: unknown, __: unknown, index: number) => index + 1
  },
  {
    title: '类型',
    dataIndex: 'item_type',
    width: 80,
    render: (type: string) => formatItemType(type)
  },
  {
    title: '物料名称',
    dataIndex: 'item_name',
    width: 150
  },
  {
    title: '规格型号',
    dataIndex: 'specification',
    width: 150,
    render: (value: string) => value || '-'
  },
  {
    title: '品牌',
    dataIndex: 'brand',
    width: 100,
    render: (value: string) => value || '-'
  },
  {
    title: '所属系统',
    dataIndex: 'system_category_name',
    width: 120,
    render: (value: string) => value ? (
      <Tag color="blue">{value}</Tag>
    ) : '-'
  },
  {
    title: '单位',
    dataIndex: 'unit',
    width: 60
  },
  {
    title: '申购数量',
    dataIndex: 'quantity',
    width: 100,
    render: (value: string) => parseFloat(value).toFixed(2)
  },
  {
    title: '剩余可申购',
    dataIndex: 'remaining_quantity',
    width: 110,
    render: (value: number | undefined, record: PurchaseDetailItem) => {
      if (record.item_type === 'main' && record.contract_item_id) {
        if (value !== undefined && value !== null) {
          const remaining = typeof value === 'string' ? parseFloat(value) : value;
          return (
            <span style={{ color: remaining <= 0 ? '#ff4d4f' : remaining <= 10 ? '#faad14' : '#52c41a' }}>
              {remaining.toFixed(2)}
            </span>
          );
        }
        return <span style={{ color: '#999' }}>计算中...</span>;
      }
      return '-';
    }
  },
  {
    title: '已收数量',
    dataIndex: 'received_quantity',
    width: 100,
    render: (value: string) => parseFloat(value || '0').toFixed(2)
  },
  // 根据用户权限显示询价和价格信息
  ...(currentUser?.role !== 'project_manager' ? [
    {
      title: '供应商',
      dataIndex: 'supplier_name',
      width: 120,
      render: (value: string) => value || '-'
    },
    {
      title: '供应商联系人',
      dataIndex: 'supplier_contact',
      width: 120,
      render: (value: string) => value || '-'
    },
    {
      title: '付款方式',
      dataIndex: 'payment_method',
      width: 100,
      render: (value: string, record: PurchaseDetailItem) => {
        let paymentMethod = value || record.supplier_info?.payment_method || purchaseData.payment_method;

        const paymentMethods: { [key: string]: string } = {
          'PREPAYMENT': '预付款',
          'ON_DELIVERY': '货到付款',
          'MONTHLY': '月结',
          'INSTALLMENT': '分期付款'
        };
        return (paymentMethod ? paymentMethods[paymentMethod] : undefined) || paymentMethod || '-';
      }
    },
    {
      title: '预计交货',
      dataIndex: 'estimated_delivery_date',
      width: 100,
      render: (value: string, record: PurchaseDetailItem) => {
        const deliveryDate = value || record.estimated_delivery || purchaseData.estimated_delivery_date;
        if (!deliveryDate) return '-';
        return new Date(deliveryDate).toLocaleDateString('zh-CN');
      }
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      width: 100,
      render: (value: string | number) => {
        if (!value || parseFloat(value.toString()) === 0) return '-';
        return `¥${parseFloat(value.toString()).toLocaleString('zh-CN', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })}`;
      }
    },
    {
      title: '总价',
      dataIndex: 'total_price',
      width: 120,
      render: (value: string | number) => {
        if (!value || parseFloat(value.toString()) === 0) return '-';
        return `¥${parseFloat(value.toString()).toLocaleString('zh-CN', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })}`;
      }
    }
  ] : []),
  {
    title: '备注',
    dataIndex: 'remarks',
    width: 150,
    render: (value: string) => value || '-'
  }
];
