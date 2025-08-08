import React, { useState } from 'react';
import { Card, Tabs, Modal, message } from 'antd';
import {
  ShoppingCartOutlined,
  TeamOutlined,
  SettingOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import PurchaseRequestList from './PurchaseRequestList';
import PurchaseRequestForm from './PurchaseRequestForm';
import SupplierManagement from './SupplierManagement';

const { TabPane } = Tabs;

interface PurchaseManagementProps {
  projectId?: number;
}

const PurchaseManagement: React.FC<PurchaseManagementProps> = ({ projectId }) => {
  const [activeTab, setActiveTab] = useState('requests');
  
  // 新建申购单弹窗
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editingRequestId, setEditingRequestId] = useState<number | undefined>();

  // 处理新建申购单
  const handleCreateRequest = () => {
    if (!projectId) {
      message.warning('请先选择项目');
      return;
    }
    setEditingRequestId(undefined);
    setCreateModalVisible(true);
  };

  // 处理编辑申购单
  const handleEditRequest = (requestId: number) => {
    setEditingRequestId(requestId);
    setCreateModalVisible(true);
  };

  // 关闭申购单表单
  const handleCloseForm = () => {
    setCreateModalVisible(false);
    setEditingRequestId(undefined);
  };

  // 申购单操作成功回调
  const handleFormSuccess = () => {
    setCreateModalVisible(false);
    setEditingRequestId(undefined);
    // 刷新列表将由子组件处理
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          type="card"
        >
          <TabPane
            tab={
              <span>
                <ShoppingCartOutlined />
                申购管理
              </span>
            }
            key="requests"
          >
            <PurchaseRequestList 
              projectId={projectId}
              onCreateRequest={handleCreateRequest}
              onEditRequest={handleEditRequest}
            />
          </TabPane>

          <TabPane
            tab={
              <span>
                <TeamOutlined />
                供应商管理
              </span>
            }
            key="suppliers"
          >
            <SupplierManagement />
          </TabPane>

          <TabPane
            tab={
              <span>
                <BarChartOutlined />
                采购统计
              </span>
            }
            key="statistics"
          >
            <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
              采购统计功能正在开发中...
            </div>
          </TabPane>

          <TabPane
            tab={
              <span>
                <SettingOutlined />
                辅材模板
              </span>
            }
            key="templates"
          >
            <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
              辅材模板管理功能正在开发中...
            </div>
          </TabPane>
        </Tabs>
      </Card>

      {/* 申购单创建/编辑弹窗 */}
      <Modal
        title={editingRequestId ? '编辑申购单' : '新建申购单'}
        open={createModalVisible}
        onCancel={handleCloseForm}
        footer={null}
        width={1200}
        destroyOnClose
      >
        {projectId && (
          <PurchaseRequestForm
            projectId={projectId}
            requestId={editingRequestId}
            onClose={handleCloseForm}
            onSuccess={handleFormSuccess}
          />
        )}
      </Modal>
    </div>
  );
};

export default PurchaseManagement;