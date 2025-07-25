import React, { useState, useEffect } from 'react';
import { Card, Button, Space, Table, message, Typography, Row, Col } from 'antd';
import { ReloadOutlined, PlusOutlined, ApiOutlined } from '@ant-design/icons';
import './App.css';

const { Title, Text } = Typography;

// 类型定义
interface Project {
  id: string;
  name: string;
  status: string;
  progress: number;
  manager: string;
  budget: number;
}

interface SystemStats {
  total_projects: number;
  completed_projects: number;
  ongoing_projects: number;
  delayed_projects: number;
}

function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<SystemStats>({
    total_projects: 0,
    completed_projects: 0,
    ongoing_projects: 0,
    delayed_projects: 0
  });
  const [loading, setLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  // API基础URL
  const API_BASE = 'http://localhost:8000/api';

  // 获取项目列表
  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/projects`);
      if (response.ok) {
        const data = await response.json();
        setProjects(data);
      } else {
        message.error('获取项目列表失败');
      }
    } catch (error) {
      message.error('无法连接到后端服务器');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取统计数据
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // 测试后端连接
  const testConnection = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      if (data.status === 'healthy') {
        setIsConnected(true);
        message.success('后端连接成功！');
        return true;
      }
    } catch (error) {
      setIsConnected(false);
      message.error('无法连接到后端服务器');
      return false;
    }
  };

  // 页面加载时获取数据
  useEffect(() => {
    const initData = async () => {
      const connected = await testConnection();
      if (connected) {
        fetchProjects();
        fetchStats();
      }
    };
    initData();
  }, []);

  // 简化的表格列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      render: (text: string, record: any, index: number) => index + 1,
    },
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: { [key: string]: { text: string; color: string } } = {
          planning: { text: '规划中', color: '#108ee9' },
          ongoing: { text: '进行中', color: '#1890ff' },
          completed: { text: '已完成', color: '#52c41a' },
          delayed: { text: '已延期', color: '#f5222d' },
        };
        const statusInfo = statusMap[status] || { text: status, color: '#999' };
        return (
          <span style={{ 
            color: statusInfo.color, 
            fontWeight: 'bold',
          }}>
            {statusInfo.text}
          </span>
        );
      },
    },
  ];

  return (
    <div className="modern-app">
      {/* 顶部导航栏 */}
      <div className="top-header">
        <div className="header-content">
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            弱电工程ERP系统
          </Title>
          <span style={{ color: '#8892b0', marginLeft: '10px' }}>
            V62版本
          </span>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="main-content">
        
        {/* 欢迎横幅 */}
        <div className="welcome-banner">
          <div className="banner-content">
            <Title level={2} style={{ color: 'white', textAlign: 'center', marginBottom: '10px' }}>
              欢迎使用弱电工程ERP系统！
            </Title>
            <Text style={{ color: '#a0a9c0', textAlign: 'center', display: 'block' }}>
              基于V62开发文档的现代化企业资源计划系统
            </Text>
          </div>
        </div>

        {/* 系统状态检查 */}
        <Card className="status-card" title="系统状态检查">
          <div className="status-item">
            <Text strong>后端服务状态：</Text>
            <span className={`status-badge ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? '已连接' : '未连接'}
            </span>
          </div>
          <div className="status-item" style={{ marginTop: '10px' }}>
            <Text>后端地址：http://localhost:8000</Text>
          </div>
          <div style={{ marginTop: '20px' }}>
            <Space>
              <Button 
                type="primary" 
                icon={<ReloadOutlined />}
                onClick={() => {
                  testConnection();
                  fetchProjects();
                  fetchStats();
                }}
              >
                测试后端连接
              </Button>
              <Button 
                icon={<ApiOutlined />}
                onClick={() => window.open('http://localhost:8000/docs', '_blank')}
              >
                访问项目数据
              </Button>
            </Space>
          </div>
        </Card>

        {/* 项目管理 */}
        <Card 
          className="project-card" 
          title="项目管理"
          extra={<Text style={{ color: '#666' }}>共 {stats.total_projects} 个项目</Text>}
        >
          <Table 
            columns={columns} 
            dataSource={projects}
            rowKey="id"
            loading={loading}
            pagination={false}
            size="middle"
            showHeader={true}
          />
        </Card>

        {/* 底部信息 */}
        <div className="footer">
          <Text style={{ color: '#8892b0' }}>
            弱电工程ERP系统 ©2025 基于V62开发文档 | 前端React + 后端FastAPI
          </Text>
        </div>

      </div>
    </div>
  );
}

export default App;