import React from 'react';
import { Tag, Steps, Space, Tooltip } from 'antd';
import { 
  EditOutlined, 
  DollarOutlined, 
  CheckCircleOutlined, 
  CrownOutlined,
  ClockCircleOutlined 
} from '@ant-design/icons';

// 工作流状态类型定义
export type PurchaseStatus = 
  | 'draft' 
  | 'submitted' 
  | 'price_quoted' 
  | 'dept_approved' 
  | 'final_approved' 
  | 'rejected' 
  | 'cancelled' 
  | 'completed';

export type WorkflowStep = 
  | 'project_manager' 
  | 'purchaser' 
  | 'dept_manager' 
  | 'general_manager' 
  | 'completed';

interface WorkflowStatusProps {
  status: PurchaseStatus;
  currentStep?: WorkflowStep;
  showSteps?: boolean;
  size?: 'small' | 'default';
}

// 状态配置
const statusConfig = {
  draft: { 
    color: 'default', 
    text: '草稿', 
    icon: <EditOutlined /> 
  },
  submitted: { 
    color: 'processing', 
    text: '已提交', 
    icon: <ClockCircleOutlined /> 
  },
  price_quoted: { 
    color: 'warning', 
    text: '已询价', 
    icon: <DollarOutlined /> 
  },
  dept_approved: { 
    color: 'blue', 
    text: '部门已批', 
    icon: <CheckCircleOutlined /> 
  },
  final_approved: { 
    color: 'success', 
    text: '最终批准', 
    icon: <CrownOutlined /> 
  },
  rejected: { 
    color: 'error', 
    text: '已拒绝', 
    icon: <ClockCircleOutlined /> 
  },
  cancelled: { 
    color: 'default', 
    text: '已取消', 
    icon: <ClockCircleOutlined /> 
  },
  completed: { 
    color: 'success', 
    text: '已完成', 
    icon: <CheckCircleOutlined /> 
  }
};

// 工作流步骤配置
const stepConfig = {
  project_manager: { title: '项目经理', icon: <EditOutlined /> },
  purchaser: { title: '采购员', icon: <DollarOutlined /> },
  dept_manager: { title: '部门主管', icon: <CheckCircleOutlined /> },
  general_manager: { title: '总经理', icon: <CrownOutlined /> },
  completed: { title: '完成', icon: <CheckCircleOutlined /> }
};

// 根据状态确定当前步骤索引
const getStepIndex = (status: PurchaseStatus, currentStep?: WorkflowStep): number => {
  if (status === 'rejected' || status === 'cancelled') {
    return -1; // 特殊状态
  }
  
  const stepOrder = ['project_manager', 'purchaser', 'dept_manager', 'general_manager', 'completed'];
  
  if (currentStep) {
    return stepOrder.indexOf(currentStep);
  }
  
  // 根据状态推断步骤
  switch (status) {
    case 'draft': return 0;
    case 'submitted': return 1;
    case 'price_quoted': return 2;
    case 'dept_approved': return 3;
    case 'final_approved':
    case 'completed': return 4;
    default: return 0;
  }
};

const WorkflowStatus: React.FC<WorkflowStatusProps> = ({ 
  status, 
  currentStep, 
  showSteps = false, 
  size = 'default' 
}) => {
  const config = statusConfig[status];
  
  if (!showSteps) {
    // 简单标签显示 - 增强版本
    const tooltipTitle = (
      <div>
        <div><strong>状态:</strong> {config.text}</div>
        {currentStep && (
          <div><strong>当前步骤:</strong> {stepConfig[currentStep]?.title}</div>
        )}
        <div style={{ fontSize: '11px', opacity: 0.8, marginTop: '4px' }}>
          点击查看详细工作流程
        </div>
      </div>
    );

    return (
      <Tooltip title={tooltipTitle} overlayStyle={{ maxWidth: '200px' }}>
        <Tag 
          color={config.color} 
          icon={config.icon}
          style={{ 
            margin: 0,
            cursor: 'pointer',
            fontSize: size === 'small' ? '12px' : '13px',
            padding: size === 'small' ? '2px 6px' : '4px 8px'
          }}
        >
          {config.text}
          {currentStep && status !== 'draft' && (
            <span style={{ marginLeft: '4px', opacity: 0.7 }}>
              · {stepConfig[currentStep]?.title}
            </span>
          )}
        </Tag>
      </Tooltip>
    );
  }
  
  // 步骤条显示
  const stepIndex = getStepIndex(status, currentStep);
  const isError = status === 'rejected' || status === 'cancelled';
  
  const steps = Object.entries(stepConfig).map(([key, stepConf], index) => {
    let stepStatus: 'wait' | 'process' | 'finish' | 'error' = 'wait';
    let description = '';
    
    if (isError) {
      stepStatus = index <= stepIndex ? 'error' : 'wait';
      description = index <= stepIndex ? '已终止' : '未执行';
    } else {
      if (index < stepIndex) {
        stepStatus = 'finish';
        description = '已完成';
      } else if (index === stepIndex) {
        stepStatus = 'process';
        description = '进行中';
      } else {
        stepStatus = 'wait';
        description = '等待中';
      }
    }
    
    return {
      title: stepConf.title,
      description: description,
      icon: stepConf.icon,
      status: stepStatus
    };
  });
  
  return (
    <div style={{ width: '100%' }}>
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Tag color={config.color} icon={config.icon} style={{ fontSize: '13px' }}>
            {config.text}
          </Tag>
          {currentStep && (
            <Tag color="blue" style={{ fontSize: '12px' }}>
              当前: {stepConfig[currentStep]?.title}
            </Tag>
          )}
        </div>
        <div style={{ 
          background: '#fafafa', 
          padding: '16px', 
          borderRadius: '8px',
          border: '1px solid #f0f0f0'
        }}>
          <Steps
            size={size === 'small' ? 'small' : 'default'}
            current={stepIndex}
            status={isError ? 'error' : 'process'}
            items={steps}
            style={{ width: '100%' }}
          />
        </div>
      </Space>
    </div>
  );
};

export default WorkflowStatus;