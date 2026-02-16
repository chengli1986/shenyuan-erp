import React, { useState } from 'react';
import {
  Modal,
  Upload,
  Button,
  Space,
  Select,
  Progress,
  List,
  Divider,
  message
} from 'antd';
import { FolderOpenOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd/es/upload';
import {
  FileType,
  FILE_TYPE_DISPLAY,
  BatchUploadItem,
  formatFileSize,
  getFileIcon
} from '../types/projectFile';
import { ProjectFileService } from '../services/projectFile';

const { Option } = Select;
const { Dragger } = Upload;

interface BatchUploadModalProps {
  projectId: number;
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const BatchUploadModal: React.FC<BatchUploadModalProps> = ({
  projectId,
  visible,
  onClose,
  onSuccess
}) => {
  const [batchFiles, setBatchFiles] = useState<BatchUploadItem[]>([]);
  const [batchUploading, setBatchUploading] = useState(false);

  const handleClose = () => {
    setBatchFiles([]);
    onClose();
  };

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

      if (successCount > 0) message.success(`成功上传 ${successCount} 个文件`);
      if (errorCount > 0) message.error(`${errorCount} 个文件上传失败`);

      setTimeout(() => {
        handleClose();
        onSuccess();
      }, 2000);
    } catch (error) {
      message.error('批量上传失败');
    } finally {
      setBatchUploading(false);
    }
  };

  const batchUploadProps: UploadProps = {
    multiple: true,
    beforeUpload: () => false,
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

  return (
    <Modal
      title="🗂️ 批量上传文件"
      open={visible}
      onCancel={handleClose}
      width={800}
      footer={
        <Space>
          <Button onClick={handleClose}>取消</Button>
          <Button type="primary" onClick={handleBatchUpload} loading={batchUploading} disabled={batchFiles.length === 0}>
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
        <p className="ant-upload-hint">支持同时选择多个文件，拖拽或点击选择</p>
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
                    onClick={() => setBatchFiles(prev => prev.filter((_, i) => i !== index))}
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
  );
};

export default BatchUploadModal;
