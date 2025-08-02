// frontend/src/components/ProjectFileManager.tsx
/**
 * 项目文件管理组件
 * 包含文件上传、列表显示、下载、删除等功能
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Upload,
  Button,
  Table,
  Space,
  Select,
  message,
  Modal,
  Form,
  Input,
  Tag,
  Tooltip,
  Popconfirm,
  Progress,
  Row,
  Col,
  Statistic,
  Empty,
  List,
  Divider
} from 'antd';
import {
  UploadOutlined,
  DownloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  InboxOutlined,
  CloudUploadOutlined,
  FolderOpenOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { UploadFile, UploadProps } from 'antd/es/upload';

import { 
  ProjectFile, 
  FileType, 
  FILE_TYPE_DISPLAY,
  formatFileSize,
  getFileIcon,
  FileSystemConfig,
  BatchUploadItem,
  validateFile,
  canPreviewFile
} from '../types/projectFile';
import { ProjectFileService } from '../services/projectFile';

const { Option } = Select;
const { TextArea } = Input;
const { Dragger } = Upload;

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
  // 状态管理
  const [files, setFiles] = useState<ProjectFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [filterType, setFilterType] = useState<FileType | ''>('');
  const [fileConfig, setFileConfig] = useState<FileSystemConfig | null>(null);
  
  // 上传表单
  const [uploadForm] = Form.useForm();
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // 批量上传
  const [batchUploadVisible, setBatchUploadVisible] = useState(false);
  const [batchFiles, setBatchFiles] = useState<BatchUploadItem[]>([]);
  const [batchUploading, setBatchUploading] = useState(false);

  // 文件预览
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewFile, setPreviewFile] = useState<ProjectFile | null>(null);

  // 表格选择
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  // 默认文件类型配置（防止后端接口失败）
  const defaultFileTypes = [
    {
      value: 'award_notice',
      label: '中标通知书',
      icon: '📋',
      color: 'blue',
      max_count: 5,
      description: '项目中标通知书等相关文件'
    },
    {
      value: 'contract',
      label: '合同文件',
      icon: '📄',
      color: 'green',
      max_count: 10,
      description: '项目合同、协议等文件'
    },
    {
      value: 'attachment',
      label: '附件',
      icon: '📎',
      color: 'orange',
      max_count: 50,
      description: '项目相关附件'
    },
    {
      value: 'other',
      label: '其他文件',
      icon: '📁',
      color: 'gray',
      max_count: 20,
      description: '其他类型文件'
    }
  ];

  // 获取文件列表
  const fetchFiles = useCallback(async () => {
    setLoading(true);
    try {
      const response = await ProjectFileService.getProjectFiles(
        projectId,
        filterType || undefined
      );
      setFiles(response.items);
    } catch (error) {
      message.error('获取文件列表失败');
      console.error('Error fetching files:', error);
    } finally {
      setLoading(false);
    }
  }, [projectId, filterType]);

  // 获取文件系统配置
  const fetchFileConfig = useCallback(async () => {
    try {
      const config = await ProjectFileService.getFileSystemConfig();
      setFileConfig(config);
      console.log('获取到文件配置:', config);
    } catch (error) {
      console.warn('获取文件配置失败，使用默认配置:', error);
      // 使用默认配置
      setFileConfig({
        file_types: defaultFileTypes,
        allowed_extensions: ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.zip', '.rar'],
        max_file_size: 50 * 1024 * 1024,
        max_file_size_mb: 50
      });
    }
  }, []);

  // 组件挂载时获取数据
  useEffect(() => {
    if (visible) {
      fetchFiles();
      fetchFileConfig();
    }
  }, [visible, fetchFiles, fetchFileConfig]);

  // 处理文件上传
  const handleUpload = async (values: any) => {
    if (!selectedFile) {
      message.error('请选择要上传的文件');
      return;
    }

    // 验证文件
    const validation = validateFile(selectedFile, values.file_type);
    if (!validation.valid) {
      message.error(validation.message);
      return;
    }

    setUploadLoading(true);
    setUploadProgress(0);

    try {
      await ProjectFileService.uploadFileWithRetry(
        projectId,
        selectedFile,
        values.file_type,
        values.description,
        '当前用户', // 后续从用户状态获取
        (percent) => setUploadProgress(percent)
      );

      message.success('文件上传成功');
      setUploadModalVisible(false);
      uploadForm.resetFields();
      setSelectedFile(null);
      setUploadProgress(0);
      fetchFiles(); // 刷新列表
    } catch (error: any) {
      message.error(error.response?.data?.detail || '文件上传失败');
    } finally {
      setUploadLoading(false);
    }
  };

  // 处理文件下载
  const handleDownload = async (file: ProjectFile) => {
    try {
      await ProjectFileService.downloadFile(
        projectId,
        file.id,
        file.file_name
      );
      message.success('文件下载开始');
    } catch (error) {
      message.error('文件下载失败');
    }
  };

  // 处理文件删除
  const handleDelete = async (file: ProjectFile) => {
    try {
      await ProjectFileService.deleteFile(projectId, file.id);
      message.success(`文件 "${file.file_name}" 删除成功`);
      fetchFiles(); // 刷新列表
    } catch (error) {
      message.error('文件删除失败');
    }
  };

  // 处理文件预览
  const handlePreview = (file: ProjectFile) => {
    if (canPreviewFile(file.file_extension)) {
      setPreviewFile(file);
      setPreviewVisible(true);
    } else {
      message.info('该文件类型不支持预览，请下载查看');
    }
  };

  // 批量删除
  const handleBatchDelete = async () => {
    const selectedFiles = files.filter(file => selectedRowKeys.includes(file.id));
    try {
      const result = await ProjectFileService.deleteMultipleFiles(
        projectId, 
        selectedFiles.map(f => f.id)
      );
      
      if (result.success > 0) {
        message.success(`成功删除 ${result.success} 个文件`);
      }
      if (result.failed > 0) {
        message.error(`${result.failed} 个文件删除失败`);
      }
      
      setSelectedRowKeys([]);
      fetchFiles();
    } catch (error) {
      message.error('批量删除失败');
    }
  };

  // 批量下载
  const handleBatchDownload = async () => {
    const selectedFiles = files.filter(file => selectedRowKeys.includes(file.id));
    try {
      await ProjectFileService.downloadMultipleFiles(projectId, selectedFiles);
      message.success('批量下载开始');
    } catch (error) {
      message.error('批量下载失败');
    }
  };

  // 处理批量上传
  const handleBatchUpload = async () => {
    if (batchFiles.length === 0) {
      message.error('请添加要上传的文件');
      return;
    }

    setBatchUploading(true);
    
    const updatedFiles = [...batchFiles];
    
    try {
      await ProjectFileService.uploadMultipleFiles(
        projectId,
        batchFiles.map(item => ({
          file: item.file,
          fileType: item.fileType,
          description: item.description
        })),
        '当前用户',
        (fileIndex, percent) => {
          updatedFiles[fileIndex] = {
            ...updatedFiles[fileIndex],
            progress: percent,
            status: 'uploading'
          };
          setBatchFiles([...updatedFiles]);
        },
        (fileIndex, result) => {
          updatedFiles[fileIndex] = {
            ...updatedFiles[fileIndex],
            status: result.success ? 'success' : 'error',
            error: result.success ? undefined : result.message,
            progress: 100
          };
          setBatchFiles([...updatedFiles]);
        }
      );

      const successCount = updatedFiles.filter(f => f.status === 'success').length;
      const errorCount = updatedFiles.filter(f => f.status === 'error').length;
      
      if (successCount > 0) {
        message.success(`成功上传 ${successCount} 个文件`);
      }
      if (errorCount > 0) {
        message.error(`${errorCount} 个文件上传失败`);
      }

      // 延迟关闭弹窗，让用户看到结果
      setTimeout(() => {
        setBatchUploadVisible(false);
        setBatchFiles([]);
        fetchFiles();
      }, 2000);

    } catch (error) {
      message.error('批量上传失败');
    } finally {
      setBatchUploading(false);
    }
  };

  // 自定义文件上传
  const uploadProps: UploadProps = {
    beforeUpload: (file) => {
      setSelectedFile(file);
      return false; // 阻止自动上传
    },
    onRemove: () => {
      setSelectedFile(null);
    },
    fileList: selectedFile ? [{
      uid: '1',
      name: selectedFile.name,
      status: 'done'
    } as UploadFile] : [],
  };

  // 批量上传的拖拽组件
  const batchUploadProps: UploadProps = {
    multiple: true,
    beforeUpload: () => false, // 阻止自动上传
    onChange: ({ fileList }) => {
      const files = fileList.map(item => item.originFileObj).filter(Boolean) as File[];
      const newBatchFiles: BatchUploadItem[] = files.map(file => ({
        file,
        fileType: FileType.OTHER,
        status: 'pending',
        progress: 0
      }));
      setBatchFiles(newBatchFiles);
    },
    showUploadList: false
  };

  // 表格行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: setSelectedRowKeys,
  };

  // 表格列定义
  const columns: ColumnsType<ProjectFile> = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (text, record) => (
        <Space>
          <span style={{ fontSize: '16px' }}>
            {getFileIcon(record.file_extension)}
          </span>
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
              <Button
                type="link"
                icon={<EyeOutlined />}
                size="small"
                onClick={() => handlePreview(record)}
              />
            </Tooltip>
          )}
          <Tooltip title="下载文件">
            <Button
              type="link"
              icon={<DownloadOutlined />}
              size="small"
              onClick={() => handleDownload(record)}
            />
          </Tooltip>
          <Tooltip title="删除文件">
            <Popconfirm
              title="确定要删除这个文件吗？"
              onConfirm={() => handleDelete(record)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="link"
                danger
                icon={<DeleteOutlined />}
                size="small"
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 统计信息
  const stats = {
    total: files.length,
    awardNotice: files.filter(f => f.file_type === FileType.AWARD_NOTICE).length,
    contract: files.filter(f => f.file_type === FileType.CONTRACT).length,
    attachment: files.filter(f => f.file_type === FileType.ATTACHMENT).length,
    other: files.filter(f => f.file_type === FileType.OTHER).length,
  };

  // 批量操作组件
  const BatchOperations = () => {
    if (selectedRowKeys.length === 0) return null;
    
    return (
      <Space>
        <span>已选择 {selectedRowKeys.length} 项</span>
        <Button size="small" onClick={handleBatchDownload}>
          批量下载
        </Button>
        <Popconfirm
          title={`确定要删除选中的 ${selectedRowKeys.length} 个文件吗？`}
          onConfirm={handleBatchDelete}
          okText="确定"
          cancelText="取消"
        >
          <Button danger size="small">
            批量删除
          </Button>
        </Popconfirm>
        <Button size="small" onClick={() => setSelectedRowKeys([])}>
          取消选择
        </Button>
      </Space>
    );
  };

  // 渲染文件类型选择器
  const renderFileTypeSelect = () => {
    // 优先使用 fileConfig，如果没有则使用默认配置
    const fileTypes = fileConfig?.file_types || defaultFileTypes;
    
    return (
      <Select placeholder="请选择文件类型">
        {fileTypes.map((type) => (
          <Option key={type.value} value={type.value}>
            <Space>
              <span>{type.icon}</span>
              <span>{type.label}</span>
            </Space>
          </Option>
        ))}
      </Select>
    );
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
          <Card size="small">
            <Statistic title="总文件数" value={stats.total} prefix="📊" />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="中标通知书" value={stats.awardNotice} prefix="📋" />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="合同文件" value={stats.contract} prefix="📄" />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="其他文件" value={stats.attachment + stats.other} prefix="📎" />
          </Card>
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
                  <Option key={key} value={key}>
                    {config.icon} {config.name}
                  </Option>
                ))}
              </Select>
              <Button onClick={fetchFiles} loading={loading}>
                刷新
              </Button>
              <BatchOperations />
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<CloudUploadOutlined />}
                onClick={() => setBatchUploadVisible(true)}
              >
                批量上传
              </Button>
              <Button
                type="primary"
                icon={<UploadOutlined />}
                onClick={() => setUploadModalVisible(true)}
              >
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
          rowSelection={rowSelection}
          locale={{
            emptyText: <Empty description="暂无文件" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          }}
          scroll={{ x: 1000 }}
          pagination={{
            pageSize: 10,
            showSizeChanger: false,
            showTotal: (total) => `共 ${total} 个文件`,
          }}
        />
      </Card>

      {/* 上传文件弹窗 */}
      <Modal
        title="📤 上传文件"
        open={uploadModalVisible}
        onCancel={() => {
          setUploadModalVisible(false);
          uploadForm.resetFields();
          setSelectedFile(null);
          setUploadProgress(0);
        }}
        footer={null}
        width={600}
      >
        <Form
          form={uploadForm}
          layout="vertical"
          onFinish={handleUpload}
        >
          <Form.Item
            label="选择文件"
            required
          >
            <Dragger {...uploadProps}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                支持 PDF, Word, Excel, 图片等格式，单个文件不超过 50MB
              </p>
            </Dragger>
          </Form.Item>

          <Form.Item
            name="file_type"
            label="文件类型"
            rules={[{ required: true, message: '请选择文件类型' }]}
          >
            {renderFileTypeSelect()}
          </Form.Item>

          <Form.Item
            name="description"
            label="文件描述"
          >
            <TextArea
              rows={3}
              placeholder="请输入文件描述（可选）"
              maxLength={200}
              showCount
            />
          </Form.Item>

          {uploadLoading && (
            <Form.Item>
              <Progress percent={uploadProgress} status="active" />
            </Form.Item>
          )}

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button 
                onClick={() => setUploadModalVisible(false)}
                disabled={uploadLoading}
              >
                取消
              </Button>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={uploadLoading}
                disabled={!selectedFile}
              >
                {uploadLoading ? '上传中...' : '开始上传'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 批量上传弹窗 */}
      <Modal
        title="🗂️ 批量上传文件"
        open={batchUploadVisible}
        onCancel={() => {
          setBatchUploadVisible(false);
          setBatchFiles([]);
        }}
        width={800}
        footer={
          <Space>
            <Button onClick={() => setBatchUploadVisible(false)}>
              取消
            </Button>
            <Button 
              type="primary" 
              onClick={handleBatchUpload}
              loading={batchUploading}
              disabled={batchFiles.length === 0}
            >
              开始批量上传
            </Button>
          </Space>
        }
      >
        <Dragger {...batchUploadProps} style={{ marginBottom: 16 }}>
          <p className="ant-upload-drag-icon">
            <FolderOpenOutlined />
          </p>
          <p className="ant-upload-text">选择多个文件进行批量上传</p>
          <p className="ant-upload-hint">
            支持同时选择多个文件，拖拽或点击选择
          </p>
        </Dragger>

        {batchFiles.length > 0 && (
          <>
            <Divider>待上传文件列表 ({batchFiles.length} 个文件)</Divider>
            <List
              size="small"
              dataSource={batchFiles}
              renderItem={(item, index) => (
                <List.Item
                  actions={[
                    <Select
                      size="small"
                      value={item.fileType}
                      onChange={(value) => {
                        const newFiles = [...batchFiles];
                        newFiles[index].fileType = value;
                        setBatchFiles(newFiles);
                      }}
                      style={{ width: 120 }}
                    >
                      {Object.entries(FILE_TYPE_DISPLAY).map(([key, config]) => (
                        <Option key={key} value={key}>
                          {config.icon} {config.name}
                        </Option>
                      ))}
                    </Select>,
                    <Button
                      size="small"
                      danger
                      onClick={() => {
                        setBatchFiles(prev => prev.filter((_, i) => i !== index));
                      }}
                      disabled={batchUploading}
                    >
                      移除
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<span>{getFileIcon('.' + item.file.name.split('.').pop())}</span>}
                    title={item.file.name}
                    description={
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <span>{formatFileSize(item.file.size)}</span>
                        {item.status !== 'pending' && (
                          <Progress 
                            percent={item.progress} 
                            status={item.status === 'error' ? 'exception' : 'active'}
                            size="small"
                          />
                        )}
                        {item.error && (
                          <span style={{ color: 'red', fontSize: '12px' }}>{item.error}</span>
                        )}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </>
        )}
      </Modal>

      {/* 文件预览弹窗 */}
      <Modal
        title={`📄 文件预览 - ${previewFile?.file_name}`}
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="download" onClick={() => previewFile && handleDownload(previewFile)}>
            下载文件
          </Button>,
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>
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