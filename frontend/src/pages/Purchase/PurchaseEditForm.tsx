import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  DatePicker,
  Button,
  Table,
  Select,
  InputNumber,
  Space,
  message,
  Popconfirm,
  Divider,
  Card
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  SaveOutlined,
  CloseOutlined
} from '@ant-design/icons';
import api from '../../services/api';
import { AuthService } from '../../services/auth';
import dayjs, { Dayjs } from 'dayjs';

// 生成唯一ID的简单函数，替代uuid
const generateId = () => Math.random().toString(36).substring(2) + Date.now().toString(36);

interface Project {
  id: number;
  project_name: string;
  customer_name: string;
  project_manager: string;
}

interface SystemCategory {
  id: number;
  category_name: string;
  category_code?: string;
  description?: string;
  is_suggested?: boolean;
  items_count?: number;
}

interface SpecificationOption {
  specification: string;
  brand_model: string;
  unit: string;
  remaining_quantity?: number;
  total_quantity?: number;
  contract_item_id?: number;
}

interface PurchaseEditItem {
  id: string;
  contract_item_id?: number;
  system_category_id?: number;
  system_category_name?: string;  // 添加系统分类名称字段
  item_name: string;
  specification?: string;
  brand?: string;
  unit: string;
  quantity: number;
  unit_price?: number;
  total_price?: number;
  item_type: 'main' | 'auxiliary';
  remarks?: string;
  
  // 合同清单相关信息（用于数量上限）
  remaining_quantity?: number;  // 剩余可申购数量
  max_quantity?: number;        // 合同清单总数量
  
  // UI状态
  availableSpecifications?: SpecificationOption[];
  availableSystemCategories?: SystemCategory[];
}

interface PurchaseRequest {
  id: number;
  request_code: string;
  project_id: number;
  project_name?: string;
  required_date?: string;
  remarks?: string;
  items?: any[];
}

interface PurchaseEditFormProps {
  visible: boolean;
  purchaseData: PurchaseRequest | null;
  onCancel: () => void;
  onSave: (data: any) => Promise<void>;
}

const PurchaseEditForm: React.FC<PurchaseEditFormProps> = ({
  visible,
  purchaseData,
  onCancel,
  onSave
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [items, setItems] = useState<PurchaseEditItem[]>([]);
  const [materialNames, setMaterialNames] = useState<string[]>([]);

  // 初始化表单数据
  useEffect(() => {
    if (visible && purchaseData) {
      // 设置基本信息
      form.setFieldsValue({
        project_id: purchaseData.project_id,
        required_date: purchaseData.required_date ? dayjs(purchaseData.required_date) : null,
        remarks: purchaseData.remarks || ''
      });

      // 转换items数据格式
      const convertedItems = (purchaseData.items || []).map((item: any, index: number) => {
        const converted = {
          id: generateId(),
          contract_item_id: item.contract_item_id,
          system_category_id: item.system_category_id,
          system_category_name: item.system_category_name, // 添加系统分类名称
          item_name: item.item_name,
          specification: item.specification,
          brand: item.brand_model || item.brand, // 兼容不同的字段名
          unit: item.unit,
          quantity: parseFloat(item.quantity || '0'),
          unit_price: item.unit_price ? parseFloat(item.unit_price) : undefined,
          total_price: item.total_price ? parseFloat(item.total_price) : undefined,
          item_type: item.item_type || 'auxiliary',
          remarks: item.remarks || '',
          // 对于主材，需要获取剩余数量信息
          remaining_quantity: item.remaining_quantity, // 从后端数据中获取
          max_quantity: item.max_quantity
        };
        
        return converted;
      });
      
      setItems(convertedItems);
      
      // 为所有明细项加载项目系统分类（支持手动选择）
      const projectId = purchaseData.project_id;
      getAllSystemCategoriesByProject(projectId).then(allCategories => {
        // 确保allCategories是数组类型
        const categoriesArray = Array.isArray(allCategories) ? allCategories : [];
        setItems(prevItems => prevItems.map(prevItem => ({
          ...prevItem,
          availableSystemCategories: categoriesArray
        })));
      });
      
      // 对于主材，异步加载剩余数量信息和规格选项
      convertedItems.forEach(async (item) => {
        if (item.item_type === 'main' && item.contract_item_id) {
          try {
            await loadContractItemDetails(item.id, item.contract_item_id);
          } catch (error) {
            console.error('加载合同清单项详情失败:', error);
          }
        }
        // 如果是主材且有物料名称，加载规格选项
        if (item.item_type === 'main' && item.item_name) {
          try {
            const [specResponse, categoryResponse] = await Promise.all([
              getSpecificationsByMaterial(projectId, item.item_name),
              getSystemCategoriesByMaterial(projectId, item.item_name)
            ]);
            
            setItems(prevItems => prevItems.map(prevItem => 
              prevItem.id === item.id ? {
                ...prevItem,
                availableSpecifications: specResponse.specifications || [],
                // 保持已加载的项目系统分类，但标记智能推荐的分类
                availableSystemCategories: Array.isArray(prevItem.availableSystemCategories) 
                  ? prevItem.availableSystemCategories.map(cat => ({
                      ...cat,
                      is_suggested: categoryResponse.categories?.some((suggestedCat: SystemCategory) => suggestedCat.id === cat.id)
                    }))
                  : categoryResponse.categories || []
              } : prevItem
            ));
          } catch (error) {
            console.error('加载主材规格选项失败:', error);
          }
        }
      });
    } else {
      // 重置表单
      form.resetFields();
      setItems([]);
    }
  }, [visible, purchaseData, form]);

  // 加载项目列表
  useEffect(() => {
    if (visible) {
      loadProjects();
    }
  }, [visible]);

  // 加载物料名称（当项目改变时）
  useEffect(() => {
    const projectId = form.getFieldValue('project_id');
    if (projectId && visible) {
      loadMaterialNames(projectId);
    }
  }, [visible, purchaseData?.project_id]);

  const loadProjects = async () => {
    try {
      const response = await api.get('projects/');
      setProjects(response.data.items || []);
    } catch (error: any) {
      console.error('加载项目列表失败:', error);
      message.error('加载项目列表失败');
    }
  };

  const loadMaterialNames = async (projectId: number) => {
    try {
      const response = await api.get(`purchases/material-names/by-project/${projectId}`);
      setMaterialNames(response.data.material_names || []);
    } catch (error: any) {
      console.error('加载物料名称失败:', error);
    }
  };

  const getSpecificationsByMaterial = async (projectId: number, materialName: string) => {
    try {
      const response = await api.get('purchases/specifications/by-material', {
        params: { project_id: projectId, item_name: materialName }
      });
      return response.data;
    } catch (error: any) {
      console.error('加载规格信息失败:', error);
      return { specifications: [] };
    }
  };

  const getSystemCategoriesByMaterial = async (projectId: number, materialName: string) => {
    try {
      const response = await api.get('purchases/system-categories/by-material', {
        params: { project_id: projectId, material_name: materialName }
      });
      return response.data;
    } catch (error: any) {
      console.error('加载系统分类失败:', error);
      return { categories: [] };
    }
  };

  const getAllSystemCategoriesByProject = async (projectId: number) => {
    try {
      const response = await api.get(`purchases/system-categories/by-project/${projectId}`);
      const data = response.data;
      // 确保返回数组类型，处理不同的API响应格式
      if (Array.isArray(data)) {
        return data;
      } else if (data && Array.isArray(data.categories)) {
        return data.categories;
      } else {
        return [];
      }
    } catch (error: any) {
      console.error('加载项目系统分类失败:', error);
      return [];
    }
  };

  const loadContractItemDetails = async (itemId: string, contractItemId: number) => {
    try {
      const response = await api.get(`purchases/contract-items/${contractItemId}/details`);
      const details = response.data;
      
      // 更新对应item的剩余数量信息
      setItems(items => items.map(item => {
        if (item.id === itemId) {
          return {
            ...item,
            remaining_quantity: details.remaining_quantity,
            max_quantity: details.total_quantity
          };
        }
        return item;
      }));
    } catch (error: any) {
      console.error('加载合同清单项详情失败:', error);
    }
  };

  // 获取项目的所有系统分类
  const getProjectSystemCategories = async (projectId: number) => {
    try {
      const response = await api.get(`purchases/system-categories/by-project/${projectId}`);
      return response.data.categories;
    } catch (error: any) {
      console.error('获取项目系统分类失败:', error);
      throw error;
    }
  };

  // 处理辅材的系统分类选择（需要加载所有可选系统）
  const handleAuxiliarySystemCategory = async (itemId: string) => {
    const projectId = form.getFieldValue('project_id');
    if (!projectId) return;

    try {
      const categories = await getProjectSystemCategories(projectId);
      setItems(items => items.map(item => 
        item.id === itemId ? { 
          ...item, 
          availableSystemCategories: categories
        } : item
      ));
    } catch (error) {
      message.error('获取系统分类失败');
    }
  };

  const handleMaterialNameChange = async (itemId: string, materialName: string) => {
    const projectId = form.getFieldValue('project_id');
    if (!projectId || !materialName) {
      // 清空相关字段
      setItems(items => items.map(item => 
        item.id === itemId ? {
          ...item,
          item_name: '',
          availableSpecifications: [],
          specification: '',
          brand: '',
          unit: '',
          contract_item_id: undefined,
          max_quantity: undefined,
          remaining_quantity: undefined,
          system_category_id: undefined,
          availableSystemCategories: []
        } : item
      ));
      return;
    }

    try {
      const [specResponse, categoryResponse] = await Promise.all([
        getSpecificationsByMaterial(projectId, materialName),
        getSystemCategoriesByMaterial(projectId, materialName)
      ]);

      setItems(items => items.map(item => {
        if (item.id === itemId) {
          const updatedItem: PurchaseEditItem = {
            ...item,
            item_name: materialName,
            availableSpecifications: specResponse.specifications || [],
            availableSystemCategories: categoryResponse.categories || [],
            // 重置相关字段，等待用户选择
            specification: '',
            brand: '',
            unit: '',
            contract_item_id: undefined,
            max_quantity: undefined,
            remaining_quantity: undefined,
            system_category_id: undefined
          };
          
          // 如果只有一个规格，自动选择
          if (specResponse.specifications?.length === 1) {
            const spec = specResponse.specifications[0];
            updatedItem.specification = spec.specification;
            updatedItem.brand = spec.brand_model;
            updatedItem.unit = spec.unit;
            updatedItem.remaining_quantity = spec.remaining_quantity;
            updatedItem.max_quantity = spec.total_quantity;
            updatedItem.contract_item_id = spec.contract_item_id;
            updatedItem.item_type = 'main';
            
            // 如果当前数量超过剩余数量，调整数量
            if (updatedItem.quantity > spec.remaining_quantity) {
              updatedItem.quantity = Math.max(1, spec.remaining_quantity);
              message.warning(`申购数量已调整为最大可申购数量 ${spec.remaining_quantity}`);
            }
          } else if (specResponse.specifications?.length > 1) {
            // 如果有多个规格选项，设置为主材但需要用户手动选择规格
            updatedItem.item_type = 'main';
          }
          
          // 如果只有一个系统分类，自动选择
          if (categoryResponse.categories?.length === 1) {
            updatedItem.system_category_id = categoryResponse.categories[0].id;
          }
          
          return updatedItem;
        }
        return item;
      }));
    } catch (error) {
      console.error('处理物料名称变化失败:', error);
      message.error('获取物料信息失败，请重试');
    }
  };

  const handleSpecificationChange = (itemId: string, specification: string) => {
    setItems(items => items.map(item => {
      if (item.id === itemId && item.availableSpecifications) {
        const spec = item.availableSpecifications.find(s => s.specification === specification);
        if (spec) {
          return {
            ...item,
            specification,
            brand: spec.brand_model,
            unit: spec.unit,
            remaining_quantity: spec.remaining_quantity,
            contract_item_id: spec.contract_item_id,
            item_type: 'main'
          };
        }
      }
      return item;
    }));
  };

  const handleSystemCategoryChange = (itemId: string, categoryId: number) => {
    setItems(items => items.map(item => {
      if (item.id === itemId) {
        return { ...item, system_category_id: categoryId };
      }
      return item;
    }));
  };

  const handleQuantityChange = (itemId: string, quantity: number) => {
    setItems(items => items.map(item => {
      if (item.id === itemId) {
        if (item.remaining_quantity !== undefined && quantity > item.remaining_quantity) {
          message.warning(`申购数量已调整为最大可申购数量 ${item.remaining_quantity}`);
          return { ...item, quantity: Math.max(1, item.remaining_quantity) };
        }
        return { ...item, quantity };
      }
      return item;
    }));
  };

  const handlePriceChange = (itemId: string, unitPrice: number) => {
    setItems(items => items.map(item => {
      if (item.id === itemId) {
        const totalPrice = unitPrice * item.quantity;
        return { ...item, unit_price: unitPrice, total_price: totalPrice };
      }
      return item;
    }));
  };

  const addItem = () => {
    const newItem: PurchaseEditItem = {
      id: generateId(),
      item_name: '',
      unit: '个',
      quantity: 1,
      item_type: 'auxiliary'
    };
    setItems([...items, newItem]);
  };

  const removeItem = (itemId: string) => {
    setItems(items.filter(item => item.id !== itemId));
  };

  const updateItem = (itemId: string, field: keyof PurchaseEditItem, value: any) => {
    setItems(items => items.map(item => {
      if (item.id === itemId) {
        return { ...item, [field]: value };
      }
      return item;
    }));
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      
      // 验证基本信息
      const values = await form.validateFields();
      
      // 验证申购明细
      if (items.length === 0) {
        message.error('请至少添加一个申购物料');
        return;
      }

      for (const item of items) {
        if (!item.item_name.trim()) {
          message.error('请填写物料名称');
          return;
        }
        if (item.quantity <= 0) {
          message.error('申购数量必须大于0');
          return;
        }
      }

      // 构造请求数据
      const requestData = {
        required_date: values.required_date?.toISOString() || null,
        remarks: values.remarks?.trim() || null,
        items: items.map(item => ({
          contract_item_id: item.contract_item_id || null,
          system_category_id: item.system_category_id || null,
          item_name: item.item_name.trim(),
          specification: item.specification?.trim() || null,
          brand: item.brand?.trim() || null,
          unit: item.unit,
          quantity: item.quantity,
          unit_price: item.unit_price || null,
          total_price: item.total_price || null,
          item_type: item.item_type,
          remarks: item.remarks?.trim() || null
        }))
      };

      await onSave(requestData);
      message.success('申购单更新成功');
      onCancel();
      
    } catch (error: any) {
      console.error('保存申购单失败:', error);
      if (error.response?.data?.detail) {
        message.error(`保存失败: ${error.response.data.detail}`);
      } else {
        message.error('保存失败，请重试');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleItemTypeChange = async (itemId: string, itemType: 'main' | 'auxiliary') => {
    if (itemType === 'main') {
      // 切换到主材时，尝试重新加载合同清单信息
      const currentItem = items.find(item => item.id === itemId);
      if (currentItem && currentItem.item_name && materialNames.includes(currentItem.item_name)) {
        // 如果物料名称在合同清单中，尝试加载规格信息
        try {
          const projectId = form.getFieldValue('project_id');
          const specResponse = await getSpecificationsByMaterial(projectId, currentItem.item_name);
          
          setItems(items => items.map(item => {
            if (item.id === itemId) {
              const updatedItem = { ...item, item_type: itemType };
              
              // 设置规格选项
              updatedItem.availableSpecifications = specResponse.specifications;
              
              // 如果只有一个规格，自动选择
              if (specResponse.specifications.length === 1) {
                const spec = specResponse.specifications[0];
                updatedItem.contract_item_id = spec.contract_item_id;
                updatedItem.specification = spec.specification;
                updatedItem.brand = spec.brand_model;
                updatedItem.unit = spec.unit;
                updatedItem.max_quantity = spec.total_quantity;
                updatedItem.remaining_quantity = spec.remaining_quantity;
                
                // 如果当前数量超过剩余数量，调整数量
                if (updatedItem.quantity > spec.remaining_quantity) {
                  updatedItem.quantity = Math.max(1, spec.remaining_quantity);
                  message.warning(`申购数量已调整为最大可申购数量 ${spec.remaining_quantity}`);
                }
              }
              
              return updatedItem;
            }
            return item;
          }));
          
        } catch (error) {
          console.error('加载规格信息失败:', error);
          // 如果加载失败，仍然切换类型，但提示用户
          setItems(items => items.map(item => {
            if (item.id === itemId) {
              return { ...item, item_type: itemType };
            }
            return item;
          }));
          message.warning('未找到该物料的合同清单信息，请检查物料名称是否正确');
        }
        return;
      }
    }
    
    // 普通类型切换或切换到辅材
    setItems(items => items.map(item => {
      if (item.id === itemId) {
        const updatedItem = { ...item, item_type: itemType };
        
        // 如果切换到辅材，清空合同清单相关限制
        if (itemType === 'auxiliary') {
          updatedItem.contract_item_id = undefined;
          updatedItem.availableSpecifications = [];
          updatedItem.max_quantity = undefined;
          updatedItem.remaining_quantity = undefined;
        }
        
        return updatedItem;
      }
      return item;
    }));
  };

  // 获取当前用户角色
  const authService = AuthService.getInstance();
  const currentUser = authService.getCurrentUser();
  const isProjectManager = currentUser?.role === 'project_manager';

  const columns = [
    {
      title: '序号',
      width: 60,
      render: (_: any, __: any, index: number) => index + 1
    },
    {
      title: '类型',
      dataIndex: 'item_type',
      width: 100,
      render: (value: 'main' | 'auxiliary', record: PurchaseEditItem) => (
        <Select
          value={value}
          style={{ width: '100%' }}
          onChange={(itemType: 'main' | 'auxiliary') => handleItemTypeChange(record.id, itemType)}
        >
          <Select.Option value="main">主材</Select.Option>
          <Select.Option value="auxiliary">辅材</Select.Option>
        </Select>
      )
    },
    {
      title: '物料名称',
      dataIndex: 'item_name',
      width: 180,
      render: (value: string, record: PurchaseEditItem) => {
        if (record.item_type === 'main') {
          // 主材：从合同清单下拉选择
          return (
            <Select
              value={value}
              onChange={(materialName) => handleMaterialNameChange(record.id, materialName)}
              placeholder="请选择物料名称"
              style={{ width: '100%' }}
              showSearch
              filterOption={(input, option: any) =>
                (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
              }
              allowClear
            >
              {materialNames.map(name => (
                <Select.Option key={name} value={name}>{name}</Select.Option>
              ))}
            </Select>
          );
        } else {
          // 辅材：自由输入
          return (
            <Input
              value={value}
              placeholder="请输入物料名称"
              onChange={(e) => updateItem(record.id, 'item_name', e.target.value)}
            />
          );
        }
      }
    },
    {
      title: '规格型号',
      dataIndex: 'specification',
      width: 160,
      render: (value: string, record: PurchaseEditItem) => {
        if (record.item_type === 'main' && record.availableSpecifications?.length) {
          // 主材且有可选规格：下拉选择
          return (
            <Select
              value={value}
              placeholder="请选择规格型号"
              style={{ width: '100%' }}
              onChange={(specification) => handleSpecificationChange(record.id, specification)}
              allowClear
            >
              {record.availableSpecifications.map((spec, index) => (
                <Select.Option key={index} value={spec.specification}>
                  <div>
                    <div>{spec.specification}</div>
                    <div style={{ fontSize: '12px', color: '#999' }}>
                      剩余: {spec.remaining_quantity}/{spec.total_quantity} {spec.unit}
                    </div>
                  </div>
                </Select.Option>
              ))}
            </Select>
          );
        } else {
          // 辅材或主材无可选规格：可以输入
          return (
            <Input
              value={value || ''}
              placeholder="规格型号"
              disabled={!!(record.item_type === 'main' && record.item_name && !record.availableSpecifications?.length)}
              onChange={(e) => updateItem(record.id, 'specification', e.target.value)}
            />
          );
        }
      }
    },
    {
      title: '品牌',
      dataIndex: 'brand',
      width: 120,
      render: (value: string, record: PurchaseEditItem) => (
        <Input
          value={value || ''}
          onChange={(e) => updateItem(record.id, 'brand', e.target.value)}
          placeholder="品牌"
          disabled={record.item_type === 'main'}
          style={record.item_type === 'main' ? { backgroundColor: '#f5f5f5', color: '#999' } : {}}
        />
      )
    },
    {
      title: '所属系统',
      dataIndex: 'system_category_id',
      width: 140,
      render: (value: number, record: PurchaseEditItem) => {
        // 如果有系统分类选择器，显示选择器（无论是否已有分类）
        if (Array.isArray(record.availableSystemCategories) && record.availableSystemCategories.length > 0) {
          return (
            <Select
              value={value}
              placeholder={record.system_category_name ? record.system_category_name : "选择系统"}
              style={{ width: '100%' }}
              onChange={(categoryId) => {
                handleSystemCategoryChange(record.id, categoryId);
                // 同时更新系统分类名称
                const selectedCategory = Array.isArray(record.availableSystemCategories) 
                  ? record.availableSystemCategories.find(cat => cat.id === categoryId)
                  : null;
                if (selectedCategory) {
                  setItems(items => items.map(item => 
                    item.id === record.id ? {
                      ...item,
                      system_category_id: categoryId,
                      system_category_name: selectedCategory.category_name
                    } : item
                  ));
                }
              }}
              allowClear
              showSearch
              filterOption={(input, option: any) =>
                (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {record.availableSystemCategories.map(cat => (
                <Select.Option key={cat.id} value={cat.id}>
                  {cat.is_suggested ? '⭐ ' : ''}{cat.category_name}
                </Select.Option>
              ))}
            </Select>
          );
        }
        
        // 如果已有系统分类名称但没有选择器，显示名称
        if (record.system_category_name) {
          return (
            <span style={{ color: '#1890ff' }}>
              {record.system_category_name}
            </span>
          );
        }
        
        // 默认显示横杠
        return <span style={{ color: '#ccc' }}>-</span>;
      }
    },
    {
      title: '单位',
      dataIndex: 'unit',
      width: 80,
      render: (value: string, record: PurchaseEditItem) => {
        if (record.item_type === 'main') {
          // 主材：不可编辑，从合同清单自动填充
          return (
            <Input
              value={value || ''}
              disabled
              style={{ backgroundColor: '#f5f5f5', color: '#999' }}
              placeholder="自动填充"
            />
          );
        } else {
          // 辅材：可选择单位
          return (
            <Select
              value={value}
              onChange={(unit) => updateItem(record.id, 'unit', unit)}
              style={{ width: '100%' }}
            >
              <Select.Option value="个">个</Select.Option>
              <Select.Option value="台">台</Select.Option>
              <Select.Option value="套">套</Select.Option>
              <Select.Option value="米">米</Select.Option>
              <Select.Option value="公斤">公斤</Select.Option>
              <Select.Option value="箱">箱</Select.Option>
              <Select.Option value="包">包</Select.Option>
            </Select>
          );
        }
      }
    },
    {
      title: '申购数量',
      dataIndex: 'quantity',
      width: 100,
      render: (value: number, record: PurchaseEditItem) => {
        const maxQuantity = record.remaining_quantity;
        const hasLimit = record.item_type === 'main' && maxQuantity !== undefined;
        
        return (
          <div>
            <InputNumber
              value={value}
              onChange={(quantity) => handleQuantityChange(record.id, quantity || 1)}
              min={1}
              max={hasLimit ? maxQuantity : undefined}
              style={{ width: '100%' }}
              placeholder="数量"
            />
            {record.item_type === 'main' && record.contract_item_id && hasLimit && (
              <div style={{ fontSize: '10px', color: '#999', marginTop: '2px' }}>
                上限: {maxQuantity}
              </div>
            )}
            {record.item_type === 'main' && !record.contract_item_id && (
              <div style={{ fontSize: '10px', color: '#ff7875', marginTop: '2px' }}>
                请选择物料和规格关联合同清单
              </div>
            )}
          </div>
        );
      }
    },
    // 价格字段：项目经理不显示
    ...(isProjectManager ? [] : [{
      title: '单价',
      dataIndex: 'unit_price',
      width: 100,
      render: (value: number, record: PurchaseEditItem) => (
        <InputNumber
          value={value}
          onChange={(price) => handlePriceChange(record.id, price || 0)}
          min={0}
          precision={2}
          style={{ width: '100%' }}
          placeholder="单价"
        />
      )
    }]),
    {
      title: '备注',
      dataIndex: 'remarks',
      width: 120,
      render: (value: string, record: PurchaseEditItem) => (
        <Input
          value={value}
          onChange={(e) => updateItem(record.id, 'remarks', e.target.value)}
          placeholder="备注"
        />
      )
    },
    {
      title: '操作',
      width: 80,
      render: (_: any, record: PurchaseEditItem) => (
        <Popconfirm
          title="确定删除这一项吗？"
          onConfirm={() => removeItem(record.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button 
            type="text" 
            icon={<DeleteOutlined />} 
            size="small" 
            danger
          />
        </Popconfirm>
      )
    }
  ];

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
              filterOption={(input, option: any) =>
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

        <Table
          columns={columns}
          dataSource={items}
          rowKey="id"
          pagination={false}
          scroll={{ x: 1000 }}
          size="small"
          bordered
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