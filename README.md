# 门诊管理系统 (Outpatient Management System)

这是一个基于 Flask 的门诊管理系统，从原来的命令行界面（CLI）改造为 Web 应用程序。

## 功能特点

### 病人端
- 病人注册和登录
- 查询病人信息
- 查看科室信息
- 在线挂号
- 查询挂号记录
- 查询处方信息
- 在线缴费
- 修改个人信息

### 医生端
- 医生登录
- 查看待办挂号
- 开具处方

### 管理员端
- 科室管理（新增、修改）
- 医生管理（新增、修改科室、修改职称）
- 药品管理（新增、修改价格和库存）
- 挂号受理（分配医生）
- 查看所有表数据
- 系统重置

## 技术栈

- **后端**: Flask 3.0.0
- **数据库**: MySQL (通过 PyMySQL)
- **前端**: HTML5, CSS3 (响应式设计)
- **模板引擎**: Jinja2

## 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/18434017252/Outpatient-management-system.git
cd Outpatient-management-system
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置数据库连接

编辑 `app.py` 文件，修改数据库配置：

```python
config = {
    'host': 'your_host',
    'port': 3306,
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}
```

4. 初始化数据库

首次运行时，可以使用 `main.py` 来初始化数据库表和测试数据：

```bash
python main.py
```

注意：这将重置数据库并创建初始测试数据。

## 运行应用

### 使用 Flask 开发服务器

```bash
python app.py
```

应用将在 `http://127.0.0.1:5000` 上运行。

### 生产环境部署

对于生产环境，建议使用 WSGI 服务器如 Gunicorn：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 使用说明

1. **首页**: 访问 `http://127.0.0.1:5000` 查看首页，选择进入病人、医生或管理员系统

2. **病人系统**:
   - 新用户先注册，获得病历号
   - 使用病历号登录
   - 可进行挂号、查询、缴费等操作

3. **医生系统**:
   - 使用工号登录
   - 查看分配给自己的挂号
   - 为病人开具处方

4. **管理员系统**:
   - 管理科室、医生、药品信息
   - 处理挂号分配
   - 查看系统数据

## 项目结构

```
Outpatient-management-system/
├── app.py                  # Flask 主应用
├── frontend.py            # 原命令行界面（已弃用）
├── main.py               # 数据库初始化脚本
├── setup.py              # 数据库表创建脚本
├── requirements.txt      # Python 依赖
├── entity/               # 实体模块
│   ├── patient.py       # 病人相关操作
│   ├── doctor.py        # 医生相关操作
│   ├── department.py    # 科室相关操作
│   ├── drug.py          # 药品相关操作
│   ├── registration.py  # 挂号相关操作
│   ├── prescription.py  # 处方相关操作
│   └── payment.py       # 缴费相关操作
├── templates/            # HTML 模板
│   ├── base.html        # 基础模板
│   ├── index.html       # 首页
│   ├── patient/         # 病人模板
│   ├── doctor/          # 医生模板
│   └── admin/           # 管理员模板
└── static/              # 静态文件
    └── css/
        └── style.css    # 样式表
```

## 数据库表结构

系统使用 7 个主要表：

1. **patient** - 病人信息表
2. **department** - 科室信息表
3. **doctor** - 医生信息表
4. **drug** - 药品信息表
5. **payment** - 缴费记录表
6. **registration** - 挂号记录表
7. **prescription** - 处方记录表

详细表结构请参考 `setup.py`。

## 安全注意事项

⚠️ **重要**: 在生产环境中使用前，请务必：

1. 修改 `app.secret_key` 为随机字符串
2. 不要在代码中硬编码数据库密码
3. 使用环境变量存储敏感信息
4. 启用 HTTPS
5. 添加适当的用户认证和授权机制
6. 实施 SQL 注入防护（已有基础防护）
7. 添加 CSRF 保护

## 从 CLI 到 Web 的改造

本项目原本是一个基于命令行的系统（`frontend.py`），现已改造为 Web 应用：

- ✅ 所有 CLI 功能已迁移到 Web 界面
- ✅ 使用 Flask 框架构建 RESTful 路由
- ✅ 响应式 Web 设计，支持移动设备
- ✅ 用户友好的界面和操作流程
- ✅ 保留原有所有业务逻辑和数据库操作

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。