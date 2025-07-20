# PUBG 游戏分析系统

一个基于机器学习的 PUBG（绝地求生）游戏数据分析和预测系统，提供吃鸡概率预测、AI 游戏建议生成、数据可视化分析等功能。

## 🎯 功能特性

### 核心功能

- **🎮 吃鸡概率预测**：基于游戏数据预测获胜概率
- **🤖 AI 游戏建议**：使用 DeepSeek AI 生成个性化游戏策略建议
- **📊 数据可视化**：多维度游戏数据分析图表
- **📝 历史记录管理**：预测历史查询、统计分析

### 技术特点

- **机器学习预测**：使用 scikit-learn 训练的预测模型
- **智能 AI 建议**：集成 DeepSeek AI API 生成专业建议
- **响应式界面**：现代化 Web 界面，支持移动端
- **数据库存储**：SQLite 数据库存储历史记录

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 8GB+ 内存（用于处理大型数据集）
- 网络连接（用于 AI 服务）

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd GameAnalysis
```

2. **安装依赖**

```bash
pip install -r app/requirements.txt
```

3. **配置环境变量**

```bash
# 复制环境变量模板
cp app/.env.example app/.env

# 编辑.env文件，配置DeepSeek API Key
DEEPSEEK_API_KEY=your_api_key_here
```

4. **启动应用**

```bash
cd app
python main.py
```

5. **访问应用**
   打开浏览器访问：http://127.0.0.1:5000

## 📁 项目结构

```
GameAnalysis/
├── app/                    # 应用主目录
│   ├── config/            # 配置文件
│   │   └── config.py      # 应用配置
│   ├── routes/            # 路由模块
│   │   └── api_routes.py  # API路由定义
│   ├── services/          # 服务模块
│   │   └── advice.py      # AI建议服务
│   ├── storage/           # 数据存储
│   │   └── database.py    # 数据库操作
│   ├── main.py           # 应用入口
│   ├── requirements.txt  # 依赖包列表
│   └── .env             # 环境变量配置
├── data/                 # 数据文件
│   ├── agg_match_stats_0_half.csv    # 聚合统计数据
│   ├── kill_match_stats_final_0_half.csv  # 击杀数据
│   └── *.png            # 图片资源
├── model/               # 机器学习模型
│   └── pubg_winner_model.joblib  # 预测模型文件
├── static/              # 静态资源
│   ├── css/            # 样式文件
│   └── js/             # JavaScript文件
├── templates/           # HTML模板
│   ├── index.html      # 主页
│   ├── predict.html    # 预测页面
│   └── history.html    # 历史记录页面
└── README.md           # 项目文档
```

## 🔧 API 接口文档

### 预测相关 API

#### 1. 吃鸡概率预测

```http
POST /api/predict
Content-Type: application/json

{
  "game_size": 100,
  "party_size": 4,
  "player_kills": 8,
  "player_dmg": 1200,
  "player_dbno": 3,
  "player_assists": 2,
  "player_survive_time": 1800,
  "player_dist_walk": 3000,
  "player_dist_ride": 8000
}
```

**响应示例：**

```json
{
  "probability": 0.983,
  "confidence": "high",
  "percentage": 98.3,
  "record_id": 123
}
```

#### 2. AI 建议生成

```http
POST /api/generate-advice
Content-Type: application/json

{
  "record_id": 123  // 可选，关联预测记录
}
```

**响应示例：**

```json
{
  "success": true,
  "advice": "基于您的游戏数据分析...",
  "message": "AI建议生成成功",
  "database_saved": true,
  "record_id": 123,
  "operation": "updated"
}
```

### 历史记录 API

#### 3. 获取历史记录

```http
GET /api/history?page=1&per_page=10
```

**响应示例：**

```json
{
  "history": [...],
  "pagination": {
    "current_page": 1,
    "per_page": 10,
    "total_pages": 5,
    "total_items": 50,
    "has_prev": false,
    "has_next": true
  }
}
```

#### 4. 获取统计信息

```http
GET /api/history/stats
```

### 数据可视化 API

#### 5. 测试数据连接

```http
GET /api/test
```

## 🎮 使用指南

### 1. 预测吃鸡概率

1. 访问预测页面：http://127.0.0.1:5000/predict
2. 填写游戏参数（队伍规模、击杀数、伤害等）
3. 点击"开始预测"获取吃鸡概率
4. 查看预测结果和置信度

### 2. 生成 AI 建议

1. 在预测结果页面点击"生成 AI 建议"
2. 等待 AI 分析并生成个性化建议
3. 查看详细的游戏策略建议

### 3. 查看历史记录

1. 访问历史页面：http://127.0.0.1:5000/history
2. 浏览所有预测历史和 AI 建议
3. 查看统计信息和趋势分析

## ⚙️ 配置说明

### 环境变量配置

在`app/.env`文件中配置以下参数：

```env
# AI API配置
DEEPSEEK_API_KEY=your_deepseek_api_key

# API超时设置（秒）
API_TIMEOUT=30

# 服务器配置
PORT=5000
```

### 数据库配置

系统使用 SQLite 数据库，数据库文件位于：

- `app/history_service.db`

数据库会在首次运行时自动创建和初始化。

## 🔍 故障排除

### 常见问题

1. **模型文件未找到**

   - 确保`model/pubg_winner_model.joblib`文件存在
   - 检查文件路径是否正确

2. **AI 建议生成失败**

   - 检查 DeepSeek API Key 是否正确配置
   - 确认网络连接正常
   - 检查 API 配额是否充足

3. **数据加载失败**

   - 确保`data/`目录下的 CSV 文件存在
   - 检查文件权限和路径

4. **端口占用**
   - 修改`.env`文件中的 PORT 配置
   - 或终止占用 5000 端口的进程

## 📊 数据说明

### 输入参数说明

- `game_size`: 游戏总人数 (50-100)
- `party_size`: 队伍规模 (1-4)
- `player_kills`: 击杀数 (0-50)
- `player_dmg`: 造成伤害 (0-10000)
- `player_dbno`: 击倒数 (0-50)
- `player_assists`: 助攻数 (0-20)
- `player_survive_time`: 生存时间 (0-3600 秒)
- `player_dist_walk`: 步行距离 (0-20000 米)
- `player_dist_ride`: 载具行驶距离 (0-20000 米)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目！

### 代码规范

- 遵循 PEP 8 编码规范
- 使用 4 空格缩进
- 行长度 ≤88 字符
- 优先使用 f-string 格式化

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至：[your-email@example.com]

---

**享受游戏，提升技能！** 🎮✨
