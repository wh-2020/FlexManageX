# FlexManageX

基于Python 3.13、 FastAPI + Tortoise ORM + MySQL实现的后端API接口。

## 技术栈

- Python 3.13+
- FastAPI
- Tortoise ORM
- MySQL
- Redis
- JWT认证

## 项目结构

```
python_api/
├── app/                    # 应用目录
│   ├── api/                # API接口
│   │   ├── endpoints/      # API端点
│   │   └── __init__.py     # API路由注册
│   ├── core/               # 核心配置
│   │   ├── config.py       # 配置文件
│   │   ├── redis.py        # Redis客户端
│   │   └── security.py     # 安全相关
│   ├── db/                 # 数据库
│   │   └── init_db.py      # 数据库初始化
│   ├── models/             # 数据模型
│   │   ├── user.py         # 用户模型
│   │   ├── role.py         # 角色模型
│   │   └── permission.py   # 权限模型
│   ├── schemas/            # 请求/响应模式
│   │   ├── user.py         # 用户相关模式
│   │   ├── role.py         # 角色相关模式
│   │   └── permission.py   # 权限相关模式
│   ├── services/           # 业务服务
│   │   ├── user.py         # 用户服务
│   │   ├── role.py         # 角色服务
│   │   ├── permission.py   # 权限服务
│   │   └── auth.py         # 认证服务
│   ├── utils/              # 工具函数
│   │   ├── dependencies.py # 依赖函数
│   │   ├── exceptions.py   # 异常处理
│   │   └── response.py     # 响应格式
│   └── main.py             # 应用入口
├── .env                    # 环境变量
├── requirements.txt        # 依赖包
└── run.py                  # 启动脚本
```

## 安装与运行

1. 克隆项目

```bash
git clone <repository-url>
cd python_api
```

2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 配置环境变量

编辑 `.env` 文件，设置数据库连接等配置。

5. 初始化数据库

使用 `init.sql` 脚本初始化数据库。

6. 运行应用

```bash
python run.py
```

应用将在 http://localhost:8089 运行。

## API文档

启动应用后，访问 http://localhost:8089/docs 查看API文档。

## 许可证

MIT 
