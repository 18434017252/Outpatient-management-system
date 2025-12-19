# 存储过程和触发器使用说明

## 概述

本项目已在 setup.py 中添加了存储过程和触发器，用于封装常用的数据库操作并确保数据一致性。

## 存储过程 (Stored Procedures)

### 1. sp_register_patient_with_registration
**功能**: 病人注册并创建挂号缴费记录（一次性完成病人注册、缴费记录创建和挂号记录创建）

**参数**:
- 输入参数:
  - `p_name` VARCHAR(50): 病人姓名
  - `p_gender` ENUM('男', '女'): 性别
  - `p_phone_number` VARCHAR(20): 电话号码
  - `p_department_id` INT: 科室编号
  - `p_registration_fee` DECIMAL(10,2): 挂号费用
- 输出参数:
  - `p_patient_id` INT: 新创建的病历号
  - `p_registration_id` INT: 新创建的挂号编号
  - `p_payment_id` INT: 新创建的缴费号

**使用场景**: 新病人首次挂号时使用，一次性完成注册和挂号操作

**调用示例**:
```python
cursor.callproc('sp_register_patient_with_registration', 
                ['张三', '男', '13800138000', 1, 50.0, 0, 0, 0])
```

### 2. sp_create_prescription_with_inventory_update
**功能**: 开具处方并自动更新药品库存

**参数**:
- 输入参数:
  - `p_registration_id` INT: 挂号编号
  - `p_drug_id` INT: 药品编号
  - `p_quantity` INT: 药品数量
  - `p_payment_id` INT: 缴费号
- 输出参数:
  - `p_prescription_id` INT: 新创建的处方号
  - `p_result_code` INT: 结果码（0=成功，1=药品不存在，2=库存不足，-1=数据库错误）
  - `p_result_message` VARCHAR(200): 结果消息

**使用场景**: 医生开具处方时使用，自动检查库存并更新

**实体模块调用**:
```python
# 在 entity/prescription.py 中
prescription_id = prescription_module.create_prescription(
    cursor, registration_id, drug_id, quantity, payment_id, 
    use_stored_procedure=True  # 使用存储过程
)
```

**优势**:
- 自动检查药品库存
- 事务处理确保数据一致性
- 自动更新库存数量

### 3. sp_complete_payment
**功能**: 完成缴费操作

**参数**:
- 输入参数:
  - `p_payment_id` INT: 缴费号
- 输出参数:
  - `p_result_code` INT: 结果码（0=成功，1=已经缴费过，-1=数据库错误）
  - `p_result_message` VARCHAR(200): 结果消息

**使用场景**: 病人完成缴费时使用

**实体模块调用**:
```python
# 在 entity/payment.py 中
success = payment_module.complete_payment(
    cursor, payment_id, 
    use_stored_procedure=True  # 使用存储过程
)
```

### 4. sp_create_registration_with_payment
**功能**: 创建挂号并生成缴费记录

**参数**:
- 输入参数:
  - `p_patient_id` INT: 病历号
  - `p_department_id` INT: 科室编号
  - `p_registration_fee` DECIMAL(10,2): 挂号费用
- 输出参数:
  - `p_registration_id` INT: 新创建的挂号编号
  - `p_payment_id` INT: 新创建的缴费号

**使用场景**: 已注册病人挂号时使用

**实体模块调用**:
```python
# 在 entity/registration.py 中
registration_id, payment_id = registration_module.create_registration_with_payment(
    cursor, patient_id, department_id, registration_fee,
    use_stored_procedure=True  # 使用存储过程
)
```

## 触发器 (Triggers)

### 1. tr_prescription_delete_restore_inventory
**功能**: 处方删除时自动恢复药品库存

**触发时机**: AFTER DELETE ON prescription

**作用**: 当处方被删除时，自动将药品数量加回到库存中

**示例场景**: 医生取消处方时，库存自动恢复

### 2. tr_prescription_update_adjust_inventory
**功能**: 处方更新时自动调整药品库存

**触发时机**: BEFORE UPDATE ON prescription

**作用**: 
- 当处方数量被修改时，自动调整药品库存
- 检查库存是否充足，不足则拒绝更新

**示例场景**: 医生修改处方药品数量时，库存自动调整

### 3. tr_registration_delete_cleanup_payment
**功能**: 挂号删除时自动清理关联的未缴费记录

**触发时机**: BEFORE DELETE ON registration

**作用**: 删除挂号记录时，如果关联的缴费记录未缴费，自动删除该缴费记录

**示例场景**: 取消未缴费的挂号时，避免遗留未使用的缴费记录

## 初始化和管理

### 创建存储过程和触发器

在数据库初始化时调用：

```python
import setup
import pymysql

# 连接数据库
connection = pymysql.connect(**config)
cursor = connection.cursor()

# 创建表
setup.create_table(cursor)

# 创建存储过程
setup.create_stored_procedures(cursor)

# 创建触发器
setup.create_triggers(cursor)

cursor.close()
connection.close()
```

### 删除存储过程和触发器

如果需要删除：

```python
import setup
import pymysql

connection = pymysql.connect(**config)
cursor = connection.cursor()

# 删除存储过程
setup.drop_stored_procedures(cursor)

# 删除触发器
setup.drop_triggers(cursor)

cursor.close()
connection.close()
```

## Entity 模块调整

### prescription.py
- `create_prescription()` 函数添加了 `use_stored_procedure` 参数（默认True）
- 使用存储过程时，自动更新药品库存，无需手动调用 drug 模块

### payment.py
- `complete_payment()` 函数添加了 `use_stored_procedure` 参数（默认True）
- 使用存储过程时，自动检查是否已缴费并更新缴费时间

### registration.py
- 新增 `create_registration_with_payment()` 函数
- 提供 `use_stored_procedure` 参数（默认True）
- 使用存储过程时，在事务中创建挂号和缴费记录，确保数据一致性

## 优势

1. **数据一致性**: 使用事务确保多表操作的原子性
2. **性能提升**: 减少客户端和数据库之间的往返次数
3. **业务逻辑封装**: 将常用操作封装在数据库层面
4. **自动化处理**: 触发器自动维护数据关系和库存
5. **错误处理**: 存储过程内置错误检查和回滚机制
6. **向后兼容**: 保留原有的直接SQL方式，可通过参数选择

## 测试

运行测试脚本验证功能：

```bash
python test_stored_procedures.py
```

测试内容包括：
1. 创建存储过程和触发器
2. 测试挂号和缴费记录创建
3. 测试缴费完成
4. 测试处方开具和库存更新
5. 测试触发器的库存恢复功能

## 注意事项

1. 存储过程默认启用，如需使用原有方式，设置 `use_stored_procedure=False`
2. 触发器自动生效，删除处方时会自动恢复库存
3. 更新处方数量时会自动检查库存，不足时会拒绝更新
4. 删除挂号时会自动清理未缴费记录，已缴费记录不会被删除
