/**
 * 采购请购相关的API服务
 */

import {
  PurchaseRequest,
  PurchaseRequestCreate,
  PurchaseRequestUpdate,
  PurchaseRequestWithItems,
  PurchaseRequestListResponse,
  PurchaseRequestSubmit,
  PurchaseRequestQuote,
  PurchaseRequestApprove,
  Supplier,
  SupplierCreate,
  SupplierUpdate,
  SupplierListResponse,
  AuxiliaryTemplate,
  AuxiliaryTemplateCreate,
  AuxiliaryRecommendation
} from '../types/purchase';

// 使用相对路径通过代理访问API
const API_BASE = '/api/v1';

// 通用请求处理函数
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP ${response.status}: ${errorText}`);
  }
  return response.json();
}

// ============================
// 申购单管理 API
// ============================

/**
 * 获取申购单列表
 */
export async function getPurchaseRequests(params?: {
  page?: number;
  size?: number;
  project_id?: number;
  status?: string;
  requester_id?: number;
  search?: string;
}): Promise<PurchaseRequestListResponse> {
  const queryString = new URLSearchParams();
  
  if (params?.page) queryString.append('page', params.page.toString());
  if (params?.size) queryString.append('size', params.size.toString());
  if (params?.project_id) queryString.append('project_id', params.project_id.toString());
  if (params?.status) queryString.append('status', params.status);
  if (params?.requester_id) queryString.append('requester_id', params.requester_id.toString());
  if (params?.search) queryString.append('search', params.search);

  const url = `${API_BASE}/purchases/${queryString.toString() ? `?${queryString}` : ''}`;
  const response = await fetch(url);
  return handleResponse<PurchaseRequestListResponse>(response);
}

/**
 * 获取申购单详情
 */
export async function getPurchaseRequest(requestId: number): Promise<PurchaseRequestWithItems> {
  const response = await fetch(`${API_BASE}/purchases/${requestId}`);
  return handleResponse<PurchaseRequestWithItems>(response);
}

/**
 * 创建申购单
 */
export async function createPurchaseRequest(
  requestData: PurchaseRequestCreate
): Promise<PurchaseRequest> {
  const response = await fetch(`${API_BASE}/purchases/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestData),
  });
  return handleResponse<PurchaseRequest>(response);
}

/**
 * 更新申购单
 */
export async function updatePurchaseRequest(
  requestId: number,
  updateData: PurchaseRequestUpdate
): Promise<PurchaseRequest> {
  const response = await fetch(`${API_BASE}/purchases/${requestId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updateData),
  });
  return handleResponse<PurchaseRequest>(response);
}

/**
 * 提交申购单
 */
export async function submitPurchaseRequest(requestId: number): Promise<PurchaseRequest> {
  const response = await fetch(`${API_BASE}/purchases/${requestId}/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  });
  return handleResponse<PurchaseRequest>(response);
}

/**
 * 申购单询价
 */
export async function quotePurchaseRequest(
  requestId: number,
  quoteData: PurchaseRequestQuote
): Promise<PurchaseRequest> {
  const response = await fetch(`${API_BASE}/purchases/${requestId}/quote`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(quoteData),
  });
  return handleResponse<PurchaseRequest>(response);
}

/**
 * 审批申购单
 */
export async function approvePurchaseRequest(
  requestId: number,
  approvalData: PurchaseRequestApprove
): Promise<PurchaseRequest> {
  const response = await fetch(`${API_BASE}/purchases/${requestId}/approve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(approvalData),
  });
  return handleResponse<PurchaseRequest>(response);
}

/**
 * 删除申购单
 */
export async function deletePurchaseRequest(requestId: number): Promise<{ detail: string }> {
  const response = await fetch(`${API_BASE}/purchases/${requestId}`, {
    method: 'DELETE',
  });
  return handleResponse<{ detail: string }>(response);
}

// ============================
// 供应商管理 API  
// ============================

/**
 * 获取供应商列表
 */
export async function getSuppliers(params?: {
  page?: number;
  size?: number;
  search?: string;
  is_active?: boolean;
}): Promise<SupplierListResponse> {
  const queryString = new URLSearchParams();
  
  if (params?.page) queryString.append('page', params.page.toString());
  if (params?.size) queryString.append('size', params.size.toString());
  if (params?.search) queryString.append('search', params.search);
  if (params?.is_active !== undefined) queryString.append('is_active', params.is_active.toString());

  const url = `${API_BASE}/purchases/suppliers/${queryString.toString() ? `?${queryString}` : ''}`;
  const response = await fetch(url);
  return handleResponse<SupplierListResponse>(response);
}

/**
 * 创建供应商
 */
export async function createSupplier(supplierData: SupplierCreate): Promise<Supplier> {
  const response = await fetch(`${API_BASE}/purchases/suppliers/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(supplierData),
  });
  return handleResponse<Supplier>(response);
}

/**
 * 更新供应商
 */
export async function updateSupplier(
  supplierId: number,
  updateData: SupplierUpdate
): Promise<Supplier> {
  const response = await fetch(`${API_BASE}/purchases/suppliers/${supplierId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updateData),
  });
  return handleResponse<Supplier>(response);
}

// ============================
// 辅材智能推荐 API
// ============================

/**
 * 根据主材推荐辅材
 */
export async function getAuxiliaryRecommendations(
  mainMaterialId: number
): Promise<AuxiliaryRecommendation[]> {
  const response = await fetch(
    `${API_BASE}/purchases/auxiliary/recommend?main_material_id=${mainMaterialId}`
  );
  return handleResponse<AuxiliaryRecommendation[]>(response);
}

/**
 * 创建辅材模板
 */
export async function createAuxiliaryTemplate(
  templateData: AuxiliaryTemplateCreate
): Promise<AuxiliaryTemplate> {
  const response = await fetch(`${API_BASE}/purchases/auxiliary/templates/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(templateData),
  });
  return handleResponse<AuxiliaryTemplate>(response);
}

// ============================
// 工具函数
// ============================

/**
 * 格式化申购单状态
 */
export function formatPurchaseStatus(status: string): string {
  const statusMap: Record<string, string> = {
    'draft': '草稿',
    'submitted': '已提交',
    'price_quoted': '已询价',
    'dept_approved': '部门审批通过',
    'final_approved': '最终审批通过',
    'rejected': '已拒绝',
    'cancelled': '已取消',
    'completed': '已完成'
  };
  return statusMap[status] || status;
}

/**
 * 格式化物料类型
 */
export function formatItemType(itemType: string): string {
  const typeMap: Record<string, string> = {
    'main': '主材',
    'auxiliary': '辅材'
  };
  return typeMap[itemType] || itemType;
}

/**
 * 格式化审批状态
 */
export function formatApprovalStatus(status: string): string {
  const statusMap: Record<string, string> = {
    'pending': '待审批',
    'approved': '已通过',
    'rejected': '已拒绝'
  };
  return statusMap[status] || status;
}

/**
 * 获取申购单状态颜色
 */
export function getPurchaseStatusColor(status: string): string {
  const colorMap: Record<string, string> = {
    'draft': 'default',
    'submitted': 'processing',
    'price_quoted': 'warning',
    'dept_approved': 'success',
    'final_approved': 'success',
    'rejected': 'error',
    'cancelled': 'default',
    'completed': 'success'
  };
  return colorMap[status] || 'default';
}