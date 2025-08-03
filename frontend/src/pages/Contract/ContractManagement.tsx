// frontend/src/pages/Contract/ContractManagement.tsx
/**
 * 合同清单管理主页面
 */

import React, { useState, useEffect } from 'react';
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
  AppstoreOutlined
} from '@ant-design/icons';

import { ContractSummary } from '../../types/contract';
import { getContractSummary } from '../../services/contract';
import { formatAmount } from '../../services/contract';
import ContractFileUpload from '../../components/Contract/ContractFileUpload';
import ContractItemList from '../../components/Contract/ContractItemList';
import ContractVersionList from '../../components/Contract/ContractVersionList';
import SystemCategoryList from '../../components/Contract/SystemCategoryList';

const { Title } = Typography;
const { TabPane } = Tabs;

interface ContractManagementProps {
  projectId: number;
}

const ContractManagement: React.FC<ContractManagementProps> = ({ projectId }) => {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<ContractSummary | null>(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [refreshKey, setRefreshKey] = useState(0);

  // 加载汇总信息
  const loadSummary = async () => {
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
    } finally {
      setLoading(false);
    }
  };

  // 刷新数据
  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    loadSummary();
  };

  // 文件上传成功回调
  const handleUploadSuccess = () => {
    message.success('文件上传成功！');
    handleRefresh();
    setActiveTab('categories'); // 切换到系统分类页面，让用户了解文件结构
  };

  useEffect(() => {
    loadSummary();
  }, [projectId]);

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
                <AppstoreOutlined />
                系统分类
              </span>
            }
            key="categories"
          >
            <SystemCategoryList
              projectId={projectId}
              currentVersion={summary?.current_version}
              refreshKey={refreshKey}
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