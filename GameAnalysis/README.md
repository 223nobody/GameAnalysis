# 题目服务 API

基于 FastAPI 的 Web 服务，使用 AI 生成和管理编程题目。

## 项目概述

题目服务 API 是一个现代化的 Web 应用程序，专门用于生成和管理编程相关的题目。该系统集成了 DeepSeek AI 服务，能够自动生成高质量的编程题目，支持单选题、多选题和编程题三种类型。

### 主要功能

- 🤖 **AI 驱动的题目生成**：集成 DeepSeek API，智能生成编程题目
- 📊 **多种题目类型**：支持单选题、多选题和编程题
- 🔍 **分页和搜索**：高效的数据检索和分页显示
- 💾 **持久化存储**：使用 SQLite 数据库存储题目数据
- 🌐 **RESTful API**：完整的 CRUD 操作接口
- 🚀 **高性能异步**：基于 FastAPI 的异步架构
- 🔧 **批量操作**：支持批量插入和删除题目

## 技术栈

### 核心框架

- **Web 框架**: FastAPI 0.104.1
- **ASGI 服务器**: Uvicorn 0.24.0
- **数据库**: SQLite + aiosqlite 0.19.0

### AI 服务

- **AI 提供商**: DeepSeek API
- **HTTP 客户端**: httpx 0.25.2

### 数据处理

- **数据验证**: Pydantic 2.5.0
- **配置管理**: python-dotenv 1.0.0

### 开发工具

- **测试框架**: pytest 7.4.3 + pytest-asyncio 0.21.1
- **代码格式化**: black 23.11.0
- **代码检查**: flake8 6.1.0

## 项目结构

```
python/
├── app/                          # 应用程序核心代码
│   ├── api/                      # API 响应工具
│   │   └── response.py          # 统一响应格式
│   ├── config/                   # 配置管理
│   │   └── config.py            # 应用配置和验证
│   ├── controllers/              # 控制器层
│   │   ├── actions.py           # 题目管理操作
│   │   └── question.py          # AI 题目生成
│   ├── services/                 # 服务层
│   │   ├── client.py            # AI 服务客户端接口
│   │   └── deepseek.py          # DeepSeek API 实现
│   └── storage/                  # 数据存储层
│       └── database.py          # 数据库操作
├── main.py                       # 应用程序入口
├── requirements.txt              # 项目依赖
├── question_service.db          # SQLite 数据库文件
└── README.md                    # 项目文档
```

## 安装和运行

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装步骤

1. **克隆项目**

   ```bash
   git clone <repository-url>
   cd python
   ```

2. **创建虚拟环境（推荐）**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**

   创建 `.env` 文件：

   ```bash
   # DeepSeek API 配置
   DEEPSEEK_API_KEY=your_deepseek_api_key_here

   # 可选配置
   API_TIMEOUT=30
   ```

5. **启动应用**
   ```bash
   python main.py
   ```

应用将在 `http://localhost:8080` 启动。

## 配置说明

### 环境变量

| 变量名             | 必需 | 默认值 | 说明                   |
| ------------------ | ---- | ------ | ---------------------- |
| `DEEPSEEK_API_KEY` | ✅   | -      | DeepSeek API 密钥      |
| `API_TIMEOUT`      | ❌   | 30     | API 请求超时时间（秒） |

### 题目类型

- **类型 1**: 单选题 - 必须有且仅有一个正确答案
- **类型 2**: 多选题 - 2-4 个正确答案，按字母顺序排列
- **类型 3**: 编程题 - 不需要选项和标准答案

### 支持的编程语言

- Go、Java、Python、JavaScript、C++、CSS、HTML

## API 接口文档

服务启动后，可以访问：

- **交互式 API 文档**: http://localhost:8080/docs
- **备用 API 文档**: http://localhost:8080/redoc

### 主要接口

#### AI 题目生成

**POST** `/api/question/CreateByAI`

生成 AI 题目

请求体示例：

```json
{
  "keyword": "golang并发",
  "model": "deepseek",
  "language": "go",
  "count": 3,
  "type": 1
}
```

**POST** `/api/question/batch-insert`

批量插入题目到数据库

#### 题目管理

**DELETE** `/api/stats/batch-delete`

批量删除题目

请求体示例：

```json
{
  "ids": [1, 2, 3]
}
```

#### 统计和查询

**GET** `/api/stats/summary`

获取所有题目（分页）

查询参数：

- `page`: 页码（默认：1）
- `page_size`: 每页大小（默认：10）
- `search`: 搜索关键词（可选）

**GET** `/api/stats/bytype1`

获取单选题（分页）

**GET** `/api/stats/bytype2`

获取多选题（分页）

**GET** `/api/stats/bytype3`

获取编程题（分页）

#### 系统接口

**GET** `/api/health`

健康检查接口

### 数据库结构

应用使用 SQLite 数据库 (`question_service.db`)，表结构如下：

```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    type INTEGER NOT NULL,  -- 1: 单选题, 2: 多选题, 3: 编程题
    language TEXT NOT NULL,
    answers TEXT NOT NULL,  -- JSON 数组
    rights TEXT NOT NULL    -- 正确答案的 JSON 数组
);
```

## 使用示例

### 生成 AI 题目

```bash
curl -X POST "http://localhost:8080/api/question/CreateByAI" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "python列表",
    "model": "deepseek",
    "language": "python",
    "count": 3,
    "type": 2
  }'
```

### 按类型获取题目

```bash
curl "http://localhost:8080/api/stats/bytype1?page=1&page_size=10&search=golang"
```

### 批量删除题目

```bash
curl -X DELETE "http://localhost:8080/api/stats/batch-delete" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [1, 2, 3]
  }'
```

### 批量插入题目

```bash
curl -X POST "http://localhost:8080/api/question/batch-insert" \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      {
        "type": 1,
        "title": "Go语言中哪个关键字用于声明变量？",
        "language": "go",
        "answers": ["A: var", "B: let", "C: const", "D: define"],
        "rights": ["A"]
      }
    ]
  }'
```

## 开发指南

### 代码规范

本项目遵循 Python 最佳实践：

- **PEP 8** 代码格式规范
- **snake_case** 变量和函数命名
- **PascalCase** 类命名
- **4 空格** 缩进
- **行长度 ≤ 88** 字符
- **f-string** 字符串格式化

### 运行测试

```bash
# 安装测试依赖（如果尚未安装）
pip install pytest pytest-asyncio

# 运行测试
pytest
```

### 代码格式化

```bash
# 使用 black 格式化代码
black .

# 使用 flake8 检查代码风格
flake8 .
```

## 架构特点

### 异步架构

- 基于 FastAPI 的全异步实现
- 使用 aiosqlite 进行异步数据库操作
- httpx 异步 HTTP 客户端

### 模块化设计

- **控制器层**：处理 HTTP 请求和响应
- **服务层**：业务逻辑和 AI 服务集成
- **存储层**：数据库操作和数据持久化
- **配置层**：环境变量和应用配置管理

## 故障排除

### 常见问题

1. **导入错误**

   - 确保在正确的目录中且虚拟环境已激活
   - 检查所有依赖是否已安装：`pip install -r requirements.txt`

2. **API 密钥错误**

   - 验证 `.env` 文件中配置了 DeepSeek API 密钥
   - 检查 API 密钥的有效性和权限

3. **数据库错误**

   - 确保应用程序目录有写权限
   - 数据库文件将在首次运行时自动创建

4. **端口被占用**
   - 修改应用程序中的端口配置或终止占用端口的进程

### 日志

应用程序将重要事件记录到控制台。查看控制台输出以获取详细的错误消息和调试信息。

## 性能优化

### 数据库优化

- 使用连接池管理数据库连接
- 对常用查询字段建立索引
- 批量操作减少数据库访问次数

### API 优化

- 异步处理提高并发性能
- 分页查询避免大量数据传输
- 响应缓存减少重复计算

## 许可证

本项目采用 MIT 许可证。
