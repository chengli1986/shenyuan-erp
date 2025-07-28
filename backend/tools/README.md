# 开发工具 (Development Tools)

本目录包含开发和调试过程中使用的实用工具脚本。

## 数据库工具

### check_database_tables.py
- **用途**: 检查数据库表结构和数据完整性
- **使用**: `python tools/check_database_tables.py`
- **说明**: 验证数据库模型是否正确创建，检查表关系
- **数据库**: 使用当前项目的 `erp_test.db`

### debug_database_data.py  
- **用途**: 调试数据库中的具体数据内容
- **使用**: `python tools/debug_database_data.py`
- **说明**: 查看和分析数据库中的实际数据，用于排查数据问题

## Excel处理工具

### check_excel_headers.py
- **用途**: 检查Excel文件的表头结构
- **使用**: `python tools/check_excel_headers.py`
- **说明**: 验证Excel模板的表头格式是否符合解析要求

### debug_column_mapping.py
- **用途**: 调试Excel列映射过程
- **使用**: `python tools/debug_column_mapping.py`  
- **说明**: 排查Excel解析中的列名映射问题

## 使用说明

1. 所有工具都应该从backend根目录运行
2. 确保已激活虚拟环境并安装依赖
3. 这些工具主要用于开发调试，不是生产代码的一部分
4. 工具可能会随着项目发展而更新或删除

## 注意事项

- 运行前确保数据库文件存在
- 某些工具可能需要特定的Excel文件路径
- 建议在开发环境中使用，避免在生产环境运行