/**
 * 系统测试仪表板页面
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Table,
  message,
  Space,
  Select
} from 'antd';
import {
  PlayCircleOutlined,
  ReloadOutlined,
  ExperimentOutlined,
  BarChartOutlined,
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
import { getTestRunColumns, LatestStatusCard } from './SystemTestDashboardColumns';

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.locale('zh-cn');
// 设置默认时区为用户本地时区
dayjs.tz.setDefault(dayjs.tz.guess());

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
    setRefreshing(true);
    try {
      const result = await testService.triggerTestRun(testType);
      message.success(result.message || '测试已触发');
      // 刷新列表
      await loadTestRuns();
      await loadLatestStatus();
    } catch (error: unknown) {
      console.error('触发测试失败:', error);
      message.error(error instanceof Error ? error.message : '触发测试失败');
    } finally {
      setRefreshing(false);
    }
  }, [loadTestRuns, loadLatestStatus]);

  useEffect(() => {
    loadTestRuns();
    loadLatestStatus();
  }, [loadTestRuns, loadLatestStatus]);

  // 表格列定义
  const columns = getTestRunColumns({
    onViewDetail: (runId) => {
      setSelectedRun(runId);
      setDetailModalVisible(true);
    },
  });

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
                onClick={() => triggerTest('all')}
                loading={refreshing}
              >
                运行全部测试
              </Button>
              <Button
                icon={<PlayCircleOutlined />}
                onClick={() => triggerTest('unit')}
                loading={refreshing}
              >
                运行单元测试
              </Button>
              <Button
                icon={<PlayCircleOutlined />}
                onClick={() => triggerTest('integration')}
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
      {latestStatus && <LatestStatusCard latestStatus={latestStatus} />}

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
