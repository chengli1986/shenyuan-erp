/**
 * 系统测试仪表板 — 表格列定义、状态标签、最新状态卡片
 */

import React from 'react';
import {
  Button,
  Tag,
  Space,
  Progress,
  Tooltip,
  Badge,
  Card,
  Row,
  Col,
  Statistic,
  Alert,
  Collapse,
  Typography
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  ExperimentOutlined,
  BugOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { TestRun, LatestTestStatus } from '../../types/test';

const { Panel } = Collapse;
const { Text } = Typography;

// 获取状态标签
export const getStatusTag = (status: string) => {
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
export const getRunTypeTag = (runType: string) => {
  return (
    <Tag color={runType === 'scheduled' ? 'blue' : 'green'}>
      {runType === 'scheduled' ? '定时执行' : '手动触发'}
    </Tag>
  );
};

interface ColumnActions {
  onViewDetail: (runId: string) => void;
}

export function getTestRunColumns(actions: ColumnActions) {
  return [
    {
      title: '运行ID',
      dataIndex: 'run_id',
      key: 'run_id',
      width: 200,
      render: (text: string) => (
        <Button type="link" onClick={() => actions.onViewDetail(text)}>
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
}

// 最新状态卡片
interface LatestStatusCardProps {
  latestStatus: LatestTestStatus;
}

export const LatestStatusCard: React.FC<LatestStatusCardProps> = ({ latestStatus }) => {
  if (!latestStatus.has_run || !latestStatus.latest_run) return null;

  const run = latestStatus.latest_run;

  return (
    <Card bordered={false} style={{ marginBottom: 16 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Statistic
            title="最新测试状态"
            value={
              run.status === 'completed' ? '已完成' :
              run.status === 'failed' ? '失败' :
              run.status === 'running' ? '运行中' : '未知'
            }
            prefix={
              run.status === 'completed' ?
                <CheckCircleOutlined style={{ color: '#52c41a' }} /> :
              run.status === 'failed' ?
                <CloseCircleOutlined style={{ color: '#ff4d4f' }} /> :
              run.status === 'running' ?
                <ClockCircleOutlined style={{ color: '#1890ff' }} /> :
                <QuestionCircleOutlined style={{ color: '#8c8c8c' }} />
            }
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="成功率"
            value={run.success_rate}
            suffix="%"
            valueStyle={{
              color: run.success_rate === 100 ? '#52c41a' :
                     run.success_rate < 80 ? '#f5222d' : '#faad14'
            }}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="测试总数"
            value={run.total_tests}
            prefix={<ExperimentOutlined />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="失败数量"
            value={run.failed_tests}
            prefix={<BugOutlined />}
            valueStyle={{ color: run.failed_tests > 0 ? '#f5222d' : '#52c41a' }}
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
  );
};
