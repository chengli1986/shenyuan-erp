import React from 'react';
import { Space, Tag, Tooltip, Button, Popconfirm } from 'antd';
import { EyeOutlined, DownloadOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  ProjectFile,
  FileType,
  FILE_TYPE_DISPLAY,
  formatFileSize,
  getFileIcon,
  canPreviewFile
} from '../types/projectFile';

interface FileManagerColumnHandlers {
  onPreview: (file: ProjectFile) => void;
  onDownload: (file: ProjectFile) => void;
  onDelete: (file: ProjectFile) => void;
}

export const getFileManagerColumns = (handlers: FileManagerColumnHandlers): ColumnsType<ProjectFile> => [
  {
    title: '文件名',
    dataIndex: 'file_name',
    key: 'file_name',
    render: (text, record) => (
      <Space>
        <span style={{ fontSize: '16px' }}>{getFileIcon(record.file_extension)}</span>
        <span>{text}</span>
      </Space>
    ),
  },
  {
    title: '文件类型',
    dataIndex: 'file_type',
    key: 'file_type',
    width: 120,
    render: (type: FileType) => {
      const config = FILE_TYPE_DISPLAY[type];
      return (
        <Tag color={config.color}>
          {config.icon} {config.name}
        </Tag>
      );
    },
  },
  {
    title: '文件大小',
    dataIndex: 'file_size',
    key: 'file_size',
    width: 100,
    render: (size: number) => formatFileSize(size),
  },
  {
    title: '上传人',
    dataIndex: 'uploaded_by',
    key: 'uploaded_by',
    width: 100,
  },
  {
    title: '上传时间',
    dataIndex: 'upload_time',
    key: 'upload_time',
    width: 150,
    render: (time: string) => new Date(time).toLocaleString('zh-CN'),
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    ellipsis: true,
    render: (text) => text || '-',
  },
  {
    title: '操作',
    key: 'action',
    width: 180,
    render: (_, record) => (
      <Space size="small">
        {canPreviewFile(record.file_extension) && (
          <Tooltip title="预览文件">
            <Button type="link" icon={<EyeOutlined />} size="small" onClick={() => handlers.onPreview(record)} />
          </Tooltip>
        )}
        <Tooltip title="下载文件">
          <Button type="link" icon={<DownloadOutlined />} size="small" onClick={() => handlers.onDownload(record)} />
        </Tooltip>
        <Tooltip title="删除文件">
          <Popconfirm
            title="确定要删除这个文件吗？"
            onConfirm={() => handlers.onDelete(record)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        </Tooltip>
      </Space>
    ),
  },
];
