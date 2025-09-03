# 🎮 Projet_3 API Architecture Diagram

## System Architecture Overview

```mermaid
graph TB
    %% External Clients
    subgraph "🌐 External Clients"
        WEB[Web Frontend]
        MOBILE[Mobile App]
        STREAMLIT[Streamlit Dashboard]
        CLI[CLI Tools]
    end

    %% Load Balancer & Gateway
    subgraph "🛡️ API Gateway Layer"
        LB[Load Balancer]
        GATEWAY[API Gateway]
    end

    %% API Application
    subgraph "🚀 FastAPI Application"
        subgraph "🔧 Core Layer"
            CONFIG[Configuration<br/>config.py]
            SECURITY[Security Service<br/>security.py]
            DB[Database Layer<br/>database.py]
            LOGGING[Logging Config<br/>logging_config.py]
        end

        subgraph "🔄 Middleware Layer"
            RATE_LIMIT[Rate Limiting<br/>middleware.py]
            CORS[CORS Middleware]
            SEC_HEADERS[Security Headers]
            AUTH_MIDDLEWARE[Auth Middleware]
        end

        subgraph "🎯 Service Layer"
            PRED_SERVICE[Prediction Service<br/>prediction_service.py]
            USER_SERVICE[User Service<br/>user_service.py]
        end

        subgraph "📡 API Endpoints"
            AUTH_ROUTES[Authentication<br/>/auth/*]
            PRED_ROUTES[Prediction<br/>/predict/*]
            ADMIN_ROUTES[Admin<br/>/admin/*]
            HEALTH_ROUTES[Health<br/>/health]
        end
    end

    %% External Services
    subgraph "🤖 ML & AI Services"
        TF_MODEL[TensorFlow Model<br/>CNN Transfer Learning]
        OPENAI[OpenAI API<br/>Text Generation]
        ANTHROPIC[Anthropic API<br/>Claude]
    end

    %% Data Storage
    subgraph "💾 Data Storage"
        SQLITE[(SQLite Database<br/>projet3_api.db)]
        FILE_STORAGE[File Storage<br/>uploads/ predictions/]
        MODEL_STORAGE[Model Storage<br/>modele_cnn_transfer.h5]
    end

    %% Monitoring & Logging
    subgraph "📊 Monitoring"
        PROMETHEUS[Prometheus<br/>Metrics]
        LOGS[Structured Logs]
        METRICS[Custom Metrics]
    end

    %% Connections
    WEB --> LB
    MOBILE --> LB
    STREAMLIT --> LB
    CLI --> LB
    
    LB --> GATEWAY
    GATEWAY --> AUTH_MIDDLEWARE
    
    AUTH_MIDDLEWARE --> SEC_HEADERS
    SEC_HEADERS --> CORS
    CORS --> RATE_LIMIT
    
    RATE_LIMIT --> AUTH_ROUTES
    RATE_LIMIT --> PRED_ROUTES
    RATE_LIMIT --> ADMIN_ROUTES
    RATE_LIMIT --> HEALTH_ROUTES
    
    AUTH_ROUTES --> USER_SERVICE
    PRED_ROUTES --> PRED_SERVICE
    ADMIN_ROUTES --> USER_SERVICE
    ADMIN_ROUTES --> PRED_SERVICE
    
    USER_SERVICE --> SECURITY
    PRED_SERVICE --> TF_MODEL
    
    SECURITY --> DB
    USER_SERVICE --> DB
    PRED_SERVICE --> DB
    
    DB --> SQLITE
    PRED_SERVICE --> FILE_STORAGE
    PRED_SERVICE --> MODEL_STORAGE
    
    TF_MODEL --> MODEL_STORAGE
    PRED_SERVICE --> OPENAI
    PRED_SERVICE --> ANTHROPIC
    
    CONFIG --> SECURITY
    CONFIG --> DB
    CONFIG --> LOGGING
    
    LOGGING --> LOGS
    PRED_SERVICE --> METRICS
    METRICS --> PROMETHEUS

    %% Styling
    classDef clientStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef apiStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serviceStyle fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef storageStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef mlStyle fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef monitoringStyle fill:#f1f8e9,stroke:#33691e,stroke-width:2px

    class WEB,MOBILE,STREAMLIT,CLI clientStyle
    class LB,GATEWAY,AUTH_MIDDLEWARE,SEC_HEADERS,CORS,RATE_LIMIT,AUTH_ROUTES,PRED_ROUTES,ADMIN_ROUTES,HEALTH_ROUTES apiStyle
    class CONFIG,SECURITY,DB,LOGGING,USER_SERVICE,PRED_SERVICE serviceStyle
    class SQLITE,FILE_STORAGE,MODEL_STORAGE storageStyle
    class TF_MODEL,OPENAI,ANTHROPIC mlStyle
    class PROMETHEUS,LOGS,METRICS monitoringStyle
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant Client as 🌐 Client
    participant Gateway as 🛡️ API Gateway
    participant Auth as 🔐 Auth Middleware
    participant RateLimit as ⏱️ Rate Limiter
    participant Service as 🎯 Service Layer
    participant ML as 🤖 ML Model
    participant DB as 💾 Database
    participant External as 🌍 External APIs

    %% Authentication Flow
    Client->>Gateway: POST /auth/login
    Gateway->>RateLimit: Check rate limit
    RateLimit->>Auth: Validate credentials
    Auth->>DB: Query user
    DB-->>Auth: User data
    Auth-->>Client: JWT Token

    %% Prediction Flow
    Client->>Gateway: POST /predict/image
    Note over Client,Gateway: With JWT token
    Gateway->>RateLimit: Check rate limit
    RateLimit->>Auth: Verify JWT
    Auth->>Service: Forward request
    Service->>ML: Load & predict
    ML-->>Service: Prediction result
    Service->>DB: Store prediction
    Service->>External: Generate description (optional)
    External-->>Service: Generated text
    Service-->>Client: Prediction response

    %% Admin Flow
    Client->>Gateway: GET /admin/stats
    Note over Client,Gateway: With admin JWT
    Gateway->>RateLimit: Check rate limit
    RateLimit->>Auth: Verify admin role
    Auth->>Service: Forward request
    Service->>DB: Query statistics
    DB-->>Service: Stats data
    Service-->>Client: Admin response
```

## Database Schema

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        boolean is_active
        datetime created_at
        datetime last_login
        int prediction_count
    }

    PREDICTIONS {
        int id PK
        int user_id FK
        string filename
        string predicted_category
        float confidence
        text probabilities
        float processing_time
        string status
        text error_message
        datetime created_at
    }

    API_KEYS {
        int id PK
        int user_id FK
        string key_hash UK
        string name
        boolean is_active
        datetime last_used
        datetime created_at
        datetime expires_at
    }

    LOGIN_ATTEMPTS {
        int id PK
        string username
        string ip_address
        boolean success
        text user_agent
        datetime created_at
    }

    USERS ||--o{ PREDICTIONS : "makes"
    USERS ||--o{ API_KEYS : "has"
    USERS ||--o{ LOGIN_ATTEMPTS : "attempts"
```

## Service Dependencies

```mermaid
graph LR
    subgraph "🎯 Main Services"
        MAIN[main.py]
        PRED[PredictionService]
        USER[UserService]
    end

    subgraph "🔧 Core Dependencies"
        CONFIG[config.py]
        SECURITY[security.py]
        DB[database.py]
        MIDDLEWARE[middleware.py]
        LOGGING[logging_config.py]
    end

    subgraph "📦 External Dependencies"
        FASTAPI[FastAPI]
        SQLALCHEMY[SQLAlchemy]
        JWT[python-jose]
        BCRYPT[passlib/bcrypt]
        TENSORFLOW[TensorFlow]
        PIL[Pillow]
        OPENAI[OpenAI]
        ANTHROPIC[Anthropic]
    end

    MAIN --> PRED
    MAIN --> USER
    MAIN --> CONFIG
    MAIN --> SECURITY
    MAIN --> MIDDLEWARE
    MAIN --> LOGGING

    PRED --> TENSORFLOW
    PRED --> PIL
    PRED --> OPENAI
    PRED --> ANTHROPIC
    PRED --> DB

    USER --> JWT
    USER --> BCRYPT
    USER --> DB

    DB --> SQLALCHEMY
    SECURITY --> JWT
    SECURITY --> BCRYPT

    MAIN --> FASTAPI
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "🐳 Docker Container"
        subgraph "🚀 API Container"
            API[FastAPI App<br/>Port 8080]
            MODEL[ML Model<br/>9.5MB]
            DB_FILE[SQLite DB<br/>60KB]
        end
    end

    subgraph "📊 Monitoring Stack"
        PROMETHEUS[Prometheus<br/>Metrics Collection]
        GRAFANA[Grafana<br/>Visualization]
    end

    subgraph "🌐 Network"
        NGINX[Nginx<br/>Reverse Proxy]
        SSL[SSL/TLS<br/>Termination]
    end

    subgraph "💾 Persistent Storage"
        VOLUME[Data Volume<br/>uploads/ predictions/ logs/]
    end

    NGINX --> SSL
    SSL --> API
    API --> MODEL
    API --> DB_FILE
    API --> VOLUME
    API --> PROMETHEUS
    PROMETHEUS --> GRAFANA

    classDef containerStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef monitoringStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef networkStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef storageStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    class API,MODEL,DB_FILE containerStyle
    class PROMETHEUS,GRAFANA monitoringStyle
    class NGINX,SSL networkStyle
    class VOLUME storageStyle
```

## Security Architecture

```mermaid
graph TB
    subgraph "🛡️ Security Layers"
        subgraph "🌐 Network Security"
            HTTPS[HTTPS/TLS]
            FIREWALL[Firewall Rules]
            WAF[Web Application Firewall]
        end

        subgraph "🔐 Application Security"
            JWT_AUTH[JWT Authentication]
            ROLE_BASED[Role-Based Access Control]
            RATE_LIMIT[Rate Limiting]
            INPUT_VALIDATION[Input Validation]
        end

        subgraph "🔒 Data Security"
            PASSWORD_HASH[Password Hashing<br/>bcrypt]
            API_KEYS[API Key Management]
            ENCRYPTION[Data Encryption]
        end

        subgraph "📊 Security Monitoring"
            AUDIT_LOGS[Audit Logging]
            SECURITY_METRICS[Security Metrics]
            ALERTS[Security Alerts]
        end
    end

    subgraph "🎯 Protected Resources"
        USER_DATA[User Data]
        PREDICTIONS[Prediction Data]
        ADMIN_FUNCTIONS[Admin Functions]
        ML_MODEL[ML Model]
    end

    HTTPS --> FIREWALL
    FIREWALL --> WAF
    WAF --> JWT_AUTH
    JWT_AUTH --> ROLE_BASED
    ROLE_BASED --> RATE_LIMIT
    RATE_LIMIT --> INPUT_VALIDATION

    INPUT_VALIDATION --> USER_DATA
    INPUT_VALIDATION --> PREDICTIONS
    INPUT_VALIDATION --> ADMIN_FUNCTIONS
    INPUT_VALIDATION --> ML_MODEL

    PASSWORD_HASH --> USER_DATA
    API_KEYS --> PREDICTIONS
    ENCRYPTION --> USER_DATA
    ENCRYPTION --> PREDICTIONS

    AUDIT_LOGS --> SECURITY_METRICS
    SECURITY_METRICS --> ALERTS

    classDef securityStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef resourceStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef monitoringStyle fill:#fff3e0,stroke:#ef6c00,stroke-width:2px

    class HTTPS,FIREWALL,WAF,JWT_AUTH,ROLE_BASED,RATE_LIMIT,INPUT_VALIDATION,PASSWORD_HASH,API_KEYS,ENCRYPTION securityStyle
    class USER_DATA,PREDICTIONS,ADMIN_FUNCTIONS,ML_MODEL resourceStyle
    class AUDIT_LOGS,SECURITY_METRICS,ALERTS monitoringStyle
```

## Key Features Summary

### 🔐 **Authentication & Authorization**
- JWT-based authentication with refresh tokens
- Role-based access control (user/admin)
- API key management for programmatic access
- Secure password hashing with bcrypt

### 🎯 **ML Prediction Pipeline**
- TensorFlow CNN model for image classification
- Support for multiple image formats (JPEG, PNG, WebP)
- Batch prediction capabilities
- Integration with OpenAI/Anthropic for text generation

### 🛡️ **Security Features**
- Rate limiting (100 requests/hour per client)
- CORS protection with allowed origins
- Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- Input validation and sanitization

### 📊 **Monitoring & Observability**
- Structured logging with different levels
- Health check endpoints
- Prometheus metrics integration
- Audit logging for security events

### 🚀 **Production Ready**
- Docker containerization
- Environment-based configuration
- Database connection pooling
- Error handling and recovery
- Comprehensive API documentation

This architecture demonstrates a well-designed, production-ready API with proper separation of concerns, security measures, and scalability considerations.
