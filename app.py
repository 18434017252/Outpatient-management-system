from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import entity.patient as patient_module
import entity.department as department_module
import entity.registration as registration_module
import entity.prescription as prescription_module
import entity.payment as payment_module
import entity.doctor as doctor_module
import entity.drug as drug_module
import setup

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Change this in production

registration_fee = 50  # 挂号费用

# 配置数据库连接
config = {
    'host': '124.70.86.207',
    'port': 3306,
    'user': 'u23371057',
    'password': 'Aa727319',
    'database': 'try_db23371057',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}

def get_db_cursor():
    """获取数据库游标"""
    connection = pymysql.connect(**config)
    return connection.cursor()

# 主页路由
@app.route('/')
def index():
    return render_template('index.html')

# ============ 病人相关路由 ============

@app.route('/patient')
def patient_home():
    return render_template('patient/home.html')

@app.route('/patient/query', methods=['GET', 'POST'])
def patient_query():
    results = []
    if request.method == 'POST':
        cursor = get_db_cursor()
        query_type = request.form.get('query_type')
        query_key = request.form.get('query_key')
        
        if query_type and query_key:
            results = patient_module.query_patient(cursor, **{query_type: query_key})
    
    return render_template('patient/query.html', results=results)

@app.route('/patient/register', methods=['GET', 'POST'])
def patient_register():
    if request.method == 'POST':
        cursor = get_db_cursor()
        name = request.form.get('name')
        gender = request.form.get('gender')
        phone_number = request.form.get('phone_number')
        
        patient_id = patient_module.register_patient(cursor, name, gender, phone_number)
        if patient_id:
            flash(f'注册成功！您的病历号是: {patient_id}', 'success')
            return redirect(url_for('patient_home'))
        else:
            flash('注册失败，请重试', 'danger')
    
    return render_template('patient/register.html')

@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        cursor = get_db_cursor()
        patient_id = request.form.get('patient_id')
        
        results = patient_module.query_patient(cursor, patient_id=int(patient_id))
        if results:
            session['patient_id'] = int(patient_id)
            session['user_type'] = 'patient'
            flash(f'登录成功！欢迎回来', 'success')
            return redirect(url_for('patient_dashboard'))
        else:
            flash('未找到您的信息，请先注册', 'danger')
    
    return render_template('patient/login.html')

@app.route('/patient/dashboard')
def patient_dashboard():
    if 'patient_id' not in session or session.get('user_type') != 'patient':
        flash('请先登录', 'warning')
        return redirect(url_for('patient_login'))
    
    cursor = get_db_cursor()
    patient_id = session['patient_id']
    patient_info = patient_module.query_patient(cursor, patient_id=patient_id)
    
    return render_template('patient/dashboard.html', patient=patient_info[0] if patient_info else None)

@app.route('/patient/update', methods=['GET', 'POST'])
def patient_update():
    if 'patient_id' not in session or session.get('user_type') != 'patient':
        flash('请先登录', 'warning')
        return redirect(url_for('patient_login'))
    
    cursor = get_db_cursor()
    patient_id = session['patient_id']
    
    if request.method == 'POST':
        update_type = request.form.get('update_type')
        update_value = request.form.get('update_value')
        
        if patient_module.update_patient(cursor, patient_id, **{update_type: update_value}):
            flash('信息更新成功', 'success')
        else:
            flash('信息更新失败', 'danger')
        
        return redirect(url_for('patient_dashboard'))
    
    patient_info = patient_module.query_patient(cursor, patient_id=patient_id)
    return render_template('patient/update.html', patient=patient_info[0] if patient_info else None)

@app.route('/patient/department_query')
def patient_department_query():
    if 'patient_id' not in session or session.get('user_type') != 'patient':
        flash('请先登录', 'warning')
        return redirect(url_for('patient_login'))
    
    cursor = get_db_cursor()
    departments = department_module.query_department(cursor)
    
    return render_template('patient/department_query.html', departments=departments)

@app.route('/patient/create_registration', methods=['GET', 'POST'])
def patient_create_registration():
    if 'patient_id' not in session or session.get('user_type') != 'patient':
        flash('请先登录', 'warning')
        return redirect(url_for('patient_login'))
    
    cursor = get_db_cursor()
    patient_id = session['patient_id']
    
    if request.method == 'POST':
        department_id = request.form.get('department_id')
        registration_module.create_registration(cursor, patient_id, int(department_id))
        flash('挂号成功', 'success')
        return redirect(url_for('patient_registration_query'))
    
    departments = department_module.query_department(cursor)
    return render_template('patient/create_registration.html', departments=departments)

@app.route('/patient/registration_query')
def patient_registration_query():
    if 'patient_id' not in session or session.get('user_type') != 'patient':
        flash('请先登录', 'warning')
        return redirect(url_for('patient_login'))
    
    cursor = get_db_cursor()
    patient_id = session['patient_id']
    registrations = registration_module.query_registration(cursor, patient_id=patient_id)
    
    return render_template('patient/registration_query.html', registrations=registrations)

@app.route('/patient/prescription_query', methods=['GET', 'POST'])
def patient_prescription_query():
    if 'patient_id' not in session or session.get('user_type') != 'patient':
        flash('请先登录', 'warning')
        return redirect(url_for('patient_login'))
    
    cursor = get_db_cursor()
    prescriptions = []
    
    if request.method == 'POST':
        registration_id = request.form.get('registration_id')
        prescriptions = prescription_module.query_prescription(cursor, registration_id=int(registration_id))
    
    return render_template('patient/prescription_query.html', prescriptions=prescriptions)

@app.route('/patient/payment', methods=['GET', 'POST'])
def patient_payment():
    if 'patient_id' not in session or session.get('user_type') != 'patient':
        flash('请先登录', 'warning')
        return redirect(url_for('patient_login'))
    
    cursor = get_db_cursor()
    patient_id = session['patient_id']
    
    if request.method == 'POST':
        payment_id = request.form.get('payment_id')
        payment_module.complete_payment(cursor, int(payment_id))
        flash('缴费成功', 'success')
    
    payments = payment_module.query_payment(cursor, patient_id=patient_id, time_is_null=True)
    return render_template('patient/payment.html', payments=payments)

@app.route('/patient/logout')
def patient_logout():
    session.pop('patient_id', None)
    session.pop('user_type', None)
    flash('已退出登录', 'info')
    return redirect(url_for('patient_home'))

# ============ 医生相关路由 ============

@app.route('/doctor')
def doctor_home():
    return render_template('doctor/home.html')

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        cursor = get_db_cursor()
        doctor_id = request.form.get('doctor_id')
        
        if doctor_module.check_doctor_exists(cursor, int(doctor_id)):
            session['doctor_id'] = int(doctor_id)
            session['user_type'] = 'doctor'
            flash('登录成功', 'success')
            return redirect(url_for('doctor_dashboard'))
        else:
            flash('未找到您的信息，请先联系管理员入职', 'danger')
    
    return render_template('doctor/login.html')

@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'doctor_id' not in session or session.get('user_type') != 'doctor':
        flash('请先登录', 'warning')
        return redirect(url_for('doctor_login'))
    
    cursor = get_db_cursor()
    doctor_id = session['doctor_id']
    doctor_info = doctor_module.query_doctor(cursor, doctor_id=doctor_id)
    
    return render_template('doctor/dashboard.html', doctor=doctor_info[0] if doctor_info else None)

@app.route('/doctor/registrations')
def doctor_registrations():
    if 'doctor_id' not in session or session.get('user_type') != 'doctor':
        flash('请先登录', 'warning')
        return redirect(url_for('doctor_login'))
    
    cursor = get_db_cursor()
    doctor_id = session['doctor_id']
    registrations = registration_module.query_registration(cursor, doctor_id=doctor_id)
    
    return render_template('doctor/registrations.html', registrations=registrations)

@app.route('/doctor/create_prescription', methods=['GET', 'POST'])
def doctor_create_prescription():
    if 'doctor_id' not in session or session.get('user_type') != 'doctor':
        flash('请先登录', 'warning')
        return redirect(url_for('doctor_login'))
    
    cursor = get_db_cursor()
    doctor_id = session['doctor_id']
    
    if request.method == 'POST':
        registration_id = request.form.get('registration_id')
        drug_id = request.form.get('drug_id')
        quantity = request.form.get('quantity')
        
        if not drug_module.check_drug_exists(cursor, int(drug_id)):
            flash('未找到药品信息，请先联系管理员添加药品', 'danger')
            return redirect(url_for('doctor_create_prescription'))
        
        price = drug_module.get_drug_info(cursor, int(drug_id), info_type='price') * int(quantity)
        patient_id = registration_module.get_registration_info(cursor, int(registration_id), info_type='patient')
        payment_id = payment_module.create_payment(cursor, patient_id, price)
        
        prescription_module.create_prescription(cursor, int(registration_id), int(drug_id), int(quantity), payment_id)
        
        original_quantity = drug_module.get_drug_info(cursor, int(drug_id), info_type='quantity')
        drug_module.update_drug_info(cursor, int(drug_id), stored_quantity=original_quantity - int(quantity))
        
        flash(f'处方开具成功，药品剩余库存: {original_quantity - int(quantity)}', 'success')
        return redirect(url_for('doctor_registrations'))
    
    drugs = drug_module.query_drug(cursor)
    return render_template('doctor/create_prescription.html', drugs=drugs)

@app.route('/doctor/logout')
def doctor_logout():
    session.pop('doctor_id', None)
    session.pop('user_type', None)
    flash('已退出登录', 'info')
    return redirect(url_for('doctor_home'))

# ============ 管理员相关路由 ============

@app.route('/admin')
def admin_home():
    return render_template('admin/home.html')

@app.route('/admin/departments', methods=['GET', 'POST'])
def admin_departments():
    cursor = get_db_cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            name = request.form.get('name')
            department_module.create_department(cursor, name)
            flash('科室创建成功', 'success')
        elif action == 'update':
            department_id = request.form.get('department_id')
            new_name = request.form.get('new_name')
            department_module.update_department(cursor, int(department_id), new_name)
            flash('科室更新成功', 'success')
    
    departments = department_module.query_department(cursor)
    return render_template('admin/departments.html', departments=departments)

@app.route('/admin/doctors', methods=['GET', 'POST'])
def admin_doctors():
    cursor = get_db_cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            name = request.form.get('name')
            gender = request.form.get('gender')
            phone_number = request.form.get('phone_number')
            doctor_module.register_doctor(cursor, name, gender, phone_number)
            flash('医生添加成功', 'success')
        elif action == 'set_department':
            doctor_id = request.form.get('doctor_id')
            department_id = request.form.get('department_id')
            doctor_module.set_doctor_department(cursor, int(doctor_id), int(department_id))
            flash('医生科室更新成功', 'success')
        elif action == 'set_position':
            doctor_id = request.form.get('doctor_id')
            position = request.form.get('position')
            doctor_module.set_doctor_position(cursor, int(doctor_id), position)
            flash('医生职称更新成功', 'success')
    
    doctors = doctor_module.query_doctor(cursor)
    departments = department_module.query_department(cursor)
    return render_template('admin/doctors.html', doctors=doctors, departments=departments)

@app.route('/admin/drugs', methods=['GET', 'POST'])
def admin_drugs():
    cursor = get_db_cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            name = request.form.get('name')
            quantity = request.form.get('quantity')
            price = request.form.get('price')
            drug_module.add_drug(cursor, name, int(quantity), float(price))
            flash('药品添加成功', 'success')
        elif action == 'update':
            drug_id = request.form.get('drug_id')
            update_type = request.form.get('update_type')
            update_value = request.form.get('update_value')
            
            if update_type == 'price':
                drug_module.update_drug(cursor, int(drug_id), price=float(update_value))
            elif update_type == 'quantity':
                drug_module.update_drug(cursor, int(drug_id), quantity=int(update_value))
            
            flash('药品更新成功', 'success')
    
    drugs = drug_module.query_drug(cursor)
    return render_template('admin/drugs.html', drugs=drugs)

@app.route('/admin/registrations', methods=['GET', 'POST'])
def admin_registrations():
    cursor = get_db_cursor()
    
    if request.method == 'POST':
        registration_id = request.form.get('registration_id')
        doctor_id = request.form.get('doctor_id')
        
        if registration_module.process_registration(cursor, int(registration_id), int(doctor_id)):
            patient_id = registration_module.get_registration_info(cursor, int(registration_id), info_type='patient')
            payment_id = payment_module.create_payment(cursor, patient_id, registration_fee)
            registration_module.set_registration_payment(cursor, int(registration_id), payment_id)
            flash('挂号受理成功', 'success')
        else:
            flash('挂号受理失败', 'danger')
    
    registrations = registration_module.query_registration(cursor, unassigned_only=True)
    doctors = doctor_module.query_doctor(cursor)
    return render_template('admin/registrations.html', registrations=registrations, doctors=doctors)

@app.route('/admin/tables')
def admin_tables():
    cursor = get_db_cursor()
    
    tables = {
        'patient': [],
        'department': [],
        'doctor': [],
        'drug': [],
        'payment': [],
        'registration': [],
        'prescription': []
    }
    
    for table_name in tables.keys():
        cursor.execute(f"SELECT * FROM {table_name}")
        tables[table_name] = cursor.fetchall()
    
    return render_template('admin/tables.html', tables=tables)

@app.route('/admin/reset', methods=['POST'])
def admin_reset():
    cursor = get_db_cursor()
    
    setup.drop_all_tables_for_testing(cursor)
    setup.create_table(cursor)
    
    flash('系统重置成功！', 'success')
    return redirect(url_for('admin_home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
