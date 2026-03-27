from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
import logging

from app.core.auth import get_current_user
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

@router.get("/overview")
async def get_metrics_overview(
    current_user: dict = Depends(get_current_user),
    hours: int = Query(default=24, description="Hours of data to analyze")
):
    """
    Get comprehensive metrics overview for DroitAI dashboard
    Returns business and operational metrics for the specified time period
    """
    try:
        # This would typically query Application Insights
        # For now, return mock data structure that matches expected format
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        return {
            "time_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "business_metrics": {
                "groundedness_score": 0.87,  # Percentage of answers supported by contract text
                "citation_accuracy": {
                    "total_citations": 1245,
                    "valid_citations": 1089,
                    "invalid_citations": 156,
                    "accuracy_percentage": 87.5
                },
                "compliance_breakdown": {
                    "compliant": 892,
                    "partial": 234,
                    "non_compliant": 89,
                    "total_analyzed": 1215
                }
            },
            "operational_metrics": {
                "token_consumption": {
                    "total_tokens": 45678,
                    "average_per_query": 127,
                    "cost_estimate_usd": 1.37
                },
                "performance": {
                    "average_search_latency_ms": 145,
                    "average_llm_latency_ms": 2340,
                    "overall_average_latency_ms": 2485,
                    "requests_per_hour": 36
                },
                "reliability": {
                    "total_requests": 864,
                    "successful_requests": 821,
                    "failed_requests": 43,
                    "success_rate_percentage": 95.0
                }
            },
            "trends": {
                "hourly_requests": [
                    {"hour": i, "count": 30 + (i % 12) * 5} 
                    for i in range(hours)
                ],
                "daily_tokens": [
                    {"day": "Mon", "tokens": 12000},
                    {"day": "Tue", "tokens": 14500},
                    {"day": "Wed", "tokens": 13200},
                    {"day": "Thu", "tokens": 15800},
                    {"day": "Fri", "tokens": 11200},
                    {"day": "Sat", "tokens": 8900},
                    {"day": "Sun", "tokens": 7800}
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Metrics Error: {str(e)}")

@router.get("/kql-queries")
async def get_kql_queries():
    """
    Get KQL queries for Azure Application Insights dashboard
    These queries can be used directly in Azure Portal to create custom dashboards
    """
    return {
        "queries": {
            "performance_overview": """
traces
| where name == "LegalQueryProcessed"
| extend tokens = toint(customDimensions.tokens_used)
| extend latency = todouble(customDimensions.latency_ms)
| summarize AvgTokens=avg(tokens), AvgLatency=avg(latency), RequestCount=count() by bin(timestamp, 1h)
| render timechart
            """.strip(),
            
            "groundedness_analysis": """
traces
| where name == "LegalQueryProcessed"
| extend groundedness = todouble(customDimensions.groundedness_score)
| summarize AvgGroundedness=avg(groundedness), MaxGroundedness=max(groundedness), MinGroundedness=min(groundedness) by bin(timestamp, 1h)
| render timechart
            """.strip(),
            
            "citation_accuracy": """
traces
| where name == "LegalQueryProcessed"
| extend accuracy = (toint(customDimensions.citation_accuracy_valid) * 100.0) / toint(customDimensions.citation_accuracy_total)
| summarize AvgAccuracy=avg(accuracy), RequestCount=count() by bin(timestamp, 1h)
| render timechart
            """.strip(),
            
            "error_analysis": """
traces
| where name == "LegalQueryFailed"
| extend error_type = customDimensions.error_type
| summarize ErrorCount=count() by error_type, bin(timestamp, 1h)
| render barchart
            """.strip(),
            
            "token_consumption": """
traces
| where name == "LegalQueryProcessed"
| extend tokens = toint(customDimensions.tokens_used)
| summarize TotalTokens=sum(tokens), AvgTokens=avg(tokens), RequestCount=count() by bin(timestamp, 1d)
| render timechart
            """.strip()
        },
        "dashboard_instructions": {
            "setup": [
                "1. Go to Azure Portal > Application Insights",
                "2. Select 'Logs (Analytics)'",
                "3. Copy and paste any query above",
                "4. Click 'Run' to visualize data",
                "5. Click 'Pin to Dashboard' to save visualization"
            ],
            "recommended_charts": [
                "Performance Overview (query 1)",
                "Groundedness Score Trend (query 2)", 
                "Citation Accuracy Over Time (query 3)",
                "Error Breakdown (query 4)",
                "Token Consumption (query 5)"
            ]
        }
    }
