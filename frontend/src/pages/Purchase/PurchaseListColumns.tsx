/**
 * 申购单列表 — 表格列定义与工作流统计卡片
 */

import React from 'react';
import { Button, Space, Popconfirm, Card } from 'antd';
import { EyeOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';
import WorkflowStatus, { PurchaseStatus, WorkflowStep } from '../../components/Purchase/WorkflowStatus';

// 申购单类型定义（支持工作流）
export interface SimplePurchaseRequest {
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
  items?: Record<string, unknown>[];
}

interface ColumnActions {
  onView: (record: SimplePurchaseRequest) => void;
  onEdit: (record: SimplePurchaseRequest) => void;
  onDelete: (id: number, requestCode: string) => void;
  detailLoading: boolean;
  editLoading: boolean;
  deleteLoading: boolean;
}

export function getPurchaseListColumns(actions: ColumnActions): ColumnsType<SimplePurchaseRequest> {
  return [
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
            onClick={() => actions.onView(record)}
            loading={actions.detailLoading}
          >
            查看
          </Button>
          {record.status === 'draft' && (
            <Button
              type="text"
              icon={<EditOutlined />}
              size="small"
              onClick={() => actions.onEdit(record)}
              loading={actions.editLoading}
            >
              编辑
            </Button>
          )}
          {record.status === 'draft' && (
            <Popconfirm
              title="删除确认"
              description={`确定要删除申购单 ${record.request_code} 吗？`}
              onConfirm={() => actions.onDelete(record.id, record.request_code)}
              okText="确认删除"
              cancelText="取消"
              okType="danger"
            >
              <Button
                type="text"
                icon={<DeleteOutlined />}
                size="small"
                danger
                loading={actions.deleteLoading}
              >
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];
}

// 工作流统计卡片
interface WorkflowStatsProps {
  data: SimplePurchaseRequest[];
}

export const WorkflowStatsCard: React.FC<WorkflowStatsProps> = ({ data }) => (
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
);
