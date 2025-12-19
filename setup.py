import pymysql

def create_table(cursor):
    
    # 1. 创建病人表 (patient)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient (
            patient_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '病历号',
            name VARCHAR(50) NOT NULL COMMENT '姓名',
            gender ENUM('男', '女') NOT NULL COMMENT '性别',
            phone_number VARCHAR(20) NOT NULL COMMENT '电话号码',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_patient_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='病人信息表'
    """)
    
    # 2. 创建科室表 (department)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS department (
            department_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '科室编号',
            department_name VARCHAR(100) NOT NULL COMMENT '科室名称',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='科室信息表'
    """)
    
    # 3. 创建医生表 (doctor)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor (
            doctor_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '医生工号',
            name VARCHAR(50) NOT NULL COMMENT '姓名',
            gender ENUM('男', '女') NOT NULL COMMENT '性别',
            phone_number VARCHAR(20) NOT NULL COMMENT '电话号码',
            position VARCHAR(50) NULL COMMENT '职称',
            department_id INT NULL COMMENT '科室编号',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            FOREIGN KEY (department_id) REFERENCES department(department_id) ON DELETE SET NULL,
            INDEX idx_doctor_name (name),
            INDEX idx_doctor_dept_pos (department_id, position)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='医生信息表'
    """)
    
    # 4. 创建药品表 (drug)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drug (
            drug_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '药品编号',
            drug_name VARCHAR(100) NOT NULL COMMENT '药品名称',
            stored_quantity INT NOT NULL DEFAULT 0 COMMENT '药品库存数量',
            drug_price DECIMAL(10,2) NOT NULL COMMENT '药品单价',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='药品信息表'
    """)
    
    # 5. 创建缴费表 (payment)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment (
            payment_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '缴费号',
            patient_id INT NOT NULL COMMENT '病历号',
            price DECIMAL(10,2) NOT NULL COMMENT '缴费价格',
            time TIMESTAMP NULL COMMENT '缴费时间',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            FOREIGN KEY (patient_id) REFERENCES patient(patient_id) ON DELETE CASCADE,
            INDEX idx_payment_patient (patient_id),
            INDEX idx_payment_patient_time (patient_id, time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='缴费记录表'
    """)
    
    # 6. 创建挂号表 (registration)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registration (
            registration_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '挂号编号',
            patient_id INT NOT NULL COMMENT '病历号',
            department_id INT NOT NULL COMMENT '科室编号',
            doctor_id INT NULL COMMENT '医生工号',
            payment_id INT NULL COMMENT '缴费号',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            FOREIGN KEY (patient_id) REFERENCES patient(patient_id) ON DELETE CASCADE,
            FOREIGN KEY (department_id) REFERENCES department(department_id) ON DELETE RESTRICT,
            FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id) ON DELETE SET NULL,
            FOREIGN KEY (payment_id) REFERENCES payment(payment_id) ON DELETE SET NULL,
            INDEX idx_registration_doctor (doctor_id),
            INDEX idx_registration_patient (patient_id),
            INDEX idx_registration_doctor_patient (doctor_id, patient_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='挂号记录表'
    """)
    
    # 7. 创建处方表 (prescription)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescription (
            prescription_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '处方号',
            registration_id INT NOT NULL COMMENT '挂号编号',
            drug_id INT NOT NULL COMMENT '药品编号',
            quantity INT NOT NULL COMMENT '药品数量',
            payment_id INT NOT NULL COMMENT '缴费号',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            FOREIGN KEY (registration_id) REFERENCES registration(registration_id) ON DELETE CASCADE,
            FOREIGN KEY (drug_id) REFERENCES drug(drug_id) ON DELETE RESTRICT,
            FOREIGN KEY (payment_id) REFERENCES payment(payment_id) ON DELETE CASCADE,
            INDEX idx_prescription_registration (registration_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='处方记录表'
    """)

def show_table_content(cursor, table_name):
    """
    显示指定表的内容
    
    Args:
        cursor: 数据库游标
        table_name: 表名
    """
    try:
        # 获取表数据
        cursor.execute(f"SELECT * FROM {table_name}")
        records = cursor.fetchall()
        
        print(f"\n=== {table_name} 表内容 ===")
        if records:
            # 显示列名
            headers = list(records[0].keys())
            header_line = " | ".join(f"{h:<15}" for h in headers)
            print(header_line)
            print("-" * len(header_line))
            
            # 显示数据
            for record in records:
                row_data = " | ".join(f"{str(v):<15}" for v in record.values())
                print(row_data)
            
            print("-" * len(header_line))
            print(f"记录数: {len(records)}")
        else:
            print("表为空")
            
    except Exception as e:
        print(f"查询表 {table_name} 失败: {e}")

def drop_all_tables_for_testing(cursor):
    """
    测试阶段：删除所有表，方便重新创建测试不同的建表语句
    
    Args:
        cursor: 数据库游标
    """
    try:
        # 临时禁用外键检查，避免删除顺序问题
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 删除所有表（按照从依赖表到基础表的顺序）
        tables_to_drop = [
            'prescription',    # 处方表（依赖挂号、药品、缴费）
            'registration',    # 挂号表（依赖病人、科室、医生、缴费）
            'payment',         # 缴费表（依赖病人）
            'doctor',          # 医生表（依赖科室）
            'drug',            # 药品表
            'patient',         # 病人表
            'department'       # 科室表
        ]
        
        for table_name in tables_to_drop:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            print(f"🗑️ 已删除表: {table_name}")
        
        # 重新启用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        print("✅ 所有表已删除，可以重新测试建表语句")
        
    except Exception as e:
        print(f"❌ 删除表失败: {e}")

def show_all_tables_content(cursor):
    """
    显示所有表的内容
    
    Args:
        cursor: 数据库游标
    """
    show_table_content(cursor, 'patient')
    show_table_content(cursor, 'department')
    show_table_content(cursor, 'doctor')
    show_table_content(cursor, 'drug')
    show_table_content(cursor, 'payment')
    show_table_content(cursor,'registration')
    show_table_content(cursor, 'prescription')