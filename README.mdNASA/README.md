# 🚀 NEXUS - NASA Space Biology Knowledge Engine

<div align="center">
  <img src="frontend/public/logo.jpg" alt="NEXUS Logo" width="300"/>
  
  **AI-Powered Platform for NASA Open Science Data Repository (OSDR) Exploration**
  
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
  [![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Workflow](#-workflow)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Data Sources](#-data-sources)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Project Overview

**NEXUS** is an advanced AI-powered knowledge engine designed to explore, analyze, and visualize NASA's Open Science Data Repository (OSDR). The platform provides researchers, scientists, and space biology enthusiasts with intuitive tools to discover insights from thousands of space biology datasets.

### Mission
To democratize access to NASA's space biology research data through intelligent search, interactive visualizations, and AI-powered analysis tools.

### Vision
Create a unified platform that transforms complex space biology data into actionable insights, accelerating scientific discovery and space exploration research.

---

## ✨ Key Features

### 🔍 **Neural Search Command**
- **AI-Powered Semantic Search**: Natural language queries across 138,000+ NASA datasets
- **Advanced Filtering**: Filter by organisms (Mus musculus, Arabidopsis, etc.) and missions (SpaceX CRS, ISS Expeditions)
- **Real-time Results**: Instant search with intelligent ranking
- **Smart Suggestions**: AI-generated search recommendations

### 🧬 **Knowledge Graph Laboratory**
- **Interactive Visualization**: 3D force-directed graph of biological relationships
- **Dynamic Filtering**: Filter by study, organism, or mission nodes
- **Relationship Mapping**: Visualize connections between studies, organisms, and missions
- **Real-time Updates**: Graph builds dynamically from NASA OSDR data

### 📊 **Mission Control Dashboard**
- **Live Statistics**: Real-time counts of datasets, organisms, and missions
- **Dataset Cards**: Beautiful cards with descriptions, organisms, and missions
- **Quick Launch**: Fast access to all platform features
- **AI Insights**: Automated insights from space biology research

### 📄 **Publication Analysis**
- **AI Summarization**: Automated summaries of research publications
- **Citation Analysis**: Track research impact and connections
- **Trend Detection**: Identify emerging research areas

### 📁 **Dataset Detail Pages**
- **Comprehensive Metadata**: Full study information from NASA OSDR
- **File Management**: Browse and download study files
- **Rich Descriptions**: Detailed study descriptions and objectives
- **Study Details**: Organisms, missions, assay types, and more

---

## 🛠️ Tech Stack

### **Frontend**
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3+ | UI Framework |
| **TypeScript** | 5.0+ | Type Safety |
| **Vite** | 5.4+ | Build Tool & Dev Server |
| **TailwindCSS** | 3.4+ | Styling Framework |
| **React Router** | 6.0+ | Client-side Routing |
| **React Query** | 5.0+ | Data Fetching & Caching |
| **Lucide React** | Latest | Icon Library |
| **Recharts** | 2.0+ | Data Visualization |

### **Backend**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming Language |
| **FastAPI** | 0.104+ | Web Framework |
| **Uvicorn** | 0.24+ | ASGI Server |
| **httpx** | 0.25+ | Async HTTP Client |
| **SQLite** | 3.0+ | Caching & Graph Storage |
| **Pydantic** | 2.0+ | Data Validation |
| **python-dotenv** | 1.0+ | Environment Management |

### **AI & ML**
| Technology | Purpose |
|------------|---------|
| **Google Gemini API** | AI-powered insights and summarization |
| **OpenAI API** | Alternative AI provider (optional) |

### **Data Sources**
| Source | Purpose |
|--------|---------|
| **NASA OSDR API** | Primary data source for space biology datasets |
| **NASA GEODE API** | Experiments, missions, and metadata |
| **GeneLab** | Genomics and omics data |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     NEXUS Platform                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   Frontend   │◄────►│   Backend    │                   │
│  │   (React)    │      │  (FastAPI)   │                   │
│  └──────────────┘      └──────────────┘                   │
│         │                      │                           │
│         │                      ▼                           │
│         │              ┌──────────────┐                   │
│         │              │  Cache Layer │                   │
│         │              │   (SQLite)   │                   │
│         │              └──────────────┘                   │
│         │                      │                           │
│         ▼                      ▼                           │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  UI Components│      │ NASA OSDR API│                   │
│  │  - Dashboard  │      │ - Search     │                   │
│  │  - Laboratory │      │ - Metadata   │                   │
│  │  - Search     │      │ - Files      │                   │
│  │  - Publications│     └──────────────┘                   │
│  └──────────────┘              │                           │
│         │                      ▼                           │
│         │              ┌──────────────┐                   │
│         │              │  AI Services │                   │
│         │              │  - Gemini    │                   │
│         │              │  - OpenAI    │                   │
│         │              └──────────────┘                   │
│         │                      │                           │
│         ▼                      ▼                           │
│  ┌──────────────────────────────────┐                     │
│  │     Knowledge Graph Engine       │                     │
│  │  - Node/Edge Management          │                     │
│  │  - Relationship Mapping          │                     │
│  │  - Dynamic Updates               │                     │
│  └──────────────────────────────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow

### **Data Flow Architecture**


    A[User Request] --> B{Request Type}
    B -->|Search| C[Neural Search]
    B -->|Browse| D[Dashboard]
    B -->|Visualize| E[Laboratory]
    B -->|Details| F[Dataset Detail]
    
    C --> G[Backend API]
    D --> G
    E --> G
    F --> G
    
    G --> H{Cache Check}
    H -->|Hit| I[Return Cached Data]
    H -->|Miss| J[NASA OSDR API]
    
    J --> K[Data Processing]
    K --> L[Transform & Filter]
    L --> M[Cache Storage]
    M --> N[Return to Frontend]
    
    I --> N
    N --> O[UI Rendering]
```

### **Key Workflows**

#### 1. **Dataset Discovery Workflow**
```
User Input → Search Query → Backend Processing → NASA OSDR Search API
→ Filter (OSD-*, GLDS-* only) → Extract Metadata → Cache Results
→ Return to Frontend → Display Cards → User Selection → Detail Page
```

#### 2. **Knowledge Graph Building Workflow**
```
Fetch Datasets → Extract Entities (Studies, Organisms, Missions)
→ Create Nodes → Establish Relationships → Build Edges
→ Store in SQLite → Render 3D Graph → Interactive Exploration
```

#### 3. **AI Analysis Workflow**
```
Dataset Selection → Fetch Full Metadata → Send to AI Service
→ Generate Insights → Extract Key Findings → Format Results
→ Display to User → Cache for Future Use
```

---

## 📦 Installation

### **Prerequisites**
- **Node.js** 18+ and npm/yarn
- **Python** 3.11+
- **Git**

### **Backend Setup**

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/nexus.git
cd nexus/backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
cp .env.example .env

# 6. Edit .env and add your API keys
# GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here (optional)

# 7. Start the backend server
uvicorn app.main:app --reload
```

Backend will run on: `http://localhost:8000`

### **Frontend Setup**

```bash
# 1. Navigate to frontend directory
cd ../frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

Frontend will run on: `http://localhost:3000`

---

## 🚀 Usage

### **Accessing the Platform**

1. **Open your browser** and navigate to `http://localhost:3000`
2. **Explore the Dashboard** to see recent NASA datasets
3. **Use Neural Search** to find specific studies
4. **Visit the Laboratory** to visualize knowledge graphs
5. **Click on any dataset** to view detailed information

### **Common Tasks**

#### **Search for Datasets**
```
1. Go to Neural Search page
2. Enter search terms (e.g., "microgravity effects on cells")
3. Apply filters (organisms, missions)
4. Browse results
5. Click on a dataset for details
```

#### **Explore Knowledge Graph**
```
1. Navigate to Laboratory page
2. Wait for graph to load
3. Use filters to focus on specific node types
4. Click on nodes to see details
5. Explore relationships between entities
```

#### **View Dataset Details**
```
1. Click on any dataset card
2. View full description and metadata
3. Browse available files
4. Download data files
5. View related studies
```

---

## 📚 API Documentation

### **Base URL**
```
http://localhost:8000/api
```

### **Key Endpoints**

#### **Datasets**
```http
GET /api/datasets?limit=50&page=0
```
Returns paginated list of NASA OSDR datasets.

**Response:**
```json
{
  "data": [...],
  "count": 50,
  "total": 138336,
  "page": 0,
  "size": 50,
  "source": "NASA OSDR API"
}
```

#### **Study Details**
```http
GET /api/study/{study_id}
```
Returns comprehensive metadata for a specific study.

**Example:**
```http
GET /api/study/OSD-575
```

#### **Search**
```http
POST /api/search
```
Search datasets with filters.

**Request Body:**
```json
{
  "query": "microgravity",
  "organisms": ["Mus musculus"],
  "missions": ["SpaceX CRS-4"]
}
```

#### **Organisms**
```http
GET /api/organisms
```
Returns list of organisms from NASA studies.

#### **Missions**
```http
GET /api/missions
```
Returns list of space missions.

#### **Knowledge Graph**
```http
GET /api/graph
```
Returns graph nodes and edges.

For complete API documentation, visit: `http://localhost:8000/docs`

---

## 📁 Project Structure

```
NEXUS/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration and settings
│   │   ├── routes.py            # API route definitions
│   │   ├── nasa_client.py       # NASA OSDR API client
│   │   ├── cache_service.py     # Caching layer
│   │   ├── graph_service.py     # Knowledge graph management
│   │   ├── ai_service.py        # AI/ML integration
│   │   └── models.py            # Pydantic models
│   ├── data/                    # SQLite databases
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example            # Environment template
│   └── README.md               # Backend documentation
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx   # Main dashboard
│   │   │   ├── Laboratory.tsx  # Knowledge graph
│   │   │   ├── Search.tsx      # Neural search
│   │   │   ├── Publication.tsx # Publication analysis
│   │   │   └── DatasetDetail.tsx # Dataset details
│   │   ├── components/
│   │   │   ├── Navbar.tsx      # Navigation bar
│   │   │   ├── MissionCard.tsx # Dataset card component
│   │   │   └── ui/             # UI components
│   │   ├── hooks/
│   │   │   └── useNasaData.ts  # React Query hooks
│   │   ├── services/
│   │   │   └── nasaApi.ts      # API client
│   │   └── App.tsx             # React app root
│   ├── public/
│   │   └── logo.jpg            # NEXUS logo
│   ├── package.json            # Node dependencies
│   ├── tailwind.config.ts      # Tailwind configuration
│   └── vite.config.ts          # Vite configuration
│
├── README.md                   # This file
└── LICENSE                     # MIT License
```

---

## 🌐 Data Sources

### **NASA Open Science Data Repository (OSDR)**
- **URL**: https://osdr.nasa.gov
- **Purpose**: Primary source for space biology datasets
- **Data**: 138,000+ studies, experiments, and datasets
- **API**: RESTful API with search, metadata, and file endpoints

### **NASA GeneLab**
- **URL**: https://genelab.nasa.gov
- **Purpose**: Genomics and omics data
- **Data**: Gene expression, proteomics, metabolomics

### **NASA GEODE**
- **URL**: https://visualization.osdr.nasa.gov
- **Purpose**: Experiments, missions, and metadata
- **Data**: Mission details, payload information

---

## 📊 Summary

### **Project Highlights**

- ✅ **138,000+ Datasets**: Access to NASA's complete OSDR collection
- ✅ **AI-Powered Search**: Intelligent semantic search with natural language
- ✅ **Interactive Visualization**: 3D knowledge graph of biological relationships
- ✅ **Real-time Data**: Live updates from NASA OSDR API
- ✅ **Modern UI**: Beautiful cyan-themed interface with smooth animations
- ✅ **Fast Performance**: Optimized caching and data fetching
- ✅ **Type-Safe**: Full TypeScript support on frontend
- ✅ **API-First**: RESTful API with comprehensive documentation

### **Key Achievements**

1. **Data Integration**: Successfully integrated multiple NASA APIs
2. **Filtering System**: Implemented robust filtering for genuine NASA studies (OSD-*, GLDS-*)
3. **Knowledge Graph**: Built dynamic graph from real NASA data
4. **AI Integration**: Integrated Google Gemini for insights and analysis
5. **Caching Layer**: Implemented efficient SQLite caching
6. **Responsive Design**: Mobile-friendly interface with TailwindCSS
7. **Performance**: Optimized data fetching with React Query

### **Technical Innovations**

- **Dual-source Data Fetching**: Combines search API and metadata API for complete data
- **Smart Caching**: Multi-layer caching (browser, backend, database)
- **Dynamic Graph Building**: Real-time graph construction from live data
- **Intelligent Filtering**: Backend and frontend filtering for data quality
- **Async Architecture**: Fully asynchronous backend for high performance

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### **Development Guidelines**

- Follow existing code style
- Write meaningful commit messages
- Add tests for new features
- Update documentation
- Ensure all tests pass

---



---

## 🙏 Acknowledgments

- **NASA Open Science Data Repository** for providing open access to space biology data
- **NASA GeneLab** for genomics and omics datasets
- **FastAPI** for the excellent Python web framework
- **React** and **Vite** for modern frontend development
- **Google Gemini** for AI capabilities

---

## 📞 Contact

**Project Maintainer**: Neil and Ancilla 
- **Email**: mathiasneilemmanuel@gmail.com and ancilla.souza2005@gmail.com
- **GitHub**: [@Neil2813](https://github.com/Neil2813) and 
              [@ancilla13] (https://github.com/ancilla13)


---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

<div align="center">
  <p>Made with ❤️ for Space Biology Research</p>
  <p>© 2025 NEXUS - NASA Space Biology Knowledge Engine</p>
</div>
