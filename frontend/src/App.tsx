// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, Layout, Menu, theme } from 'antd';
import {
  ProjectOutlined,
  FileTextOutlined,
  ShoppingCartOutlined,
  InboxOutlined,
  BarChartOutlined,
  UserOutlined
} from '@ant-design/icons';
import zhCN from 'antd/locale/zh_CN';

// 导入页面组件
import ProjectList from './pages/Project/ProjectList';
import ConnectionStatus from './components/ConnectionStatus';
import { ConnectionProvider } from './contexts/ConnectionContext';

const { Header, Sider, Content } = Layout;
const { useToken } = theme;

function App() {
  const { token } = useToken();
  
  // 菜单项配置
  const menuItems = [
    {
      key: '/projects',
      icon: <ProjectOutlined />,
      label: '项目管理',
    },
    {
      key: '/contracts',
      icon: <FileTextOutlined />,
      label: '合同清单',
    },
    {
      key: '/purchases',
      icon: <ShoppingCartOutlined />,
      label: '申购管理',
    },
    {
      key: '/inventory',
      icon: <InboxOutlined />,
      label: '库存管理',
    },
    {
      key: '/reports',
      icon: <BarChartOutlined />,
      label: '统计报表',
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: '用户管理',
    },
  ];

  return (
    <ConfigProvider locale={zhCN}>
      <ConnectionProvider>
        <Router>
        <Layout style={{ minHeight: '100vh' }}>
          {/* 侧边栏 */}
          <Sider
            width={256}
            style={{
              background: token.colorBgContainer,
              borderRight: `1px solid ${token.colorBorderSecondary}`,
            }}
          >
            {/* Logo区域 */}
            <div style={{
              height: 64,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderBottom: `1px solid ${token.colorBorderSecondary}`,
              background: token.colorPrimary,
              color: 'white',
              fontSize: '18px',
              fontWeight: 'bold'
            }}>
              ⚡ 弱电工程ERP
            </div>

            {/* 导航菜单 */}
            <Menu
              mode="inline"
              defaultSelectedKeys={['/projects']}
              style={{ borderRight: 0, paddingTop: '16px' }}
              items={menuItems}
              onClick={({ key }) => {
                // 这里可以添加页面跳转逻辑
                if (key !== '/projects') {
                  // 暂时显示提示信息
                  console.log(`${key} 功能开发中...`);
                }
              }}
            />
          </Sider>

          <Layout>
            {/* 顶部导航 */}
            <Header style={{
              padding: '0 24px',
              background: token.colorBgContainer,
              borderBottom: `1px solid ${token.colorBorderSecondary}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div style={{ fontSize: '16px', fontWeight: 500 }}>
                弱电工程项目管理系统
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <ConnectionStatus />
                <span>👨‍💼 张工程师</span>
                <span style={{ color: token.colorTextSecondary }}>
                  {new Date().toLocaleDateString('zh-CN')}
                </span>
              </div>
            </Header>

            {/* 主内容区域 */}
            <Content style={{
              background: token.colorBgLayout,
              overflow: 'auto'
            }}>
              <Routes>
                {/* 默认跳转到项目管理 */}
                <Route path="/" element={<Navigate to="/projects" replace />} />
                
                {/* 项目管理页面 */}
                <Route path="/projects" element={<ProjectList />} />
                
                {/* 其他页面暂时显示开发中 */}
                <Route path="/*" element={
                  <div style={{ 
                    padding: '48px', 
                    textAlign: 'center',
                    fontSize: '18px',
                    color: token.colorTextSecondary 
                  }}>
                    🚧 该功能正在开发中，敬请期待...
                  </div>
                } />
              </Routes>
            </Content>
          </Layout>
        </Layout>
              </Router>
      </ConnectionProvider>
    </ConfigProvider>
  );
}

export default App;