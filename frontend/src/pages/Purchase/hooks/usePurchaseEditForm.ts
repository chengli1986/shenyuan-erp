import { useState, useEffect } from 'react';
import { Form, message } from 'antd';
import dayjs from 'dayjs';
import api from '../../../services/api';
import { AuthService } from '../../../services/auth';
import type { PurchaseDetailItem } from '../../../types/purchase';

// Generate unique ID, replacing uuid
const generateId = () => Math.random().toString(36).substring(2) + Date.now().toString(36);

export interface Project {
  id: number;
  project_name: string;
  customer_name: string;
  project_manager: string;
}

export interface SystemCategory {
  id: number;
  category_name: string;
  category_code?: string;
  description?: string;
  is_suggested?: boolean;
  items_count?: number;
}

export interface SpecificationOption {
  specification: string;
  brand_model: string;
  unit: string;
  remaining_quantity?: number;
  total_quantity?: number;
  contract_item_id?: number;
}

export interface PurchaseEditItem {
  id: string;
  contract_item_id?: number;
  system_category_id?: number;
  system_category_name?: string;
  item_name: string;
  specification?: string;
  brand?: string;
  unit: string;
  quantity: number;
  unit_price?: number;
  total_price?: number;
  item_type: 'main' | 'auxiliary';
  remarks?: string;

  // Contract list info (for quantity caps)
  remaining_quantity?: number;
  max_quantity?: number;

  // UI state
  availableSpecifications?: SpecificationOption[];
  availableSystemCategories?: SystemCategory[];
}

export interface PurchaseRequest {
  id: number;
  request_code: string;
  project_id: number;
  project_name?: string;
  required_date?: string;
  remarks?: string;
  items?: PurchaseDetailItem[];
}

export interface PurchaseEditFormProps {
  visible: boolean;
  purchaseData: PurchaseRequest | null;
  onCancel: () => void;
  onSave: (data: Record<string, unknown>) => Promise<void>;
}

export function usePurchaseEditForm({ visible, purchaseData, onCancel, onSave }: PurchaseEditFormProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [items, setItems] = useState<PurchaseEditItem[]>([]);
  const [materialNames, setMaterialNames] = useState<string[]>([]);

  // Current user role
  const authService = AuthService.getInstance();
  const currentUser = authService.getCurrentUser();
  const isProjectManager = currentUser?.role === 'project_manager';

  // --- API helper functions ---

  const loadProjects = async () => {
    try {
      const response = await api.get('projects/');
      setProjects(response.data.items || []);
    } catch (error: unknown) {
      console.error('加载项目列表失败:', error);
      message.error('加载项目列表失败');
    }
  };

  const loadMaterialNames = async (projectId: number) => {
    try {
      const response = await api.get(`purchases/material-names/by-project/${projectId}`);
      setMaterialNames(response.data.material_names || []);
    } catch (error: unknown) {
      console.error('加载物料名称失败:', error);
    }
  };

  const getSpecificationsByMaterial = async (projectId: number, materialName: string) => {
    try {
      const response = await api.get('purchases/specifications/by-material', {
        params: { project_id: projectId, item_name: materialName }
      });
      return response.data;
    } catch (error: unknown) {
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
    } catch (error: unknown) {
      console.error('加载系统分类失败:', error);
      return { categories: [] };
    }
  };

  const getAllSystemCategoriesByProject = async (projectId: number) => {
    try {
      const response = await api.get(`purchases/system-categories/by-project/${projectId}`);
      const data = response.data;
      if (Array.isArray(data)) {
        return data;
      } else if (data && Array.isArray(data.categories)) {
        return data.categories;
      } else {
        return [];
      }
    } catch (error: unknown) {
      console.error('加载项目系统分类失败:', error);
      return [];
    }
  };

  const loadContractItemDetails = async (itemId: string, contractItemId: number) => {
    try {
      const response = await api.get(`purchases/contract-items/${contractItemId}/details`);
      const details = response.data;

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
    } catch (error: unknown) {
      console.error('加载合同清单项详情失败:', error);
    }
  };

  const getProjectSystemCategories = async (projectId: number) => {
    try {
      const response = await api.get(`purchases/system-categories/by-project/${projectId}`);
      return response.data.categories;
    } catch (error: unknown) {
      console.error('获取项目系统分类失败:', error);
      throw error;
    }
  };

  // --- Effects ---

  // Initialize form data
  useEffect(() => {
    if (visible && purchaseData) {
      form.setFieldsValue({
        project_id: purchaseData.project_id,
        required_date: purchaseData.required_date ? dayjs(purchaseData.required_date) : null,
        remarks: purchaseData.remarks || ''
      });

      const convertedItems = (purchaseData.items || []).map((item: PurchaseDetailItem) => {
        const converted = {
          id: generateId(),
          contract_item_id: item.contract_item_id,
          system_category_id: item.system_category_id,
          system_category_name: item.system_category_name,
          item_name: item.item_name,
          specification: item.specification,
          brand: item.brand_model || item.brand,
          unit: item.unit,
          quantity: typeof item.quantity === 'string' ? parseFloat(item.quantity || '0') : (item.quantity || 0),
          unit_price: item.unit_price ? (typeof item.unit_price === 'string' ? parseFloat(item.unit_price) : item.unit_price) : undefined,
          total_price: item.total_price ? (typeof item.total_price === 'string' ? parseFloat(item.total_price) : item.total_price) : undefined,
          item_type: (item.item_type === 'main' || item.item_type === 'auxiliary' ? item.item_type : 'auxiliary') as 'main' | 'auxiliary',
          remarks: item.remarks || '',
          remaining_quantity: item.remaining_quantity,
          max_quantity: undefined as number | undefined
        };

        return converted;
      });

      setItems(convertedItems);

      // Load project system categories for all items
      const projectId = purchaseData.project_id;
      getAllSystemCategoriesByProject(projectId).then(allCategories => {
        const categoriesArray = Array.isArray(allCategories) ? allCategories : [];
        setItems(prevItems => prevItems.map(prevItem => ({
          ...prevItem,
          availableSystemCategories: categoriesArray
        })));
      });

      // For main materials, async load remaining quantity info and specification options
      convertedItems.forEach(async (item) => {
        if (item.item_type === 'main' && item.contract_item_id) {
          try {
            await loadContractItemDetails(item.id, item.contract_item_id);
          } catch (error) {
            console.error('加载合同清单项详情失败:', error);
          }
        }
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
      form.resetFields();
      setItems([]);
    }
  }, [visible, purchaseData, form]);

  // Load projects
  useEffect(() => {
    if (visible) {
      loadProjects();
    }
  }, [visible]);

  // Load material names when project changes
  useEffect(() => {
    const projectId = form.getFieldValue('project_id');
    if (projectId && visible) {
      loadMaterialNames(projectId);
    }
  }, [visible, purchaseData?.project_id]);

  // --- Event handlers ---

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
            specification: '',
            brand: '',
            unit: '',
            contract_item_id: undefined,
            max_quantity: undefined,
            remaining_quantity: undefined,
            system_category_id: undefined
          };

          if (specResponse.specifications?.length === 1) {
            const spec = specResponse.specifications[0];
            updatedItem.specification = spec.specification;
            updatedItem.brand = spec.brand_model;
            updatedItem.unit = spec.unit;
            updatedItem.remaining_quantity = spec.remaining_quantity;
            updatedItem.max_quantity = spec.total_quantity;
            updatedItem.contract_item_id = spec.contract_item_id;
            updatedItem.item_type = 'main';

            if (updatedItem.quantity > spec.remaining_quantity) {
              updatedItem.quantity = Math.max(1, spec.remaining_quantity);
              message.warning(`申购数量已调整为最大可申购数量 ${spec.remaining_quantity}`);
            }
          } else if (specResponse.specifications?.length > 1) {
            updatedItem.item_type = 'main';
          }

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

  const updateItem = (itemId: string, field: keyof PurchaseEditItem, value: string | number | boolean | undefined | null) => {
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

      const values = await form.validateFields();

      if (items.length === 0) {
        message.error('请至少添加一个申购物料');
        return;
      }

      // Remaining quantity validation
      const problematicItems = items.filter(item => {
        if (item.item_type === 'main') {
          if (item.remaining_quantity !== undefined && item.remaining_quantity <= 0) {
            return true;
          }
          if (item.remaining_quantity !== undefined && item.quantity > item.remaining_quantity) {
            return true;
          }
        }
        return false;
      });

      if (problematicItems.length > 0) {
        const itemList = problematicItems.map((item, index) => {
          const remaining = item.remaining_quantity || 0;
          return `${index + 1}. ${item.item_name} (${item.specification}) - 申购: ${item.quantity}, 剩余: ${remaining}`;
        }).join('\n');

        const errorMessage = `申购数量验证失败！\n\n以下物料的剩余可申购数量不足：\n\n${itemList}\n\n请调整申购数量后再保存。`;
        alert(errorMessage);

        setLoading(false);
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

    } catch (error: unknown) {
      console.error('保存申购单失败:', error);
      const axiosError = error as { response?: { data?: { detail?: string } } };
      if (axiosError.response?.data?.detail) {
        message.error(`保存失败: ${axiosError.response.data.detail}`);
      } else {
        message.error('保存失败，请重试');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleItemTypeChange = async (itemId: string, itemType: 'main' | 'auxiliary') => {
    if (itemType === 'main') {
      const currentItem = items.find(item => item.id === itemId);
      if (currentItem && currentItem.item_name && materialNames.includes(currentItem.item_name)) {
        try {
          const projectId = form.getFieldValue('project_id');
          const specResponse = await getSpecificationsByMaterial(projectId, currentItem.item_name);

          setItems(items => items.map(item => {
            if (item.id === itemId) {
              const updatedItem = { ...item, item_type: itemType };

              updatedItem.availableSpecifications = specResponse.specifications;

              if (specResponse.specifications.length === 1) {
                const spec = specResponse.specifications[0];
                updatedItem.contract_item_id = spec.contract_item_id;
                updatedItem.specification = spec.specification;
                updatedItem.brand = spec.brand_model;
                updatedItem.unit = spec.unit;
                updatedItem.max_quantity = spec.total_quantity;
                updatedItem.remaining_quantity = spec.remaining_quantity;

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

    setItems(items => items.map(item => {
      if (item.id === itemId) {
        const updatedItem = { ...item, item_type: itemType };

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

  return {
    form,
    loading,
    projects,
    items,
    setItems,
    materialNames,
    isProjectManager,
    handleMaterialNameChange,
    handleSpecificationChange,
    handleSystemCategoryChange,
    handleQuantityChange,
    handlePriceChange,
    handleItemTypeChange,
    handleAuxiliarySystemCategory,
    addItem,
    removeItem,
    updateItem,
    handleSave,
  };
}
