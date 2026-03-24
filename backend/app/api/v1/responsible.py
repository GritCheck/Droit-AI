"""
Responsible AI API endpoints for serving governance and safety metrics
"""

import logging
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/responsible", tags=["responsible"])


@router.get("/overview")
async def get_responsible_overview() -> Dict[str, Any]:
    """
    Get responsible AI overview data including governance metrics and safety data
    """
    try:
        responsible_data = {
            "summary": {
                "totalAssertions": 12450,
                "safetyFiltered": 9876,
                "highConfidenceCitations": 8234
            },
            "groundedness": {
                "title": "Query Groundedness Score",
                "total": 89.2,
                "percent": 2.6,
                "chart": {
                    "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                    "series": [{"data": [85, 87, 88, 89, 88, 90, 89, 91, 89.2]}]
                }
            },
            "reliability": {
                "title": "Response Reliability",
                "data": [
                    {"value": 85, "status": 'Fully Grounded', "quantity": 10582},
                    {"value": 12, "status": 'Partially Cited', "quantity": 1494},
                    {"value": 3, "status": 'Requires Review', "quantity": 374}
                ]
            },
            "safetyChecks": {
                "chart": {
                    "series": [
                        {"label": 'PII Redaction Success', "percent": 94.2, "total": 11732},
                        {"label": 'Jailbreak Attempts Blocked', "percent": 87.8, "total": 10932}
                    ]
                }
            },
            "performance": {
                "title": "Model Performance Telemetry",
                "chart": {
                    "series": [
                        {
                            "name": 'Weekly',
                            "categories": ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
                            "data": [
                                {"name": 'Coherence Score', "data": [92, 91, 93, 94, 93]},
                                {"name": 'Relevance Score', "data": [88, 89, 87, 90, 91]}
                            ]
                        },
                        {
                            "name": 'Monthly',
                            "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                            "data": [
                                {"name": 'Coherence Score', "data": [90, 91, 92, 91, 93, 92, 94, 93, 92]},
                                {"name": 'Relevance Score', "data": [87, 88, 86, 89, 88, 90, 89, 91, 90]}
                            ]
                        },
                        {
                            "name": 'Yearly',
                            "categories": ['2018', '2019', '2020', '2021', '2022', '2023'],
                            "data": [
                                {"name": 'Coherence Score', "data": [85, 87, 89, 91, 92, 93]},
                                {"name": 'Relevance Score', "data": [82, 84, 86, 88, 89, 90]}
                            ]
                        }
                    ]
                }
            },
            "moderation": {
                "title": "Content Moderation Distribution",
                "chart": {
                    "series": [
                        {"label": 'Hate/Bias Blocked', "value": 247},
                        {"label": 'Safe to Deploy', "value": 12203}
                    ]
                }
            },
            "feedback": {
                "title": "System Feedback Audit",
                "subheader": "Internal Expert Review Tags",
                "list": [
                    {
                        "id": "1",
                        "name": "Dr. Sarah Chen",
                        "rating": 5,
                        "tags": ["Legal Compliance", "Expert Review"],
                        "avatarUrl": "/assets/images/avatars/avatar-1.jpg",
                        "description": "Model response shows excellent grounding in legal precedents",
                        "postedAt": "2024-01-15T10:30:00Z"
                    },
                    {
                        "id": "2",
                        "name": "Prof. Michael Roberts",
                        "rating": 4,
                        "tags": ["Privacy Protection", "PII Handling"],
                        "avatarUrl": "/assets/images/avatars/avatar-2.jpg",
                        "description": "PII redaction working effectively across all test cases",
                        "postedAt": "2024-01-14T15:45:00Z"
                    },
                    {
                        "id": "3",
                        "name": "Dr. Emily Johnson",
                        "rating": 3,
                        "tags": ["Security Review", "Jailbreak Detection"],
                        "avatarUrl": "/assets/images/avatars/avatar-3.jpg",
                        "description": "Jailbreak detection needs improvement for edge cases",
                        "postedAt": "2024-01-13T09:20:00Z"
                    }
                ]
            },
            "interventions": {
                "title": "Recent Flagged Interventions",
                "list": [
                    {
                        "id": "1",
                        "name": "Medical Advice Query",
                        "price": 0,
                        "guests": "Healthcare Staff",
                        "isHot": True,
                        "duration": "15 minutes",
                        "coverUrl": "/assets/images/covers/medical-cover.jpg",
                        "avatarUrl": "/assets/images/avatars/avatar-4.jpg",
                        "bookedAt": "2024-01-15T14:30:00Z"
                    },
                    {
                        "id": "2",
                        "name": "Legal Interpretation Request",
                        "price": 0,
                        "guests": "Legal Team",
                        "isHot": False,
                        "duration": "20 minutes",
                        "coverUrl": "/assets/images/covers/legal-cover.jpg",
                        "avatarUrl": "/assets/images/avatars/avatar-5.jpg",
                        "bookedAt": "2024-01-15T12:15:00Z"
                    },
                    {
                        "id": "3",
                        "name": "Financial Guidance Query",
                        "price": 0,
                        "guests": "Finance Team",
                        "isHot": False,
                        "duration": "10 minutes",
                        "coverUrl": "/assets/images/covers/finance-cover.jpg",
                        "avatarUrl": "/assets/images/avatars/avatar-6.jpg",
                        "bookedAt": "2024-01-15T10:45:00Z"
                    }
                ]
            },
            "audit": {
                "title": "Governance Audit Trail",
                "headers": [
                    {"id": 'destination', "label": 'Query Intent'},
                    {"id": 'customer', "label": 'User Group'},
                    {"id": 'checkIn', "label": 'Safety Score'},
                    {"id": 'checkOut', "label": 'Audit Timestamp'},
                    {"id": 'status', "label": 'Action Taken'},
                    {"id": '', "label": ''}
                ],
                "tableData": [
                    {
                        "id": "1",
                        "status": "approved",
                        "checkIn": "2024-01-15T10:30:00Z",
                        "checkOut": "2024-01-15T10:35:00Z",
                        "destination": {
                            "name": "Legal Research",
                            "coverUrl": "/assets/images/destinations/legal.jpg"
                        },
                        "customer": {
                            "name": "Legal Team",
                            "avatarUrl": "/assets/images/avatars/legal-team.jpg",
                            "phoneNumber": "+1-555-0123"
                        }
                    },
                    {
                        "id": "2",
                        "status": "flagged",
                        "checkIn": "2024-01-15T09:15:00Z",
                        "checkOut": "2024-01-15T09:20:00Z",
                        "destination": {
                            "name": "Medical Information",
                            "coverUrl": "/assets/images/destinations/medical.jpg"
                        },
                        "customer": {
                            "name": "Healthcare Staff",
                            "avatarUrl": "/assets/images/avatars/healthcare.jpg",
                            "phoneNumber": "+1-555-0124"
                        }
                    },
                    {
                        "id": "3",
                        "status": "reviewed",
                        "checkIn": "2024-01-15T08:45:00Z",
                        "checkOut": "2024-01-15T08:50:00Z",
                        "destination": {
                            "name": "Financial Analysis",
                            "coverUrl": "/assets/images/destinations/finance.jpg"
                        },
                        "customer": {
                            "name": "Finance Team",
                            "avatarUrl": "/assets/images/avatars/finance.jpg",
                            "phoneNumber": "+1-555-0125"
                        }
                    },
                    {
                        "id": "4",
                        "status": "approved",
                        "checkIn": "2024-01-15T07:30:00Z",
                        "checkOut": "2024-01-15T07:35:00Z",
                        "destination": {
                            "name": "Technical Support",
                            "coverUrl": "/assets/images/destinations/tech.jpg"
                        },
                        "customer": {
                            "name": "IT Department",
                            "avatarUrl": "/assets/images/avatars/it.jpg",
                            "phoneNumber": "+1-555-0126"
                        }
                    },
                    {
                        "id": "5",
                        "status": "approved",
                        "checkIn": "2024-01-15T06:15:00Z",
                        "checkOut": "2024-01-15T06:20:00Z",
                        "destination": {
                            "name": "HR Policy Query",
                            "coverUrl": "/assets/images/destinations/hr.jpg"
                        },
                        "customer": {
                            "name": "Human Resources",
                            "avatarUrl": "/assets/images/avatars/hr.jpg",
                            "phoneNumber": "+1-555-0127"
                        }
                    }
                ]
            }
        }
        
        logger.info("Responsible AI overview data retrieved successfully")
        return responsible_data
        
    except Exception as e:
        logger.error(f"Failed to get responsible AI overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve responsible AI data: {str(e)}"
        )


@router.get("/summary")
async def get_responsible_summary() -> Dict[str, Any]:
    """
    Get responsible AI summary metrics
    """
    try:
        summary_data = {
            "totalAssertions": 12450,
            "safetyFiltered": 9876,
            "highConfidenceCitations": 8234
        }
        
        logger.info("Responsible AI summary retrieved successfully")
        return summary_data
        
    except Exception as e:
        logger.error(f"Failed to get responsible AI summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve responsible AI summary: {str(e)}"
        )


@router.get("/performance")
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Get model performance telemetry data
    """
    try:
        performance_data = {
            "title": "Model Performance Telemetry",
            "chart": {
                "series": [
                    {
                        "name": 'Weekly',
                        "categories": ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
                        "data": [
                            {"name": 'Coherence Score', "data": [92, 91, 93, 94, 93]},
                            {"name": 'Relevance Score', "data": [88, 89, 87, 90, 91]}
                        ]
                    },
                    {
                        "name": 'Monthly',
                        "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                        "data": [
                            {"name": 'Coherence Score', "data": [90, 91, 92, 91, 93, 92, 94, 93, 92]},
                            {"name": 'Relevance Score', "data": [87, 88, 86, 89, 88, 90, 89, 91, 90]}
                        ]
                    },
                    {
                        "name": 'Yearly',
                        "categories": ['2018', '2019', '2020', '2021', '2022', '2023'],
                        "data": [
                            {"name": 'Coherence Score', "data": [85, 87, 89, 91, 92, 93]},
                            {"name": 'Relevance Score', "data": [82, 84, 86, 88, 89, 90]}
                        ]
                    }
                ]
            }
        }
        
        logger.info("Performance metrics retrieved successfully")
        return performance_data
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance metrics: {str(e)}"
        )


@router.get("/safety")
async def get_safety_metrics() -> Dict[str, Any]:
    """
    Get safety and moderation metrics
    """
    try:
        safety_data = {
            "groundedness": {
                "title": "Query Groundedness Score",
                "total": 89.2,
                "percent": 2.6,
                "chart": {
                    "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                    "series": [{"data": [85, 87, 88, 89, 88, 90, 89, 91, 89.2]}]
                }
            },
            "reliability": {
                "title": "Response Reliability",
                "data": [
                    {"value": 85, "status": 'Fully Grounded', "quantity": 10582},
                    {"value": 12, "status": 'Partially Cited', "quantity": 1494},
                    {"value": 3, "status": 'Requires Review', "quantity": 374}
                ]
            },
            "safetyChecks": {
                "chart": {
                    "series": [
                        {"label": 'PII Redaction Success', "percent": 94.2, "total": 11732},
                        {"label": 'Jailbreak Attempts Blocked', "percent": 87.8, "total": 10932}
                    ]
                }
            },
            "moderation": {
                "title": "Content Moderation Distribution",
                "chart": {
                    "series": [
                        {"label": 'Hate/Bias Blocked', "value": 247},
                        {"label": 'Safe to Deploy', "value": 12203}
                    ]
                }
            }
        }
        
        logger.info("Safety metrics retrieved successfully")
        return safety_data
        
    except Exception as e:
        logger.error(f"Failed to get safety metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve safety metrics: {str(e)}"
        )


@router.get("/health")
async def responsible_health() -> Dict[str, Any]:
    """Responsible AI service health check"""
    return {
        "status": "healthy",
        "service": "Responsible AI API",
        "timestamp": time.time(),
        "endpoints": {
            "overview": "/responsible/overview",
            "summary": "/responsible/summary",
            "performance": "/responsible/performance",
            "safety": "/responsible/safety"
        }
    }
