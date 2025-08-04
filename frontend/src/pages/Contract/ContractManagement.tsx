// frontend/src/pages/Contract/ContractManagement.tsx
/**
 * 合同清单管理主页面
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Tabs,
  Button,
  Typography,
  Statistic,
  Row,
  Col,
  message,
  Spin,
  Alert
} from 'antd';
import {
  FileTextOutlined,
  UploadOutlined,
  UnorderedListOutlined,
  BarChartOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';

import { ContractSummary } from '../../types/contract';
import { getContractSummary } from '../../services/contract';
import { formatAmount } from '../../services/contract';
import ContractFileUpload from '../../components/Contract/ContractFileUpload';
import ContractItemList from '../../components/Contract/ContractItemList';
import ContractVersionList from '../../components/Contract/ContractVersionList';

const { Title } = Typography;
const { TabPane } = Tabs;

interface ContractManagementProps {
  projectId?: number;
}

const ContractManagement: React.FC<ContractManagementProps> = ({ projectId: propProjectId }) => {
  const { projectId: urlProjectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  // React Hooks必须在所有条件语句之前声明
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<ContractSummary | null>(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [refreshKey, setRefreshKey] = useState(0);

  // 优先使用props传入的projectId，如果没有则使用URL参数
  const projectId = propProjectId || (urlProjectId ? parseInt(urlProjectId, 10) : null);
  
  // 判断是否为独立页面模式（通过URL访问）
  const isStandalonePage = !propProjectId && urlProjectId;
  
  // 加载汇总信息
  const loadSummary = useCallback(async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      console.log(`开始加载项目 ${projectId} 的合同清单汇总...`);
      const summaryData = await getContractSummary(projectId);
      console.log('=== 合同清单汇总数据 ===');
      console.log('summaryData:', summaryData);
      console.log('current_version:', summaryData?.current_version);
      console.log('current_version.id:', summaryData?.current_version?.id);
      console.log('total_items:', summaryData?.total_items);
      setSummary(summaryData);
    } catch (error) {
      console.error('加载合同清单汇总失败:', error);
      message.error('加载合同清单汇总失败');
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }, [projectId]);
  
  // 刷新数据
  const handleRefresh = useCallback(() => {
    setRefreshKey(prev => prev + 1);
    loadSummary();
  }, [loadSummary]);

  // 文件上传成功回调
  const handleUploadSuccess = useCallback(() => {
    message.success('文件上传成功！');
    handleRefresh();
    setActiveTab('items'); // 切换到设备清单页面
  }, [handleRefresh]);

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);
  
  if (!projectId) {
    return (
      <Card style={{ margin: '24px' }}>
        <Alert
          message="缺少项目ID"
          description="无法加载合同清单信息，请检查项目ID是否正确。"
          type="error"
        />
      </Card>
    );
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>加载合同清单信息...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: 24 }}>
        {isStandalonePage && (
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/contracts')}
            style={{ marginBottom: 16 }}
          >
            返回合同总览
          </Button>
        )}
        <Title level={2}>
          <FileTextOutlined style={{ marginRight: 8 }} />
          合同清单管理
        </Title>
      </div>

      {/* 汇总信息卡片 */}
      {summary && (
        <Card style={{ marginBottom: 24 }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={6}>
              <Statistic
                title="合同版本数"
                value={summary.total_versions}
                prefix={<FileTextOutlined />}
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic
                title="系统分类数"
                value={summary.total_categories}
                prefix={<UnorderedListOutlined />}
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic
                title="设备明细数"
                value={summary.total_items}
                prefix={<BarChartOutlined />}
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic
                title="合同总金额"
                value={summary.total_amount || 0}
                formatter={(value) => formatAmount(Number(value))}
                precision={2}
              />
            </Col>
          </Row>

          {summary.current_version && (
            <Alert
              style={{ marginTop: 16 }}
              message={`当前版本: v${summary.current_version.version_number}`}
              description={
                <div>
                  <div>文件: {summary.current_version.original_filename}</div>
                  <div>上传人: {summary.current_version.upload_user_name}</div>
                  <div>上传时间: {new Date(summary.current_version.upload_time).toLocaleString()}</div>
                </div>
              }
              type="info"
              showIcon
            />
          )}

          {summary.total_versions === 0 && (
            <Alert
              style={{ marginTop: 16 }}
              message="暂无合同清单"
              description="请先上传Excel格式的投标清单文件"
              type="warning"
              showIcon
            />
          )}
        </Card>
      )}

      {/* 功能标签页 */}
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          tabBarExtraContent={
            <Button type="primary" onClick={handleRefresh}>
              刷新
            </Button>
          }
        >
          <TabPane
            tab={
              <span>
                <UploadOutlined />
                文件上传
              </span>
            }
            key="upload"
          >
            <ContractFileUpload
              projectId={projectId}
              onUploadSuccess={handleUploadSuccess}
            />
          </TabPane>

          <TabPane
            tab={
              <span>
                <UnorderedListOutlined />
                设备清单
              </span>
            }
            key="items"
          >
            <ContractItemList
              projectId={projectId}
              currentVersion={summary?.current_version}
              refreshKey={refreshKey}
            />
          </TabPane>

          <TabPane
            tab={
              <span>
                <FileTextOutlined />
                版本管理
              </span>
            }
            key="versions"
          >
            <ContractVersionList
              projectId={projectId}
              refreshKey={refreshKey}
              onRefresh={handleRefresh}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default ContractManagement;