// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider, Layout, Menu, theme } from 'antd';
import {
  ProjectOutlined,
  FileTextOutlined,
  ShoppingCartOutlined,
  InboxOutlined,
  BarChartOutlined,
  UserOutlined,
  ExperimentOutlined
} from '@ant-design/icons';
import zhCN from 'antd/locale/zh_CN';

// 导入页面组件
import ProjectList from './pages/Project/ProjectList';
import ContractOverview from './pages/Contract/ContractOverview';
import ContractManagement from './pages/Contract/ContractManagement';
import SimplePurchaseList from './pages/Purchase/SimplePurchaseList';
import EnhancedPurchaseForm from './pages/Purchase/EnhancedPurchaseForm';
import SystemTestDashboard from './pages/SystemTest/SystemTestDashboard';
import ConnectionStatus from './components/ConnectionStatus';
import { ConnectionProvider } from './contexts/ConnectionContext';

const { Header, Sider, Content } = Layout;
const { useToken } = theme;

// 主应用组件（需要在Router内部）
function AppContent() {
  const { token } = useToken();
  const navigate = useNavigate();
  const location = useLocation();
  
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
    <ConfigProvider locale={zhCN}>
      <ConnectionProvider>
        <Router>
          <AppContent />
        </Router>
      </ConnectionProvider>
    </ConfigProvider>
  );
}

export default App;