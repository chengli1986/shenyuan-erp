/**
 * 登录页面组件
 */

import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Select } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { authService, LoginRequest } from '../services/auth';

const { Option } = Select;

interface LoginProps {
  onLoginSuccess: () => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [loading, setLoading] = useState(false);

  // 预设账号列表
  const presetAccounts = [
    { username: 'admin', password: 'admin123', name: '系统管理员' },
    { username: 'general_manager', password: 'gm123', name: '张总经理' },
    { username: 'dept_manager', password: 'dept123', name: '李工程部主管' },
    { username: 'sunyun', password: 'sunyun123', name: '孙赟(项目经理)' },
    { username: 'liqiang', password: 'liqiang123', name: '李强(项目经理)' },
    { username: 'purchaser', password: 'purchase123', name: '赵采购员' },
    { username: 'worker', password: 'worker123', name: '刘施工队长' },
    { username: 'finance', password: 'finance123', name: '陈财务' },
  ];

  const onFinish = async (values: LoginRequest) => {
    setLoading(true);
    try {
      await authService.login(values);
      message.success('登录成功');
      onLoginSuccess();
    } catch (error: any) {
      console.error('Login error:', error);
      message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (account: any) => {
    onFinish({
      username: account.username,
      password: account.password,
    });
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      background: '#f0f2f5'
    }}>
      <Card title="深源ERP系统 - 用户登录" style={{ width: 400 }}>
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名!' }]}
          >
            <Input 
              prefix={<UserOutlined />} 
              placeholder="用户名" 
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              style={{ width: '100%' }}
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ marginTop: 16 }}>
          <h4>快速登录（测试用）</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            {presetAccounts.map((account) => (
              <Button
                key={account.username}
                size="small"
                onClick={() => handleQuickLogin(account)}
                disabled={loading}
              >
                {account.name}
              </Button>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Login;