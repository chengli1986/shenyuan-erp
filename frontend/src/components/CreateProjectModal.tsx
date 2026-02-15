// frontend/src/components/CreateProjectModal.tsx
/**
 * 新建项目弹窗组件
 * 包含项目表单，处理创建逻辑
 */

import React, { useState } from 'react';
import { Modal, Form, message } from 'antd';
import ProjectForm from './ProjectForm';
import { ProjectCreate, Project } from '../types/project';
import { ProjectService } from '../services/project';

interface CreateProjectModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: (project: Project) => void; // 创建成功回调
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  visible,
  onCancel,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  // 处理表单提交
  const handleFinish = async (values: ProjectCreate) => {
    setLoading(true);
    try {
      // 调用API创建项目
      const newProject = await ProjectService.createProject(values);
      
      // 成功提示
      message.success(`项目 "${newProject.project_name}" 创建成功！`);
      
      // 重置表单
      form.resetFields();
      
      // 通知父组件刷新列表
      onSuccess(newProject);
      
      // 关闭弹窗
      onCancel();
      
    } catch (error: unknown) {
      console.error('创建项目失败:', error);
      message.error(error instanceof Error ? error.message : '创建项目失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理弹窗关闭
  const handleCancel = () => {
    if (loading) {
      message.warning('正在创建项目，请稍等...');
      return;
    }
    
    // 重置表单
    form.resetFields();
    onCancel();
  };

  return (
    <Modal
      title="🚀 新建项目"
      open={visible}
      onCancel={handleCancel}
      footer={null} // 使用表单内的按钮
      width={800}
      destroyOnClose // 关闭时销毁内容，确保表单重置
      maskClosable={!loading} // 加载时不允许点击遮罩关闭
    >
      <ProjectForm
        form={form}
        onFinish={handleFinish}
        onCancel={handleCancel}
        loading={loading}
      />
    </Modal>
  );
};

export default CreateProjectModal;