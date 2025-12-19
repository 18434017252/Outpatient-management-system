import pymysql

def create_department(cursor, department_name):
    """
    创建新科室
    
    Args:
        cursor: 数据库游标
        department_name: 科室名称
    
    Returns:
        int: 新创建科室的编号，失败返回None
    """
    try:
        # 检查科室名称是否已存在
        cursor.execute("SELECT department_id FROM department WHERE department_name = %s", (department_name,))
        if cursor.fetchone():
            print(f"❌ 科室 '{department_name}' 已存在")
            return None
        
        # 插入新科室
        sql = """
        INSERT INTO department (department_name, created_at) 
        VALUES (%s, NOW())
        """
        cursor.execute(sql, (department_name,))
        
        # 获取刚插入的科室编号
        cursor.execute("SELECT LAST_INSERT_ID()")
        result = cursor.fetchone()
        
        if isinstance(result, tuple):
            department_id = result[0]
        else:
            department_id = result['LAST_INSERT_ID()']
        
        print(f"✅ 科室创建成功！科室编号: {department_id}, 科室名称: {department_name}")
        return department_id
        
    except Exception as e:
        print(f"❌ 创建科室失败: {e}")
        return None

def update_department(cursor, department_id, new_department_name):
    """
    更新科室名称
    
    Args:
        cursor: 数据库游标
        department_id: 科室编号
        new_department_name: 新的科室名称
    
    Returns:
        bool: 更新是否成功
    """
    try:
        # 检查科室是否存在
        cursor.execute("SELECT department_name FROM department WHERE department_id = %s", (department_id,))
        old_department = cursor.fetchone()
        
        if not old_department:
            print(f"❌ 科室编号 {department_id} 不存在")
            return False
        
        old_name = old_department['department_name'] if isinstance(old_department, dict) else old_department[1]
        
        # 检查新名称是否与其他科室重复
        cursor.execute("SELECT department_id FROM department WHERE department_name = %s AND department_id != %s", 
                      (new_department_name, department_id))
        if cursor.fetchone():
            print(f"❌ 科室名称 '{new_department_name}' 已被其他科室使用")
            return False
        
        # 更新科室名称
        sql = """
        UPDATE department 
        SET department_name = %s, updated_at = NOW() 
        WHERE department_id = %s
        """
        cursor.execute(sql, (new_department_name, department_id))
        
        print(f"✅ 科室更新成功！科室编号: {department_id}")
        print(f"   原名称: {old_name}")
        print(f"   新名称: {new_department_name}")
        return True
        
    except Exception as e:
        print(f"❌ 更新科室失败: {e}")
        return False

def query_department(cursor, department_id=None, department_name=None):
    """
    查询科室信息
    
    Args:
        cursor: 数据库游标
        department_id: 科室编号（可选）
        department_name: 科室名称（可选，支持模糊查询）
    
    Returns:
        list: 查询结果列表
    """
    try:
        # 构建查询条件
        conditions = []
        params = []
        
        if department_id:
            conditions.append("department_id = %s")
            params.append(department_id)
        
        if department_name:
            conditions.append("department_name LIKE %s")
            params.append(f"%{department_name}%")
        
        # 构建SQL查询
        if not conditions:
            sql = "SELECT * FROM department ORDER BY department_id"
        else:
            sql = f"SELECT * FROM department WHERE {' AND '.join(conditions)} ORDER BY department_id"
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # 输出查询结果
        print(f"\n🔍 查询到 {len(results)} 条科室记录")
        print("-" * 80)
        print(f"{'科室编号':<10} {'科室名称':<20} {'创建时间':<20} {'更新时间':<20}")
        print("-" * 80)
        
        if results:
            for dept in results:
                created_time = str(dept['created_at']) if dept['created_at'] else 'NULL'
                updated_time = str(dept['updated_at']) if dept['updated_at'] else 'NULL'
                
                print(f"{dept['department_id']:<10} {dept['department_name']:<20} "
                      f"{created_time:<20} {updated_time:<20}")
        else:
            print("  没有找到匹配的科室记录")
        
        print("-" * 80)
        
        return results
        
    except Exception as e:
        print(f"❌ 查询科室失败: {e}")
        return []
    
def check_department_exists(cursor, department_id):
    """
    判断科室ID是否存在
    
    Args:
        cursor: 数据库游标
        department_id: 科室编号
    
    Returns:
        bool: 存在返回True，不存在返回False
    """
    try:
        # 查询科室是否存在
        cursor.execute("SELECT department_id FROM department WHERE department_id = %s", (department_id,))
        result = cursor.fetchone()
        
        if result:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 检查科室ID失败: {e}")
        return False