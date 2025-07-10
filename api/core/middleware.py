from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from typing import Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

from .config import settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de limitation du taux de requêtes"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.requests = defaultdict(list)
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window_seconds = settings.RATE_LIMIT_WINDOW
        self.cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Démarrage de la tâche de nettoyage périodique"""
        async def cleanup():
            while True:
                await asyncio.sleep(300)  # Nettoyage toutes les 5 minutes
                await self._cleanup_old_requests()
        
        self.cleanup_task = asyncio.create_task(cleanup())
    
    async def _cleanup_old_requests(self):
        """Nettoyage des anciennes requêtes"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.window_seconds)
        
        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > cutoff_time
            ]
            
            if not self.requests[client_id]:
                del self.requests[client_id]
    
    def _get_client_identifier(self, request: Request) -> str:
        """Identification du client (IP + User-Agent)"""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        return f"{client_ip}:{hash(user_agent)}"
    
    async def dispatch(self, request: Request, call_next):
        """Traitement des requêtes avec limitation du taux"""
        # Exemption pour les routes de santé
        if request.url.path in ["/health", "/", "/docs", "/redoc"]:
            return await call_next(request)
        
        client_id = self._get_client_identifier(request)
        now = datetime.utcnow()
        
        # Nettoyage des anciennes requêtes pour ce client
        cutoff_time = now - timedelta(seconds=self.window_seconds)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff_time
        ]
        
        # Vérification de la limite
        if len(self.requests[client_id]) >= self.max_requests:
            logger.warning(f"Rate limit dépassé pour {client_id}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Trop de requêtes",
                    "detail": f"Limite de {self.max_requests} requêtes par {self.window_seconds}s dépassée",
                    "retry_after": self.window_seconds
                },
                headers={"Retry-After": str(self.window_seconds)}
            )
        
        # Enregistrement de la requête
        self.requests[client_id].append(now)
        
        # Ajout des headers de rate limiting
        response = await call_next(request)
        
        remaining = max(0, self.max_requests - len(self.requests[client_id]))
        reset_time = int((now + timedelta(seconds=self.window_seconds)).timestamp())
        
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware pour les headers de sécurité"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Headers de sécurité
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware de logging des requêtes"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Informations de la requête
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Traitement de la requête
        try:
            response = await call_next(request)
            
            # Calcul du temps de traitement
            process_time = time.time() - start_time
            
            # Logging de la requête
            logger.info(
                f"{client_ip} - {method} {url} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            # Ajout du header de temps de traitement
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                f"{client_ip} - {method} {url} - "
                f"Error: {str(e)} - "
                f"Time: {process_time:.3f}s"
            )
            
            raise e

class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware de validation des requêtes"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.max_content_length = settings.MAX_FILE_SIZE
    
    async def dispatch(self, request: Request, call_next):
        # Validation de la taille du contenu
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_content_length:
            return JSONResponse(
                status_code=413,
                content={
                    "error": "Contenu trop volumineux",
                    "detail": f"Taille maximale autorisée : {self.max_content_length / (1024*1024):.1f}MB"
                }
            )
        
        # Validation du Content-Type pour les uploads
        if request.method == "POST" and "/predict/" in request.url.path:
            content_type = request.headers.get("content-type", "")
            if "multipart/form-data" not in content_type:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Type de contenu invalide",
                        "detail": "Les prédictions nécessitent multipart/form-data"
                    }
                )
        
        return await call_next(request)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware de collecte de métriques"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.metrics = {
            "requests_total": 0,
            "requests_by_method": defaultdict(int),
            "requests_by_status": defaultdict(int),
            "response_times": [],
            "errors_total": 0,
            "predictions_total": 0
        }
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Collecte des métriques
            process_time = time.time() - start_time
            
            self.metrics["requests_total"] += 1
            self.metrics["requests_by_method"][request.method] += 1
            self.metrics["requests_by_status"][response.status_code] += 1
            self.metrics["response_times"].append(process_time)
            
            # Comptage des prédictions
            if "/predict/" in request.url.path and response.status_code == 200:
                self.metrics["predictions_total"] += 1
            
            # Limitation de l'historique des temps de réponse
            if len(self.metrics["response_times"]) > 1000:
                self.metrics["response_times"] = self.metrics["response_times"][-1000:]
            
            return response
            
        except Exception as e:
            self.metrics["errors_total"] += 1
            process_time = time.time() - start_time
            self.metrics["response_times"].append(process_time)
            raise e
    
    def get_metrics(self) -> Dict[str, Any]:
        """Récupération des métriques collectées"""
        response_times = self.metrics["response_times"]
        
        return {
            "requests_total": self.metrics["requests_total"],
            "requests_by_method": dict(self.metrics["requests_by_method"]),
            "requests_by_status": dict(self.metrics["requests_by_status"]),
            "errors_total": self.metrics["errors_total"],
            "predictions_total": self.metrics["predictions_total"],
            "response_time_stats": {
                "count": len(response_times),
                "avg": sum(response_times) / len(response_times) if response_times else 0,
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0
            }
        }

# Instance globale des métriques
metrics_middleware = None

def get_metrics() -> Dict[str, Any]:
    """Fonction pour récupérer les métriques"""
    if metrics_middleware:
        return metrics_middleware.get_metrics()
    return {"error": "Métriques non disponibles"} 