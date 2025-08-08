import React, { useState } from 'react';
import {
  Modal,
  Descriptions,
  Table,
  Tag,
  Space,
  message
} from 'antd';
import { formatPurchaseStatus, formatItemType } from '../../services/purchase';

interface SimplePurchaseDetailProps {
  visible: boolean;
  purchaseData: any;
  onClose: () => void;
}

const SimplePurchaseDetail: React.FC<SimplePurchaseDetailProps> = ({
  visible,
  purchaseData,
  onClose
}) => {
  if (!purchaseData) return null;

  const columns = [
    {
      title: '序号',
      width: 60,
      render: (_: any, __: any, index: number) => index + 1
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
      title: '已收数量',
      dataIndex: 'received_quantity',
      width: 100,
      render: (value: string) => parseFloat(value || '0').toFixed(2)
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      width: 150,
      render: (value: string) => value || '-'
    }
  ];

  return (
    <Modal
      title={`申购单详情 - ${purchaseData.request_code}`}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
    >
      {/* 基本信息 */}
      <Descriptions bordered style={{ marginBottom: 16 }}>
        <Descriptions.Item label="申购单号">
          {purchaseData.request_code}
        </Descriptions.Item>
        <Descriptions.Item label="项目名称">
          {purchaseData.project_name || `项目ID: ${purchaseData.project_id}`}
        </Descriptions.Item>
        <Descriptions.Item label="申请日期">
          {new Date(purchaseData.request_date).toLocaleDateString('zh-CN')}
        </Descriptions.Item>
        <Descriptions.Item label="申请人">
          {purchaseData.requester_name || '系统管理员'}
        </Descriptions.Item>
        <Descriptions.Item label="需求日期">
          {purchaseData.required_date 
            ? new Date(purchaseData.required_date).toLocaleDateString('zh-CN') 
            : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="状态">
          <Tag color={purchaseData.status === 'draft' ? 'orange' : 'blue'}>
            {formatPurchaseStatus(purchaseData.status)}
          </Tag>
        </Descriptions.Item>
        <Descriptions.Item label="申购说明" span={3}>
          {purchaseData.remarks || '-'}
        </Descriptions.Item>
      </Descriptions>

      {/* 申购明细 */}
      <Table
        columns={columns}
        dataSource={purchaseData.items || []}
        rowKey="id"
        pagination={false}
        size="small"
        scroll={{ x: 900 }}
      />
    </Modal>
  );
};

export default SimplePurchaseDetail;