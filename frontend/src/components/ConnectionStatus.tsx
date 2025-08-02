// frontend/src/components/ConnectionStatus.tsx
/**
 * 后端连接状态检查组件
 * 实时监控后端API服务状态
 */

import React, { useEffect, useCallback } from 'react';
import { Badge, Tooltip, Space, Typography } from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  LoadingOutlined,
  WarningOutlined 
} from '@ant-design/icons';
import axios from 'axios';
import { useConnection } from '../contexts/ConnectionContext';
import { API_BASE_URL } from '../config/api';

const { Text } = Typography;

interface ConnectionStatusProps {
  showText?: boolean;  // 是否显示文字
  size?: 'small' | 'default';  // 修复：Badge只支持small和default
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  showText = true, 
  size = 'default' 
}) => {
  const { status, lastCheck, setStatus } = useConnection();

  // 检查后端连接状态
  const checkConnection = useCallback(async () => {
    try {
      setStatus('checking');
      
      // 调用后端健康检查接口
      const response = await axios.get(`${API_BASE_URL}/health`, {
        timeout: 3000, // 缩短到3秒超时，更快响应
      });
      
      if (response.status === 200) {
        setStatus('connected');
      } else {
        setStatus('error');
      }
    } catch (error) {
      console.warn('后端连接检查失败:', error);
      setStatus('disconnected');
    }
  }, [setStatus]);

  // 组件挂载时检查连接，然后每10秒检查一次
  useEffect(() => {
    checkConnection();
    
    const interval = setInterval(checkConnection, 10000); // 改为10秒检查一次，更及时
    
    return () => clearInterval(interval);
  }, [checkConnection]);

  // 状态配置
  const statusConfig = {
    checking: {
      color: 'blue',
      icon: <LoadingOutlined spin />,
      text: '检查中...',
      tooltip: '正在检查后端服务连接状态'
    },
    connected: {
      color: 'green',
      icon: <CheckCircleOutlined />,
      text: '已连接',
      tooltip: `后端服务正常运行\n最后检查: ${lastCheck.toLocaleTimeString()}`
    },
    disconnected: {
      color: 'red',
      icon: <CloseCircleOutlined />,
      text: '未连接',
      tooltip: `无法连接到后端服务\n请检查后端是否启动\n最后检查: ${lastCheck.toLocaleTimeString()}`
    },
    error: {
      color: 'orange',
      icon: <WarningOutlined />,
      text: '连接异常',
      tooltip: `后端服务响应异常\n最后检查: ${lastCheck.toLocaleTimeString()}`
    }
  };

  const config = statusConfig[status];

  return (
    <Tooltip 
      title={config.tooltip} 
      placement="bottomRight"
    >
      <Space 
        size={4} 
        style={{ cursor: 'pointer' }}
        onClick={checkConnection} // 点击手动检查
      >
        <Badge 
          color={config.color} 
          size={size === 'small' ? 'small' : 'default'}
        />
        {config.icon}
        {showText && (
          <Text 
            style={{ 
              fontSize: size === 'small' ? '12px' : '14px',
              color: config.color === 'green' ? '#52c41a' : 
                     config.color === 'red' ? '#ff4d4f' : 
                     config.color === 'orange' ? '#fa8c16' : '#1890ff'
            }}
          >
            {config.text}
          </Text>
        )}
      </Space>
    </Tooltip>
  );
};

export default ConnectionStatus;