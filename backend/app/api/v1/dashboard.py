"""
Dashboard API endpoints for serving live metrics from Azure Monitor
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
import time

from app.services.metrics_service import metrics_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
async def get_dashboard_overview() -> Dict[str, Any]:
    """
    Get dashboard overview data including stats, charts, and metrics
    Fetches live data from Azure Monitor with fallback to static data
    """
    try:
        # Fetch live metrics in parallel
        import asyncio
        groundedness_task = metrics_service.get_groundedness_metrics()
        indexing_task = metrics_service.get_indexing_metrics()
        compliance_task = metrics_service.get_compliance_metrics()
        distribution_task = metrics_service.get_knowledge_distribution()
        volume_task = metrics_service.get_query_volume_metrics()
        token_task = metrics_service.get_token_usage_metrics()
        
        # Wait for all metrics to complete
        groundedness, indexing, compliance, distribution, volume, tokens = await asyncio.gather(
            groundedness_task, indexing_task, compliance_task, distribution_task, volume_task, token_task,
            return_exceptions=True
        )
        
        # Handle exceptions and use fallback data
        groundedness = groundedness if not isinstance(groundedness, Exception) else {
            "percent": 2.6, "total": 4.9, "series": [15, 18, 12, 51, 68, 11, 39, 37]
        }
        indexing = indexing if not isinstance(indexing, Exception) else {
            "percent": 0.2, "total": 2448, "series": [20, 41, 63, 33, 28, 35, 50, 46]
        }
        compliance = compliance if not isinstance(compliance, Exception) else {
            "percent": -100, "total": 0, "series": [18, 19, 31, 8, 16, 37, 12, 33]
        }
        distribution = distribution if not isinstance(distribution, Exception) else [
            {"label": 'Legal Contracts', "value": 2448},
            {"label": 'Clinical SOPs', "value": 1206},
            {"label": 'Technical Docs', "value": 0},
        ]
        volume = volume if not isinstance(volume, Exception) else {
            "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            "series": [
                {"name": 'Grounded', "data": [{"name": 'Grounded', "data": [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16]}]},
                {"name": 'Safety-Filtered', "data": [{"name": 'Safety-Filtered', "data": [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16]}]}
            ]
        }
        tokens = tokens if not isinstance(tokens, Exception) else {
            "total": 55566, "series": 75
        }
        
        dashboard_data = {
            "welcome": {
                "title": "Welcome to Droit AI Workspace ⚖️",
                "description": "Azure-governed intelligence for regulated industries.",
                "actionText": "Explore Knowledge Base",
                "actionHref": 'user/'
            },
            "stats": {
                "groundedness": {
                    "title": "Groundedness Score",
                    "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                    **groundedness
                },
                "indexing": {
                    "title": "Indexed Documents (ADLS)",
                    "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                    **indexing
                },
                "compliance": {
                    "title": "Compliance Violations",
                    "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                    **compliance
                }
            },
            "charts": {
                "distribution": {
                    "title": "Knowledge Source Distribution",
                    "subheader": "",
                    "series": distribution
                },
                "volume": {
                    "title": "Query Volume & Accuracy",
                    "subheader": "(+43%) grounded responses than last year",
                    **volume
                }
            },
            "audit": {
                "title": "Governance Audit Trail",
                "headers": [
                    {"id": 'id', "label": 'Request ID'},
                    {"id": 'category', "label": 'User Group'},
                    {"id": 'price', "label": 'Safety Score'},
                    {"id": 'status', "label": 'Status'},
                    {"id": '', "label": ''}
                ]
            },
            "widgets": {
                "optimization": {
                    "title": "Index Optimization",
                    "total": indexing.get("total", 48),
                    "icon": "solar:user-rounded-bold",
                    "series": indexing.get("total", 48)
                },
                "azureTokens": {
                    "title": "Azure Token Usage",
                    "total": tokens.get("total", 55566),
                    "icon": "fluent:mail-24-filled",
                    "series": tokens.get("series", 75)
                }
            },
            "recent": {
                "title": "Recent Document Ingestions",
                "list": []
            }
        }
        
        logger.info("Dashboard overview data retrieved successfully")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        )


@router.get("/stats")
async def get_dashboard_stats() -> Dict[str, Any]:
    """
    Get dashboard statistics data with live Azure metrics
    """
    try:
        # Fetch live metrics in parallel
        import asyncio
        groundedness_task = metrics_service.get_groundedness_metrics()
        indexing_task = metrics_service.get_indexing_metrics()
        compliance_task = metrics_service.get_compliance_metrics()
        
        # Wait for all metrics to complete
        groundedness, indexing, compliance = await asyncio.gather(
            groundedness_task, indexing_task, compliance_task,
            return_exceptions=True
        )
        
        # Handle exceptions and use fallback data
        groundedness = groundedness if not isinstance(groundedness, Exception) else {
            "percent": 2.6, "total": 4.9, "series": [15, 18, 12, 51, 68, 11, 39, 37]
        }
        indexing = indexing if not isinstance(indexing, Exception) else {
            "percent": 0.2, "total": 2448, "series": [20, 41, 63, 33, 28, 35, 50, 46]
        }
        compliance = compliance if not isinstance(compliance, Exception) else {
            "percent": -100, "total": 0, "series": [18, 19, 31, 8, 16, 37, 12, 33]
        }
        
        stats_data = {
            "groundedness": {
                "title": "Groundedness Score",
                "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                **groundedness
            },
            "indexing": {
                "title": "Indexed Documents (ADLS)",
                "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                **indexing
            },
            "compliance": {
                "title": "Compliance Violations",
                "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                **compliance
            }
        }
        
        logger.info("Dashboard stats retrieved successfully")
        return stats_data
        
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard stats: {str(e)}"
        )


@router.get("/charts")
async def get_dashboard_charts() -> Dict[str, Any]:
    """
    Get dashboard charts data with live Azure metrics
    """
    try:
        # Fetch live metrics in parallel
        import asyncio
        distribution_task = metrics_service.get_knowledge_distribution()
        volume_task = metrics_service.get_query_volume_metrics()
        
        # Wait for all metrics to complete
        distribution, volume = await asyncio.gather(
            distribution_task, volume_task,
            return_exceptions=True
        )
        
        # Handle exceptions and use fallback data
        distribution = distribution if not isinstance(distribution, Exception) else [
            {"label": 'Legal Contracts', "value": 2448},
            {"label": 'Clinical SOPs', "value": 1206},
            {"label": 'Technical Docs', "value": 0},
        ]
        volume = volume if not isinstance(volume, Exception) else {
            "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            "series": [
                {"name": 'Grounded', "data": [{"name": 'Grounded', "data": [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16]}]},
                {"name": 'Safety-Filtered', "data": [{"name": 'Safety-Filtered', "data": [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16]}]}
            ]
        }
        
        charts_data = {
            "distribution": {
                "title": "Knowledge Source Distribution",
                "subheader": "",
                "series": distribution
            },
            "volume": {
                "title": "Query Volume & Accuracy",
                "subheader": "(+43%) grounded responses than last year",
                **volume
            }
        }
        
        logger.info("Dashboard charts retrieved successfully")
        return charts_data
        
    except Exception as e:
        logger.error(f"Failed to get dashboard charts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard charts: {str(e)}"
        )


@router.get("/widgets")
async def get_dashboard_widgets() -> Dict[str, Any]:
    """
    Get dashboard widgets data with live Azure metrics
    """
    try:
        # Fetch live metrics in parallel
        import asyncio
        indexing_task = metrics_service.get_indexing_metrics()
        token_task = metrics_service.get_token_usage_metrics()
        
        # Wait for all metrics to complete
        indexing, tokens = await asyncio.gather(
            indexing_task, token_task,
            return_exceptions=True
        )
        
        # Handle exceptions and use fallback data
        indexing = indexing if not isinstance(indexing, Exception) else {"total": 48}
        tokens = tokens if not isinstance(tokens, Exception) else {"total": 55566, "series": 75}
        
        widgets_data = {
            "optimization": {
                "title": "Index Optimization",
                "total": indexing.get("total", 48),
                "icon": "solar:user-rounded-bold",
                "series": indexing.get("total", 48)
            },
            "azureTokens": {
                "title": "Azure Token Usage",
                "total": tokens.get("total", 55566),
                "icon": "fluent:mail-24-filled",
                "series": tokens.get("series", 75)
            }
        }
        
        logger.info("Dashboard widgets retrieved successfully")
        return widgets_data
        
    except Exception as e:
        logger.error(f"Failed to get dashboard widgets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard widgets: {str(e)}"
        )


@router.get("/health")
async def dashboard_health() -> Dict[str, Any]:
    """Dashboard service health check"""
    return {
        "status": "healthy",
        "service": "Dashboard API",
        "timestamp": time.time(),
        "endpoints": {
            "overview": "/dashboard/overview",
            "stats": "/dashboard/stats",
            "charts": "/dashboard/charts",
            "widgets": "/dashboard/widgets"
        }
    }
