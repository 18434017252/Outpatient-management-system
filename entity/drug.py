import pymysql

def add_drug(cursor, drug_name, stored_quantity, drug_price):
    """
    新药品入库
    
    Args:
        cursor: 数据库游标
        drug_name: 药品名称
        stored_quantity: 库存数量
        drug_price: 单价
    
    Returns:
        int: 新入库药品的编号，失败返回None
    """
    try:
        # 插入新药品信息
        sql = """
        INSERT INTO drug (drug_name, stored_quantity, drug_price, created_at) 
        VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(sql, (drug_name, stored_quantity, drug_price))
        
        # 获取刚插入的药品编号
        cursor.execute("SELECT LAST_INSERT_ID()")
        result = cursor.fetchone()
        
        if isinstance(result, tuple):
            drug_id = result[0]
        else:
            drug_id = result['LAST_INSERT_ID()']
        
        print(f"✅ 药品入库成功！药品编号: {drug_id}")
        return drug_id
        
    except Exception as e:
        print(f"❌ 药品入库失败: {e}")
        return None

def query_drug(cursor, drug_id=None, drug_name=None):
    """
    查询药品信息
    
    Args:
        cursor: 数据库游标
        drug_id: 药品编号（可选）
        drug_name: 药品名称（可选，支持模糊查询）
    
    Returns:
        list: 查询结果列表
    """
    try:
        # 构建查询条件
        conditions = []
        params = []
        
        if drug_id:
            conditions.append("drug_id = %s")
            params.append(drug_id)
        
        if drug_name:
            conditions.append("drug_name LIKE %s")
            params.append(f"%{drug_name}%")
        
        # 如果没有查询条件，返回所有药品
        if not conditions:
            sql = "SELECT * FROM drug ORDER BY drug_id"
        else:
            sql = f"SELECT * FROM drug WHERE {' AND '.join(conditions)} ORDER BY drug_id"
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # 输出查询结果
        print(f"\n🔍 查询到 {len(results)} 条药品记录")
        print("-" * 90)
        print(f"{'药品编号':<8} {'药品名称':<20} {'库存数量':<10} {'单价':<10} {'创建时间':<20}")
        print("-" * 90)
        
        if results:
            for drug in results:
                # 确保时间字段正确显示
                created_time = str(drug['created_at']) if drug['created_at'] else 'NULL'
                print(f"{drug['drug_id']:<8} {drug['drug_name']:<20} {drug['stored_quantity']:<10} "
                      f"{drug['drug_price']:<10} {created_time:<20}")
        else:
            print("  没有找到匹配的药品记录")
        
        print("-" * 90)
        
        return results
        
    except Exception as e:
        print(f"❌ 查询药品失败: {e}")
        return []

def update_drug_info(cursor, drug_id, stored_quantity=None, drug_price=None):
    """
    修改药品信息（库存或价格）
    
    Args:
        cursor: 数据库游标
        drug_id: 药品编号
        stored_quantity: 新库存数量（可选）
        drug_price: 新单价（可选）
    
    Returns:
        bool: 修改是否成功
    """
    try:
        # 检查药品是否存在
        cursor.execute("SELECT * FROM drug WHERE drug_id = %s", (drug_id,))
        if not cursor.fetchone():
            print(f"❌ 药品编号 {drug_id} 不存在")
            return False
        
        # 构建更新语句
        updates = []
        params = []
        
        if stored_quantity is not None:
            updates.append("stored_quantity = %s")
            params.append(stored_quantity)
        
        if drug_price is not None:
            updates.append("drug_price = %s")
            params.append(drug_price)
        
        if not updates:
            print("❌ 没有提供要更新的信息")
            return False
        
        # 添加更新时间和药品编号
        updates.append("updated_at = NOW()")
        params.append(drug_id)
        
        sql = f"UPDATE drug SET {', '.join(updates)} WHERE drug_id = %s"
        cursor.execute(sql, params)
        
        print(f"✅ 药品 {drug_id} 信息更新成功")
        return True
        
    except Exception as e:
        print(f"❌ 更新药品信息失败: {e}")
        return False

def get_drug_info(cursor, drug_id, info_type='drug_name'):
    """
    根据药品编号获取指定的药品信息
    
    Args:
        cursor: 数据库游标
        drug_id: 药品编号
        info_type: 信息类型，可选值：'drug_name'（药品名称）、'quantity'（库存数量）、'price'（单价）
    
    Returns:
        根据info_type返回对应的信息值，如果不存在或查询失败返回None
    """
    try:
        # 检查药品是否存在
        if not check_drug_exists(cursor, drug_id):
            print(f"❌ 获取药品信息失败：药品编号 {drug_id} 不存在")
            return None
        
        # 查询药品记录
        cursor.execute("SELECT drug_name, stored_quantity, drug_price FROM drug WHERE drug_id = %s", (drug_id,))
        drug = cursor.fetchone()
        
        if not drug:
            print(f"❌ 获取药品信息失败：药品编号 {drug_id} 的记录不存在")
            return None
        
        # 根据info_type返回对应的信息
        if info_type == 'drug_name':
            result = drug['drug_name']
            print(f"✅ 药品编号 {drug_id} 对应的药品名称: {result}")
        elif info_type == 'quantity':
            result = drug['stored_quantity']
            print(f"✅ 药品编号 {drug_id} 对应的库存数量: {result}")
        elif info_type == 'price':
            result = drug['drug_price']
            print(f"✅ 药品编号 {drug_id} 对应的单价: {result}")
        else:
            print(f"❌ 无效的信息类型: {info_type}，请使用 'drug_name', 'quantity' 或 'price'")
            return None
        
        return result
        
    except Exception as e:
        print(f"❌ 获取药品信息失败: {e}")
        return None

def check_drug_exists(cursor, drug_id):
    """
    判断药品ID是否存在
    
    Args:
        cursor: 数据库游标
        drug_id: 药品编号
    
    Returns:
        bool: 存在返回True，不存在返回False
    """
    try:
        # 查询药品是否存在
        cursor.execute("SELECT drug_id FROM drug WHERE drug_id = %s", (drug_id,))
        result = cursor.fetchone()
        
        if result:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 检查药品ID失败: {e}")
        return False
