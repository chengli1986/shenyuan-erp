/**
 * 系统测试仪表板页面
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Button, 
  Table, 
  Tag, 
  message,
  Space,
  Progress,
  Alert,
  Tooltip,
  Badge,
  Modal,
  Collapse,
  Typography,
  Select
} from 'antd';
import {
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  BugOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import 'dayjs/locale/zh-cn';
import { testService } from '../../services/test';
import { TestRun, LatestTestStatus } from '../../types/test';
import TestResultDetail from './TestResultDetail';
import TestStatisticsChart from './TestStatisticsChart';

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.locale('zh-cn');
// 设置默认时区为用户本地时区
dayjs.tz.setDefault(dayjs.tz.guess());

const { Panel } = Collapse;
const { Text } = Typography;

const SystemTestDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [latestStatus, setLatestStatus] = useState<LatestTestStatus | null>(null);
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [statisticsVisible, setStatisticsVisible] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [filters, setFilters] = useState({
    run_type: undefined as string | undefined,
    status: undefined as string | undefined,
    days: 7
  });

  // 加载测试运行列表
  const loadTestRuns = useCallback(async () => {
    setLoading(true);
    try {
      const response = await testService.getTestRuns({
        page: pagination.current,
        size: pagination.pageSize,
        ...filters
      });
      setTestRuns(response.items);
      setPagination(prev => ({
        ...prev,
        total: response.total
      }));
    } catch (error) {
      message.error('加载测试记录失败');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters]);

  // 加载最新状态
  const loadLatestStatus = useCallback(async () => {
    try {
      const status = await testService.getLatestTestStatus();
      setLatestStatus(status);
    } catch (error) {
      console.error('加载最新状态失败:', error);
    }
  }, []);

  // 触发测试 - 简化版本，直接触发不需要确认
  const triggerTest = useCallback(async (testType: 'all' | 'unit' | 'integration') => {
    console.log('触发测试:', testType);
    setRefreshing(true);
    try {
      const result = await testService.triggerTestRun(testType);
      console.log('测试触发结果:', result);
      message.success(result.message || '测试已触发');
      // 刷新列表
      await loadTestRuns();
      await loadLatestStatus();
    } catch (error: any) {
      console.error('触发测试失败:', error);
      message.error(error.response?.data?.detail || error.message || '触发测试失败');
    } finally {
      setRefreshing(false);
    }
  }, [loadTestRuns, loadLatestStatus]);

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      running: { color: 'processing', text: '运行中' },
      completed: { color: 'success', text: '已完成' },
      failed: { color: 'error', text: '失败' },
      passed: { color: 'success', text: '通过' },
      skipped: { color: 'warning', text: '跳过' },
      error: { color: 'error', text: '错误' }
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 获取运行类型标签
  const getRunTypeTag = (runType: string) => {
    return (
      <Tag color={runType === 'scheduled' ? 'blue' : 'green'}>
        {runType === 'scheduled' ? '定时执行' : '手动触发'}
      </Tag>
    );
  };

  useEffect(() => {
    loadTestRuns();
    loadLatestStatus();
  }, [loadTestRuns, loadLatestStatus]);

  const columns = [
    {
      title: '运行ID',
      dataIndex: 'run_id',
      key: 'run_id',
      width: 200,
      render: (text: string) => (
        <Button type="link" onClick={() => {
          setSelectedRun(text);
          setDetailModalVisible(true);
        }}>
          {text}
        </Button>
      )
    },
    {
      title: '运行类型',
      dataIndex: 'run_type',
      key: 'run_type',
      width: 100,
      render: getRunTypeTag
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: getStatusTag
    },
    {
      title: '测试统计',
      key: 'statistics',
      width: 300,
      render: (record: TestRun) => (
        <Space size="small">
          <Tooltip title="总数">
            <Badge count={record.total_tests} showZero style={{ backgroundColor: '#52c41a' }} />
          </Tooltip>
          <Tooltip title="通过">
            <Badge count={record.passed_tests} showZero style={{ backgroundColor: '#52c41a' }} />
          </Tooltip>
          <Tooltip title="失败">
            <Badge count={record.failed_tests} showZero style={{ backgroundColor: record.failed_tests > 0 ? '#f5222d' : '#d9d9d9' }} />
          </Tooltip>
          <Tooltip title="跳过">
            <Badge count={record.skipped_tests} showZero style={{ backgroundColor: record.skipped_tests > 0 ? '#faad14' : '#d9d9d9' }} />
          </Tooltip>
          <Progress
            percent={record.success_rate}
            size="small"
            style={{ width: 80 }}
            status={record.success_rate === 100 ? 'success' : record.success_rate < 80 ? 'exception' : 'normal'}
          />
        </Space>
      )
    },
    {
      title: '持续时间',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      render: (duration?: number) => duration ? `${duration.toFixed(2)}s` : '-'
    },
    {
      title: '触发人',
      dataIndex: 'trigger_user',
      key: 'trigger_user',
      width: 100
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 180,
      render: (time: string) => {
        // 将UTC时间转换为本地时间
        return dayjs.utc(time).local().format('YYYY-MM-DD HH:mm:ss');
      }
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 页面标题和操作按钮 */}
      <Card bordered={false} style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <h2 style={{ margin: 0 }}>
              <ExperimentOutlined /> 系统测试中心
            </h2>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<BarChartOutlined />}
                onClick={() => setStatisticsVisible(true)}
              >
                查看统计
              </Button>
              <Button
                icon={<PlayCircleOutlined />}
                type="primary"
                onClick={() => {
                  console.log('全部测试按钮点击');
                  triggerTest('all');
                }}
                loading={refreshing}
              >
                运行全部测试
              </Button>
              <Button
                icon={<PlayCircleOutlined />}
                onClick={() => {
                  console.log('单元测试按钮点击');
                  triggerTest('unit');
                }}
                loading={refreshing}
              >
                运行单元测试
              </Button>
              <Button
                icon={<PlayCircleOutlined />}
                onClick={() => {
                  console.log('集成测试按钮点击');
                  triggerTest('integration');
                }}
                loading={refreshing}
              >
                运行集成测试
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  loadTestRuns();
                  loadLatestStatus();
                }}
              >
                刷新
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 最新状态卡片 */}
      {latestStatus?.has_run && latestStatus.latest_run && (
        <Card bordered={false} style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="最新测试状态"
                value={
                  latestStatus.latest_run.status === 'completed' ? '已完成' :
                  latestStatus.latest_run.status === 'failed' ? '失败' :
                  latestStatus.latest_run.status === 'running' ? '运行中' : '未知'
                }
                prefix={
                  latestStatus.latest_run.status === 'completed' ? 
                    <CheckCircleOutlined style={{ color: '#52c41a' }} /> :
                  latestStatus.latest_run.status === 'failed' ?
                    <CloseCircleOutlined style={{ color: '#ff4d4f' }} /> :
                  latestStatus.latest_run.status === 'running' ?
                    <ClockCircleOutlined style={{ color: '#1890ff' }} /> :
                    <QuestionCircleOutlined style={{ color: '#8c8c8c' }} />
                }
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="成功率"
                value={latestStatus.latest_run.success_rate}
                suffix="%"
                valueStyle={{ 
                  color: latestStatus.latest_run.success_rate === 100 ? '#52c41a' : 
                         latestStatus.latest_run.success_rate < 80 ? '#f5222d' : '#faad14'
                }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="测试总数"
                value={latestStatus.latest_run.total_tests}
                prefix={<ExperimentOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="失败数量"
                value={latestStatus.latest_run.failed_tests}
                prefix={<BugOutlined />}
                valueStyle={{ color: latestStatus.latest_run.failed_tests > 0 ? '#f5222d' : '#52c41a' }}
              />
            </Col>
          </Row>

          {/* 失败测试提示 */}
          {latestStatus.failed_tests && latestStatus.failed_tests.length > 0 && (
            <Alert
              message="存在失败的测试"
              description={
                <Collapse ghost size="small">
                  <Panel header={`查看失败详情 (${latestStatus.failed_tests.length}个)`} key="1">
                    {latestStatus.failed_tests.map((test, index) => (
                      <div key={index} style={{ marginBottom: 8 }}>
                        <Text code>{test.test_suite}.{test.test_name}</Text>
                        <br />
                        <Text type="danger" style={{ fontSize: 12 }}>
                          {test.error_message}
                        </Text>
                      </div>
                    ))}
                  </Panel>
                </Collapse>
              }
              type="error"
              showIcon
              style={{ marginTop: 16 }}
            />
          )}
        </Card>
      )}

      {/* 筛选器 */}
      <Card bordered={false} style={{ marginBottom: 16 }}>
        <Space>
          <Select
            placeholder="运行类型"
            style={{ width: 120 }}
            allowClear
            value={filters.run_type}
            onChange={(value) => setFilters(prev => ({ ...prev, run_type: value }))}
          >
            <Select.Option value="scheduled">定时执行</Select.Option>
            <Select.Option value="manual">手动触发</Select.Option>
          </Select>
          <Select
            placeholder="运行状态"
            style={{ width: 120 }}
            allowClear
            value={filters.status}
            onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
          >
            <Select.Option value="running">运行中</Select.Option>
            <Select.Option value="completed">已完成</Select.Option>
            <Select.Option value="failed">失败</Select.Option>
          </Select>
          <Select
            value={filters.days}
            style={{ width: 120 }}
            onChange={(value) => setFilters(prev => ({ ...prev, days: value }))}
          >
            <Select.Option value={1}>最近1天</Select.Option>
            <Select.Option value={7}>最近7天</Select.Option>
            <Select.Option value={30}>最近30天</Select.Option>
            <Select.Option value={90}>最近90天</Select.Option>
          </Select>
        </Space>
      </Card>

      {/* 测试运行列表 */}
      <Card bordered={false}>
        <Table
          loading={loading}
          dataSource={testRuns}
          columns={columns}
          rowKey="run_id"
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              setPagination(prev => ({
                ...prev,
                current: page,
                pageSize: pageSize || prev.pageSize
              }));
            }
          }}
        />
      </Card>

      {/* 测试详情弹窗 */}
      <TestResultDetail
        visible={detailModalVisible}
        runId={selectedRun}
        onClose={() => {
          setDetailModalVisible(false);
          setSelectedRun(null);
        }}
      />

      {/* 统计图表弹窗 */}
      <TestStatisticsChart
        visible={statisticsVisible}
        onClose={() => setStatisticsVisible(false)}
      />
    </div>
  );
};

export default SystemTestDashboard;