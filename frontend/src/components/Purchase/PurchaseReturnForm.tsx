import React, { useState } from 'react';
import {
  Modal,
  Form,
  Input,
  Button,
  message,
  Space,
  Typography,
  Alert
} from 'antd';
import { UndoOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import api from '../../services/api';

const { TextArea } = Input;
const { Text } = Typography;

interface PurchaseReturnFormProps {
  visible: boolean;
  purchaseData: any;
  onClose: () => void;
  onSuccess: () => void;
}

const PurchaseReturnForm: React.FC<PurchaseReturnFormProps> = ({
  visible,
  purchaseData,
  onClose,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();
      
      const returnData = {
        approval_status: 'rejected', // 使用rejected状态表示退回
        approval_notes: values.return_reason
      };

      await api.post(`purchases/${purchaseData.id}/return`, returnData);
      message.success('申购单已退回给项目经理');
      onSuccess();
      onClose();
      form.resetFields();
    } catch (error: any) {
      console.error('退回失败:', error);
      message.error(error.response?.data?.detail || '退回失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title={
        <Space>
          <UndoOutlined />
          <span>退回申购单 - {purchaseData?.request_code}</span>
        </Space>
      }
      visible={visible}
      onCancel={handleCancel}
      width={600}
      footer={[
        <Button key="cancel" onClick={handleCancel}>
          取消
        </Button>,
        <Button key="submit" type="primary" danger loading={loading} onClick={handleSubmit}>
          确认退回
        </Button>
      ]}
    >
      <Alert
        message="退回说明"
        description="退回后申购单将返回草稿状态，项目经理需要重新修改并提交。请填写退回原因，以便项目经理了解需要修改的内容。"
        type="warning"
        icon={<ExclamationCircleOutlined />}
        style={{ marginBottom: 24 }}
      />

      <Form
        form={form}
        layout="vertical"
      >
        <div style={{ marginBottom: 16 }}>
          <Text strong>申购单信息：</Text>
          <div style={{ marginTop: 8, padding: 12, backgroundColor: '#f5f5f5', borderRadius: 4 }}>
            <Text>申购单号：{purchaseData?.request_code}</Text><br />
            <Text>项目：{purchaseData?.project_name}</Text><br />
            <Text>申请人：{purchaseData?.requester_name}</Text><br />
            <Text>申请日期：{purchaseData?.request_date}</Text>
          </div>
        </div>

        <Form.Item
          label="退回原因"
          name="return_reason"
          rules={[
            { required: true, message: '请填写退回原因' },
            { min: 10, message: '退回原因至少需要10个字符' },
            { max: 500, message: '退回原因不能超过500个字符' }
          ]}
        >
          <TextArea
            placeholder="请详细说明退回原因，例如：规格型号不准确、品牌要求有变更、数量需要调整等..."
            rows={6}
            maxLength={500}
            showCount
          />
        </Form.Item>

        <Alert
          message="注意事项"
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              <li>退回原因将记录到工作流历史中</li>
              <li>项目经理会收到退回通知</li>
              <li>退回后申购单状态变为草稿，需要重新提交</li>
            </ul>
          }
          type="info"
          style={{ marginTop: 16 }}
        />
      </Form>
    </Modal>
  );
};

export default PurchaseReturnForm;