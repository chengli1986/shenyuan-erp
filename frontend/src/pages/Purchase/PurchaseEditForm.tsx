import React, { useCallback } from 'react';
import {
  Modal,
  Form,
  Input,
  DatePicker,
  Button,
  Select,
  Space,
  Divider,
  Card
} from 'antd';
import {
  PlusOutlined,
  SaveOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { usePurchaseEditForm } from './hooks/usePurchaseEditForm';
import type { PurchaseEditFormProps } from './hooks/usePurchaseEditForm';
import PurchaseEditFormItems from './PurchaseEditFormItems';

const PurchaseEditForm: React.FC<PurchaseEditFormProps> = ({
  visible,
  purchaseData,
  onCancel,
  onSave
}) => {
  const {
    form,
    loading,
    projects,
    items,
    setItems,
    materialNames,
    isProjectManager,
    handleMaterialNameChange,
    handleSpecificationChange,
    handleQuantityChange,
    handlePriceChange,
    handleItemTypeChange,
    addItem,
    removeItem,
    updateItem,
    handleSave,
  } = usePurchaseEditForm({ visible, purchaseData, onCancel, onSave });

  // Wrapper that updates both system_category_id and system_category_name in one pass
  const handleSystemCategoryWithName = useCallback(
    (itemId: string, categoryId: number, categoryName: string) => {
      setItems(prev =>
        prev.map(item =>
          item.id === itemId
            ? { ...item, system_category_id: categoryId, system_category_name: categoryName }
            : item
        )
      );
    },
    [setItems]
  );

  return (
    <Modal
      title={`编辑申购单 - ${purchaseData?.request_code}`}
      open={visible}
      onCancel={onCancel}
      width={1200}
      footer={null}
      destroyOnClose
    >
      <Card>
        <Form
          form={form}
          layout="vertical"
          style={{ marginBottom: 16 }}
        >
          <Form.Item
            name="project_id"
            label="项目"
            rules={[{ required: true, message: '请选择项目' }]}
          >
            <Select
              placeholder="选择项目"
              disabled={!!purchaseData?.project_id}
              showSearch
              filterOption={(input, option: { children?: string } | undefined) =>
                (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {projects.map(project => (
                <Select.Option key={project.id} value={project.id}>
                  {project.project_name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="required_date"
            label="需求日期"
          >
            <DatePicker
              style={{ width: '100%' }}
              placeholder="选择需求日期"
            />
          </Form.Item>

          <Form.Item
            name="remarks"
            label="备注说明"
          >
            <Input.TextArea
              rows={3}
              placeholder="请输入申购说明和备注信息"
            />
          </Form.Item>
        </Form>

        <Divider>申购明细</Divider>

        <div style={{ marginBottom: 16 }}>
          <Button
            type="dashed"
            onClick={addItem}
            icon={<PlusOutlined />}
            style={{ width: '100%' }}
          >
            添加申购项
          </Button>
        </div>

        <PurchaseEditFormItems
          items={items}
          materialNames={materialNames}
          isProjectManager={isProjectManager}
          onMaterialNameChange={handleMaterialNameChange}
          onSpecificationChange={handleSpecificationChange}
          onSystemCategoryWithName={handleSystemCategoryWithName}
          onQuantityChange={handleQuantityChange}
          onPriceChange={handlePriceChange}
          onItemTypeChange={handleItemTypeChange}
          onRemoveItem={removeItem}
          onUpdateItem={updateItem}
        />

        <div style={{ marginTop: 16, textAlign: 'right' }}>
          <Space>
            <Button
              icon={<CloseOutlined />}
              onClick={onCancel}
            >
              取消
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={loading}
            >
              保存修改
            </Button>
          </Space>
        </div>
      </Card>
    </Modal>
  );
};

export default PurchaseEditForm;
