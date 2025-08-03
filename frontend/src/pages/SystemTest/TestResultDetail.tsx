/**
 * 测试结果详情组件
 */

import React, { useState, useEffect } from 'react';
import {
  Modal,
  Descriptions,
  Table,
  Tag,
  Tabs,
  Card,
  Collapse,
  Typography,
  Space,
  Spin,
  Alert,
  Button,
  Tooltip
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  CodeOutlined,
  BugOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import { testService } from '../../services/test';
import { TestRun, TestResult, TestRunDetailResponse } from '../../types/test';

dayjs.extend(duration);
dayjs.extend(utc);
dayjs.extend(timezone);

const { TabPane } = Tabs;
const { Panel } = Collapse;
const { Text, Title, Paragraph } = Typography;

interface TestResultDetailProps {
  visible: boolean;
  runId: string | null;
  onClose: () => void;
}

const TestResultDetail: React.FC<TestResultDetailProps> = ({
  visible,
  runId,
  onClose
}) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<TestRunDetailResponse | null>(null);
  const [activeTab, setActiveTab] = useState('summary');

  // 加载测试详情
  const loadDetail = async () => {
    if (!runId) return;
    
    setLoading(true);
    try {
      const response = await testService.getTestRunDetail(runId);
      setData(response);
    } catch (error) {
      console.error('加载测试详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (visible && runId) {
      loadDetail();
      setActiveTab('summary');
    }
  }, [visible, runId]);

  // 获取状态图标
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <CloseCircleOutlined style={{ color: '#f5222d' }} />;
      case 'skipped':
        return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      case 'error':
        return <BugOutlined style={{ color: '#f5222d' }} />;
      default:
        return <ClockCircleOutlined />;
    }
  };

  // 渲染测试结果表格
  const renderTestResults = (results: TestResult[]) => {
    const columns = [
      {
        title: '测试名称',
        dataIndex: 'test_name',
        key: 'test_name',
        width: '40%',
        render: (text: string, record: TestResult) => (
          <Space>
            {getStatusIcon(record.status)}
            <Text>{text}</Text>
          </Space>
        )
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        width: 100,
        render: (status: string) => {
          const statusMap: Record<string, { color: string; text: string }> = {
            passed: { color: 'success', text: '通过' },
            failed: { color: 'error', text: '失败' },
            skipped: { color: 'warning', text: '跳过' },
            error: { color: 'error', text: '错误' }
          };
          const config = statusMap[status] || { color: 'default', text: status };
          return <Tag color={config.color}>{config.text}</Tag>;
        }
      },
      {
        title: '耗时',
        dataIndex: 'duration',
        key: 'duration',
        width: 100,
        render: (duration?: number) => duration ? `${duration.toFixed(3)}s` : '-'
      },
      {
        title: '错误信息',
        dataIndex: 'error_message',
        key: 'error_message',
        ellipsis: true,
        render: (text?: string) => text ? (
          <Tooltip title={text}>
            <Text type="danger" ellipsis>{text}</Text>
          </Tooltip>
        ) : '-'
      }
    ];

    return (
      <Table
        dataSource={results}
        columns={columns}
        rowKey="id"
        size="small"
        pagination={false}
        expandable={{
          expandedRowRender: (record: TestResult) => {
            if (!record.error_message && !record.stack_trace) return null;
            return (
              <div style={{ padding: '8px 0' }}>
                {record.error_message && (
                  <Alert
                    message="错误信息"
                    description={record.error_message}
                    type="error"
                    showIcon
                    style={{ marginBottom: 8 }}
                  />
                )}
                {record.stack_trace && (
                  <Collapse ghost>
                    <Panel header="堆栈跟踪" key="1">
                      <pre style={{ 
                        backgroundColor: '#f5f5f5', 
                        padding: 8, 
                        borderRadius: 4,
                        overflow: 'auto',
                        maxHeight: 300
                      }}>
                        {record.stack_trace}
                      </pre>
                    </Panel>
                  </Collapse>
                )}
              </div>
            );
          },
          rowExpandable: (record) => !!record.error_message || !!record.stack_trace
        }}
      />
    );
  };

  return (
    <Modal
      title={`测试运行详情 - ${runId}`}
      visible={visible}
      onCancel={onClose}
      width={1200}
      footer={[
        <Button key="close" onClick={onClose}>
          关闭
        </Button>
      ]}
    >
      <Spin spinning={loading}>
        {data && (
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane tab="概览" key="summary">
              <Descriptions bordered column={2} style={{ marginBottom: 16 }}>
                <Descriptions.Item label="运行ID">{data.run.run_id}</Descriptions.Item>
                <Descriptions.Item label="运行类型">
                  <Tag color={data.run.run_type === 'scheduled' ? 'blue' : 'green'}>
                    {data.run.run_type === 'scheduled' ? '定时执行' : '手动触发'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag color={data.run.status === 'completed' ? 'success' : 'processing'}>
                    {data.run.status === 'completed' ? '已完成' : '运行中'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="触发人">{data.run.trigger_user || '-'}</Descriptions.Item>
                <Descriptions.Item label="开始时间">
                  {dayjs.utc(data.run.start_time).local().format('YYYY-MM-DD HH:mm:ss')}
                </Descriptions.Item>
                <Descriptions.Item label="结束时间">
                  {data.run.end_time ? dayjs.utc(data.run.end_time).local().format('YYYY-MM-DD HH:mm:ss') : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="持续时间">
                  {data.run.duration ? `${data.run.duration.toFixed(2)}秒` : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="成功率">
                  <Text strong style={{ 
                    color: data.run.success_rate === 100 ? '#52c41a' : 
                           data.run.success_rate < 80 ? '#f5222d' : '#faad14'
                  }}>
                    {data.run.success_rate}%
                  </Text>
                </Descriptions.Item>
              </Descriptions>

              <Card title="测试统计" size="small">
                <Space size="large">
                  <div>
                    <Text type="secondary">总测试数：</Text>
                    <Text strong>{data.run.total_tests}</Text>
                  </div>
                  <div>
                    <Text type="secondary">通过：</Text>
                    <Text strong style={{ color: '#52c41a' }}>{data.run.passed_tests}</Text>
                  </div>
                  <div>
                    <Text type="secondary">失败：</Text>
                    <Text strong style={{ color: '#f5222d' }}>{data.run.failed_tests}</Text>
                  </div>
                  <div>
                    <Text type="secondary">跳过：</Text>
                    <Text strong style={{ color: '#faad14' }}>{data.run.skipped_tests}</Text>
                  </div>
                  <div>
                    <Text type="secondary">错误：</Text>
                    <Text strong style={{ color: '#f5222d' }}>{data.run.error_tests}</Text>
                  </div>
                </Space>
              </Card>
            </TabPane>

            <TabPane tab="测试结果" key="results">
              <Collapse defaultActiveKey={Object.keys(data.results)}>
                {Object.entries(data.results).map(([suite, results]) => {
                  const passed = results.filter(r => r.status === 'passed').length;
                  const failed = results.filter(r => r.status === 'failed').length;
                  const total = results.length;
                  
                  return (
                    <Panel
                      key={suite}
                      header={
                        <Space>
                          <CodeOutlined />
                          <Text strong>{suite}</Text>
                          <Tag color="blue">{total} 个测试</Tag>
                          {passed > 0 && <Tag color="success">{passed} 通过</Tag>}
                          {failed > 0 && <Tag color="error">{failed} 失败</Tag>}
                        </Space>
                      }
                      extra={
                        failed > 0 ? 
                          <CloseCircleOutlined style={{ color: '#f5222d' }} /> :
                          <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      }
                    >
                      {renderTestResults(results)}
                    </Panel>
                  );
                })}
              </Collapse>
            </TabPane>

            <TabPane tab="环境信息" key="environment">
              {data.run.environment && (
                <Descriptions bordered column={1}>
                  {Object.entries(data.run.environment).map(([key, value]) => (
                    <Descriptions.Item key={key} label={key}>
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </Descriptions.Item>
                  ))}
                </Descriptions>
              )}
            </TabPane>
          </Tabs>
        )}
      </Spin>
    </Modal>
  );
};

export default TestResultDetail;