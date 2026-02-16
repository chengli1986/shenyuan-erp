// frontend/src/components/ProjectFileManager.tsx
/**
 * 项目文件管理组件
 * 包含文件上传、列表显示、下载、删除等功能
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Button,
  Table,
  Space,
  Select,
  message,
  Modal,
  Popconfirm,
  Row,
  Col,
  Statistic,
  Empty,
} from 'antd';
import {
  UploadOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons';

import {
  ProjectFile,
  FileType,
  FILE_TYPE_DISPLAY,
  FileSystemConfig,
  canPreviewFile
} from '../types/projectFile';
import { ProjectFileService } from '../services/projectFile';
import FileUploadModal from './FileUploadModal';
import BatchUploadModal from './BatchUploadModal';
import { getFileManagerColumns } from './FileManagerColumns';

const { Option } = Select;

interface ProjectFileManagerProps {
  projectId: number;
  projectName: string;
  visible: boolean;
  onCancel: () => void;
}

const ProjectFileManager: React.FC<ProjectFileManagerProps> = ({
  projectId,
  projectName,
  visible,
  onCancel
}) => {
  const [files, setFiles] = useState<ProjectFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState<FileType | ''>('');
  const [fileConfig, setFileConfig] = useState<FileSystemConfig | null>(null);

  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [batchUploadVisible, setBatchUploadVisible] = useState(false);

  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewFile, setPreviewFile] = useState<ProjectFile | null>(null);

  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  const defaultFileTypes = [
    { value: 'award_notice', label: '中标通知书', icon: '📋', color: 'blue', max_count: 5, description: '项目中标通知书等相关文件' },
    { value: 'contract', label: '合同文件', icon: '📄', color: 'green', max_count: 10, description: '项目合同、协议等文件' },
    { value: 'attachment', label: '附件', icon: '📎', color: 'orange', max_count: 50, description: '项目相关附件' },
    { value: 'other', label: '其他文件', icon: '📁', color: 'gray', max_count: 20, description: '其他类型文件' }
  ];

  const fetchFiles = useCallback(async () => {
    setLoading(true);
    try {
      const response = await ProjectFileService.getProjectFiles(projectId, filterType || undefined);
      setFiles(response.items);
    } catch (error) {
      message.error('获取文件列表失败');
      console.error('Error fetching files:', error);
    } finally {
      setLoading(false);
    }
  }, [projectId, filterType]);

  const fetchFileConfig = useCallback(async () => {
    try {
      const config = await ProjectFileService.getFileSystemConfig();
      setFileConfig(config);
    } catch {
      setFileConfig({
        file_types: defaultFileTypes,
        allowed_extensions: ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.zip', '.rar'],
        max_file_size: 50 * 1024 * 1024,
        max_file_size_mb: 50
      });
    }
  }, []);

  useEffect(() => {
    if (visible) {
      fetchFiles();
      fetchFileConfig();
    }
  }, [visible, fetchFiles, fetchFileConfig]);

  const handleDownload = async (file: ProjectFile) => {
    try {
      await ProjectFileService.downloadFile(projectId, file.id, file.file_name);
      message.success('文件下载开始');
    } catch {
      message.error('文件下载失败');
    }
  };

  const handleDelete = async (file: ProjectFile) => {
    try {
      await ProjectFileService.deleteFile(projectId, file.id);
      message.success(`文件 "${file.file_name}" 删除成功`);
      fetchFiles();
    } catch {
      message.error('文件删除失败');
    }
  };

  const handlePreview = (file: ProjectFile) => {
    if (canPreviewFile(file.file_extension)) {
      setPreviewFile(file);
      setPreviewVisible(true);
    } else {
      message.info('该文件类型不支持预览，请下载查看');
    }
  };

  const handleBatchDelete = async () => {
    const selectedFiles = files.filter(file => selectedRowKeys.includes(file.id));
    try {
      const result = await ProjectFileService.deleteMultipleFiles(projectId, selectedFiles.map(f => f.id));
      if (result.success > 0) message.success(`成功删除 ${result.success} 个文件`);
      if (result.failed > 0) message.error(`${result.failed} 个文件删除失败`);
      setSelectedRowKeys([]);
      fetchFiles();
    } catch {
      message.error('批量删除失败');
    }
  };

  const handleBatchDownload = async () => {
    const selectedFiles = files.filter(file => selectedRowKeys.includes(file.id));
    try {
      await ProjectFileService.downloadMultipleFiles(projectId, selectedFiles);
      message.success('批量下载开始');
    } catch {
      message.error('批量下载失败');
    }
  };

  const columns = getFileManagerColumns({
    onPreview: handlePreview,
    onDownload: handleDownload,
    onDelete: handleDelete,
  });

  const stats = {
    total: files.length,
    awardNotice: files.filter(f => f.file_type === FileType.AWARD_NOTICE).length,
    contract: files.filter(f => f.file_type === FileType.CONTRACT).length,
    attachment: files.filter(f => f.file_type === FileType.ATTACHMENT).length,
    other: files.filter(f => f.file_type === FileType.OTHER).length,
  };

  return (
    <Modal
      title={`📁 ${projectName} - 文件管理`}
      open={visible}
      onCancel={onCancel}
      width={1400}
      footer={null}
      destroyOnClose
    >
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card size="small"><Statistic title="总文件数" value={stats.total} prefix="📊" /></Card>
        </Col>
        <Col span={6}>
          <Card size="small"><Statistic title="中标通知书" value={stats.awardNotice} prefix="📋" /></Card>
        </Col>
        <Col span={6}>
          <Card size="small"><Statistic title="合同文件" value={stats.contract} prefix="📄" /></Card>
        </Col>
        <Col span={6}>
          <Card size="small"><Statistic title="其他文件" value={stats.attachment + stats.other} prefix="📎" /></Card>
        </Col>
      </Row>

      {/* 操作栏 */}
      <Card size="small" style={{ marginBottom: '16px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Select
                placeholder="筛选文件类型"
                value={filterType}
                onChange={setFilterType}
                allowClear
                style={{ width: 150 }}
              >
                {Object.entries(FILE_TYPE_DISPLAY).map(([key, config]) => (
                  <Option key={key} value={key}>{config.icon} {config.name}</Option>
                ))}
              </Select>
              <Button onClick={fetchFiles} loading={loading}>刷新</Button>
              {selectedRowKeys.length > 0 && (
                <Space>
                  <span>已选择 {selectedRowKeys.length} 项</span>
                  <Button size="small" onClick={handleBatchDownload}>批量下载</Button>
                  <Popconfirm
                    title={`确定要删除选中的 ${selectedRowKeys.length} 个文件吗？`}
                    onConfirm={handleBatchDelete}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button danger size="small">批量删除</Button>
                  </Popconfirm>
                  <Button size="small" onClick={() => setSelectedRowKeys([])}>取消选择</Button>
                </Space>
              )}
            </Space>
          </Col>
          <Col>
            <Space>
              <Button icon={<CloudUploadOutlined />} onClick={() => setBatchUploadVisible(true)}>
                批量上传
              </Button>
              <Button type="primary" icon={<UploadOutlined />} onClick={() => setUploadModalVisible(true)}>
                上传文件
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 文件列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={files}
          rowKey="id"
          loading={loading}
          rowSelection={{ selectedRowKeys, onChange: setSelectedRowKeys }}
          locale={{ emptyText: <Empty description="暂无文件" image={Empty.PRESENTED_IMAGE_SIMPLE} /> }}
          scroll={{ x: 1000 }}
          pagination={{ pageSize: 10, showSizeChanger: false, showTotal: (total) => `共 ${total} 个文件` }}
        />
      </Card>

      {/* 上传文件弹窗 */}
      <FileUploadModal
        projectId={projectId}
        visible={uploadModalVisible}
        fileConfig={fileConfig}
        onClose={() => setUploadModalVisible(false)}
        onSuccess={fetchFiles}
      />

      {/* 批量上传弹窗 */}
      <BatchUploadModal
        projectId={projectId}
        visible={batchUploadVisible}
        onClose={() => setBatchUploadVisible(false)}
        onSuccess={fetchFiles}
      />

      {/* 文件预览弹窗 */}
      <Modal
        title={`📄 文件预览 - ${previewFile?.file_name}`}
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="download" onClick={() => previewFile && handleDownload(previewFile)}>下载文件</Button>,
          <Button key="close" onClick={() => setPreviewVisible(false)}>关闭</Button>
        ]}
        width={900}
      >
        {previewFile && (
          <div style={{ textAlign: 'center', minHeight: '400px' }}>
            {previewFile.file_extension.toLowerCase() === '.pdf' ? (
              <iframe
                src={ProjectFileService.getFilePreviewUrl(projectId, previewFile.id)}
                width="100%"
                height="500px"
                title="文件预览"
                style={{ border: 'none' }}
              />
            ) : (
              <img
                src={ProjectFileService.getFilePreviewUrl(projectId, previewFile.id)}
                alt="文件预览"
                style={{ maxWidth: '100%', maxHeight: '500px', objectFit: 'contain' }}
              />
            )}
          </div>
        )}
      </Modal>
    </Modal>
  );
};

export default ProjectFileManager;
