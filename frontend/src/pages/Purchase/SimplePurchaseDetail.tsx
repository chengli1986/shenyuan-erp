import React, { useState } from 'react';
import {
  Modal,
  Descriptions,
  Table,
  Space,
  Button,
} from 'antd';
import {
  EditOutlined,
  HistoryOutlined,
  UpOutlined,
  DownOutlined
} from '@ant-design/icons';
import WorkflowStatus, { PurchaseStatus, WorkflowStep } from '../../components/Purchase/WorkflowStatus';
import WorkflowHistory from '../../components/Purchase/WorkflowHistory';
import PurchaseQuoteForm from '../../components/Purchase/PurchaseQuoteForm';
import PurchaseReturnForm from '../../components/Purchase/PurchaseReturnForm';
import WorkflowActionsPanel from './WorkflowActionsPanel';
import { getPurchaseDetailColumns } from './PurchaseDetailColumns';
import { PurchaseDetailData } from '../../types/purchase';

interface SimplePurchaseDetailProps {
  visible: boolean;
  purchaseData: PurchaseDetailData | null;
  onClose: () => void;
  onRefresh?: () => void; // 刷新列表的回调函数
  onEdit?: (purchaseData: PurchaseDetailData) => void; // 编辑申购单的回调函数
}

const SimplePurchaseDetail: React.FC<SimplePurchaseDetailProps> = ({
  visible,
  purchaseData,
  onClose,
  onRefresh,
  onEdit
}) => {
  const [historyVisible, setHistoryVisible] = useState(false);
  const [quoteVisible, setQuoteVisible] = useState(false);
  const [returnVisible, setReturnVisible] = useState(false);
  const [workflowExpanded, setWorkflowExpanded] = useState(false);
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
  
  if (!purchaseData) {
    // 静默返回，不显示调试信息，因为这是正常的初始状态
    return null;
  }
  
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

  const columns = getPurchaseDetailColumns(currentUser, purchaseData);

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
        width={1300}
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
          {purchaseData.total_amount ? `¥${Number(purchaseData.total_amount).toLocaleString()}` : '-'}
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
      <WorkflowActionsPanel
        purchaseData={purchaseData}
        currentUser={currentUser}
        onClose={onClose}
        onRefresh={onRefresh}
        onQuoteOpen={() => setQuoteVisible(true)}
        onReturnOpen={() => setReturnVisible(true)}
      />
      
      {/* 申购明细 */}
      <Table
        columns={columns}
        dataSource={purchaseData.items || []}
        rowKey="id"
        pagination={false}
        size="small"
        scroll={{ x: 1500 }}
      />
      
      {/* 工作流进展 - 可折叠显示 */}
      <div style={{ marginTop: 24, borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
        <div style={{ marginBottom: 16 }}>
          <Button 
            type="text" 
            icon={workflowExpanded ? <UpOutlined /> : <DownOutlined />}
            onClick={() => setWorkflowExpanded(!workflowExpanded)}
            style={{ padding: 0, height: 'auto', fontSize: 16, fontWeight: 600 }}
          >
            <Space>
              <HistoryOutlined />
              工作流进展
            </Space>
          </Button>
        </div>
        
        {workflowExpanded && (
          <WorkflowHistory
            purchaseId={purchaseData.id}
            visible={true}
            onClose={() => {}}
            embedded={true}
          />
        )}
      </div>
      
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

    </>
  );
};

export default SimplePurchaseDetail;