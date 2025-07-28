/**
 * 测试统计图表组件
 */

import React, { useState, useEffect } from 'react';
import {
  Modal,
  Card,
  Row,
  Col,
  Statistic,
  Select,
  Spin,
  Empty,
  Space,
  Progress,
  Table,
  Tag
} from 'antd';
import {
  ExperimentOutlined,
  RiseOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';
import { testService } from '../../services/test';
import { TestStatistics } from '../../types/test';

interface TestStatisticsChartProps {
  visible: boolean;
  onClose: () => void;
}

const TestStatisticsChart: React.FC<TestStatisticsChartProps> = ({
  visible,
  onClose
}) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<TestStatistics | null>(null);
  const [days, setDays] = useState(30);

  // 加载统计数据
  const loadStatistics = async () => {
    setLoading(true);
    try {
      const statistics = await testService.getTestStatistics(days);
      setData(statistics);
    } catch (error) {
      console.error('加载统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (visible) {
      loadStatistics();
    }
  }, [visible, days]);

  // 准备表格数据
  const getTableData = () => {
    if (!data) return [];
    
    return data.daily_stats.map((stat, index) => ({
      key: index,
      date: stat.date,
      runs: stat.runs,
      tests: stat.tests,
      passed: stat.passed,
      failed: stat.failed,
      success_rate: stat.tests > 0 ? Math.round((stat.passed / stat.tests) * 100) : 0
    }));
  };

  // 表格列配置
  const columns = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: '运行次数',
      dataIndex: 'runs',
      key: 'runs',
    },
    {
      title: '测试总数',
      dataIndex: 'tests',
      key: 'tests',
    },
    {
      title: '通过数',
      dataIndex: 'passed',
      key: 'passed',
      render: (value: number) => (
        <Tag color="success">{value}</Tag>
      )
    },
    {
      title: '失败数',
      dataIndex: 'failed',
      key: 'failed',
      render: (value: number) => (
        <Tag color={value > 0 ? 'error' : 'default'}>{value}</Tag>
      )
    },
    {
      title: '成功率',
      dataIndex: 'success_rate',
      key: 'success_rate',
      render: (value: number) => (
        <Progress 
          percent={value} 
          size="small" 
          status={value === 100 ? 'success' : value < 80 ? 'exception' : 'normal'}
        />
      )
    }
  ];

  return (
    <Modal
      title="测试统计分析"
      visible={visible}
      onCancel={onClose}
      width={1200}
      footer={null}
    >
      <div style={{ marginBottom: 16 }}>
        <Space>
          <span>统计周期：</span>
          <Select
            value={days}
            onChange={setDays}
            style={{ width: 120 }}
          >
            <Select.Option value={7}>最近7天</Select.Option>
            <Select.Option value={30}>最近30天</Select.Option>
            <Select.Option value={90}>最近90天</Select.Option>
          </Select>
        </Space>
      </div>

      <Spin spinning={loading}>
        {data ? (
          <>
            {/* 汇总统计 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="总运行次数"
                    value={data.summary.total_runs}
                    prefix={<ExperimentOutlined />}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="总测试数"
                    value={data.summary.total_tests}
                    prefix={<ExperimentOutlined />}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="总成功率"
                    value={data.summary.success_rate}
                    suffix="%"
                    prefix={<RiseOutlined />}
                    valueStyle={{ 
                      color: data.summary.success_rate >= 95 ? '#52c41a' : 
                             data.summary.success_rate >= 80 ? '#faad14' : '#f5222d'
                    }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Progress
                    type="dashboard"
                    percent={data.summary.success_rate}
                    strokeColor={{
                      '0%': '#f5222d',
                      '50%': '#faad14',
                      '100%': '#52c41a'
                    }}
                  />
                </Card>
              </Col>
            </Row>

            {/* 简化的统计表格 */}
            <Row gutter={16}>
              <Col span={12}>
                <Card title="测试结果分布" bordered={false}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div style={{ textAlign: 'center' }}>
                      <Progress
                        type="circle"
                        percent={data.summary.success_rate}
                        format={(percent) => `${percent}%`}
                        strokeColor={{
                          '0%': '#f5222d',
                          '50%': '#faad14', 
                          '100%': '#52c41a'
                        }}
                      />
                      <div style={{ marginTop: 16 }}>
                        <Space size="large">
                          <div>
                            <CheckCircleOutlined style={{ color: '#52c41a' }} />
                            <span style={{ marginLeft: 8 }}>通过: {data.summary.total_passed}</span>
                          </div>
                          <div>
                            <CloseCircleOutlined style={{ color: '#f5222d' }} />
                            <span style={{ marginLeft: 8 }}>失败: {data.summary.total_failed}</span>
                          </div>
                        </Space>
                      </div>
                    </div>
                  </Space>
                </Card>
              </Col>

              <Col span={12}>
                <Card title="统计汇总" bordered={false}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Statistic
                      title="总运行次数"
                      value={data.summary.total_runs}
                      prefix={<ExperimentOutlined />}
                    />
                    <Statistic
                      title="总测试数"
                      value={data.summary.total_tests}
                      prefix={<ExperimentOutlined />}
                    />
                    <Statistic
                      title="整体成功率"
                      value={data.summary.success_rate}
                      suffix="%"
                      valueStyle={{
                        color: data.summary.success_rate >= 95 ? '#52c41a' : 
                               data.summary.success_rate >= 80 ? '#faad14' : '#f5222d'
                      }}
                    />
                  </Space>
                </Card>
              </Col>
            </Row>

            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={24}>
                <Card title="每日测试详情" bordered={false}>
                  <Table
                    dataSource={getTableData()}
                    columns={columns}
                    pagination={false}
                    size="small"
                  />
                </Card>
              </Col>
            </Row>
          </>
        ) : (
          <Empty description="暂无统计数据" />
        )}
      </Spin>
    </Modal>
  );
};

export default TestStatisticsChart;