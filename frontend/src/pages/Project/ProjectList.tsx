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
  message,
  Typography,
  Row,
  Col,
  Statistic,
  Alert,
  Modal
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { Project, ProjectStatus, PROJECT_STATUS_CONFIG } from '../../types/project';
import { ProjectService } from '../../services/project';
import { useConnection } from '../../contexts/ConnectionContext';
import CreateProjectModal from '../../components/CreateProjectModal';
import EditProjectModal from '../../components/EditProjectModal';
import ProjectFileManager from '../../components/ProjectFileManager';
import ContractManagement from '../Contract/ContractManagement';
import { getProjectListColumns } from './ProjectListColumns';

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
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingProjectId, setEditingProjectId] = useState<number | null>(null);
  const [fileManagerVisible, setFileManagerVisible] = useState(false);
  const [fileManagerProject, setFileManagerProject] = useState<Project | null>(null);
  const [contractManagementVisible, setContractManagementVisible] = useState(false);
  const [contractManagementProject, setContractManagementProject] = useState<Project | null>(null);

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

  // 处理新建项目成功
  const handleCreateSuccess = (newProject: Project) => {
    message.success(`项目 "${newProject.project_name}" 已添加到列表`);
    fetchProjects(); // 刷新项目列表
  };

  // 处理编辑项目
  const handleEdit = (project: Project) => {
    setEditingProjectId(project.id);
    setEditModalVisible(true);
  };

  // 处理编辑项目成功
  const handleEditSuccess = (updatedProject: Project) => {
    message.success(`项目 "${updatedProject.project_name}" 更新成功`);
    fetchProjects(); // 刷新项目列表
  };

  // 处理文件管理
  const handleFileManager = (project: Project) => {
    setFileManagerProject(project);
    setFileManagerVisible(true);
  };

  // 处理合同清单管理
  const handleContractManagement = (project: Project) => {
    setContractManagementProject(project);
    setContractManagementVisible(true);
  };

  // 表格列定义
  const columns = getProjectListColumns({
    onContractManagement: handleContractManagement,
    onFileManager: handleFileManager,
    onEdit: handleEdit,
    onDelete: handleDelete,
  });

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
            onClick={() => setCreateModalVisible(true)}
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

      {/* 新建项目弹窗 */}
      <CreateProjectModal
        visible={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        onSuccess={handleCreateSuccess}
      />

      {/* 编辑项目弹窗 */}
      <EditProjectModal
        visible={editModalVisible}
        projectId={editingProjectId}
        onCancel={() => {
          setEditModalVisible(false);
          setEditingProjectId(null);
        }}
        onSuccess={handleEditSuccess}
      />

      {/* 文件管理弹窗 */}
      {fileManagerProject && (
        <ProjectFileManager
          projectId={fileManagerProject.id}
          projectName={fileManagerProject.project_name}
          visible={fileManagerVisible}
          onCancel={() => {
            setFileManagerVisible(false);
            setFileManagerProject(null);
          }}
        />
      )}

      {/* 合同清单管理弹窗 */}
      {contractManagementProject && (
        <Modal
          title={`合同清单管理 - ${contractManagementProject.project_name}`}
          open={contractManagementVisible}
          onCancel={() => {
            setContractManagementVisible(false);
            setContractManagementProject(null);
          }}
          footer={null}
          width="90%"
          style={{ top: 20 }}
        >
          <ContractManagement projectId={contractManagementProject.id} />
        </Modal>
      )}
    </div>
  );
};

export default ProjectList;
