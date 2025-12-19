# 实施总结：存储过程和触发器

## 概述

本次更新在 setup.py 中添加了存储过程和触发器，用于封装常用的数据库操作并确保数据一致性。同时调整了 entity 模块中的数据库操作，使其可以使用存储过程。

## 新增功能

### 存储过程 (4个)

1. **sp_register_patient_with_registration**
   - 功能：病人注册并创建挂号缴费记录（一站式服务）
   - 适用场景：新病人首次挂号
   - 优势：事务性保证，一次性完成三个表的插入

2. **sp_create_prescription_with_inventory_update**
   - 功能：开具处方并自动更新药品库存
   - 适用场景：医生开具处方
   - 优势：自动检查库存，事务性更新，避免超卖

3. **sp_complete_payment**
   - 功能：完成缴费操作
   - 适用场景：病人缴费
   - 优势：自动检查重复缴费，防止错误

4. **sp_create_registration_with_payment**
   - 功能：创建挂号并生成缴费记录
   - 适用场景：已注册病人挂号
   - 优势：事务性保证，确保挂号和缴费记录同步创建

### 触发器 (3个)

1. **tr_prescription_delete_restore_inventory**
   - 功能：处方删除时自动恢复药品库存
   - 触发时机：DELETE on prescription
   - 优势：自动维护库存一致性，无需手动操作

2. **tr_prescription_update_adjust_inventory**
   - 功能：处方更新时自动调整药品库存
   - 触发时机：UPDATE on prescription
   - 优势：自动检查库存并调整，防止库存不足

3. **tr_registration_delete_cleanup_payment**
   - 功能：挂号删除时自动清理未缴费记录
   - 触发时机：DELETE on registration
   - 优势：自动清理，避免遗留无效数据

## 代码修改

### setup.py
- 新增函数：
  - `create_stored_procedures(cursor)` - 创建所有存储过程
  - `create_triggers(cursor)` - 创建所有触发器
  - `drop_stored_procedures(cursor)` - 删除所有存储过程
  - `drop_triggers(cursor)` - 删除所有触发器

### entity/prescription.py
- 修改函数：`create_prescription()`
  - 新增参数：`use_stored_procedure=True`
  - 默认使用存储过程
  - 保留原有 SQL 方式作为备用

### entity/payment.py
- 修改函数：`complete_payment()`
  - 新增参数：`use_stored_procedure=True`
  - 默认使用存储过程
  - 保留原有 SQL 方式作为备用

### entity/registration.py
- 新增函数：`create_registration_with_payment()`
  - 参数：`use_stored_procedure=True`
  - 默认使用存储过程
  - 返回挂号编号和缴费号

### main.py
- 在数据库初始化时自动创建存储过程和触发器

## 向后兼容性

所有修改都保持了向后兼容：
- 原有函数签名未改变，仅新增可选参数
- 默认启用存储过程，但可通过参数关闭
- 原有的直接 SQL 方式仍然可用

## 使用示例

### 使用存储过程（推荐）

```python
# 创建挂号并生成缴费记录
registration_id, payment_id = registration_module.create_registration_with_payment(
    cursor, patient_id, department_id, 50.0
)

# 开具处方（自动更新库存）
prescription_id = prescription_module.create_prescription(
    cursor, registration_id, drug_id, quantity, payment_id
)

# 完成缴费
success = payment_module.complete_payment(cursor, payment_id)
```

### 使用原有方式（可选）

```python
# 如果需要使用原有的直接 SQL 方式
prescription_id = prescription_module.create_prescription(
    cursor, registration_id, drug_id, quantity, payment_id,
    use_stored_procedure=False
)
```

## 性能优势

1. **减少网络往返**：存储过程在数据库服务器执行，减少客户端-服务器通信
2. **事务性保证**：多表操作在一个事务中完成，确保数据一致性
3. **自动化处理**：触发器自动维护数据关系，减少人工错误
4. **预编译执行**：存储过程预编译，执行效率更高

## 安全性

- 所有存储过程使用参数化查询，防止 SQL 注入
- 事务处理确保数据完整性
- 触发器自动维护约束关系
- 测试文件不包含硬编码凭据，使用模板方式

## 测试

测试脚本已提供（test_stored_procedures_template.py），涵盖：
1. 存储过程的正确性
2. 触发器的自动化功能
3. 库存更新的准确性
4. 事务回滚机制

## 文档

详细文档请参考：
- `STORED_PROCEDURES_README.md` - 完整的使用说明和 API 文档

## 部署建议

1. 在生产环境部署前，先在测试环境验证
2. 使用 main.py 初始化数据库时会自动创建存储过程和触发器
3. 如需重建，可使用 `drop_*` 函数删除后重新创建
4. 建议保持默认的存储过程模式，以获得最佳性能

## 总结

本次更新通过添加存储过程和触发器，提升了系统的：
- ✅ 性能：减少网络往返
- ✅ 可靠性：事务处理保证数据一致性
- ✅ 可维护性：业务逻辑封装在数据库层
- ✅ 自动化：触发器自动维护数据关系
- ✅ 兼容性：完全向后兼容，不影响现有代码
