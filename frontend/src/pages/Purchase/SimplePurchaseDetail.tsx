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
  DatePicker,
  Select,
  InputNumber,
  Divider,
  message
} from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  SendOutlined,
  DollarOutlined,
  CrownOutlined,
  EditOutlined
} from '@ant-design/icons';
import { formatPurchaseStatus, formatItemType } from '../../services/purchase';
import WorkflowStatus, { PurchaseStatus, WorkflowStep } from '../../components/Purchase/WorkflowStatus';
import dayjs from 'dayjs';

interface SimplePurchaseDetailProps {
  visible: boolean;
  purchaseData: any;
  onClose: () => void;
  onRefresh?: () => void; // 刷新列表的回调函数
}

const SimplePurchaseDetail: React.FC<SimplePurchaseDetailProps> = ({
  visible,
  purchaseData,
  onClose,
  onRefresh
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
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
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/purchases/${purchaseData.id}/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        message.success('申购单提交成功');
        onRefresh?.();
        onClose();
      } else {
        const error = await response.text();
        message.error(`提交失败: ${error}`);
      }
    } catch (error) {
      console.error('提交申购单失败:', error);
      message.error('网络连接失败');
    } finally {
      setLoading(false);
    }
  };

  // 采购员询价
  const handleQuote = async (values: any) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      
      // 构造询价数据
      const quoteData = {
        payment_method: values.payment_method,
        estimated_delivery_date: values.estimated_delivery_date?.toISOString(),
        quote_notes: values.quote_notes,
        items: purchaseData.items?.map((item: any) => ({
          item_id: item.id,
          unit_price: values[`unit_price_${item.id}`] || 0,
          supplier_name: values[`supplier_name_${item.id}`] || '',
          supplier_contact: values[`supplier_contact_${item.id}`] || '',
          estimated_delivery: values.estimated_delivery_date?.toISOString()
        })) || []
      };

      const response = await fetch(`/api/v1/purchases/${purchaseData.id}/quote`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(quoteData)
      });

      if (response.ok) {
        message.success('询价完成');
        form.resetFields();
        onRefresh?.();
        onClose();
      } else {
        const error = await response.text();
        message.error(`询价失败: ${error}`);
      }
    } catch (error) {
      console.error('询价失败:', error);
      message.error('网络连接失败');
    } finally {
      setLoading(false);
    }
  };

  // 部门主管审批
  const handleDeptApprove = async (approved: boolean, notes: string) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const approvalData = {
        approval_status: approved ? 'approved' : 'rejected',
        approval_notes: notes
      };

      const response = await fetch(`/api/v1/purchases/${purchaseData.id}/dept-approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(approvalData)
      });

      if (response.ok) {
        message.success(approved ? '审批通过' : '审批拒绝');
        onRefresh?.();
        onClose();
      } else {
        const error = await response.text();
        message.error(`审批失败: ${error}`);
      }
    } catch (error) {
      console.error('审批失败:', error);
      message.error('网络连接失败');
    } finally {
      setLoading(false);
    }
  };

  // 总经理最终审批
  const handleFinalApprove = async (approved: boolean, notes: string) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const approvalData = {
        approval_status: approved ? 'approved' : 'rejected',
        approval_notes: notes
      };

      const response = await fetch(`/api/v1/purchases/${purchaseData.id}/final-approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(approvalData)
      });

      if (response.ok) {
        message.success(approved ? '最终审批通过' : '最终审批拒绝');
        onRefresh?.();
        onClose();
      } else {
        const error = await response.text();
        message.error(`最终审批失败: ${error}`);
      }
    } catch (error) {
      console.error('最终审批失败:', error);
      message.error('网络连接失败');
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

          {/* 采购员询价 */}
          {status === 'submitted' && currentStep === 'purchaser' && canOperate('purchaser') && (
            <Button
              type="primary"
              icon={<DollarOutlined />}
              onClick={() => {
                Modal.confirm({
                  title: '采购员询价',
                  content: (
                    <Form
                      form={form}
                      layout="vertical"
                      onFinish={handleQuote}
                    >
                      <Form.Item
                        name="payment_method"
                        label="付款方式"
                        rules={[{ required: true, message: '请选择付款方式' }]}
                      >
                        <Select>
                          <Select.Option value="prepayment">预付款</Select.Option>
                          <Select.Option value="installment">分期付款</Select.Option>
                          <Select.Option value="on_delivery">货到付款</Select.Option>
                        </Select>
                      </Form.Item>
                      <Form.Item
                        name="estimated_delivery_date"
                        label="预计到货时间"
                        rules={[{ required: true, message: '请选择预计到货时间' }]}
                      >
                        <DatePicker showTime />
                      </Form.Item>
                      <Form.Item name="quote_notes" label="询价备注">
                        <Input.TextArea rows={3} />
                      </Form.Item>
                      <Divider />
                      {purchaseData.items?.map((item: any) => (
                        <div key={item.id} style={{ marginBottom: 16, padding: 8, border: '1px solid #d9d9d9' }}>
                          <h5>{item.item_name}</h5>
                          <Form.Item
                            name={`unit_price_${item.id}`}
                            label="单价"
                            rules={[{ required: true, message: '请输入单价' }]}
                          >
                            <InputNumber min={0} precision={2} style={{ width: '100%' }} />
                          </Form.Item>
                          <Form.Item name={`supplier_name_${item.id}`} label="供应商名称">
                            <Input />
                          </Form.Item>
                          <Form.Item name={`supplier_contact_${item.id}`} label="供应商联系方式">
                            <Input />
                          </Form.Item>
                        </div>
                      ))}
                    </Form>
                  ),
                  width: 600,
                  onOk: () => form.submit(),
                  okText: '确认询价',
                  cancelText: '取消'
                });
              }}
            >
              询价
            </Button>
          )}

          {/* 部门主管审批 */}
          {status === 'price_quoted' && currentStep === 'dept_manager' && canOperate('dept_manager') && (
            <>
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={() => {
                  Modal.confirm({
                    title: '部门主管审批',
                    content: (
                      <Form form={form}>
                        <Form.Item name="approval_notes" label="审批意见">
                          <Input.TextArea rows={3} placeholder="请输入审批意见..." />
                        </Form.Item>
                      </Form>
                    ),
                    onOk: () => {
                      const notes = form.getFieldValue('approval_notes') || '';
                      handleDeptApprove(true, notes);
                    },
                    okText: '批准',
                    cancelText: '取消'
                  });
                }}
                loading={loading}
              >
                批准
              </Button>
              <Button
                danger
                icon={<CloseCircleOutlined />}
                onClick={() => {
                  Modal.confirm({
                    title: '部门主管审批',
                    content: (
                      <Form form={form}>
                        <Form.Item 
                          name="rejection_notes" 
                          label="拒绝理由"
                          rules={[{ required: true, message: '请输入拒绝理由' }]}
                        >
                          <Input.TextArea rows={3} placeholder="请输入拒绝理由..." />
                        </Form.Item>
                      </Form>
                    ),
                    onOk: () => {
                      const notes = form.getFieldValue('rejection_notes') || '';
                      handleDeptApprove(false, notes);
                    },
                    okText: '确认拒绝',
                    cancelText: '取消'
                  });
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
                  Modal.confirm({
                    title: '总经理最终审批',
                    content: (
                      <Form form={form}>
                        <Form.Item name="final_approval_notes" label="最终审批意见">
                          <Input.TextArea rows={3} placeholder="请输入最终审批意见..." />
                        </Form.Item>
                      </Form>
                    ),
                    onOk: () => {
                      const notes = form.getFieldValue('final_approval_notes') || '';
                      handleFinalApprove(true, notes);
                    },
                    okText: '最终批准',
                    cancelText: '取消'
                  });
                }}
                loading={loading}
              >
                最终批准
              </Button>
              <Button
                danger
                icon={<CloseCircleOutlined />}
                onClick={() => {
                  Modal.confirm({
                    title: '总经理最终审批',
                    content: (
                      <Form form={form}>
                        <Form.Item 
                          name="final_rejection_notes" 
                          label="最终拒绝理由"
                          rules={[{ required: true, message: '请输入最终拒绝理由' }]}
                        >
                          <Input.TextArea rows={3} placeholder="请输入最终拒绝理由..." />
                        </Form.Item>
                      </Form>
                    ),
                    onOk: () => {
                      const notes = form.getFieldValue('final_rejection_notes') || '';
                      handleFinalApprove(false, notes);
                    },
                    okText: '确认拒绝',
                    cancelText: '取消'
                  });
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
    {
      title: '备注',
      dataIndex: 'remarks',
      width: 150,
      render: (value: string) => value || '-'
    }
  ];

  return (
    <Modal
      title={`申购单详情 - ${purchaseData.request_code}`}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
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

      {/* 工作流操作区域 */}
      {renderWorkflowActions()}
      
      {/* 申购明细 */}
      <Table
        columns={columns}
        dataSource={purchaseData.items || []}
        rowKey="id"
        pagination={false}
        size="small"
        scroll={{ x: 900 }}
      />
    </Modal>
  );
};

export default SimplePurchaseDetail;