// frontend/src/components/Contract/ContractVersionList.tsx
/**
 * 合同清单版本管理组件
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Card,
  Space,
  Button,
  Tag,
  Typography,
  message,
  Popconfirm,
  Tooltip,
  Modal
} from 'antd';
import {
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

import {
  ContractFileVersion,
  ContractFileInfo
} from '../../types/contract';
import {
  getContractVersions,
  getContractFiles,
  deleteContractFile
} from '../../services/contract';

const { Text } = Typography;

interface ContractVersionListProps {
  projectId: number;
  refreshKey?: number;
  onRefresh?: () => void;
}

const ContractVersionList: React.FC<ContractVersionListProps> = ({
  projectId,
  refreshKey,
  onRefresh
}) => {
  const [loading, setLoading] = useState(false);
  const [versions, setVersions] = useState<ContractFileVersion[]>([]);
  const [fileList, setFileList] = useState<ContractFileInfo[]>([]);
  const [deleteLoading, setDeleteLoading] = useState<number | null>(null);

  // 加载版本列表
  const loadVersions = useCallback(async () => {
    try {
      setLoading(true);
      const [versionsData, filesData] = await Promise.all([
        getContractVersions(projectId),
        getContractFiles(projectId)
      ]);
      
      setVersions(versionsData);
      setFileList(filesData.files);
    } catch (error) {
      console.error('加载版本列表失败:', error);
      message.error('加载版本列表失败');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  // 删除版本
  const handleDelete = async (versionId: number) => {
    try {
      setDeleteLoading(versionId);
      await deleteContractFile(projectId, versionId);
      message.success('删除成功');
      loadVersions();
      onRefresh?.();
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败：' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setDeleteLoading(null);
    }
  };

  // 查看版本详情
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<ContractFileVersion | null>(null);

  const handleViewDetails = (version: ContractFileVersion) => {
    console.log('查看版本详情:', version);
    setSelectedVersion(version);
    setDetailsVisible(true);
  };

  // 下载文件
  const handleDownload = async (version: ContractFileVersion) => {
    try {
      console.log('开始下载文件:', version);
      
      // 构建下载URL - 使用相对路径避免跨域问题
      const downloadUrl = `/api/v1/contracts/projects/${projectId}/contract-versions/${version.id}/download`;
      
      console.log('下载URL:', downloadUrl);
      
      // 使用fetch下载文件
      const response = await fetch(downloadUrl);
      
      if (!response.ok) {
        throw new Error(`下载失败: ${response.status} ${response.statusText}`);
      }
      
      // 获取文件blob
      const blob = await response.blob();
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = version.original_filename;
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // 释放URL对象
      window.URL.revokeObjectURL(url);
      
      message.success('文件下载成功');
    } catch (error) {
      console.error('下载失败:', error);
      message.error(`文件下载失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  // 表格列定义
  const columns: ColumnsType<ContractFileVersion> = [
    {
      title: '版本号',
      dataIndex: 'version_number',
      key: 'version_number',
      width: 80,
      render: (value, record) => (
        <Space>
          <Text strong>v{value}</Text>
          {record.is_current && (
            <Tag color="green" icon={<CheckCircleOutlined />}>
              当前
            </Tag>
          )}
        </Space>
      )
    },
    {
      title: '文件名',
      dataIndex: 'original_filename',
      key: 'original_filename',
      ellipsis: {
        showTitle: false
      },
      render: (value) => (
        <Tooltip title={value}>
          <Space>
            <FileTextOutlined />
            <Text>{value}</Text>
          </Space>
        </Tooltip>
      )
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (value) => value ? `${(value / 1024).toFixed(1)} KB` : '-'
    },
    {
      title: '上传人员',
      dataIndex: 'upload_user_name',
      key: 'upload_user_name',
      width: 120
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      width: 160,
      render: (value) => new Date(value).toLocaleString()
    },
    {
      title: '上传原因',
      dataIndex: 'upload_reason',
      key: 'upload_reason',
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
      title: '文件状态',
      key: 'file_status',
      width: 80,
      render: (_, record) => {
        const fileInfo = fileList.find(f => f.version_id === record.id);
        return (
          <Tag color={fileInfo?.file_exists ? 'green' : 'red'}>
            {fileInfo?.file_exists ? '存在' : '丢失'}
          </Tag>
        );
      }
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetails(record)}
            />
          </Tooltip>
          
          <Tooltip title="下载文件">
            <Button
              size="small"
              icon={<DownloadOutlined />}
              disabled={!fileList.find(f => f.version_id === record.id)?.file_exists}
              onClick={() => handleDownload(record)}
            />
          </Tooltip>

          {!record.is_current && (
            <Popconfirm
              title="确定要删除这个版本吗？"
              description="删除后将无法恢复，相关的系统分类和设备明细也会被删除。"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Tooltip title="删除版本">
                <Button
                  size="small"
                  icon={<DeleteOutlined />}
                  danger
                  loading={deleteLoading === record.id}
                />
              </Tooltip>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  useEffect(() => {
    loadVersions();
  }, [projectId, refreshKey]);

  return (
    <>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Text strong>版本管理</Text>
            <Text type="secondary">
              管理项目的所有合同清单版本，支持查看、下载和删除操作
            </Text>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={versions}
          rowKey="id"
          loading={loading}
          pagination={false}
          scroll={{ x: 1000 }}
          size="small"
        />

        {versions.length === 0 && !loading && (
          <div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Text type="secondary">暂无版本记录</Text>
          </div>
        )}
      </Card>

      {/* 版本详情Modal */}
      <Modal
        title={selectedVersion ? `版本详情 - v${selectedVersion.version_number}` : '版本详情'}
        open={detailsVisible}
        onCancel={() => setDetailsVisible(false)}
        footer={null}
        width={600}
      >
        {selectedVersion && (
          <div style={{ marginTop: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <strong>文件名:</strong> {selectedVersion.original_filename}
              </div>
              <div>
                <strong>存储文件名:</strong> {selectedVersion.stored_filename}
              </div>
              <div>
                <strong>文件大小:</strong> {selectedVersion.file_size ? `${(selectedVersion.file_size / 1024).toFixed(1)} KB` : '未知'}
              </div>
              <div>
                <strong>上传人员:</strong> {selectedVersion.upload_user_name}
              </div>
              <div>
                <strong>上传时间:</strong> {new Date(selectedVersion.upload_time).toLocaleString()}
              </div>
              <div>
                <strong>上传原因:</strong> {selectedVersion.upload_reason || '-'}
              </div>
              <div>
                <strong>变更说明:</strong> {selectedVersion.change_description || '-'}
              </div>
              <div>
                <strong>是否优化版本:</strong> 
                <Tag color={selectedVersion.is_optimized ? 'green' : 'default'} style={{ marginLeft: 8 }}>
                  {selectedVersion.is_optimized ? '是' : '否'}
                </Tag>
              </div>
              <div>
                <strong>当前版本:</strong> 
                <Tag color={selectedVersion.is_current ? 'green' : 'default'} style={{ marginLeft: 8 }}>
                  {selectedVersion.is_current ? '是' : '否'}
                </Tag>
              </div>
              <div style={{ marginTop: 16, padding: 12, backgroundColor: '#f5f5f5', borderRadius: 4 }}>
                <span style={{ fontSize: '12px', color: '#666' }}>
                  注意：Excel文件无法在浏览器中直接预览，请点击下载按钮下载文件后使用Excel软件打开查看。
                </span>
              </div>
            </Space>
          </div>
        )}
      </Modal>
    </>
  );
};

export default ContractVersionList;