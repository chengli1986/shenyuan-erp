/**
 * 项目列表 — 表格列定义与格式化工具
 */

import React from 'react';
import { Button, Space, Popconfirm, Tag, Progress } from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { Project, ProjectStatus, PROJECT_STATUS_CONFIG } from '../../types/project';

// 格式化金额显示
export const formatAmount = (amount?: number) => {
  if (!amount) return '-';
  return `¥${amount.toLocaleString()}`;
};

// 格式化日期显示
export const formatDate = (dateString?: string) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('zh-CN');
};

interface ColumnActions {
  onContractManagement: (record: Project) => void;
  onFileManager: (record: Project) => void;
  onEdit: (record: Project) => void;
  onDelete: (id: number, name: string) => void;
}

export function getProjectListColumns(actions: ColumnActions): ColumnsType<Project> {
  return [
    {
      title: '项目编号',
      dataIndex: 'project_code',
      key: 'project_code',
      width: 120,
      fixed: 'left',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: '项目名称',
      dataIndex: 'project_name',
      key: 'project_name',
      width: 200,
      ellipsis: true,
    },
    {
      title: '合同金额',
      dataIndex: 'contract_amount',
      key: 'contract_amount',
      width: 120,
      render: formatAmount,
      sorter: (a, b) => (a.contract_amount || 0) - (b.contract_amount || 0),
    },
    {
      title: '项目经理',
      dataIndex: 'project_manager',
      key: 'project_manager',
      width: 100,
      render: (text) => text || '-'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: ProjectStatus) => {
        const config = PROJECT_STATUS_CONFIG[status];
        return (
          <Tag color={config.color}>
            {config.icon} {config.text}
          </Tag>
        );
      }
    },
    {
      title: '整体进度',
      dataIndex: 'overall_progress',
      key: 'overall_progress',
      width: 120,
      render: (progress: number) => (
        <Progress
          percent={Number(progress) || 0}
          size="small"
          format={(percent) => `${percent}%`}
        />
      )
    },
    {
      title: '开始日期',
      dataIndex: 'start_date',
      key: 'start_date',
      width: 110,
      render: formatDate
    },
    {
      title: '结束日期',
      dataIndex: 'end_date',
      key: 'end_date',
      width: 110,
      render: formatDate
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<FileTextOutlined />}
            size="small"
            onClick={() => actions.onContractManagement(record)}
          >
            合同清单
          </Button>
          <Button
            type="link"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => actions.onFileManager(record)}
          >
            文件
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            size="small"
            onClick={() => actions.onEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个项目吗？"
            description={`项目：${record.project_name}`}
            onConfirm={() => actions.onDelete(record.id, record.project_name)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];
}
