// frontend/src/pages/Contract/ContractOverview.tsx
/**
 * 合同清单总览页面
 * 显示所有项目的合同清单状态和统计信息
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Table,
  Space,
  Button,
  Input,
  Select,
  Statistic,
  Row,
  Col,
  Typography,
  message,
  Tooltip,
  Badge
} from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  EyeOutlined,
  UploadOutlined,
  BarChartOutlined,
  ProjectOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

import { Project } from '../../types/project';
import { ContractSummary } from '../../types/contract';
import { ProjectService } from '../../services/project';
import { getContractSummary } from '../../services/contract';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;

interface ProjectContractInfo extends Project {
  contract_summary?: ContractSummary;
  contract_status: 'uploaded' | 'not_uploaded' | 'loading';
  total_items?: number;
  total_amount?: number;
}

const ContractOverview: React.FC = () => {
  const [projects, setProjects] = useState<ProjectContractInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  
  // 统计数据
  const [statistics, setStatistics] = useState({
    total_projects: 0,
    uploaded_contracts: 0,
    total_contract_amount: '0',
    total_items: 0
  });

  // 获取项目列表和合同信息
  const fetchProjectsWithContracts = useCallback(async () => {
    setLoading(true);
    try {
      // 获取项目列表
      const projectResponse = await ProjectService.getProjects(1, 100);
      const projectList = projectResponse.items;
      
      // 初始化项目合同信息
      const projectsWithContracts: ProjectContractInfo[] = projectList.map(project => ({
        ...project,
        contract_status: 'loading'
      }));
      
      setProjects(projectsWithContracts);

      // 并行获取每个项目的合同信息
      const contractPromises = projectList.map(async (project) => {
        try {
          const summary = await getContractSummary(project.id);
          return {
            project_id: project.id,
            summary,
            status: 'uploaded' as const
          };
        } catch (error) {
          return {
            project_id: project.id,
            summary: null,
            status: 'not_uploaded' as const
          };
        }
      });

      const contractResults = await Promise.all(contractPromises);
      
      // 更新项目合同信息
      const updatedProjects = projectsWithContracts.map(project => {
        const contractInfo = contractResults.find(c => c.project_id === project.id);
        return {
          ...project,
          contract_summary: contractInfo?.summary || undefined,
          contract_status: contractInfo?.status || 'not_uploaded',
          total_items: contractInfo?.summary?.total_items || 0,
          total_amount: contractInfo?.summary?.total_amount || 0
        };
      });

      setProjects(updatedProjects);

      // 计算统计数据
      const uploadedCount = updatedProjects.filter(p => p.contract_status === 'uploaded').length;
      const totalAmount = updatedProjects
        .filter(p => p.contract_summary?.total_amount)
        .reduce((sum, p) => sum + (p.contract_summary!.total_amount || 0), 0);
      const totalItems = updatedProjects
        .reduce((sum, p) => sum + (p.total_items || 0), 0);

      setStatistics({
        total_projects: projectList.length,
        uploaded_contracts: uploadedCount,
        total_contract_amount: totalAmount.toFixed(2),
        total_items: totalItems
      });

    } catch (error) {
      message.error('获取项目合同信息失败');
      console.error('Error fetching projects with contracts:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjectsWithContracts();
  }, [fetchProjectsWithContracts]);

  // 过滤项目数据
  const filteredProjects = projects.filter(project => {
    const matchSearch = !searchText || 
      project.project_name.toLowerCase().includes(searchText.toLowerCase()) ||
      project.project_code.toLowerCase().includes(searchText.toLowerCase());
    
    const matchStatus = !statusFilter || project.contract_status === statusFilter;
    
    return matchSearch && matchStatus;
  });

  // 跳转到项目合同详情
  const handleViewContract = (project: ProjectContractInfo) => {
    // 这里可以打开项目的合同管理页面
    // 暂时显示消息，后续可以实现路由跳转或Modal
    if (project.contract_status === 'uploaded') {
      message.info(`查看项目 "${project.project_name}" 的合同清单`);
    } else {
      message.warning(`项目 "${project.project_name}" 尚未上传合同清单`);
    }
  };

  // 表格列定义
  const columns: ColumnsType<ProjectContractInfo> = [
    {
      title: '项目信息',
      key: 'project',
      width: 300,
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 500, fontSize: '14px' }}>
            {record.project_name}
          </div>
          <div style={{ color: '#666', fontSize: '12px' }}>
            {record.project_code}
          </div>
          <div style={{ color: '#666', fontSize: '12px' }}>
            {record.project_manager && `项目经理: ${record.project_manager}`}
          </div>
        </div>
      ),
    },
    {
      title: '合同状态',
      dataIndex: 'contract_status',
      key: 'contract_status',
      width: 120,
      render: (status) => {
        if (status === 'loading') {
          return <Badge status="processing" text="加载中" />;
        }
        return status === 'uploaded' 
          ? <Badge status="success" text="已上传" />
          : <Badge status="default" text="未上传" />;
      },
    },
    {
      title: '设备数量',
      dataIndex: 'total_items',
      key: 'total_items',
      width: 100,
      render: (count) => count ? `${count} 项` : '-',
    },
    {
      title: '合同金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 150,
      render: (amount) => amount && amount !== 0 ? `¥${amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}` : '-',
    },
    {
      title: '上传时间',
      key: 'upload_time',
      width: 120,
      render: (_, record) => {
        if (record.contract_summary?.current_version) {
          return new Date(record.contract_summary.current_version.upload_time).toLocaleDateString();
        }
        return '-';
      },
    },
    {
      title: '当前版本',
      key: 'current_version',
      width: 100,
      render: (_, record) => {
        if (record.contract_summary?.current_version) {
          return `v${record.contract_summary.current_version.version_number}`;
        }
        return '-';
      },
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Tooltip title="查看合同详情">
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewContract(record)}
              disabled={record.contract_status === 'loading'}
            >
              查看
            </Button>
          </Tooltip>
          {record.contract_status === 'not_uploaded' && (
            <Tooltip title="上传合同清单">
              <Button
                size="small"
                icon={<UploadOutlined />}
                type="primary"
                onClick={() => handleViewContract(record)}
              >
                上传
              </Button>
            </Tooltip>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <FileTextOutlined style={{ marginRight: '8px' }} />
          合同清单总览
        </Title>
        <Text type="secondary">
          查看所有项目的合同清单状态，管理合同信息和版本
        </Text>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="项目总数"
              value={statistics.total_projects}
              prefix={<ProjectOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已上传合同"
              value={statistics.uploaded_contracts}
              prefix={<FileTextOutlined />}
              suffix={`/ ${statistics.total_projects}`}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="合同总金额"
              value={parseFloat(statistics.total_contract_amount)}
              prefix="¥"
              precision={2}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="设备总数"
              value={statistics.total_items}
              prefix={<BarChartOutlined />}
              suffix="项"
            />
          </Card>
        </Col>
      </Row>

      {/* 搜索和过滤 */}
      <Card style={{ marginBottom: '16px' }}>
        <Space size="middle">
          <Search
            placeholder="搜索项目名称或编号"
            allowClear
            style={{ width: 300 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            prefix={<SearchOutlined />}
          />
          <Select
            placeholder="筛选合同状态"
            allowClear
            style={{ width: 150 }}
            value={statusFilter}
            onChange={setStatusFilter}
          >
            <Option value="uploaded">已上传</Option>
            <Option value="not_uploaded">未上传</Option>
          </Select>
          <Button
            icon={<SearchOutlined />}
            onClick={fetchProjectsWithContracts}
          >
            刷新
          </Button>
        </Space>
      </Card>

      {/* 项目列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredProjects}
          rowKey="id"
          loading={loading}
          pagination={{
            total: filteredProjects.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个项目`,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};

export default ContractOverview;