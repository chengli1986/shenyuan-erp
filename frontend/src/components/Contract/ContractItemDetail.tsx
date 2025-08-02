// frontend/src/components/Contract/ContractItemDetail.tsx
/**
 * 合同设备详情查看组件
 */

import React from 'react';
import { Modal, Descriptions, Tag, Typography } from 'antd';
import { ContractItem, ItemType } from '../../types/contract';
import { formatAmount } from '../../services/contract';

const { Text } = Typography;

interface ContractItemDetailProps {
  item: ContractItem | null;
  visible: boolean;
  onClose: () => void;
}

const ContractItemDetail: React.FC<ContractItemDetailProps> = ({
  item,
  visible,
  onClose
}) => {
  if (!item) return null;

  return (
    <Modal
      title={`设备详情 - ${item.item_name}`}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      <Descriptions bordered column={2}>
        <Descriptions.Item label="序号">
          {item.serial_number || '-'}
        </Descriptions.Item>
        <Descriptions.Item label="设备名称">
          <Text strong>{item.item_name}</Text>
        </Descriptions.Item>
        <Descriptions.Item label="设备品牌">
          {item.specification || '待补充'}
        </Descriptions.Item>
        <Descriptions.Item label="设备型号">
          {item.brand_model || '-'}
        </Descriptions.Item>
        <Descriptions.Item label="单位">
          {item.unit || '台'}
        </Descriptions.Item>
        <Descriptions.Item label="数量">
          <Text strong>{Number(item.quantity).toLocaleString()}</Text>
        </Descriptions.Item>
        <Descriptions.Item label="单价">
          {item.unit_price ? formatAmount(Number(item.unit_price)) : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="总价">
          <Text type="success" strong>
            {item.total_price ? formatAmount(Number(item.total_price)) : '-'}
          </Text>
        </Descriptions.Item>
        <Descriptions.Item label="物料类型">
          <Tag color={item.item_type === ItemType.PRIMARY ? 'green' : 'orange'}>
            {item.item_type || ItemType.PRIMARY}
          </Tag>
        </Descriptions.Item>
        <Descriptions.Item label="是否关键设备">
          <Tag color={item.is_key_equipment ? 'red' : 'default'}>
            {item.is_key_equipment ? '是' : '否'}
          </Tag>
        </Descriptions.Item>
        <Descriptions.Item label="原产地" span={2}>
          {item.origin_place || '中国'}
        </Descriptions.Item>
        {item.technical_params && (
          <Descriptions.Item label="技术参数" span={2}>
            <Text>{item.technical_params}</Text>
          </Descriptions.Item>
        )}
        {item.remarks && (
          <Descriptions.Item label="备注" span={2}>
            <Text>{item.remarks}</Text>
          </Descriptions.Item>
        )}
        <Descriptions.Item label="创建时间">
          {item.created_at ? new Date(item.created_at).toLocaleString() : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="更新时间">
          {item.updated_at ? new Date(item.updated_at).toLocaleString() : '-'}
        </Descriptions.Item>
      </Descriptions>
    </Modal>
  );
};

export default ContractItemDetail;