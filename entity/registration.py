import pymysql
import entity.patient as patient_module
import entity.department as department_module
import entity.payment as payment_module
import entity.doctor as doctor_module

def create_registration(cursor, patient_id, department_id):
    """
    创建挂号记录（医生和缴费信息留空）
    
    Args:
        cursor: 数据库游标
        patient_id: 病历号
        department_id: 科室编号
    
    Returns:
        int: 新创建的挂号编号，失败返回None
    """
    try:
        # 1. 检查病人是否存在
        if not patient_module.check_patient_exists(cursor, patient_id):
            print(f"❌ 创建挂号失败：病历号 {patient_id} 不存在")
            return None
        else:
            print(f"✅ 病历号 {patient_id} 存在")
        
        # 2. 检查科室是否存在
        if not department_module.check_department_exists(cursor, department_id):
            print(f"❌ 创建挂号失败：科室编号 {department_id} 不存在")
            return None
        else:
            print(f"✅ 科室编号 {department_id} 存在")

        # 3. 插入新挂号记录
        sql = """
        INSERT INTO registration (patient_id, department_id, created_at) 
        VALUES (%s, %s, NOW())
        """
        cursor.execute(sql, (patient_id, department_id))
        
        # 4. 获取刚插入的挂号编号
        cursor.execute("SELECT LAST_INSERT_ID()")
        result = cursor.fetchone()
        
        if isinstance(result, tuple):
            registration_id = result[0]
        else:
            registration_id = result['LAST_INSERT_ID()']
        
        # 5. 查询并打印详细信息
        cursor.execute("SELECT name FROM patient WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        patient_name = patient['name'] if patient else "未知病人"

        cursor.execute("SELECT department_name FROM department WHERE department_id = %s", (department_id,))
        department = cursor.fetchone()
        dept_name = department['department_name'] if department else "未知科室"
        
        print(f"✅ 挂号创建成功！")
        print(f"   挂号编号: {registration_id}")
        print(f"   病人: {patient_name} (病历号: {patient_id})")
        print(f"   挂号科室: {dept_name} (科室ID: {department_id})")
        print(f"   状态: 待分配医生")
        
        return registration_id
        
    except Exception as e:
        print(f"❌ 创建挂号失败: {e}")
        return None

def process_registration(cursor, registration_id, doctor_id):
    """
    处理挂号（为挂号分配医生）
    
    Args:
        cursor: 数据库游标
        registration_id: 挂号编号
        doctor_id: 医生工号
    
    Returns:
        bool: 处理是否成功
    """
    try:
        # 1. 检查挂号是否存在
        cursor.execute("SELECT patient_id, department_id, doctor_id FROM registration WHERE registration_id = %s", (registration_id,))
        registration = cursor.fetchone()
        
        if not registration:
            print(f"❌ 处理挂号失败：挂号编号 {registration_id} 不存在")
            return False
        
        # 2. 检查是否已经分配过医生
        if registration['doctor_id']:
            print(f"⚠️ 挂号 {registration_id} 已经分配过医生（工号: {registration['doctor_id']}），无需重复分配")
            return True
        
        # 3. 检查医生是否存在
        cursor.execute("SELECT doctor_id FROM doctor WHERE doctor_id = %s", (doctor_id,))
        if not doctor_module.check_doctor_exists(cursor, doctor_id):
            print(f"❌ 处理挂号失败：医生工号 {doctor_id} 不存在")
            return False

        # 4. 检查医生是否属于该挂号科室
        cursor.execute("SELECT department_id FROM doctor WHERE doctor_id = %s", (doctor_id,))
        doctor = cursor.fetchone()
        
        if not doctor or doctor['department_id'] != registration['department_id']:
            print(f"❌ 处理挂号失败：医生工号 {doctor_id} 不属于挂号科室 {registration['department_id']}")
            return False
        
        # 5. 更新挂号记录，分配医生
        sql = """
        UPDATE registration 
        SET doctor_id = %s, updated_at = NOW() 
        WHERE registration_id = %s
        """
        cursor.execute(sql, (doctor_id, registration_id))
        
        # 6. 查询并打印详细信息
        # 获取病人姓名
        cursor.execute("SELECT name FROM patient WHERE patient_id = %s", (registration['patient_id'],))
        patient = cursor.fetchone()
        patient_name = patient['name'] if patient else "未知病人"

        # 获取医生姓名
        cursor.execute("SELECT name FROM doctor WHERE doctor_id = %s", (doctor_id,))
        doctor_info = cursor.fetchone()
        doctor_name = doctor_info['name'] if doctor_info else "未知医生"

        # 获取科室名称
        cursor.execute("SELECT department_name FROM department WHERE department_id = %s", (registration['department_id'],))
        dept = cursor.fetchone()
        dept_name = dept['department_name'] if dept else "未知科室"
        
        print(f"✅ 挂号处理成功！")
        print(f"   挂号编号: {registration_id}")
        print(f"   病人: {patient_name} (病历号: {registration['patient_id']})")
        print(f"   科室: {dept_name} (科室ID: {registration['department_id']})")
        print(f"   已分配医生: {doctor_name} (工号: {doctor_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理挂号失败: {e}")
        return False
    
def get_registration_info(cursor, registration_id, info_type='patient'):
    """
    通过挂号编号获取对应的ID信息
    
    Args:
        cursor: 数据库游标
        registration_id: 挂号编号
        info_type: 信息类型，可选值：'patient'（病历号）、'doctor'（医生工号）、'department'（科室编号）
    
    Returns:
        int: 对应的ID值，如果不存在或查询失败返回None
    """
    try:
        # 检查挂号是否存在
        if not check_registration_exists(cursor, registration_id):
            print(f"❌ 获取挂号信息失败：挂号编号 {registration_id} 不存在")
            return None
        
        # 查询挂号记录
        cursor.execute("SELECT patient_id, doctor_id, department_id FROM registration WHERE registration_id = %s", (registration_id,))
        registration = cursor.fetchone()
        
        if not registration:
            print(f"❌ 获取挂号信息失败：挂号编号 {registration_id} 的记录不存在")
            return None
        
        # 根据info_type返回对应的ID
        if info_type == 'patient':
            result = registration['patient_id']
            print(f"✅ 挂号编号 {registration_id} 对应的病历号: {result}")
        elif info_type == 'doctor':
            result = registration['doctor_id']
            if result:
                print(f"✅ 挂号编号 {registration_id} 对应的医生工号: {result}")
            else:
                print(f"⚠️ 挂号编号 {registration_id} 尚未分配医生")
        elif info_type == 'department':
            result = registration['department_id']
            print(f"✅ 挂号编号 {registration_id} 对应的科室编号: {result}")
        elif info_type == 'payment':
            result = registration['payment_id']
            if result:
                print(f"✅ 挂号编号 {registration_id} 对应的缴费号: {result}")
            else:
                print(f"⚠️ 挂号编号 {registration_id} 尚未关联缴费")
        else:
            print(f"❌ 无效的信息类型: {info_type}，请使用 'patient', 'doctor', 'department' 或 'payment'")
            return None
        
        return result
        
    except Exception as e:
        print(f"❌ 获取挂号信息失败: {e}")
        return None

def check_registration_exists(cursor, registration_id):
    """
    判断挂号ID是否存在
    
    Args:
        cursor: 数据库游标
        registration_id: 挂号编号
    
    Returns:
        bool: 存在返回True，不存在返回False
    """
    try:
        # 查询挂号是否存在
        cursor.execute("SELECT registration_id FROM registration WHERE registration_id = %s", (registration_id,))
        result = cursor.fetchone()
        
        if result:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 检查挂号ID失败: {e}")
        return False

def set_registration_payment(cursor, registration_id, payment_id):
    """
    为挂号记录分配缴费号
    
    Args:
        cursor: 数据库游标
        registration_id: 挂号编号
        payment_id: 缴费号
    
    Returns:
        bool: 分配是否成功
    """
    try:
        # 1. 检查挂号是否存在
        if not check_registration_exists(cursor, registration_id):
            print(f"❌ 分配缴费失败：挂号编号 {registration_id} 不存在")
            return False

        # 2. 检查缴费记录是否存在 (使用新的辅助函数)
        if not payment_module.check_payment_exists(cursor, payment_id):
            print(f"❌ 分配缴费失败：缴费号 {payment_id} 不存在")
            return False

        # 3. 查询当前挂号信息，检查是否已缴费
        cursor.execute("SELECT payment_id FROM registration WHERE registration_id = %s", (registration_id,))
        registration = cursor.fetchone()
        
        if registration['payment_id']:
            print(f"⚠️ 挂号 {registration_id} 已经分配过缴费号（缴费号: {registration['payment_id']}），无需重复分配")
            return True
        
        # 4. 更新挂号记录，关联缴费号
        sql = """
        UPDATE registration 
        SET payment_id = %s, updated_at = NOW() 
        WHERE registration_id = %s
        """
        cursor.execute(sql, (payment_id, registration_id))
        
        # 5. 查询并打印详细信息
        # 获取病人姓名
        cursor.execute("SELECT p.name FROM registration r JOIN patient p ON r.patient_id = p.patient_id WHERE r.registration_id = %s", (registration_id,))
        patient = cursor.fetchone()
        patient_name = patient['name'] if patient else "未知病人"

        # 获取科室名称
        cursor.execute("SELECT d.department_name FROM registration r JOIN department d ON r.department_id = d.department_id WHERE r.registration_id = %s", (registration_id,))
        dept = cursor.fetchone()
        dept_name = dept['department_name'] if dept else "未知科室"
        
        print(f"✅ 挂号缴费关联成功！")
        print(f"   挂号编号: {registration_id}")
        print(f"   病人: {patient_name}")
        print(f"   科室: {dept_name}")
        print(f"   已关联缴费号: {payment_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分配缴费失败: {e}")
        return False

def query_registration(cursor, registration_id=None, patient_id=None, doctor_id=None, department_id=None, unassigned_only=False):
    """
    查询挂号信息
    
    Args:
        cursor: 数据库游标
        registration_id: 挂号编号（可选）
        patient_id: 病历号（可选）
        doctor_id: 医生工号（可选）
        department_id: 科室编号（可选）
        unassigned_only: 是否只查询未分配医生的挂号（布尔值，默认为False）
    
    Returns:
        list: 查询结果列表
    """
    try:
        # 构建查询条件
        conditions = []
        params = []
        
        if registration_id:
            conditions.append("r.registration_id = %s")
            params.append(registration_id)
        
        if patient_id:
            conditions.append("r.patient_id = %s")
            params.append(patient_id)
        
        if doctor_id:
            conditions.append("r.doctor_id = %s")
            params.append(doctor_id)
        
        if department_id:
            conditions.append("r.department_id = %s")
            params.append(department_id)

        # 新增：如果设置了只查询未分配的挂号，则添加条件
        if unassigned_only:
            conditions.append("r.doctor_id IS NULL")
        
        # 构建SQL查询，关联病人、科室、医生信息
        if not conditions:
            sql = """
            SELECT r.*, p.name as patient_name, d.name as doctor_name, dept.department_name
            FROM registration r
            LEFT JOIN patient p ON r.patient_id = p.patient_id
            LEFT JOIN doctor d ON r.doctor_id = d.doctor_id
            LEFT JOIN department dept ON r.department_id = dept.department_id
            ORDER BY r.registration_id
            """
        else:
            sql = f"""
            SELECT r.*, p.name as patient_name, d.name as doctor_name, dept.department_name
            FROM registration r
            LEFT JOIN patient p ON r.patient_id = p.patient_id
            LEFT JOIN doctor d ON r.doctor_id = d.doctor_id
            LEFT JOIN department dept ON r.department_id = dept.department_id
            WHERE {' AND '.join(conditions)}
            ORDER BY r.registration_id
            """
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # 输出查询结果
        query_type = "未分配医生" if unassigned_only else "挂号"
        print(f"\n🔍 查询到 {len(results)} 条{query_type}记录")
        print("-" * 140)
        print(f"{'挂号编号':<6} {'病历号':<5} {'病人姓名':<6} {'科室ID':<6} {'科室名称':<11} {'医生工号':<4} {'医生姓名':<6} {'缴费号':<7} {'创建时间':<16}")
        print("-" * 140)
        
        if results:
            for reg in results:
                patient_name = reg['patient_name'] if reg['patient_name'] else '未知病人'
                doctor_name = reg['doctor_name'] if reg['doctor_name'] else '待分配'
                dept_name = reg['department_name'] if reg['department_name'] else '未知科室'
                doctor_id_val = reg['doctor_id'] if reg['doctor_id'] else 'NULL'
                payment_id_val = reg['payment_id'] if reg['payment_id'] else 'NULL'
                created_time = str(reg['created_at']) if reg['created_at'] else 'NULL'
                
                print(f"{reg['registration_id']:<10} {reg['patient_id']:<8} {patient_name:<10} "
                      f"{reg['department_id']:<8} {dept_name:<15} {doctor_id_val:<8} {doctor_name:<10} "
                      f"{payment_id_val:<10} {created_time:<20}")
        else:
            print(f"  没有找到匹配的{query_type}记录")
        
        print("-" * 140)
        
        return results
        
    except Exception as e:
        print(f"❌ 查询挂号失败: {e}")
        return []

