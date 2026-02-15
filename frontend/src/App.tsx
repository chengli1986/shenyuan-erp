// frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider, Layout, Menu, theme, Button, Dropdown } from 'antd';
import {
  ProjectOutlined,
  FileTextOutlined,
  ShoppingCartOutlined,
  InboxOutlined,
  BarChartOutlined,
  UserOutlined,
  ExperimentOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import zhCN from 'antd/locale/zh_CN';
import { authService, User } from './services/auth';
import Login from './components/Login';

// 导入页面组件
import ProjectList from './pages/Project/ProjectList';
import ContractOverview from './pages/Contract/ContractOverview';
import ContractManagement from './pages/Contract/ContractManagement';
import SimplePurchaseList from './pages/Purchase/SimplePurchaseList';
import EnhancedPurchaseForm from './pages/Purchase/EnhancedPurchaseForm';
import SystemTestDashboard from './pages/SystemTest/SystemTestDashboard';
import ConnectionStatus from './components/ConnectionStatus';
import { ConnectionProvider } from './contexts/ConnectionContext';
import ErrorBoundary from './components/ErrorBoundary';

const { Header, Sider, Content } = Layout;
const { useToken } = theme;

// 主应用组件（需要在Router内部）
function AppContent() {
  const { token } = useToken();
  const navigate = useNavigate();
  const location = useLocation();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  
  useEffect(() => {
    const user = authService.getCurrentUser();
    setCurrentUser(user);
  }, []);
  
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
    {
      key: '/system-test',
      icon: <ExperimentOutlined />,
      label: '系统测试',
    },
  ];

  const handleLoginSuccess = () => {
    const user = authService.getCurrentUser();
    setCurrentUser(user);
  };

  // 如果用户未登录，显示登录页面
  if (!authService.isLoggedIn()) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
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
              selectedKeys={[location.pathname]}
              style={{ borderRight: 0, paddingTop: '16px' }}
              items={menuItems}
              onClick={({ key }) => {
                if (key === '/projects' || key === '/contracts' || key === '/purchases' || key === '/system-test') {
                  // 已开发的功能，进行路由跳转
                  navigate(key);
                } else {
                  // 暂时不做跳转，功能开发中
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
                <Dropdown
                  menu={{
                    items: [
                      {
                        key: 'profile',
                        label: '个人信息',
                        icon: <UserOutlined />,
                      },
                      {
                        key: 'logout',
                        label: '退出登录',
                        icon: <LogoutOutlined />,
                        onClick: async () => {
                          await authService.logout();
                          setCurrentUser(null);
                        },
                      },
                    ],
                  }}
                >
                  <Button type="text">
                    👤 {currentUser?.name || '用户'}
                  </Button>
                </Dropdown>
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
                
                {/* 合同清单总览页面 */}
                <Route path="/contracts" element={<ContractOverview />} />
                
                {/* 项目合同管理页面 */}
                <Route path="/contracts/:projectId" element={<ContractManagement />} />
                
                {/* 采购管理页面 - 简化版本 */}
                <Route path="/purchases" element={<SimplePurchaseList />} />
                <Route path="/purchases/create" element={<EnhancedPurchaseForm />} />
                
                {/* 系统测试页面 */}
                <Route path="/system-test" element={<SystemTestDashboard />} />
                
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
  );
}

// 主App组件
function App() {
  return (
    <ErrorBoundary>
      <ConfigProvider locale={zhCN}>
        <ConnectionProvider>
          <Router>
            <AppContent />
          </Router>
        </ConnectionProvider>
      </ConfigProvider>
    </ErrorBoundary>
  );
}

export default App;