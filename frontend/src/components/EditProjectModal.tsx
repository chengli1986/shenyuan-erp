// frontend/src/components/EditProjectModal.tsx
/**
 * 编辑项目弹窗组件
 * 复用ProjectForm组件，用于编辑现有项目
 */

import React, { useState, useEffect } from 'react';
import { Modal, Form, message, Spin } from 'antd';
import ProjectForm from './ProjectForm';
import { ProjectUpdate, Project } from '../types/project';
import { ProjectService } from '../services/project';
import dayjs from 'dayjs';

interface EditProjectModalProps {
  visible: boolean;
  projectId: number | null;
  onCancel: () => void;
  onSuccess: (project: Project) => void; // 编辑成功回调
}

const EditProjectModal: React.FC<EditProjectModalProps> = ({
  visible,
  projectId,
  onCancel,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(false);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);

  // 获取项目详情
  const fetchProjectDetail = async (id: number) => {
    setFetchLoading(true);
    try {
      const project = await ProjectService.getProject(id);
      setCurrentProject(project);
      
      // 设置表单初始值
      const formValues = {
        ...project,
        // 处理日期范围
        dateRange: project.start_date && project.end_date ? [
          dayjs(project.start_date),
          dayjs(project.end_date)
        ] : undefined
      };
      
      form.setFieldsValue(formValues);
    } catch (error) {
      console.error('获取项目详情失败:', error);
      message.error('获取项目信息失败');
      onCancel(); // 获取失败时关闭弹窗
    } finally {
      setFetchLoading(false);
    }
  };

  // 当弹窗打开且有项目ID时，获取项目详情
  useEffect(() => {
    if (visible && projectId) {
      fetchProjectDetail(projectId);
    }
  }, [visible, projectId]);

  // 处理表单提交
  const handleFinish = async (values: ProjectUpdate) => {
    if (!projectId || !currentProject) return;
    
    setLoading(true);
    try {
      console.log('更新的项目数据:', values);
      
      // 调用API更新项目
      const updatedProject = await ProjectService.updateProject(projectId, values);
      
      // 成功提示
      message.success(`项目 "${updatedProject.project_name}" 更新成功！`);
      
      // 通知父组件刷新列表
      onSuccess(updatedProject);
      
      // 关闭弹窗
      onCancel();
      
    } catch (error: any) {
      console.error('更新项目失败:', error);
      
      // 处理不同类型的错误
      if (error.response) {
        const { status, data } = error.response;
        
        if (status === 400) {
          // 验证错误
          if (data.detail?.includes('已存在')) {
            message.error('项目编号已存在，请使用其他编号');
          } else {
            message.error(`数据验证失败: ${data.detail || '请检查输入的数据'}`);
          }
        } else if (status === 404) {
          message.error('项目不存在，可能已被删除');
          onCancel();
        } else if (status === 500) {
          message.error('服务器内部错误，请稍后重试');
        } else {
          message.error(`更新失败: ${data.detail || '未知错误'}`);
        }
      } else if (error.code === 'ECONNABORTED') {
        message.error('请求超时，请检查网络连接');
      } else {
        message.error('网络错误，无法连接到服务器');
      }
    } finally {
      setLoading(false);
    }
  };

  // 处理弹窗关闭
  const handleCancel = () => {
    if (loading) {
      message.warning('正在更新项目，请稍等...');
      return;
    }
    
    // 重置表单和状态
    form.resetFields();
    setCurrentProject(null);
    onCancel();
  };

  return (
    <Modal
      title={`✏️ 编辑项目 ${currentProject ? `- ${currentProject.project_name}` : ''}`}
      open={visible}
      onCancel={handleCancel}
      footer={null} // 使用表单内的按钮
      width={800}
      destroyOnClose // 关闭时销毁内容，确保状态重置
      maskClosable={!loading} // 加载时不允许点击遮罩关闭
    >
      {fetchLoading ? (
        // 获取项目信息时显示加载状态
        <div style={{ 
          textAlign: 'center', 
          padding: '60px 20px',
          color: '#666' 
        }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>正在获取项目信息...</div>
        </div>
      ) : (
        // 显示编辑表单
        <ProjectForm
          form={form}
          onFinish={handleFinish}
          onCancel={handleCancel}
          loading={loading}
          initialValues={currentProject || undefined}
        />
      )}
    </Modal>
  );
};

export default EditProjectModal;