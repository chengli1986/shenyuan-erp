// frontend/src/components/Contract/ContractItemEdit.tsx
/**
 * 合同设备编辑组件
 */

import React, { useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Switch,
  message
} from 'antd';
import { ContractItem, ItemType } from '../../types/contract';
import { updateContractItem } from '../../services/contract';

const { TextArea } = Input;
const { Option } = Select;

interface ContractItemEditProps {
  item: ContractItem | null;
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const ContractItemEdit: React.FC<ContractItemEditProps> = ({
  item,
  visible,
  onClose,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = React.useState(false);

  useEffect(() => {
    if (item && visible) {
      form.setFieldsValue({
        item_name: item.item_name,
        brand_model: item.brand_model,
        specification: item.specification,
        unit: item.unit,
        quantity: item.quantity,
        unit_price: item.unit_price,
        origin_place: item.origin_place,
        item_type: item.item_type || ItemType.PRIMARY,
        is_key_equipment: item.is_key_equipment || false,
        technical_params: item.technical_params,
        remarks: item.remarks
      });
    }
  }, [item, visible, form]);

  const handleSubmit = async () => {
    if (!item) return;

    try {
      setLoading(true);
      const values = await form.validateFields();
      
      // 计算总价
      const total_price = values.quantity * values.unit_price;
      
      await updateContractItem(
        item.project_id,
        item.version_id,
        item.id,
        {
          ...values,
          total_price
        }
      );
      
      message.success('设备信息更新成功');
      onSuccess();
      onClose();
    } catch (error) {
      console.error('更新设备失败:', error);
      message.error('更新设备失败');
    } finally {
      setLoading(false);
    }
  };

  if (!item) return null;

  return (
    <Modal
      title={`编辑设备 - ${item.item_name}`}
      open={visible}
      onOk={handleSubmit}
      onCancel={onClose}
      confirmLoading={loading}
      width={800}
      okText="保存"
      cancelText="取消"
    >
      <Form
        form={form}
        layout="vertical"
        autoComplete="off"
      >
        <Form.Item
          label="设备名称"
          name="item_name"
          rules={[{ required: true, message: '请输入设备名称' }]}
        >
          <Input placeholder="请输入设备名称" />
        </Form.Item>

        <Form.Item label="设备型号" name="brand_model">
          <Input placeholder="请输入设备型号" />
        </Form.Item>

        <Form.Item label="设备品牌" name="specification">
          <Input placeholder="请输入设备品牌" />
        </Form.Item>

        <Form.Item
          label="单位"
          name="unit"
          rules={[{ required: true, message: '请输入单位' }]}
        >
          <Input placeholder="如：台、套、个" />
        </Form.Item>

        <Form.Item
          label="数量"
          name="quantity"
          rules={[
            { required: true, message: '请输入数量' },
            { type: 'number', min: 0.01, message: '数量必须大于0' }
          ]}
        >
          <InputNumber
            min={0.01}
            style={{ width: '100%' }}
            placeholder="请输入数量"
          />
        </Form.Item>

        <Form.Item
          label="单价"
          name="unit_price"
          rules={[
            { required: true, message: '请输入单价' },
            { type: 'number', min: 0, message: '单价不能为负数' }
          ]}
        >
          <InputNumber
            min={0}
            prefix="¥"
            style={{ width: '100%' }}
            placeholder="请输入单价"
          />
        </Form.Item>

        <Form.Item label="原产地" name="origin_place">
          <Input placeholder="请输入原产地" />
        </Form.Item>

        <Form.Item label="物料类型" name="item_type">
          <Select placeholder="请选择物料类型">
            <Option value={ItemType.PRIMARY}>主材</Option>
            <Option value={ItemType.AUXILIARY}>辅材</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="是否关键设备"
          name="is_key_equipment"
          valuePropName="checked"
        >
          <Switch checkedChildren="是" unCheckedChildren="否" />
        </Form.Item>

        <Form.Item label="技术参数" name="technical_params">
          <TextArea
            rows={3}
            placeholder="请输入技术参数"
          />
        </Form.Item>

        <Form.Item label="备注" name="remarks">
          <TextArea
            rows={2}
            placeholder="请输入备注信息"
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ContractItemEdit;