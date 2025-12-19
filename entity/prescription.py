import pymysql
import entity.registration as registration_module
import entity.drug as drug_module
import entity.payment as payment_module

def create_prescription(cursor, registration_id, drug_id, quantity, payment_id, use_stored_procedure=True):
    """
    开具新处方
    
    Args:
        cursor: 数据库游标
        registration_id: 挂号编号
        drug_id: 药品编号
        quantity: 药品数量
        payment_id: 缴费号
        use_stored_procedure: 是否使用存储过程（默认True）
    
    Returns:
        int: 新创建的处方号，失败返回None
    """
    try:
        if use_stored_procedure:
            # 使用存储过程开具处方并自动更新库存
            cursor.callproc('sp_create_prescription_with_inventory_update', 
                          [registration_id, drug_id, quantity, payment_id, 0, 0, ''])
            
            # 获取输出参数
            cursor.execute("SELECT @_sp_create_prescription_with_inventory_update_4 AS prescription_id, "
                          "@_sp_create_prescription_with_inventory_update_5 AS result_code, "
                          "@_sp_create_prescription_with_inventory_update_6 AS result_message")
            result = cursor.fetchone()
            
            if result['result_code'] == 0:
                prescription_id = result['prescription_id']
                
                # 查询并打印详细信息
                cursor.execute("SELECT p.name FROM registration r JOIN patient p ON r.patient_id = p.patient_id WHERE r.registration_id = %s", (registration_id,))
                patient = cursor.fetchone()
                patient_name = patient['name'] if patient else "未知病人"

                cursor.execute("SELECT drug_name FROM drug WHERE drug_id = %s", (drug_id,))
                drug_info = cursor.fetchone()
                drug_name = drug_info['drug_name'] if drug_info else "未知药品"
                
                print(f"✅ 处方开具成功！（使用存储过程）")
                print(f"   处方号: {prescription_id}")
                print(f"   病人: {patient_name} (挂号号: {registration_id})")
                print(f"   药品: {drug_name} (药品ID: {drug_id})")
                print(f"   数量: {quantity}")
                print(f"   关联缴费号: {payment_id}")
                print(f"   药品库存已自动更新")
                
                return prescription_id
            else:
                print(f"❌ {result['result_message']}")
                return None
        else:
            # 原有的直接SQL方式
            # 1. 检查挂号是否存在
            if not registration_module.check_registration_exists(cursor, registration_id):
                print(f"❌ 开具处方失败：挂号编号 {registration_id} 不存在")
                return None

            # 2. 检查药品是否存在
            if not drug_module.check_drug_exists(cursor, drug_id):
                print(f"❌ 开具处方失败：药品编号 {drug_id} 不存在")
                return None

            # 3. 检查缴费记录是否存在
            if not payment_module.check_payment_exists(cursor, payment_id):
                print(f"❌ 开具处方失败：缴费号 {payment_id} 不存在")
                return None
            
            # 4. 检查药品库存是否足够
            cursor.execute("SELECT stored_quantity FROM drug WHERE drug_id = %s", (drug_id,))
            drug = cursor.fetchone()
            if not drug or drug['stored_quantity'] < quantity:
                print(f"❌ 开具处方失败：药品库存不足。当前库存: {drug['stored_quantity'] if drug else 0}, 需求: {quantity}")
                return None

            # 5. 插入新处方记录
            sql = """
            INSERT INTO prescription (registration_id, drug_id, quantity, payment_id, created_at) 
            VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (registration_id, drug_id, quantity, payment_id))
            
            # 6. 获取刚插入的处方号
            cursor.execute("SELECT LAST_INSERT_ID()")
            result = cursor.fetchone()
            
            if isinstance(result, tuple):
                prescription_id = result[0]
            else:
                prescription_id = result['LAST_INSERT_ID()']
            
            # 7. 查询并打印详细信息
            # 获取病人姓名
            cursor.execute("SELECT p.name FROM registration r JOIN patient p ON r.patient_id = p.patient_id WHERE r.registration_id = %s", (registration_id,))
            patient = cursor.fetchone()
            patient_name = patient['name'] if patient else "未知病人"

            # 获取药品名称
            cursor.execute("SELECT drug_name FROM drug WHERE drug_id = %s", (drug_id,))
            drug_info = cursor.fetchone()
            drug_name = drug_info['drug_name'] if drug_info else "未知药品"
            
            print(f"✅ 处方开具成功！")
            print(f"   处方号: {prescription_id}")
            print(f"   病人: {patient_name} (挂号号: {registration_id})")
            print(f"   药品: {drug_name} (药品ID: {drug_id})")
            print(f"   数量: {quantity}")
            print(f"   关联缴费号: {payment_id}")
            
            return prescription_id
        
    except Exception as e:
        print(f"❌ 开具处方失败: {e}")
        return None

def check_prescription_exists(cursor, prescription_id):
    """
    判断处方ID是否存在
    
    Args:
        cursor: 数据库游标
        prescription_id: 处方号
    
    Returns:
        bool: 存在返回True，不存在返回False
    """
    try:
        # 查询处方是否存在
        cursor.execute("SELECT prescription_id FROM prescription WHERE prescription_id = %s", (prescription_id,))
        result = cursor.fetchone()
        
        if result:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 检查处方ID失败: {e}")
        return False
    
def query_prescription(cursor, prescription_id=None, registration_id=None, drug_id=None, payment_id=None):
    """
    查询处方信息（仅查询prescription表）
    
    Args:
        cursor: 数据库游标
        prescription_id: 处方号（可选）
        registration_id: 挂号编号（可选）
        drug_id: 药品编号（可选）
        payment_id: 缴费号（可选）
    
    Returns:
        list: 查询结果列表
    """
    try:
        # 构建查询条件
        conditions = []
        params = []
        
        if prescription_id:
            conditions.append("prescription_id = %s")
            params.append(prescription_id)
        
        if registration_id:
            conditions.append("registration_id = %s")
            params.append(registration_id)
            
        if drug_id:
            conditions.append("drug_id = %s")
            params.append(drug_id)

        if payment_id:
            conditions.append("payment_id = %s")
            params.append(payment_id)
        
        # 构建SQL查询，只查询单表
        if not conditions:
            sql = "SELECT * FROM prescription ORDER BY prescription_id"
        else:
            sql = f"SELECT * FROM prescription WHERE {' AND '.join(conditions)} ORDER BY prescription_id"
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # 输出查询结果
        print(f"\n🔍 查询到 {len(results)} 条处方记录")
        print("-" * 100)
        print(f"{'处方号':<10} {'挂号号':<10} {'药品ID':<8} {'数量':<8} {'缴费号':<10} {'创建时间':<20}")
        print("-" * 100)
        
        if results:
            for pre in results:
                created_time = str(pre['created_at']) if pre['created_at'] else 'NULL'
                
                print(f"{pre['prescription_id']:<10} {pre['registration_id']:<10} {pre['drug_id']:<8} "
                      f"{pre['quantity']:<8} {pre['payment_id']:<10} {created_time:<20}")
        else:
            print("  没有找到匹配的处方记录")
        
        print("-" * 100)
        
        return results
        
    except Exception as e:
        print(f"❌ 查询处方失败: {e}")
        return []
