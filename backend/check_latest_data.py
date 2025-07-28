# 检查最新的数据库状态
from app.core.database import engine
from sqlalchemy import text

def check_latest_data():
    """检查数据库中的最新数据"""
    conn = engine.connect()
    
    try:
        # 检查版本数
        result = conn.execute(text('SELECT COUNT(*) FROM contract_file_versions;'))
        total_versions = result.fetchone()[0]
        print(f'数据库中总版本数: {total_versions}')
        
        # 检查最新版本
        result = conn.execute(text('''
            SELECT id, project_id, version_number, original_filename, upload_time 
            FROM contract_file_versions 
            ORDER BY id DESC 
            LIMIT 5
        '''))
        
        print('\n最新的5个版本:')
        for row in result.fetchall():
            print(f'  版本ID={row[0]}, 项目ID={row[1]}, 版本号={row[2]}')
            print(f'    文件名={row[3]}')
            print(f'    上传时间={row[4]}')
        
        # 检查每个版本的设备数量
        result = conn.execute(text('''
            SELECT v.id, v.project_id, v.version_number, v.original_filename,
                   COUNT(i.id) as item_count,
                   COUNT(DISTINCT c.id) as category_count
            FROM contract_file_versions v
            LEFT JOIN contract_items i ON v.id = i.version_id
            LEFT JOIN system_categories c ON v.id = c.version_id
            GROUP BY v.id, v.project_id, v.version_number, v.original_filename
            ORDER BY v.id DESC
            LIMIT 5
        '''))
        
        print('\n版本详细统计:')
        for row in result.fetchall():
            print(f'  版本{row[2]} (ID={row[0]}): {row[5]}个分类, {row[4]}个设备')
            print(f'    文件: {row[3]}')
        
        # 检查最新版本的分类详情
        result = conn.execute(text('''
            SELECT version_id, category_name, total_items_count 
            FROM system_categories 
            WHERE version_id = (SELECT MAX(id) FROM contract_file_versions)
            ORDER BY id
        '''))
        
        latest_categories = result.fetchall()
        if latest_categories:
            version_id = latest_categories[0][0]
            print(f'\n最新版本(ID={version_id})的系统分类:')
            for row in latest_categories:
                print(f'  - {row[1]}: {row[2]}个设备')
        else:
            print('\n最新版本没有系统分类数据')
            
    except Exception as e:
        print(f'检查失败: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    check_latest_data()