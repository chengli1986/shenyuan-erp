import React, { useState, useEffect } from 'react';
import { 
  Timeline, 
  Card, 
  Button, 
  Spin, 
  Empty, 
  Tag, 
  Space, 
  Typography, 
  Divider,
  Collapse,
  Avatar
} from 'antd';
import { 
  UserOutlined, 
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  DollarOutlined,
  SendOutlined,
  CrownOutlined,
  EditOutlined,
  HistoryOutlined
} from '@ant-design/icons';
import api from '../../services/api';
import { formatPurchaseStatus } from '../../services/purchase';
import dayjs from 'dayjs';

const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface WorkflowLogItem {
  id: number;
  from_step: string;
  to_step: string;
  operation_type: string;
  operator_id: number;
  operator_name: string;
  operator_role: string;
  operation_notes?: string;
  operation_data?: any;
  created_at: string;
}

interface WorkflowHistoryProps {
  purchaseId: number;
  visible: boolean;
  onClose: () => void;
}

// 操作类型图标配置
const operationIcons: { [key: string]: React.ReactNode } = {
  submit: <SendOutlined style={{ color: '#1890ff' }} />,
  quote: <DollarOutlined style={{ color: '#faad14' }} />,
  approve: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
  reject: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
  final_approve: <CrownOutlined style={{ color: '#722ed1' }} />,
  create: <EditOutlined style={{ color: '#13c2c2' }} />
};

// 步骤名称配置
const stepNames: { [key: string]: string } = {
  project_manager: '项目经理',
  purchaser: '采购员', 
  dept_manager: '部门主管',
  general_manager: '总经理',
  completed: '已完成'
};

const WorkflowHistory: React.FC<WorkflowHistoryProps> = ({ 
  purchaseId, 
  visible, 
  onClose 
}) => {
  const [loading, setLoading] = useState(false);
  const [workflowLogs, setWorkflowLogs] = useState<WorkflowLogItem[]>([]);

  // 加载工作流历史
  const loadWorkflowHistory = async () => {
    if (!purchaseId || !visible) return;
    
    setLoading(true);
    try {
      const response = await api.get(`purchases/${purchaseId}/workflow-logs`);
      setWorkflowLogs(response.data.logs || []);
    } catch (error: any) {
      console.error('加载工作流历史失败:', error);
      setWorkflowLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkflowHistory();
  }, [purchaseId, visible]);

  // 格式化操作类型显示
  const formatOperationType = (operation: string, fromStep: string, toStep: string) => {
    switch (operation) {
      case 'submit': return '提交申购单';
      case 'quote': return '完成询价';
      case 'approve': return '批准';
      case 'reject': return '拒绝';
      case 'final_approve': return '最终批准';
      case 'create': return '创建申购单';
      default: return `从 ${stepNames[fromStep] || fromStep} 到 ${stepNames[toStep] || toStep}`;
    }
  };

  // 渲染操作详情
  const renderOperationDetails = (log: WorkflowLogItem) => {
    if (!log.operation_data && !log.operation_notes) return null;

    return (
      <Collapse size="small" ghost>
        <Panel 
          header={<Text type="secondary">查看详情</Text>} 
          key="details"
          style={{ padding: 0 }}
        >
          <div style={{ padding: '8px 0' }}>
            {log.operation_notes && (
              <div style={{ marginBottom: '8px' }}>
                <Text strong>操作备注：</Text>
                <Paragraph style={{ margin: 0, paddingLeft: '8px', fontStyle: 'italic' }}>
                  {log.operation_notes}
                </Paragraph>
              </div>
            )}
            
            {log.operation_data && (
              <div>
                <Text strong>详细信息：</Text>
                <div style={{ paddingLeft: '8px', marginTop: '4px' }}>
                  {/* 询价信息 */}
                  {log.operation_data.quote_price && (
                    <div>报价: <Text code>¥{log.operation_data.quote_price}</Text></div>
                  )}
                  {log.operation_data.payment_method && (
                    <div>付款方式: <Tag>{log.operation_data.payment_method}</Tag></div>
                  )}
                  {log.operation_data.estimated_delivery && (
                    <div>预计交期: {dayjs(log.operation_data.estimated_delivery).format('YYYY-MM-DD')}</div>
                  )}
                  
                  {/* 审批信息 */}
                  {log.operation_data.approval_notes && (
                    <div style={{ marginTop: '4px' }}>
                      <Text type="secondary">审批意见: {log.operation_data.approval_notes}</Text>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </Panel>
      </Collapse>
    );
  };

  // 生成时间线项目
  const timelineItems = workflowLogs.map((log, index) => {
    const isLast = index === workflowLogs.length - 1;
    const operationType = log.operation_type;
    const icon = operationIcons[operationType] || <ClockCircleOutlined />;
    
    return {
      dot: (
        <Avatar 
          size="small" 
          icon={icon} 
          style={{ 
            backgroundColor: isLast ? '#1890ff' : '#f0f0f0',
            border: '2px solid #fff',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}
        />
      ),
      children: (
        <Card 
          size="small" 
          style={{ 
            marginBottom: '8px',
            border: isLast ? '1px solid #1890ff' : '1px solid #f0f0f0',
            backgroundColor: isLast ? '#f6ffed' : 'white'
          }}
        >
          <div style={{ marginBottom: '8px' }}>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {/* 操作标题 */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text strong style={{ color: isLast ? '#1890ff' : undefined }}>
                  {formatOperationType(operationType, log.from_step, log.to_step)}
                </Text>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {dayjs(log.created_at).format('MM-DD HH:mm')}
                </Text>
              </div>
              
              {/* 操作者信息 */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Avatar size="small" icon={<UserOutlined />} />
                <span>
                  <Text>{log.operator_name}</Text>
                  <Text type="secondary" style={{ marginLeft: '8px', fontSize: '12px' }}>
                    ({log.operator_role})
                  </Text>
                </span>
              </div>
              
              {/* 操作详情 */}
              {renderOperationDetails(log)}
            </Space>
          </div>
        </Card>
      ),
    };
  });

  return (
    <Card
      title={
        <Space>
          <HistoryOutlined />
          工作流历史记录
        </Space>
      }
      extra={
        <Button type="text" onClick={onClose}>
          关闭
        </Button>
      }
      style={{ 
        position: 'fixed',
        top: '10%',
        right: '20px',
        width: '400px',
        maxHeight: '80vh',
        overflowY: 'auto',
        zIndex: 1000,
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
      }}
    >
      <Spin spinning={loading}>
        {workflowLogs.length === 0 ? (
          <Empty 
            description="暂无工作流记录" 
            style={{ padding: '20px 0' }}
          />
        ) : (
          <div style={{ maxHeight: '60vh', overflowY: 'auto' }}>
            <Timeline items={timelineItems} />
            
            <Divider style={{ margin: '16px 0' }} />
            
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                共 {workflowLogs.length} 条记录
              </Text>
            </div>
          </div>
        )}
      </Spin>
    </Card>
  );
};

export default WorkflowHistory;