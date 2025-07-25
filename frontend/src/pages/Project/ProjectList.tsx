// frontend/src/pages/Project/ProjectList.tsx
/**
 * 项目列表页面组件
 * 显示所有项目的列表，支持搜索、筛选、分页
 */

import React, { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Progress,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Statistic,
  Alert
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { Project, ProjectStatus, PROJECT_STATUS_CONFIG } from '../../types/project';
import { ProjectService } from '../../services/project';
import { useConnection } from '../../contexts/ConnectionContext';

const { Title } = Typography;
const { Option } = Select;

const ProjectList: React.FC = () => {
  const { setStatus } = useConnection(); // 获取连接状态设置函数
  // 状态管理
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [connectionError, setConnectionError] = useState<string>('');

  // 获取项目列表数据
  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await ProjectService.getProjects(
        currentPage,
        pageSize,
        searchText || undefined,
        statusFilter || undefined
      );
      setProjects(response.items);
      setTotal(response.total);
      setConnectionError(''); // 清除错误信息
    } catch (error) {
      message.error('获取项目列表失败');
      setConnectionError('无法连接到后端服务，请检查后端是否正常运行');
      setStatus('disconnected'); // 同时更新全局连接状态
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  // 组件挂载时获取数据
  useEffect(() => {
    fetchProjects();
  }, [currentPage, pageSize, searchText, statusFilter]);

  // 删除项目
  const handleDelete = async (id: number, name: string) => {
    try {
      await ProjectService.deleteProject(id);
      message.success(`项目 "${name}" 删除成功`);
      fetchProjects(); // 重新获取列表
    } catch (error) {
      message.error('删除项目失败');
    }
  };

  // 格式化金额显示
  const formatAmount = (amount?: number) => {
    if (!amount) return '-';
    return `¥${amount.toLocaleString()}`;
  };

  // 格式化日期显示
  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  // 表格列定义
  const columns: ColumnsType<Project> = [
    {
      title: '项目编号',
      dataIndex: 'project_code',
      key: 'project_code',
      width: 120,
      fixed: 'left',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: '项目名称',
      dataIndex: 'project_name',
      key: 'project_name',
      width: 200,
      ellipsis: true,
    },
    {
      title: '合同金额',
      dataIndex: 'contract_amount',
      key: 'contract_amount',
      width: 120,
      render: formatAmount,
      sorter: (a, b) => (a.contract_amount || 0) - (b.contract_amount || 0),
    },
    {
      title: '项目经理',
      dataIndex: 'project_manager',
      key: 'project_manager',
      width: 100,
      render: (text) => text || '-'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: ProjectStatus) => {
        const config = PROJECT_STATUS_CONFIG[status];
        return (
          <Tag color={config.color}>
            {config.icon} {config.text}
          </Tag>
        );
      }
    },
    {
      title: '整体进度',
      dataIndex: 'overall_progress',
      key: 'overall_progress',
      width: 120,
      render: (progress: number) => (
        <Progress 
          percent={Number(progress) || 0} 
          size="small" 
          format={(percent) => `${percent}%`}
        />
      )
    },
    {
      title: '开始日期',
      dataIndex: 'start_date',
      key: 'start_date',
      width: 110,
      render: formatDate
    },
    {
      title: '结束日期',
      dataIndex: 'end_date',
      key: 'end_date',
      width: 110,
      render: formatDate
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            size="small"
            onClick={() => message.info('查看详情功能开发中...')}
          >
            查看
          </Button>
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            size="small"
            onClick={() => message.info('编辑功能开发中...')}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个项目吗？"
            description={`项目：${record.project_name}`}
            onConfirm={() => handleDelete(record.id, record.project_name)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              type="link" 
              danger 
              icon={<DeleteOutlined />} 
              size="small"
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 计算统计数据
  const stats = {
    total: projects.length,
    planning: projects.filter(p => p.status === ProjectStatus.PLANNING).length,
    inProgress: projects.filter(p => p.status === ProjectStatus.IN_PROGRESS).length,
    completed: projects.filter(p => p.status === ProjectStatus.COMPLETED).length,
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* 页面标题 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            📋 项目管理
          </Title>
        </Col>
        <Col>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => message.info('新建项目功能开发中...')}
          >
            新建项目
          </Button>
        </Col>
      </Row>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic title="总项目数" value={stats.total} prefix="📊" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="规划中" value={stats.planning} prefix="📋" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="进行中" value={stats.inProgress} prefix="🚀" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="已完成" value={stats.completed} prefix="✅" />
          </Card>
        </Col>
      </Row>

      {/* 连接错误提示 */}
      {connectionError && (
        <Alert
          message="后端连接失败"
          description={connectionError}
          type="error"
          showIcon
          closable
          style={{ marginBottom: '24px' }}
          action={
            <Button size="small" onClick={fetchProjects}>
              重试连接
            </Button>
          }
        />
      )}

      {/* 搜索和筛选 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={16}>
          <Col span={8}>
            <Input
              placeholder="搜索项目名称或编号"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              allowClear
            />
          </Col>
          <Col span={6}>
            <Select
              placeholder="选择状态"
              value={statusFilter}
              onChange={setStatusFilter}
              allowClear
              style={{ width: '100%' }}
            >
              {Object.entries(PROJECT_STATUS_CONFIG).map(([key, config]) => (
                <Option key={key} value={key}>
                  {config.icon} {config.text}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Button onClick={fetchProjects}>刷新</Button>
          </Col>
        </Row>
      </Card>

      {/* 项目列表表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={projects}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size);
            }
          }}
        />
      </Card>
    </div>
  );
};

export default ProjectList;