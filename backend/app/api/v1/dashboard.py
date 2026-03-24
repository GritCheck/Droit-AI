"""
Dashboard API endpoints for serving static data and metrics
"""

import logging
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
async def get_dashboard_overview() -> Dict[str, Any]:
    """
    Get dashboard overview data including stats, charts, and metrics
    """
    try:
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
                    "percent": 2.6,
                    "total": 4.9,
                    "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                    "series": [15, 18, 12, 51, 68, 11, 39, 37]
                },
                "indexing": {
                    "title": "Indexed Documents (ADLS)",
                    "percent": 0.2,
                    "total": 2448,
                    "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                    "series": [20, 41, 63, 33, 28, 35, 50, 46]
                },
                "compliance": {
                    "title": "Compliance Violations",
                    "percent": -100,
                    "total": 0,
                    "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                    "series": [18, 19, 31, 8, 16, 37, 12, 33]
                }
            },
            "charts": {
                "distribution": {
                    "title": "Knowledge Source Distribution",
                    "subheader": "",
                    "series": [
                        {"label": 'Legal Contracts', "value": 2448},
                        {"label": 'Clinical SOPs', "value": 1206},
                        {"label": 'Technical Docs', "value": 0},
                    ]
                },
                "volume": {
                    "title": "Query Volume & Accuracy",
                    "subheader": "(+43%) grounded responses than last year",
                    "categories": [
                        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                    ],
                    "series": [
                        {
                            "name": 'Grounded',
                            "data": [{"name": 'Grounded', "data": [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16]}]
                        },
                        {
                            "name": 'Safety-Filtered',
                            "data": [{"name": 'Safety-Filtered', "data": [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16]}]
                        }
                    ]
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
                    "total": 48,
                    "icon": "solar:user-rounded-bold",
                    "series": 48
                },
                "azureTokens": {
                    "title": "Azure Token Usage",
                    "total": 55566,
                    "icon": "fluent:mail-24-filled",
                    "series": 75
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
    Get dashboard statistics data
    """
    try:
        stats_data = {
            "groundedness": {
                "title": "Groundedness Score",
                "percent": 2.6,
                "total": 4.9,
                "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                "series": [15, 18, 12, 51, 68, 11, 39, 37]
            },
            "indexing": {
                "title": "Indexed Documents (ADLS)",
                "percent": 0.2,
                "total": 2448,
                "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                "series": [20, 41, 63, 33, 28, 35, 50, 46]
            },
            "compliance": {
                "title": "Compliance Violations",
                "percent": -100,
                "total": 0,
                "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                "series": [18, 19, 31, 8, 16, 37, 12, 33]
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
    Get dashboard charts data
    """
    try:
        charts_data = {
            "distribution": {
                "title": "Knowledge Source Distribution",
                "subheader": "",
                "series": [
                    {"label": 'Legal Contracts', "value": 2448},
                    {"label": 'Clinical SOPs', "value": 1206},
                    {"label": 'Technical Docs', "value": 0},
                ]
            },
            "volume": {
                "title": "Query Volume & Accuracy",
                "subheader": "(+43%) grounded responses than last year",
                "categories": [
                    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                ],
                "series": [
                    {
                        "name": 'Grounded',
                        "data": [{"name": 'Grounded', "data": [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16]}]
                    },
                    {
                        "name": 'Safety-Filtered',
                        "data": [{"name": 'Safety-Filtered', "data": [12, 10, 18, 22, 20, 12, 8, 21, 20, 14, 15, 16]}]
                    }
                ]
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
    Get dashboard widgets data
    """
    try:
        widgets_data = {
            "optimization": {
                "title": "Index Optimization",
                "total": 48,
                "icon": "solar:user-rounded-bold",
                "series": 48
            },
            "azureTokens": {
                "title": "Azure Token Usage",
                "total": 55566,
                "icon": "fluent:mail-24-filled",
                "series": 75
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
