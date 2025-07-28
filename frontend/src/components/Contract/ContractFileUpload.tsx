// frontend/src/components/Contract/ContractFileUpload.tsx
/**
 * 合同清单文件上传组件
 */

import React, { useState } from 'react';
import {
  Card,
  Upload,
  Button,
  Form,
  Input,
  Space,
  Typography,
  Alert,
  Progress,
  List,
  Tag,
  message
} from 'antd';
import {
  InboxOutlined,
  UploadOutlined,
  FileExcelOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import type { UploadProps, RcFile } from 'antd/es/upload';

import { uploadContractExcel } from '../../services/contract';
import { ExcelUploadResponse } from '../../types/contract';

const { Dragger } = Upload;
const { TextArea } = Input;
const { Title, Text } = Typography;

interface ContractFileUploadProps {
  projectId: number;
  onUploadSuccess?: () => void;
}

const ContractFileUpload: React.FC<ContractFileUploadProps> = ({
  projectId,
  onUploadSuccess
}) => {
  const [form] = Form.useForm();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<ExcelUploadResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState<RcFile | null>(null);

  // 文件选择处理
  const handleFileSelect: UploadProps['beforeUpload'] = (file) => {
    const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                   file.type === 'application/vnd.ms-excel' ||
                   file.name.toLowerCase().endsWith('.xlsx') ||
                   file.name.toLowerCase().endsWith('.xls');

    if (!isExcel) {
      message.error('只能上传Excel文件（.xlsx或.xls格式）！');
      return false;
    }

    const isLt50M = file.size / 1024 / 1024 < 50;
    if (!isLt50M) {
      message.error('文件大小不能超过50MB！');
      return false;
    }

    setSelectedFile(file);
    setUploadResult(null);
    return false; // 阻止自动上传
  };

  // 提交上传
  const handleSubmit = async (values: any) => {
    if (!selectedFile) {
      message.error('请先选择要上传的Excel文件');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);

      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const formData = {
        file: selectedFile,
        upload_user_name: values.upload_user_name,
        upload_reason: values.upload_reason,
        change_description: values.change_description
      };

      const response = await uploadContractExcel(projectId, formData);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setUploadResult(response);
      
      if (response.success) {
        message.success('文件上传并解析成功！');
        form.resetFields();
        setSelectedFile(null);
        onUploadSuccess?.();
      } else {
        message.error('文件上传失败：' + response.message);
      }

    } catch (error) {
      console.error('上传失败:', error);
      message.error('上传失败：' + (error as Error).message);
      setUploadResult({
        success: false,
        message: (error as Error).message,
        errors: [(error as Error).message]
      });
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  // 移除文件
  const handleRemoveFile = () => {
    setSelectedFile(null);
    setUploadResult(null);
  };

  return (
    <div>
      <Card title="上传投标清单Excel文件" style={{ marginBottom: 24 }}>
        <Alert
          style={{ marginBottom: 24 }}
          message="支持的文件格式"
          description={
            <div>
              <div>• Excel文件（.xlsx 或 .xls 格式）</div>
              <div>• 支持多个工作表（sheet），每个sheet对应一个系统分类</div>
              <div>• 系统会自动检测表头并解析设备明细信息</div>
              <div>• 文件大小限制：50MB以内</div>
            </div>
          }
          type="info"
          showIcon
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            upload_user_name: '',
            upload_reason: '投标清单导入',
            change_description: ''
          }}
        >
          <Form.Item
            name="upload_user_name"
            label="上传人员"
            rules={[{ required: true, message: '请输入上传人员姓名' }]}
          >
            <Input placeholder="请输入上传人员姓名" />
          </Form.Item>

          <Form.Item
            name="upload_reason"
            label="上传原因"
          >
            <Input placeholder="请输入上传原因（可选）" />
          </Form.Item>

          <Form.Item
            name="change_description"
            label="变更说明"
          >
            <TextArea
              rows={3}
              placeholder="请详细描述本次上传的变更内容（可选）"
            />
          </Form.Item>

          <Form.Item label="选择文件">
            {!selectedFile ? (
              <Dragger
                beforeUpload={handleFileSelect}
                showUploadList={false}
                disabled={uploading}
              >
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持Excel格式的投标清单文件（.xlsx 或 .xls）
                </p>
              </Dragger>
            ) : (
              <Card size="small">
                <Space>
                  <FileExcelOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                  <div>
                    <div>{selectedFile.name}</div>
                    <Text type="secondary">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </Text>
                  </div>
                  <Button size="small" onClick={handleRemoveFile} disabled={uploading}>
                    移除
                  </Button>
                </Space>
              </Card>
            )}
          </Form.Item>

          {uploading && (
            <div style={{ marginBottom: 16 }}>
              <Progress percent={uploadProgress} />
              <Text type="secondary">正在上传和解析文件...</Text>
            </div>
          )}

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<UploadOutlined />}
              loading={uploading}
              disabled={!selectedFile}
              size="large"
            >
              {uploading ? '上传中...' : '开始上传'}
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* 上传结果显示 */}
      {uploadResult && (
        <Card 
          title={
            <Space>
              {uploadResult.success ? (
                <CheckCircleOutlined style={{ color: '#52c41a' }} />
              ) : (
                <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
              )}
              上传结果
            </Space>
          }
        >
          <Alert
            message={uploadResult.message}
            type={uploadResult.success ? 'success' : 'error'}
            style={{ marginBottom: 16 }}
          />

          {uploadResult.success && uploadResult.parsed_data && (
            <div style={{ marginBottom: 16 }}>
              <Title level={4}>解析统计</Title>
              <List size="small">
                <List.Item>
                  <Text strong>工作表数量:</Text> {uploadResult.parsed_data.total_sheets}
                </List.Item>
                <List.Item>
                  <Text strong>系统分类数:</Text> {uploadResult.parsed_data.total_categories}
                </List.Item>
                <List.Item>
                  <Text strong>设备明细数:</Text> {uploadResult.parsed_data.total_items}
                </List.Item>
                <List.Item>
                  <Text strong>成功导入:</Text> {uploadResult.parsed_data.imported_items}
                </List.Item>
                <List.Item>
                  <Text strong>合同金额:</Text> 
                  <Text type="success" strong>
                    ¥{uploadResult.parsed_data.total_amount.toLocaleString()}
                  </Text>
                </List.Item>
              </List>

              {uploadResult.parsed_data.categories.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <Text strong>系统分类:</Text>
                  <div style={{ marginTop: 8 }}>
                    {uploadResult.parsed_data.categories.map((category, index) => (
                      <Tag key={index} color="blue" style={{ marginBottom: 4 }}>
                        {category}
                      </Tag>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {uploadResult.errors && uploadResult.errors.length > 0 && (
            <div>
              <Title level={4}>错误信息</Title>
              <List
                size="small"
                dataSource={uploadResult.errors}
                renderItem={(error, index) => (
                  <List.Item key={index}>
                    <Text type="danger">{error}</Text>
                  </List.Item>
                )}
              />
            </div>
          )}
        </Card>
      )}
    </div>
  );
};

export default ContractFileUpload;