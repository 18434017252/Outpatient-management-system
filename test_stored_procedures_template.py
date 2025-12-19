#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试存储过程和触发器功能
注意：请复制此文件为 test_stored_procedures.py 并填入数据库配置
"""

import pymysql
import traceback
import setup
import entity.patient as patient_module
import entity.department as department_module
import entity.doctor as doctor_module
import entity.drug as drug_module
import entity.registration as registration_module
import entity.prescription as prescription_module
import entity.payment as payment_module

# 配置数据库连接
# TODO: 请填入你的数据库配置信息
config = {
    'host': 'your_host',       # 例如: 'localhost' 或 '127.0.0.1'
    'port': 3306,
    'user': 'your_username',   # 例如: 'root'
    'password': 'your_password',
    'database': 'your_database',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}

def test_stored_procedures_and_triggers():
    """测试存储过程和触发器"""
    try:
        # 连接数据库
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        print("\n" + "="*80)
        print("开始测试存储过程和触发器")
        print("="*80)
        
        # 1. 创建存储过程和触发器
        print("\n【步骤1】创建存储过程")
        setup.create_stored_procedures(cursor)
        
        print("\n【步骤2】创建触发器")
        setup.create_triggers(cursor)
        
        # 2. 测试存储过程：创建挂号并生成缴费记录
        print("\n【步骤3】测试存储过程：创建挂号并生成缴费记录")
        
        # 先确保有测试数据
        # 查询或创建病人
        cursor.execute("SELECT patient_id FROM patient LIMIT 1")
        patient = cursor.fetchone()
        if patient:
            patient_id = patient['patient_id']
        else:
            patient_id = patient_module.register_patient(cursor, "测试病人", "男", "13800000001")
        
        # 查询或创建科室
        cursor.execute("SELECT department_id FROM department LIMIT 1")
        dept = cursor.fetchone()
        if dept:
            department_id = dept['department_id']
        else:
            cursor.execute("INSERT INTO department (department_name) VALUES ('测试科室')")
            department_id = cursor.lastrowid
        
        # 使用存储过程创建挂号
        registration_id, payment_id = registration_module.create_registration_with_payment(
            cursor, patient_id, department_id, 50.0, use_stored_procedure=True
        )
        
        if registration_id and payment_id:
            print(f"✅ 存储过程测试成功：挂号ID={registration_id}, 缴费ID={payment_id}")
        else:
            print("❌ 存储过程测试失败")
        
        # 3. 测试存储过程：完成缴费
        print("\n【步骤4】测试存储过程：完成缴费")
        if payment_id:
            result = payment_module.complete_payment(cursor, payment_id, use_stored_procedure=True)
            if result:
                print("✅ 缴费存储过程测试成功")
            else:
                print("❌ 缴费存储过程测试失败")
        
        # 4. 测试存储过程：开具处方并更新库存
        print("\n【步骤5】测试存储过程：开具处方并更新库存")
        
        # 查询或创建药品
        cursor.execute("SELECT drug_id FROM drug LIMIT 1")
        drug = cursor.fetchone()
        if drug:
            drug_id = drug['drug_id']
        else:
            drug_id = drug_module.add_drug(cursor, "测试药品", 100, 25.5)
        
        # 查询当前库存
        cursor.execute("SELECT stored_quantity FROM drug WHERE drug_id = %s", (drug_id,))
        drug_info = cursor.fetchone()
        initial_quantity = drug_info['stored_quantity'] if drug_info else 0
        print(f"药品初始库存: {initial_quantity}")
        
        # 创建处方缴费记录
        prescription_payment_id = payment_module.create_payment(cursor, patient_id, 76.5, None)
        
        # 使用存储过程开具处方
        if registration_id and prescription_payment_id:
            prescription_id = prescription_module.create_prescription(
                cursor, registration_id, drug_id, 3, prescription_payment_id, use_stored_procedure=True
            )
            
            if prescription_id:
                # 验证库存是否更新
                cursor.execute("SELECT stored_quantity FROM drug WHERE drug_id = %s", (drug_id,))
                drug_info = cursor.fetchone()
                final_quantity = drug_info['stored_quantity'] if drug_info else 0
                print(f"药品最终库存: {final_quantity}")
                
                if final_quantity == initial_quantity - 3:
                    print("✅ 处方存储过程测试成功：库存已自动更新")
                else:
                    print(f"❌ 处方存储过程测试失败：库存未正确更新（期望：{initial_quantity - 3}，实际：{final_quantity}）")
            else:
                print("❌ 处方存储过程测试失败")
        
        # 5. 测试触发器：删除处方恢复库存
        print("\n【步骤6】测试触发器：删除处方恢复库存")
        if prescription_id:
            # 记录删除前的库存
            cursor.execute("SELECT stored_quantity FROM drug WHERE drug_id = %s", (drug_id,))
            drug_info = cursor.fetchone()
            before_delete_quantity = drug_info['stored_quantity'] if drug_info else 0
            
            # 删除处方
            cursor.execute("DELETE FROM prescription WHERE prescription_id = %s", (prescription_id,))
            
            # 验证库存是否恢复
            cursor.execute("SELECT stored_quantity FROM drug WHERE drug_id = %s", (drug_id,))
            drug_info = cursor.fetchone()
            after_delete_quantity = drug_info['stored_quantity'] if drug_info else 0
            
            if after_delete_quantity == before_delete_quantity + 3:
                print(f"✅ 删除触发器测试成功：库存已自动恢复（{before_delete_quantity} -> {after_delete_quantity}）")
            else:
                print(f"❌ 删除触发器测试失败：库存未正确恢复（期望：{before_delete_quantity + 3}，实际：{after_delete_quantity}）")
        
        print("\n" + "="*80)
        print("测试完成")
        print("="*80)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    test_stored_procedures_and_triggers()
