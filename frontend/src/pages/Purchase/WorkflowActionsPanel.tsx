import React, { useState } from 'react';
import {
  Modal,
  Space,
  Button,
  Form,
  Input,
  message,
  Tooltip
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SendOutlined,
  DollarOutlined,
  CrownOutlined
} from '@ant-design/icons';
import api from '../../services/api';
import { PurchaseDetailData } from '../../types/purchase';
import axios from 'axios';

const getErrorMessage = (error: unknown, fallback: string = '操作失败'): string => {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail || error.message || fallback;
  }
  if (error instanceof Error) return error.message;
  return fallback;
};

interface CurrentUser {
  role: string;
  name: string;
}

interface WorkflowActionsPanelProps {
  purchaseData: PurchaseDetailData;
  currentUser: CurrentUser | null;
  onClose: () => void;
  onRefresh?: () => void;
  onQuoteOpen: () => void;
  onReturnOpen: () => void;
}

const WorkflowActionsPanel: React.FC<WorkflowActionsPanelProps> = ({
  purchaseData,
  currentUser,
  onClose,
  onRefresh,
  onQuoteOpen,
  onReturnOpen,
}) => {
  const [approvalForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [approvalVisible, setApprovalVisible] = useState(false);
  const [approvalType, setApprovalType] = useState<'approve' | 'reject' | 'final_approve' | 'final_reject'>('approve');

  const canOperate = (requiredStep: string, requiredRole?: string) => {
    if (!currentUser) return false;
    if (purchaseData.current_step !== requiredStep) return false;

    const stepRoleMap: { [key: string]: string } = {
      'project_manager': 'project_manager',
      'purchaser': 'purchaser',
      'dept_manager': 'dept_manager',
      'general_manager': 'general_manager'
    };

    const expectedRole = requiredRole || stepRoleMap[requiredStep];
    if (expectedRole && currentUser.role !== expectedRole) return false;
    return true;
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await api.post(`purchases/${purchaseData.id}/submit`);
      message.success('申购单提交成功');
      onRefresh?.();
      onClose();
    } catch (error: unknown) {
      console.error('提交申购单失败:', error);
      message.error(`提交失败: ${getErrorMessage(error, '网络连接失败')}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeptApprove = async (approved: boolean, notes: string) => {
    setLoading(true);
    try {
      await api.post(`purchases/${purchaseData.id}/dept-approve`, {
        approval_status: approved ? 'approved' : 'rejected',
        approval_notes: notes
      });
      message.success(approved ? '审批通过' : '审批拒绝');
      onRefresh?.();
      onClose();
    } catch (error: unknown) {
      console.error('部门审批失败:', error);
      message.error(`审批失败: ${getErrorMessage(error, '网络连接失败')}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFinalApprove = async (approved: boolean, notes: string) => {
    setLoading(true);
    try {
      await api.post(`purchases/${purchaseData.id}/final-approve`, {
        approval_status: approved ? 'approved' : 'rejected',
        approval_notes: notes
      });
      message.success(approved ? '最终审批通过' : '最终审批拒绝');
      onRefresh?.();
      onClose();
    } catch (error: unknown) {
      console.error('总经理审批失败:', error);
      message.error(`最终审批失败: ${getErrorMessage(error, '网络连接失败')}`);
    } finally {
      setLoading(false);
    }
  };

  const openApprovalModal = (type: 'approve' | 'reject' | 'final_approve' | 'final_reject') => {
    setApprovalType(type);
    setApprovalVisible(true);
    approvalForm.resetFields();
  };

  const handleApprovalSubmit = async () => {
    try {
      const values = await approvalForm.validateFields();
      if (approvalType === 'approve') {
        await handleDeptApprove(true, values.approval_notes || '');
      } else if (approvalType === 'reject') {
        await handleDeptApprove(false, values.rejection_notes || '');
      } else if (approvalType === 'final_approve') {
        await handleFinalApprove(true, values.final_approval_notes || '');
      } else if (approvalType === 'final_reject') {
        await handleFinalApprove(false, values.final_rejection_notes || '');
      }
      setApprovalVisible(false);
      approvalForm.resetFields();
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  if (!currentUser) return null;

  const status = purchaseData.status;
  const currentStep = purchaseData.current_step;

  return (
    <>
      <div style={{ marginBottom: 16, padding: 16, backgroundColor: '#f5f5f5', borderRadius: 6 }}>
        <h4>工作流操作</h4>
        <Space wrap>
          {/* 项目经理提交 */}
          {status === 'draft' && currentStep === 'project_manager' && canOperate('project_manager') && (
            <Button type="primary" icon={<SendOutlined />} onClick={handleSubmit} loading={loading}>
              提交申购单
            </Button>
          )}

          {/* 采购员询价和退回 */}
          {status === 'submitted' && currentStep === 'purchaser' && canOperate('purchaser') && (
            <>
              <Button type="primary" icon={<DollarOutlined />} onClick={onQuoteOpen}>
                询价
              </Button>
              <Button danger icon={<CloseCircleOutlined />} onClick={onReturnOpen} style={{ marginLeft: 8 }}>
                退回
              </Button>
            </>
          )}

          {/* 项目经理退回（询价完成后） */}
          {status === 'price_quoted' && currentStep === 'dept_manager' && currentUser?.role === 'project_manager' && (
            <Button danger icon={<CloseCircleOutlined />} onClick={onReturnOpen}>
              退回采购员
            </Button>
          )}

          {/* 采购员查看已询价申购单 - 禁用按钮 */}
          {status === 'price_quoted' && currentStep === 'dept_manager' && currentUser?.role === 'purchaser' && (
            <>
              <Tooltip title="此申购单已询价，节点已流转到部门主管处，等待部门主管审批">
                <Button type="primary" icon={<CheckCircleOutlined />} disabled style={{ opacity: 0.5, cursor: 'not-allowed' }}>
                  批准
                </Button>
              </Tooltip>
              <Tooltip title="此申购单已询价，节点已流转到部门主管处，等待部门主管审批">
                <Button danger icon={<CloseCircleOutlined />} disabled style={{ opacity: 0.5, cursor: 'not-allowed', marginLeft: 8 }}>
                  拒绝
                </Button>
              </Tooltip>
            </>
          )}

          {/* 部门主管审批 */}
          {status === 'price_quoted' && currentStep === 'dept_manager' && canOperate('dept_manager') && (
            <>
              <Button type="primary" icon={<CheckCircleOutlined />} onClick={() => openApprovalModal('approve')} loading={loading}>
                批准
              </Button>
              <Button danger icon={<CloseCircleOutlined />} onClick={() => openApprovalModal('reject')} loading={loading}>
                拒绝
              </Button>
            </>
          )}

          {/* 采购员查看部门已批准 - 禁用按钮 */}
          {status === 'dept_approved' && currentStep === 'general_manager' && currentUser?.role === 'purchaser' && (
            <>
              <Tooltip title="此申购单已通过部门审批，节点已流转到总经理处，等待总经理最终审批">
                <Button type="primary" icon={<CrownOutlined />} disabled style={{ opacity: 0.5, cursor: 'not-allowed' }}>
                  最终批准
                </Button>
              </Tooltip>
              <Tooltip title="此申购单已通过部门审批，节点已流转到总经理处，等待总经理最终审批">
                <Button danger icon={<CloseCircleOutlined />} disabled style={{ opacity: 0.5, cursor: 'not-allowed', marginLeft: 8 }}>
                  最终拒绝
                </Button>
              </Tooltip>
            </>
          )}

          {/* 总经理最终审批 */}
          {status === 'dept_approved' && currentStep === 'general_manager' && canOperate('general_manager') && (
            <>
              <Button type="primary" icon={<CrownOutlined />} onClick={() => openApprovalModal('final_approve')} loading={loading}>
                最终批准
              </Button>
              <Button danger icon={<CloseCircleOutlined />} onClick={() => openApprovalModal('final_reject')} loading={loading}>
                最终拒绝
              </Button>
            </>
          )}

          {/* 当前用户信息 */}
          <div style={{ marginLeft: 'auto', fontSize: '12px', color: '#666' }}>
            当前用户: {currentUser?.name} ({currentUser?.role})
          </div>
        </Space>
      </div>

      {/* 审批Modal */}
      <Modal
        title={
          approvalType === 'approve' ? '部门主管审批' :
          approvalType === 'reject' ? '部门主管审批' :
          approvalType === 'final_approve' ? '总经理最终审批' :
          '总经理最终审批'
        }
        visible={approvalVisible}
        onOk={handleApprovalSubmit}
        onCancel={() => {
          setApprovalVisible(false);
          approvalForm.resetFields();
        }}
        okText={
          approvalType === 'approve' ? '确认批准' :
          approvalType === 'reject' ? '确认拒绝' :
          approvalType === 'final_approve' ? '最终批准' :
          '确认拒绝'
        }
        cancelText="取消"
        confirmLoading={loading}
      >
        <Form form={approvalForm} layout="vertical">
          {approvalType === 'approve' && (
            <Form.Item name="approval_notes" label="审批意见">
              <Input.TextArea rows={3} placeholder="请输入审批意见..." />
            </Form.Item>
          )}
          {approvalType === 'reject' && (
            <Form.Item name="rejection_notes" label="拒绝理由" rules={[{ required: true, message: '请输入拒绝理由' }]}>
              <Input.TextArea rows={3} placeholder="请输入拒绝理由..." />
            </Form.Item>
          )}
          {approvalType === 'final_approve' && (
            <Form.Item name="final_approval_notes" label="最终审批意见">
              <Input.TextArea rows={3} placeholder="请输入最终审批意见..." />
            </Form.Item>
          )}
          {approvalType === 'final_reject' && (
            <Form.Item name="final_rejection_notes" label="最终拒绝理由" rules={[{ required: true, message: '请输入最终拒绝理由' }]}>
              <Input.TextArea rows={3} placeholder="请输入最终拒绝理由..." />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </>
  );
};

export default WorkflowActionsPanel;
