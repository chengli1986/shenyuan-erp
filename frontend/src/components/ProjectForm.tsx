// frontend/src/components/ProjectForm.tsx
/**
 * 项目表单组件
 * 用于新建和编辑项目的通用表单
 */

import React from 'react';
import {
  Form,
  Input,
  InputNumber,
  DatePicker,
  Select,
  Button,
  Space,
  Row,
  Col
} from 'antd';
import type { FormInstance } from 'antd/es/form';
import { ProjectCreate, ProjectStatus, PROJECT_STATUS_CONFIG } from '../types/project';

const { TextArea } = Input;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface ProjectFormProps {
  form: FormInstance;
  onFinish: (values: ProjectCreate) => void;
  onCancel: () => void;
  loading?: boolean;
  initialValues?: Partial<ProjectCreate>;
  isEdit?: boolean; // 新增：是否为编辑模式
}

const ProjectForm: React.FC<ProjectFormProps> = ({
  form,
  onFinish,
  onCancel,
  loading = false,
  initialValues,
  isEdit = false // 默认为新建模式
}) => {

  // 表单验证规则
  const rules = {
    project_code: [
      { required: true, message: '请输入项目编号' },
      { pattern: /^[A-Z0-9]{3,20}$/, message: '项目编号格式：3-20位大写字母和数字' }
    ],
    project_name: [
      { required: true, message: '请输入项目名称' },
      { min: 2, max: 100, message: '项目名称长度2-100个字符' }
    ],
    contract_amount: [
      { type: 'number' as const, min: 0, message: '合同金额必须大于0' }
    ],
    project_manager: [
      { max: 50, message: '项目经理姓名不超过50个字符' }
    ],
    description: [
      { max: 500, message: '项目描述不超过500个字符' }
    ]
  };

  // 处理表单提交
  const handleFinish = (values: any) => {
    // 处理日期范围
    if (values.dateRange) {
      values.start_date = values.dateRange[0]?.toISOString();
      values.end_date = values.dateRange[1]?.toISOString();
      delete values.dateRange;
    }

    onFinish(values);
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleFinish}
      initialValues={{
        status: ProjectStatus.PLANNING, // 默认状态为规划中
        ...initialValues
      }}
      scrollToFirstError
    >
      <Row gutter={16}>
        {/* 项目编号 */}
        <Col span={12}>
          <Form.Item
            label="项目编号"
            name="project_code"
            rules={rules.project_code}
            tooltip="格式：PROJ001、ABC123等，3-20位大写字母和数字"
          >
            <Input 
              placeholder="如：PROJ001"
              style={{ textTransform: 'uppercase' }}
              onChange={(e) => {
                // 自动转换为大写
                e.target.value = e.target.value.toUpperCase();
              }}
            />
          </Form.Item>
        </Col>

        {/* 项目状态 */}
        <Col span={12}>
          <Form.Item
            label="项目状态"
            name="status"
          >
            <Select placeholder="选择项目状态">
              {Object.entries(PROJECT_STATUS_CONFIG).map(([key, config]) => (
                <Option key={key} value={key}>
                  {config.icon} {config.text}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
      </Row>

      {/* 项目名称 */}
      <Form.Item
        label="项目名称"
        name="project_name"
        rules={rules.project_name}
      >
        <Input 
          placeholder="请输入项目名称，如：某某大厦弱电工程"
          showCount
          maxLength={100}
        />
      </Form.Item>

      <Row gutter={16}>
        {/* 合同金额 */}
        <Col span={12}>
          <Form.Item
            label="合同金额"
            name="contract_amount"
            rules={rules.contract_amount}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="请输入合同金额"
              addonBefore="¥"
              precision={2}
              min={0}
              max={999999999.99}
              controls
            />
          </Form.Item>
        </Col>

        {/* 项目经理 */}
        <Col span={12}>
          <Form.Item
            label="项目经理"
            name="project_manager"
            rules={rules.project_manager}
          >
            <Input 
              placeholder="请输入项目经理姓名"
              maxLength={50}
            />
          </Form.Item>
        </Col>
      </Row>

      {/* 项目时间 */}
      <Form.Item
        label="项目时间"
        name="dateRange"
        tooltip="选择项目的开始和结束时间"
      >
        <RangePicker
          style={{ width: '100%' }}
          placeholder={['开始日期', '结束日期']}
          format="YYYY-MM-DD"
        />
      </Form.Item>

      {/* 项目描述 */}
      <Form.Item
        label="项目描述"
        name="description"
        rules={rules.description}
      >
        <TextArea
          placeholder="请输入项目描述、要求、注意事项等"
          rows={4}
          showCount
          maxLength={500}
        />
      </Form.Item>

      {/* 操作按钮 */}
      <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
        <Space>
          <Button onClick={onCancel}>
            取消
          </Button>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
          >
            {loading ? (isEdit ? '更新中...' : '创建中...') : (isEdit ? '更新项目' : '创建项目')}
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default ProjectForm;