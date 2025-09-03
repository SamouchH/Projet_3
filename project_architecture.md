# 🎮 Projet_3 - Complete System Architecture

## System Overview

```mermaid
graph TB
    subgraph "Development Environment"
        JUPYTER[Jupyter Notebooks]
        VSCODE[VS Code / Cursor IDE]
        GIT[Git Repository]
    end

    subgraph "ML Development Pipeline"
        subgraph "Models/"
            RESEARCH[dev_jimmy.ipynb]
            EXPERIMENTS[test_model.ipynb]
        end
        
        subgraph "MLflow Tracking"
            MLRUNS[mlruns/0/]
            METADATA[meta.yaml]
        end
        
        MODEL_FILE[modele_cnn_transfer.h5]
    end

    subgraph "Production Applications"
        subgraph "FastAPI Backend"
            API[FastAPI App]
            API_MODEL[CNN Model]
            API_DB[(SQLite DB)]
        end

        subgraph "Streamlit Frontend"
            STREAMLIT[Streamlit App]
            PAGES[6 Interactive Pages]
            ST_MODEL[CNN Model Copy]
            LOGOS[Assets & Logos]
        end
    end

    subgraph "Testing Framework"
        TEST_SUITE[9 Test Files]
        TEST_IMAGE[test_predict.jpg]
        CONFTEST[conftest.py]
    end

    subgraph "Deployment & Monitoring"
        DOCKER[Docker Containers]
        COMPOSE[docker-compose.yml]
        PROMETHEUS[Prometheus Config]
        MONITORING[Monitoring Stack]
    end

    subgraph "External Services"
        OPENAI[OpenAI API]
        ANTHROPIC[Anthropic API]
        GITHUB[GitHub Repository]
    end

    %% Development Flow
    JUPYTER --> RESEARCH
    JUPYTER --> EXPERIMENTS
    RESEARCH --> MODEL_FILE
    EXPERIMENTS --> MODEL_FILE
    MODEL_FILE --> MLRUNS
    
    %% Production Deployment
    MODEL_FILE --> API_MODEL
    MODEL_FILE --> ST_MODEL
    API --> API_MODEL
    API --> API_DB
    STREAMLIT --> ST_MODEL
    STREAMLIT --> PAGES
    
    %% Testing
    TEST_SUITE --> API
    TEST_IMAGE --> TEST_SUITE
    CONFTEST --> TEST_SUITE
    
    %% Deployment
    API --> DOCKER
    STREAMLIT --> DOCKER
    DOCKER --> COMPOSE
    PROMETHEUS --> MONITORING
    
    %% External Integration
    API --> OPENAI
    API --> ANTHROPIC
    GIT --> GITHUB
    
    %% Asset Management
    LOGOS --> STREAMLIT
```

## Application Stack

```mermaid
graph LR
    subgraph "Frontend Layer"
        ST[Streamlit App<br/>Port 8501]
    end

    subgraph "Backend Layer" 
        API[FastAPI<br/>Port 8080]
    end

    subgraph "Data Layer"
        DB[(SQLite<br/>projet3_api.db)]
        FILES[File Storage<br/>uploads/predictions/]
        MODEL[ML Model<br/>9.5MB]
    end

    subgraph "ML Services"
        TENSORFLOW[TensorFlow<br/>CNN Inference]
        OPENAI_API[OpenAI<br/>Text Generation]
        ANTHROPIC_API[Anthropic<br/>Claude API]
    end

    subgraph "Infrastructure"
        DOCKER1[API Container]
        DOCKER2[Streamlit Container]
        PROMETHEUS[Prometheus<br/>Monitoring]
    end

    ST --> API
    API --> DB
    API --> FILES
    API --> MODEL
    API --> TENSORFLOW
    API --> OPENAI_API
    API --> ANTHROPIC_API
    
    API --> DOCKER1
    ST --> DOCKER2
    DOCKER1 --> PROMETHEUS
```

## Streamlit Application Structure

```mermaid
graph TB
    subgraph "Streamlit Pages"
        HOME[Home.py<br/>Main Landing Page]
        
        subgraph "Analysis & Data"
            ANALYSIS[1_📊_Analyses.py<br/>EDA & Statistics]
            LABELLING[2_🏷️_Labelisation.py<br/>Data Labeling Tools]
            PREPROCESSING[3_🔣_Preprocessing.py<br/>Data Preparation]
        end
        
        subgraph "ML & AI Features"
            BENCHMARK[4_🕵️‍♂️_Benchmark.py<br/>Model Performance]
            ASSISTANT[5_👩‍💻_Assistant.py<br/>AI Assistant]
            HYBRID[6_🤖_Hybrid_Assistant.py<br/>Advanced AI Features]
        end
    end

    subgraph "Shared Resources"
        UTILS[utils.py<br/>Helper Functions]
        GAMES_CSV[games_categories.csv<br/>Game Categories Data]
        LOGOS_DIR[logos/<br/>Game Console Images]
        MODEL_ST[modele_cnn_transfer.h5<br/>ML Model]
    end

    HOME --> ANALYSIS
    HOME --> LABELLING
    HOME --> PREPROCESSING
    HOME --> BENCHMARK
    HOME --> ASSISTANT
    HOME --> HYBRID
    
    ANALYSIS --> UTILS
    ANALYSIS --> GAMES_CSV
    LABELLING --> UTILS
    BENCHMARK --> MODEL_ST
    ASSISTANT --> MODEL_ST
    HYBRID --> MODEL_ST
    
    ANALYSIS --> LOGOS_DIR
    BENCHMARK --> LOGOS_DIR
```

## Testing Architecture

```mermaid
graph TB
    subgraph "Test Categories"
        subgraph "API Tests"
            AUTH_TEST[test_auth.py<br/>Authentication Tests]
            ADMIN_TEST[test_admin.py<br/>Admin Endpoint Tests]
            PRED_TEST[test_prediction.py<br/>Prediction Tests]
            HEALTH_TEST[test_health.py<br/>Health Check Tests]
        end
        
        subgraph "Security Tests"
            SEC_TEST[test_security.py<br/>Security Tests]
            RATE_TEST[test_ratelimit.py<br/>Rate Limiting Tests]
            VALID_TEST[test_validation.py<br/>Input Validation Tests]
        end
        
        subgraph "Utility Tests"
            UTIL_TEST[test_utils.py<br/>Helper Function Tests]
        end
    end

    subgraph "Test Infrastructure"
        CONFTEST[conftest.py<br/>Shared Test Fixtures]
        TEST_IMG[test_predict.jpg<br/>Test Image Asset]
        TEST_DOCKER[Dockerfile<br/>Test Container]
    end

    AUTH_TEST --> CONFTEST
    ADMIN_TEST --> CONFTEST
    PRED_TEST --> CONFTEST
    PRED_TEST --> TEST_IMG
    HEALTH_TEST --> CONFTEST
    SEC_TEST --> CONFTEST
    RATE_TEST --> CONFTEST
    VALID_TEST --> CONFTEST
    UTIL_TEST --> CONFTEST
```

## File Structure Overview

```
PROJET_3/
├── api/                          # Backend FastAPI Application
│   ├── core/                     # Core utilities & configuration
│   │   ├── config.py             # App configuration
│   │   ├── database.py           # Database models & connection
│   │   ├── security.py           # Authentication & security
│   │   ├── middleware.py         # Custom middleware
│   │   ├── models.py             # Pydantic models
│   │   └── logging_config.py     # Logging configuration
│   ├── services/                 # Business logic layer
│   │   ├── user_service.py       # User management
│   │   └── prediction_service.py # ML prediction logic
│   ├── main.py                   # FastAPI app entry point
│   ├── modele_cnn_transfer.h5    # Trained CNN model (9.5MB)
│   ├── projet3_api.db            # SQLite database
│   ├── Dockerfile                # API container config
│   └── requirements.txt          # Python dependencies
├── Streamlit/                    # Frontend Streamlit Application
│   ├── pages/                    # Multi-page application
│   │   ├── 1_📊_Analyses.py      # Data analysis & visualization
│   │   ├── 2_🏷️_Labelisation.py  # Data labeling interface
│   │   ├── 3_🔣_Preprocessing.py # Data preprocessing tools
│   │   ├── 4_🕵️‍♂️_Benchmark.py    # Model performance metrics
│   │   ├── 5_👩‍💻_Assistant.py     # AI assistant interface
│   │   └── 6_🤖_Hybrid_Assistant.py # Advanced AI features
│   ├── logos/                    # Game console & UI assets
│   ├── Home.py                   # Main streamlit page
│   ├── utils.py                  # Helper functions
│   ├── games_categories.csv      # Game categories dataset
│   ├── modele_cnn_transfer.h5    # Model copy for Streamlit
│   ├── Dockerfile                # Streamlit container config
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Streamlit documentation
├── Models/                       # ML Development & Research
│   ├── dev_jimmy.ipynb           # Main development notebook
│   └── test_model.ipynb          # Model testing notebook
├── Test/                         # Comprehensive test suite
│   ├── test_auth.py              # Authentication tests
│   ├── test_admin.py             # Admin functionality tests
│   ├── test_prediction.py        # ML prediction tests
│   ├── test_health.py            # Health check tests
│   ├── test_security.py          # Security tests
│   ├── test_ratelimit.py         # Rate limiting tests
│   ├── test_validation.py        # Input validation tests
│   ├── test_utils.py             # Utility function tests
│   ├── test_predict.jpg          # Test image for ML tests
│   ├── conftest.py               # Shared test fixtures
│   ├── Dockerfile                # Test container config
│   └── requirements.txt          # Test dependencies
├── data/                         # Data storage
│   └── projet3_api.db            # Database backup/copy
├── mlruns/                       # MLflow experiment tracking
│   └── 0/                        # Experiment run data
│       └── meta.yaml             # MLflow metadata
├── monitoring/                   # Monitoring & observability
│   └── prometheus.yml            # Prometheus configuration
├── docker-compose.yml            # Multi-container orchestration
├── projet3_api.db                # Main SQLite database
├── api_architecture_diagram.md   # API architecture documentation
└── README.md                     # Main project documentation
```

## Technology Stack

### Backend (FastAPI)
- **Framework**: FastAPI with Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with python-jose
- **ML Framework**: TensorFlow for CNN inference
- **AI APIs**: OpenAI GPT & Anthropic Claude
- **Testing**: pytest with comprehensive test coverage

### Frontend (Streamlit)
- **Framework**: Streamlit multi-page application
- **Data Visualization**: Plotly, Matplotlib, Seaborn
- **Image Processing**: PIL, OpenCV
- **ML Integration**: Direct TensorFlow model loading
- **UI Components**: Custom Streamlit components

### Infrastructure & Deployment
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **Monitoring**: Prometheus metrics collection
- **Development**: Jupyter notebooks for ML research
- **Version Control**: Git with GitHub integration

### Security & Production Features
- **Authentication**: JWT-based with role management
- **Rate Limiting**: 100 requests/hour per client
- **Security Headers**: CORS, XSS protection, content type validation
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Structured error responses
- **Logging**: Structured logging with different levels
- **Health Checks**: Application health monitoring endpoints

