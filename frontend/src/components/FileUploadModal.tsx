import React, { useState } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  Upload,
  Button,
  Space,
  Progress,
  message
} from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd/es/upload';
import {
  FileType,
  FileSystemConfig,
  validateFile
} from '../types/projectFile';
import { ProjectFileService } from '../services/projectFile';

const { Option } = Select;
const { TextArea } = Input;
const { Dragger } = Upload;

const DEFAULT_FILE_TYPES = [
  { value: 'award_notice', label: '中标通知书', icon: '📋', color: 'blue', max_count: 5, description: '项目中标通知书等相关文件' },
  { value: 'contract', label: '合同文件', icon: '📄', color: 'green', max_count: 10, description: '项目合同、协议等文件' },
  { value: 'attachment', label: '附件', icon: '📎', color: 'orange', max_count: 50, description: '项目相关附件' },
  { value: 'other', label: '其他文件', icon: '📁', color: 'gray', max_count: 20, description: '其他类型文件' }
];

interface FileUploadModalProps {
  projectId: number;
  visible: boolean;
  fileConfig: FileSystemConfig | null;
  onClose: () => void;
  onSuccess: () => void;
}

const FileUploadModal: React.FC<FileUploadModalProps> = ({
  projectId,
  visible,
  fileConfig,
  onClose,
  onSuccess
}) => {
  const [uploadForm] = Form.useForm();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleClose = () => {
    uploadForm.resetFields();
    setSelectedFile(null);
    setUploadProgress(0);
    onClose();
  };

  const handleUpload = async (values: Record<string, unknown>) => {
    if (!selectedFile) {
      message.error('请选择要上传的文件');
      return;
    }

    const fileType = values.file_type as FileType;
    const description = values.description as string | undefined;
    const validation = validateFile(selectedFile, fileType);
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
        fileType,
        description,
        '当前用户',
        (percent) => setUploadProgress(percent)
      );

      message.success('文件上传成功');
      handleClose();
      onSuccess();
    } catch (error: unknown) {
      message.error(error instanceof Error ? error.message : '文件上传失败');
    } finally {
      setUploadLoading(false);
    }
  };

  const uploadProps: UploadProps = {
    beforeUpload: (file) => {
      setSelectedFile(file);
      return false;
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

  const fileTypes = fileConfig?.file_types || DEFAULT_FILE_TYPES;

  return (
    <Modal
      title="📤 上传文件"
      open={visible}
      onCancel={handleClose}
      footer={null}
      width={600}
    >
      <Form form={uploadForm} layout="vertical" onFinish={handleUpload}>
        <Form.Item label="选择文件" required>
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

        <Form.Item name="file_type" label="文件类型" rules={[{ required: true, message: '请选择文件类型' }]}>
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
        </Form.Item>

        <Form.Item name="description" label="文件描述">
          <TextArea rows={3} placeholder="请输入文件描述（可选）" maxLength={200} showCount />
        </Form.Item>

        {uploadLoading && (
          <Form.Item>
            <Progress percent={uploadProgress} status="active" />
          </Form.Item>
        )}

        <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
          <Space>
            <Button onClick={handleClose} disabled={uploadLoading}>取消</Button>
            <Button type="primary" htmlType="submit" loading={uploadLoading} disabled={!selectedFile}>
              {uploadLoading ? '上传中...' : '开始上传'}
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default FileUploadModal;
