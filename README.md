<p align="center">
  <img src="https://img.shields.io/badge/QueryMind-SQL%20RAG-6366f1?style=for-the-badge&logo=postgresql&logoColor=white" alt="QueryMind"/>
</p>

<h1 align="center">🧠 QueryMind</h1>

<p align="center">
  <strong>Natural Language to SQL — Powered by AI</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat-square&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ed?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/Azure-Deployed-0078d4?style=flat-square&logo=microsoft-azure&logoColor=white" alt="Azure"/>
</p>

</p>

---

## 🎯 What is QueryMind?

**QueryMind** is a universal SQL-RAG (Retrieval-Augmented Generation) interface that allows you to connect to any PostgreSQL database and ask questions in **natural language**. The system automatically translates your questions into SQL queries, executes them, and returns human-readable answers.

> 💡 **No SQL knowledge required!** Just connect your database and start asking questions like: *"How many orders were placed last month?"*

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language Queries** | Ask questions in plain English — no SQL required |
| 🔍 **Automatic Schema Detection** | Connects and analyzes your database structure automatically |
| ⚡ **Real-time Execution** | Generates and runs optimized SQL queries instantly |
| 📊 **Smart Responses** | Returns both raw data and natural language explanations |
| 🔐 **Secure by Design** | Read-only queries, no destructive operations allowed |
| 🌙 **Dark/Light Theme** | Modern UI with theme toggle |
| 🔑 **BYOK (Bring Your Own Key)** | Use your own OpenAI API key |
| 🐳 **Docker Ready** | One-command deployment with Docker Compose |
| ☁️ **Azure Deployed** | Production-ready on Azure Container Apps |

---

## 🛠️ Tech Stack

<table>
<tr>
<td align="center" width="96">
  <img src="https://skillicons.dev/icons?i=python" width="48" height="48" alt="Python" />
  <br><sub>Python 3.11</sub>
</td>
<td align="center" width="96">
  <img src="https://skillicons.dev/icons?i=fastapi" width="48" height="48" alt="FastAPI" />
  <br><sub>FastAPI</sub>
</td>
<td align="center" width="96">
  <img src="https://skillicons.dev/icons?i=postgres" width="48" height="48" alt="PostgreSQL" />
  <br><sub>PostgreSQL</sub>
</td>
<td align="center" width="96">
  <img src="https://skillicons.dev/icons?i=redis" width="48" height="48" alt="Redis" />
  <br><sub>Redis</sub>
</td>
<td align="center" width="96">
  <img src="https://skillicons.dev/icons?i=docker" width="48" height="48" alt="Docker" />
  <br><sub>Docker</sub>
</td>
<td align="center" width="96">
  <img src="https://skillicons.dev/icons?i=azure" width="48" height="48" alt="Azure" />
  <br><sub>Azure</sub>
</td>
</tr>
</table>

**Backend:**
- 🐍 Python 3.11+ with async/await
- ⚡ FastAPI with automatic OpenAPI docs
- 🔄 SQLAlchemy 2.0 (async) + asyncpg
- 🤖 OpenAI GPT-4o-mini for SQL generation

**Frontend:**
- 🎨 Modern single-page dashboard
- 💨 Tailwind CSS for styling
- 🌙 Dark theme
- 📱 Fully responsive design

**Infrastructure:**
- 🐳 Docker with multi-stage builds
- 📦 Docker Compose for local development
- ☁️ Azure Container Apps for production
- 🔴 Redis for schema caching (optional)

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/querymind.git
cd querymind

# Start all services
cd docker
docker-compose up -d
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/yourusername/querymind.git
cd querymind/backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

---

## 📖 Usage

### 1. Connect to Your Database

Enter your PostgreSQL connection details:
- **Host:** Your database host (e.g., `localhost`)
- **Port:** Database port (default: `5432`)
- **Database:** Database name
- **Username/Password:** Your credentials

### 2. Enter Your OpenAI API Key

QueryMind uses your own OpenAI API key to generate SQL queries. Get one at [platform.openai.com](https://platform.openai.com/api-keys).

### 3. Ask Questions!

Simply type your question in natural language:

| Question | Generated SQL |
|----------|---------------|
| "How many users do we have?" | `SELECT COUNT(*) FROM users` |
| "Show top 5 products by sales" | `SELECT name, sales FROM products ORDER BY sales DESC LIMIT 5` |
| "What's the average order value?" | `SELECT AVG(total) FROM orders` |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │────▶│    FastAPI      │────▶│   PostgreSQL    │
│   (Dashboard)   │     │    Backend      │     │   (Your DB)     │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │  OpenAI API     │
                        │  (GPT-4o-mini)  │
                        │                 │
                        └─────────────────┘
```

**Flow:**
1. User connects to their PostgreSQL database
2. System extracts and caches the schema
3. User asks a question in natural language
4. LLM generates optimized SQL based on schema
5. Query is validated and executed (read-only)
6. Results are formatted and explained

---

## 🔒 Security


| Security Feature | Description |
|-----------------|-------------|
| ✅ **Read-Only Queries** | Only SELECT statements allowed |
| ✅ **SQL Validation** | All queries checked before execution |
| ✅ **No Destructive Operations** | DROP, DELETE, UPDATE, INSERT blocked |
| ✅ **Connection Timeouts** | Prevents hanging connections |
| ✅ **Input Sanitization** | All user inputs validated |
| ✅ **BYOK Model** | Your API key never stored on server |

---

## ☁️ Azure Deployment

QueryMind is deployed on **Azure Container Apps** for production use.

### Live Demo
> 🌐 **[https://querymind.purplehill-89fc22b4.germanywestcentral.azurecontainerapps.io](https://querymind.purplehill-89fc22b4.germanywestcentral.azurecontainerapps.io)**

### Deploy Your Own

```bash
# Login to Azure
az login

# Run deployment script
cd azure
./deploy.sh
```

See [Azure Deployment Guide](azure/README.md) for detailed instructions.

---

## 📁 Project Structure

```
sql-rag-system/
├── backend/
│   └── app/
│       ├── api/routes/          # FastAPI endpoints
│       ├── core/                # Security, exceptions
│       ├── db/adapters/         # Database adapters
│       ├── llm/                 # LLM integration
│       │   └── providers/       # OpenAI, Azure OpenAI
│       ├── executor/            # Query execution
│       ├── postprocessor/       # Result formatting
│       ├── cache/               # Redis caching
│       └── models/              # Pydantic schemas
├── frontend/
│   └── index.html               # Dashboard UI
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── init-demo-db.sql
└── azure/
    └── deploy.sh
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (optional, users can provide their own) | - |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `LOG_LEVEL` | Logging level | `INFO` |

---

## 📝 API Documentation

Once running, access the interactive API docs:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/connection/connect` | Connect to database |
| `POST` | `/api/connection/disconnect` | Disconnect |
| `GET` | `/api/connection/status` | Check connection status |
| `GET` | `/api/schema/tables` | Get all tables |
| `GET` | `/api/schema/tables/{name}` | Get table details |
| `POST` | `/api/query/ask` | Ask natural language question |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
Additional Ideas:

 Data Visualization & Analysis:

    Diagram Generation (user's idea)
    Interactive Charts (bar, pie, line)
    Export to PDF/Excel

 AI & LLM Enhancements:

    Query Suggestions
    Multi-LLM Support (Claude, Gemini, Ollama)
    Query Optimization Tips
    Natural Language Explanations


---

<p align="center">
  Made with ❤️ and ☕
</p>

<p align="center">
  <a href="#-querymind">⬆️ Back to Top</a>
</p>
