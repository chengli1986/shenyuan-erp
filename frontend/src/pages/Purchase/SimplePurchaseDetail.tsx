import React, { useState } from 'react';
import {
  Modal,
  Descriptions,
  Table,
  Tag,
  Space,
  Button,
  Form,
  Input,
  message
} from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  SendOutlined,
  DollarOutlined,
  CrownOutlined,
  EditOutlined,
  HistoryOutlined
} from '@ant-design/icons';
import { formatItemType } from '../../services/purchase';
import WorkflowStatus, { PurchaseStatus, WorkflowStep } from '../../components/Purchase/WorkflowStatus';
import WorkflowHistory from '../../components/Purchase/WorkflowHistory';
import PurchaseQuoteForm from '../../components/Purchase/PurchaseQuoteForm';
import PurchaseReturnForm from '../../components/Purchase/PurchaseReturnForm';
import api from '../../services/api';

interface SimplePurchaseDetailProps {
  visible: boolean;
  purchaseData: any;
  onClose: () => void;
  onRefresh?: () => void; // 刷新列表的回调函数
  onEdit?: (purchaseData: any) => void; // 编辑申购单的回调函数
}

const SimplePurchaseDetail: React.FC<SimplePurchaseDetailProps> = ({
  visible,
  purchaseData,
  onClose,
  onRefresh,
  onEdit
}) => {
  const [approvalForm] = Form.useForm(); // 审批表单
  const [loading, setLoading] = useState(false);
  const [historyVisible, setHistoryVisible] = useState(false);
  const [quoteVisible, setQuoteVisible] = useState(false);
  const [returnVisible, setReturnVisible] = useState(false);
  // 新增：审批Modal状态
  const [approvalVisible, setApprovalVisible] = useState(false);
  const [approvalType, setApprovalType] = useState<'approve' | 'reject' | 'final_approve' | 'final_reject'>('approve');
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
  
  if (!purchaseData) {
    // 静默返回，不显示调试信息，因为这是正常的初始状态
    return null;
  }
  
  console.log('SimplePurchaseDetail props:', { visible, purchaseData });

  // 获取步骤显示标签
  const getStepLabel = (step?: string) => {
    const stepLabels = {
      'project_manager': '项目经理',
      'purchaser': '采购员',
      'dept_manager': '部门主管',
      'general_manager': '总经理',
      'completed': '已完成'
    };
    return stepLabels[step as keyof typeof stepLabels] || step || '-';
  };

  // 检查当前用户是否可以操作
  const canOperate = (requiredStep: string, requiredRole?: string) => {
    if (!currentUser) return false;
    
    // 检查是否是当前步骤
    if (purchaseData.current_step !== requiredStep) return false;
    
    // 检查角色权限
    if (requiredRole && currentUser.role !== requiredRole) return false;
    
    return true;
  };

  // 提交申购单
  const handleSubmit = async () => {
    setLoading(true);
    try {
      await api.post(`purchases/${purchaseData.id}/submit`);
      message.success('申购单提交成功');
      onRefresh?.();
      onClose();
    } catch (error: any) {
      console.error('提交申购单失败:', error);
      message.error(`提交失败: ${error.response?.data?.detail || error.message || '网络连接失败'}`);
    } finally {
      setLoading(false);
    }
  };

  // 旧的询价函数已移除，使用独立的PurchaseQuoteForm组件

  // 处理审批Modal的提交
  const handleApprovalSubmit = async () => {
    try {
      console.log('📋 [审批Modal] 开始处理审批提交, type:', approvalType);
      const values = await approvalForm.validateFields();
      console.log('📋 [审批Modal] 表单验证通过, values:', values);
      
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
      console.error('📋 [审批Modal] 表单验证失败:', error);
    }
  };

  // 开启审批Modal
  const openApprovalModal = (type: 'approve' | 'reject' | 'final_approve' | 'final_reject') => {
    console.log('📋 [审批Modal] 打开审批Modal, type:', type);
    setApprovalType(type);
    setApprovalVisible(true);
    approvalForm.resetFields();
  };

  // 部门主管审批
  const handleDeptApprove = async (approved: boolean, notes: string) => {
    console.log('🏢 [部门审批] 开始处理审批:', { approved, notes, purchaseId: purchaseData.id });
    setLoading(true);
    try {
      const approvalData = {
        approval_status: approved ? 'approved' : 'rejected',
        approval_notes: notes
      };

      console.log('🏢 [部门审批] 发送数据:', approvalData);
      await api.post(`purchases/${purchaseData.id}/dept-approve`, approvalData);
      console.log('🏢 [部门审批] API调用成功');
      message.success(approved ? '审批通过' : '审批拒绝');
      onRefresh?.();
      onClose();
    } catch (error: any) {
      console.error('🏢 [部门审批] 审批失败:', error);
      console.error('🏢 [部门审批] 错误详情:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      message.error(`审批失败: ${error.response?.data?.detail || error.message || '网络连接失败'}`);
    } finally {
      setLoading(false);
    }
  };

  // 总经理最终审批
  const handleFinalApprove = async (approved: boolean, notes: string) => {
    console.log('👑 [总经理审批] 开始处理最终审批:', { approved, notes, purchaseId: purchaseData.id });
    setLoading(true);
    try {
      const approvalData = {
        approval_status: approved ? 'approved' : 'rejected',
        approval_notes: notes
      };

      console.log('👑 [总经理审批] 发送数据:', approvalData);
      await api.post(`purchases/${purchaseData.id}/final-approve`, approvalData);
      console.log('👑 [总经理审批] API调用成功');
      message.success(approved ? '最终审批通过' : '最终审批拒绝');
      onRefresh?.();
      onClose();
    } catch (error: any) {
      console.error('👑 [总经理审批] 最终审批失败:', error);
      console.error('👑 [总经理审批] 错误详情:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      message.error(`最终审批失败: ${error.response?.data?.detail || error.message || '网络连接失败'}`);
    } finally {
      setLoading(false);
    }
  };

  // 渲染工作流操作区域
  const renderWorkflowActions = () => {
    if (!currentUser) return null;

    const status = purchaseData.status;
    const currentStep = purchaseData.current_step;

    return (
      <div style={{ marginBottom: 16, padding: 16, backgroundColor: '#f5f5f5', borderRadius: 6 }}>
        <h4>工作流操作</h4>
        <Space wrap>
          {/* 项目经理提交 */}
          {status === 'draft' && currentStep === 'project_manager' && canOperate('project_manager') && (
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSubmit}
              loading={loading}
            >
              提交申购单
            </Button>
          )}

          {/* 采购员询价和退回 */}
          {status === 'submitted' && currentStep === 'purchaser' && canOperate('purchaser') && (
            <>
              <Button
                type="primary"
                icon={<DollarOutlined />}
                onClick={() => setQuoteVisible(true)}
              >
                询价
              </Button>
              <Button
                danger
                icon={<CloseCircleOutlined />}
                onClick={() => setReturnVisible(true)}
                style={{ marginLeft: 8 }}
              >
                退回
              </Button>
            </>
          )}

          {/* 项目经理退回（在询价完成后，如对价格或供应商不满意可退回给采购员重新询价） */}
          {status === 'price_quoted' && currentStep === 'dept_manager' && currentUser?.role === 'project_manager' && (
            <Button
              danger
              icon={<CloseCircleOutlined />}
              onClick={() => setReturnVisible(true)}
            >
              退回采购员
            </Button>
          )}

          {/* 部门主管审批 */}
          {status === 'price_quoted' && currentStep === 'dept_manager' && canOperate('dept_manager') && (
            <>
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={() => {
                  console.log('🔘 [按钮点击] 部门批准按钮被点击');
                  openApprovalModal('approve');
                }}
                loading={loading}
              >
                批准
              </Button>
              <Button
                danger
                icon={<CloseCircleOutlined />}
                onClick={() => {
                  console.log('🔘 [按钮点击] 部门拒绝按钮被点击');
                  openApprovalModal('reject');
                }}
                loading={loading}
              >
                拒绝
              </Button>
            </>
          )}

          {/* 总经理最终审批 */}
          {status === 'dept_approved' && currentStep === 'general_manager' && canOperate('general_manager') && (
            <>
              <Button
                type="primary"
                icon={<CrownOutlined />}
                onClick={() => {
                  console.log('🔘 [按钮点击] 总经理最终批准按钮被点击');
                  openApprovalModal('final_approve');
                }}
                loading={loading}
              >
                最终批准
              </Button>
              <Button
                danger
                icon={<CloseCircleOutlined />}
                onClick={() => {
                  console.log('🔘 [按钮点击] 总经理最终拒绝按钮被点击');
                  openApprovalModal('final_reject');
                }}
                loading={loading}
              >
                最终拒绝
              </Button>
            </>
          )}

          {/* 显示当前用户和权限信息 */}
          <div style={{ marginLeft: 'auto', fontSize: '12px', color: '#666' }}>
            当前用户: {currentUser?.name} ({currentUser?.role})
          </div>
        </Space>
      </div>
    );
  };

  const columns = [
    {
      title: '序号',
      width: 60,
      render: (_: any, __: any, index: number) => index + 1
    },
    {
      title: '类型',
      dataIndex: 'item_type',
      width: 80,
      render: (type: string) => formatItemType(type)
    },
    {
      title: '物料名称',
      dataIndex: 'item_name',
      width: 150
    },
    {
      title: '规格型号',
      dataIndex: 'specification',
      width: 150,
      render: (value: string) => value || '-'
    },
    {
      title: '品牌',
      dataIndex: 'brand',
      width: 100,
      render: (value: string) => value || '-'
    },
    {
      title: '所属系统',
      dataIndex: 'system_category_name',
      width: 120,
      render: (value: string) => value ? (
        <Tag color="blue">{value}</Tag>
      ) : '-'
    },
    {
      title: '单位',
      dataIndex: 'unit',
      width: 60
    },
    {
      title: '申购数量',
      dataIndex: 'quantity',
      width: 100,
      render: (value: string) => parseFloat(value).toFixed(2)
    },
    {
      title: '已收数量',
      dataIndex: 'received_quantity',
      width: 100,
      render: (value: string) => parseFloat(value || '0').toFixed(2)
    },
    // 根据用户权限显示询价和价格信息
    ...(currentUser?.role !== 'project_manager' ? [
      {
        title: '供应商',
        dataIndex: 'supplier_name',
        width: 120,
        render: (value: string) => value || '-'
      },
      {
        title: '供应商联系人',
        dataIndex: 'supplier_contact',
        width: 120,
        render: (value: string) => value || '-'
      },
      {
        title: '付款方式',
        dataIndex: 'payment_method',
        width: 100,
        render: (value: string, record: any) => {
          // 正确的数据读取优先级：
          // 1. 物料级payment_method字段 
          // 2. supplier_info.payment_method (实际存储位置)
          // 3. 申购单级别payment_method
          let paymentMethod = value || record.supplier_info?.payment_method || purchaseData.payment_method;
          
          const paymentMethods: { [key: string]: string } = {
            'PREPAYMENT': '预付款',
            'ON_DELIVERY': '货到付款', 
            'MONTHLY': '月结',
            'INSTALLMENT': '分期付款'
          };
          return paymentMethods[paymentMethod] || paymentMethod || '-';
        }
      },
      {
        title: '预计交货',
        dataIndex: 'estimated_delivery_date',
        width: 100,
        render: (value: string, record: any) => {
          // 正确的数据读取优先级：
          // 1. 物料级estimated_delivery_date字段
          // 2. estimated_delivery字段 (实际存储位置)
          // 3. 申购单级别estimated_delivery_date
          const deliveryDate = value || record.estimated_delivery || purchaseData.estimated_delivery_date;
          if (!deliveryDate) return '-';
          return new Date(deliveryDate).toLocaleDateString('zh-CN');
        }
      },
      {
        title: '单价',
        dataIndex: 'unit_price',
        width: 100,
        render: (value: string | number) => {
          if (!value || parseFloat(value.toString()) === 0) return '-';
          return `¥${parseFloat(value.toString()).toLocaleString('zh-CN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          })}`;
        }
      },
      {
        title: '总价',
        dataIndex: 'total_price',
        width: 120,
        render: (value: string | number) => {
          if (!value || parseFloat(value.toString()) === 0) return '-';
          return `¥${parseFloat(value.toString()).toLocaleString('zh-CN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          })}`;
        }
      }
    ] : []),
    {
      title: '备注',
      dataIndex: 'remarks',
      width: 150,
      render: (value: string) => value || '-'
    }
  ];

  return (
    <>
      <Modal
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>申购单详情 - {purchaseData.request_code}</span>
            <Space>
              {purchaseData.status === 'draft' && onEdit && (
                <Button
                  type="text"
                  icon={<EditOutlined />}
                  onClick={() => onEdit(purchaseData)}
                  style={{ color: '#52c41a' }}
                >
                  编辑申购单
                </Button>
              )}
              <Button
                type="text"
                icon={<HistoryOutlined />}
                onClick={() => setHistoryVisible(!historyVisible)}
                style={{ color: historyVisible ? '#1890ff' : undefined }}
              >
                工作流历史
              </Button>
            </Space>
          </div>
        }
        open={visible}
        onCancel={onClose}
        footer={null}
        width={1200}
      >
      {/* 基本信息 */}
      <Descriptions bordered style={{ marginBottom: 16 }}>
        <Descriptions.Item label="申购单号">
          {purchaseData.request_code}
        </Descriptions.Item>
        <Descriptions.Item label="项目名称">
          {purchaseData.project_name || `项目ID: ${purchaseData.project_id}`}
        </Descriptions.Item>
        <Descriptions.Item label="申请日期">
          {new Date(purchaseData.request_date).toLocaleDateString('zh-CN')}
        </Descriptions.Item>
        <Descriptions.Item label="申请人">
          {purchaseData.requester_name || '系统管理员'}
        </Descriptions.Item>
        <Descriptions.Item label="需求日期">
          {purchaseData.required_date 
            ? new Date(purchaseData.required_date).toLocaleDateString('zh-CN') 
            : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="工作流状态">
          <WorkflowStatus 
            status={purchaseData.status as PurchaseStatus}
            currentStep={purchaseData.current_step as WorkflowStep}
            showSteps={false}
            size="small"
          />
        </Descriptions.Item>
        <Descriptions.Item label="所属系统">
          {purchaseData.system_category || '-'}
        </Descriptions.Item>
        <Descriptions.Item label="总金额">
          {purchaseData.total_amount ? `¥${parseFloat(purchaseData.total_amount).toLocaleString()}` : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="当前步骤">
          {getStepLabel(purchaseData.current_step)}
        </Descriptions.Item>
        <Descriptions.Item label="申购说明" span={3}>
          {purchaseData.remarks || '-'}
        </Descriptions.Item>
      </Descriptions>

      {/* 询价信息 - 根据用户角色和申购单状态显示 */}
      {(currentUser?.role !== 'project_manager' && ['price_quoted', 'dept_approved', 'final_approved'].includes(purchaseData.status)) && (
        <Descriptions 
          title="询价信息" 
          bordered 
          style={{ marginBottom: 16 }}
          size="small"
        >
          <Descriptions.Item label="付款方式">
            {purchaseData.payment_method || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="预计交货日期">
            {purchaseData.estimated_delivery_date 
              ? new Date(purchaseData.estimated_delivery_date).toLocaleDateString('zh-CN')
              : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="询价日期">
            {purchaseData.quote_date 
              ? new Date(purchaseData.quote_date).toLocaleDateString('zh-CN')
              : '-'}
          </Descriptions.Item>
        </Descriptions>
      )}

      {/* 工作流操作区域 */}
      {renderWorkflowActions()}
      
      {/* 申购明细 */}
      <Table
        columns={columns}
        dataSource={purchaseData.items || []}
        rowKey="id"
        pagination={false}
        size="small"
        scroll={{ x: 1400 }}
      />
      
      {/* 询价表单 */}
      <PurchaseQuoteForm
        visible={quoteVisible}
        purchaseData={purchaseData}
        onClose={() => setQuoteVisible(false)}
        onSuccess={() => {
          setQuoteVisible(false);
          if (onRefresh) onRefresh();
        }}
      />
      
      {/* 退回表单 */}
      <PurchaseReturnForm
        visible={returnVisible}
        purchaseData={purchaseData}
        onClose={() => setReturnVisible(false)}
        onSuccess={() => {
          setReturnVisible(false);
          if (onRefresh) onRefresh();
        }}
      />
      </Modal>

      {/* 工作流历史记录 */}
      {historyVisible && (
        <WorkflowHistory
          purchaseId={purchaseData.id}
          visible={historyVisible}
          onClose={() => setHistoryVisible(false)}
        />
      )}

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
            <Form.Item 
              name="rejection_notes" 
              label="拒绝理由"
              rules={[{ required: true, message: '请输入拒绝理由' }]}
            >
              <Input.TextArea rows={3} placeholder="请输入拒绝理由..." />
            </Form.Item>
          )}
          {approvalType === 'final_approve' && (
            <Form.Item name="final_approval_notes" label="最终审批意见">
              <Input.TextArea rows={3} placeholder="请输入最终审批意见..." />
            </Form.Item>
          )}
          {approvalType === 'final_reject' && (
            <Form.Item 
              name="final_rejection_notes" 
              label="最终拒绝理由"
              rules={[{ required: true, message: '请输入最终拒绝理由' }]}
            >
              <Input.TextArea rows={3} placeholder="请输入最终拒绝理由..." />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </>
  );
};

export default SimplePurchaseDetail;