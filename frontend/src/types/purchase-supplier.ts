/**
 * 供应商、辅材模板、入库批次相关类型定义
 */

// 供应商相关类型
export interface Supplier {
  id: number;
  supplier_name: string;
  supplier_code?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  business_license?: string;
  tax_number?: string;
  bank_account?: string;
  rating?: number;
  remarks?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SupplierCreate {
  supplier_name: string;
  supplier_code?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  business_license?: string;
  tax_number?: string;
  bank_account?: string;
  rating?: number;
  remarks?: string;
}

export interface SupplierUpdate {
  supplier_name?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  rating?: number;
  is_active?: boolean;
  remarks?: string;
}

export interface SupplierListResponse {
  items: Supplier[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface SupplierQueryParams {
  page?: number;
  size?: number;
  search?: string;
  is_active?: boolean;
}

// 辅材模板相关类型
export interface AuxiliaryTemplateItem {
  item_name: string;
  specification?: string;
  unit?: string;
  ratio?: number;
  is_required: boolean;
  reference_price?: number;
  remarks?: string;
  sort_order: number;
}

export interface AuxiliaryTemplate {
  id: number;
  template_name: string;
  project_type?: string;
  description?: string;
  usage_count: number;
  created_at: string;
  updated_at?: string;
  items: AuxiliaryTemplateItem[];
}

export interface AuxiliaryTemplateCreate {
  template_name: string;
  project_type?: string;
  description?: string;
  items: AuxiliaryTemplateItem[];
}

// 辅材智能推荐类型
export interface AuxiliaryRecommendation {
  item_name: string;
  specification?: string;
  unit?: string;
  brand?: string;
  ratio?: number;
  is_required?: boolean;
  reference_price?: number;
  source: string;
  confidence: number;
  count?: number;
  avg_quantity?: number;
}

// 入库批次相关类型
export interface InboundBatch {
  id: number;
  batch_number: string;
  purchase_request_item_id: number;
  inbound_quantity: number;
  unit_price?: number;
  quality_status: string;
  quality_check_notes?: string;
  storage_location?: string;
  supplier_batch_info?: Record<string, unknown>;
  inbound_date: string;
  operator_id?: number;
  remarks?: string;
  created_at: string;
}

export interface InboundBatchCreate {
  purchase_request_item_id: number;
  inbound_quantity: number;
  unit_price?: number;
  quality_status?: string;
  quality_check_notes?: string;
  storage_location?: string;
  supplier_batch_info?: Record<string, unknown>;
  remarks?: string;
}
