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

def create_stored_procedures(cursor):
    """
    创建存储过程，封装常用的数据库操作
    
    Args:
        cursor: 数据库游标
    """
    try:
        # 1. 存储过程：病人注册并创建挂号缴费记录
        cursor.execute("DROP PROCEDURE IF EXISTS sp_register_patient_with_registration")
        cursor.execute("""
            CREATE PROCEDURE sp_register_patient_with_registration(
                IN p_name VARCHAR(50),
                IN p_gender ENUM('男', '女'),
                IN p_phone_number VARCHAR(20),
                IN p_department_id INT,
                IN p_registration_fee DECIMAL(10,2),
                OUT p_patient_id INT,
                OUT p_registration_id INT,
                OUT p_payment_id INT
            )
            BEGIN
                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    ROLLBACK;
                    RESIGNAL;
                END;
                
                START TRANSACTION;
                
                -- 插入病人信息
                INSERT INTO patient (name, gender, phone_number, created_at) 
                VALUES (p_name, p_gender, p_phone_number, NOW());
                SET p_patient_id = LAST_INSERT_ID();
                
                -- 创建挂号缴费记录
                INSERT INTO payment (patient_id, price, time, created_at) 
                VALUES (p_patient_id, p_registration_fee, NULL, NOW());
                SET p_payment_id = LAST_INSERT_ID();
                
                -- 创建挂号记录
                INSERT INTO registration (patient_id, department_id, payment_id, created_at) 
                VALUES (p_patient_id, p_department_id, p_payment_id, NOW());
                SET p_registration_id = LAST_INSERT_ID();
                
                COMMIT;
            END
        """)
        print("✅ 创建存储过程: sp_register_patient_with_registration")
        
        # 2. 存储过程：开具处方并更新药品库存
        cursor.execute("DROP PROCEDURE IF EXISTS sp_create_prescription_with_inventory_update")
        cursor.execute("""
            CREATE PROCEDURE sp_create_prescription_with_inventory_update(
                IN p_registration_id INT,
                IN p_drug_id INT,
                IN p_quantity INT,
                IN p_payment_id INT,
                OUT p_prescription_id INT,
                OUT p_result_code INT,
                OUT p_result_message VARCHAR(200)
            )
            BEGIN
                DECLARE v_stored_quantity INT;
                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    ROLLBACK;
                    SET p_result_code = -1;
                    SET p_result_message = '处方开具失败：数据库错误';
                    RESIGNAL;
                END;
                
                START TRANSACTION;
                
                -- 检查药品库存
                SELECT stored_quantity INTO v_stored_quantity 
                FROM drug WHERE drug_id = p_drug_id FOR UPDATE;
                
                IF v_stored_quantity IS NULL THEN
                    ROLLBACK;
                    SET p_result_code = 1;
                    SET p_result_message = '处方开具失败：药品不存在';
                ELSEIF v_stored_quantity < p_quantity THEN
                    ROLLBACK;
                    SET p_result_code = 2;
                    SET p_result_message = CONCAT('处方开具失败：库存不足，当前库存：', v_stored_quantity);
                ELSE
                    -- 插入处方记录
                    INSERT INTO prescription (registration_id, drug_id, quantity, payment_id, created_at) 
                    VALUES (p_registration_id, p_drug_id, p_quantity, p_payment_id, NOW());
                    SET p_prescription_id = LAST_INSERT_ID();
                    
                    -- 更新药品库存
                    UPDATE drug 
                    SET stored_quantity = stored_quantity - p_quantity, 
                        updated_at = NOW() 
                    WHERE drug_id = p_drug_id;
                    
                    COMMIT;
                    SET p_result_code = 0;
                    SET p_result_message = '处方开具成功';
                END IF;
            END
        """)
        print("✅ 创建存储过程: sp_create_prescription_with_inventory_update")
        
        # 3. 存储过程：完成缴费
        cursor.execute("DROP PROCEDURE IF EXISTS sp_complete_payment")
        cursor.execute("""
            CREATE PROCEDURE sp_complete_payment(
                IN p_payment_id INT,
                OUT p_result_code INT,
                OUT p_result_message VARCHAR(200)
            )
            BEGIN
                DECLARE v_current_time TIMESTAMP;
                
                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    SET p_result_code = -1;
                    SET p_result_message = '缴费失败：数据库错误';
                    RESIGNAL;
                END;
                
                -- 检查缴费记录是否存在且未缴费
                SELECT time INTO v_current_time 
                FROM payment WHERE payment_id = p_payment_id;
                
                IF v_current_time IS NULL THEN
                    -- 更新缴费时间
                    UPDATE payment 
                    SET time = NOW(), updated_at = NOW() 
                    WHERE payment_id = p_payment_id;
                    
                    SET p_result_code = 0;
                    SET p_result_message = '缴费成功';
                ELSE
                    SET p_result_code = 1;
                    SET p_result_message = CONCAT('缴费失败：已经缴费过，缴费时间：', v_current_time);
                END IF;
            END
        """)
        print("✅ 创建存储过程: sp_complete_payment")
        
        # 4. 存储过程：创建挂号并生成缴费记录
        cursor.execute("DROP PROCEDURE IF EXISTS sp_create_registration_with_payment")
        cursor.execute("""
            CREATE PROCEDURE sp_create_registration_with_payment(
                IN p_patient_id INT,
                IN p_department_id INT,
                IN p_registration_fee DECIMAL(10,2),
                OUT p_registration_id INT,
                OUT p_payment_id INT
            )
            BEGIN
                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    ROLLBACK;
                    RESIGNAL;
                END;
                
                START TRANSACTION;
                
                -- 创建缴费记录
                INSERT INTO payment (patient_id, price, time, created_at) 
                VALUES (p_patient_id, p_registration_fee, NULL, NOW());
                SET p_payment_id = LAST_INSERT_ID();
                
                -- 创建挂号记录
                INSERT INTO registration (patient_id, department_id, payment_id, created_at) 
                VALUES (p_patient_id, p_department_id, p_payment_id, NOW());
                SET p_registration_id = LAST_INSERT_ID();
                
                COMMIT;
            END
        """)
        print("✅ 创建存储过程: sp_create_registration_with_payment")
        
        print("✅ 所有存储过程创建完成")
        
    except Exception as e:
        print(f"❌ 创建存储过程失败: {e}")

def create_triggers(cursor):
    """
    创建触发器，自动处理数据一致性
    
    Args:
        cursor: 数据库游标
    """
    try:
        # 1. 触发器：处方删除时恢复药品库存
        cursor.execute("DROP TRIGGER IF EXISTS tr_prescription_delete_restore_inventory")
        cursor.execute("""
            CREATE TRIGGER tr_prescription_delete_restore_inventory
            AFTER DELETE ON prescription
            FOR EACH ROW
            BEGIN
                UPDATE drug 
                SET stored_quantity = stored_quantity + OLD.quantity,
                    updated_at = NOW()
                WHERE drug_id = OLD.drug_id;
            END
        """)
        print("✅ 创建触发器: tr_prescription_delete_restore_inventory")
        
        # 2. 触发器：处方更新时调整药品库存
        cursor.execute("DROP TRIGGER IF EXISTS tr_prescription_update_adjust_inventory")
        cursor.execute("""
            CREATE TRIGGER tr_prescription_update_adjust_inventory
            BEFORE UPDATE ON prescription
            FOR EACH ROW
            BEGIN
                DECLARE v_stored_quantity INT;
                DECLARE v_quantity_diff INT;
                
                -- 计算库存变化量
                SET v_quantity_diff = NEW.quantity - OLD.quantity;
                
                -- 如果数量发生变化
                IF v_quantity_diff != 0 THEN
                    -- 检查库存是否充足
                    SELECT stored_quantity INTO v_stored_quantity 
                    FROM drug WHERE drug_id = NEW.drug_id;
                    
                    IF v_stored_quantity < v_quantity_diff THEN
                        SIGNAL SQLSTATE '45000'
                        SET MESSAGE_TEXT = '更新处方失败：药品库存不足';
                    ELSE
                        -- 更新药品库存
                        UPDATE drug 
                        SET stored_quantity = stored_quantity - v_quantity_diff,
                            updated_at = NOW()
                        WHERE drug_id = NEW.drug_id;
                    END IF;
                END IF;
            END
        """)
        print("✅ 创建触发器: tr_prescription_update_adjust_inventory")
        
        # 3. 触发器：挂号删除时自动删除关联的未缴费记录
        cursor.execute("DROP TRIGGER IF EXISTS tr_registration_delete_cleanup_payment")
        cursor.execute("""
            CREATE TRIGGER tr_registration_delete_cleanup_payment
            BEFORE DELETE ON registration
            FOR EACH ROW
            BEGIN
                -- 如果有关联的未缴费记录，自动删除
                DELETE FROM payment 
                WHERE payment_id = OLD.payment_id 
                AND time IS NULL;
            END
        """)
        print("✅ 创建触发器: tr_registration_delete_cleanup_payment")
        
        print("✅ 所有触发器创建完成")
        
    except Exception as e:
        print(f"❌ 创建触发器失败: {e}")

def drop_stored_procedures(cursor):
    """
    删除所有存储过程
    
    Args:
        cursor: 数据库游标
    """
    try:
        procedures = [
            'sp_register_patient_with_registration',
            'sp_create_prescription_with_inventory_update',
            'sp_complete_payment',
            'sp_create_registration_with_payment'
        ]
        
        for proc in procedures:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {proc}")
            print(f"🗑️ 已删除存储过程: {proc}")
        
        print("✅ 所有存储过程已删除")
        
    except Exception as e:
        print(f"❌ 删除存储过程失败: {e}")

def drop_triggers(cursor):
    """
    删除所有触发器
    
    Args:
        cursor: 数据库游标
    """
    try:
        triggers = [
            'tr_prescription_delete_restore_inventory',
            'tr_prescription_update_adjust_inventory',
            'tr_registration_delete_cleanup_payment'
        ]
        
        for trigger in triggers:
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger}")
            print(f"🗑️ 已删除触发器: {trigger}")
        
        print("✅ 所有触发器已删除")
        
    except Exception as e:
        print(f"❌ 删除触发器失败: {e}")