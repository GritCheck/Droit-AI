from fastapi import APIRouter, HTTPException
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
from app.core.config import get_settings
from datetime import timedelta
import logging

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

# Azure Monitor Query Client
client = LogsQueryClient(DefaultAzureCredential())

@router.get("/management-overview")
async def get_management_metrics():
    """
    Aggregates legal audit metrics for Management Dashboard.
    Returns high-level business metrics for Microsoft AI Innovation Challenge.
    """
    try:
        # Use the Workspace ID linked to your App Insights
        workspace_id = settings.azure_log_analytics_workspace_id
        
        if not workspace_id:
            # Return mock data if workspace not configured
            return {
                "summary": {
                    "total_contracts_audited": 1247,
                    "avg_cost_per_audit_tokens": 156,
                    "groundedness_rate": 87.3,
                    "audit_success_rate": 94.2
                },
                "risk_alerts": {
                    "high_risk_clauses_detected": 23,
                    "compliance_issues": 8,
                    "critical_findings": 3
                },
                "performance_metrics": {
                    "avg_response_time_ms": 2340,
                    "cost_efficiency_score": 91.5,
                    "token_utilization_rate": 78.2
                },
                "trend_analysis": {
                    "daily_audits": [
                        {"date": "2024-03-20", "count": 145},
                        {"date": "2024-03-21", "count": 167},
                        {"date": "2024-03-22", "count": 189},
                        {"date": "2024-03-23", "count": 201},
                        {"date": "2024-03-24", "count": 178},
                        {"date": "2024-03-25", "count": 156},
                        {"date": "2024-03-26", "count": 211}
                    ],
                    "groundedness_trend": [
                        {"date": "2024-03-20", "score": 85.2},
                        {"date": "2024-03-21", "score": 87.1},
                        {"date": "2024-03-22", "score": 86.8},
                        {"date": "2024-03-23", "score": 88.9},
                        {"date": "2024-03-24", "score": 87.6},
                        {"date": "2024-03-25", "score": 89.1},
                        {"date": "2024-03-26", "score": 87.3}
                    ]
                },
                "compliance_breakdown": {
                    "fully_compliant": 1123,
                    "partially_compliant": 89,
                    "non_compliant": 35,
                    "total_reviewed": 1247,
                    "compliance_rate": 90.1
                },
                "data_source": "mock_data",
                "last_updated": "2024-03-26T23:59:59Z"
            }
        
        # 1. KQL Query: Legal Audit Outcomes & Groundedness
        query = """
        traces
        | where name == "LegalQueryProcessed"
        | extend d = customDimensions
        | summarize 
            TotalAudits = count(),
            AvgTokens = avg(toint(d.tokens_used)),
            GroundedSuccess = countif(d.has_citations == "True"),
            NonCompliantCount = countif(d.compliance_status == "NON_COMPLIANT"),
            AvgLatency = avg(todouble(d.latency_ms))
        by bin(timestamp, 1d)
        | order by bin(timestamp, 1d) desc
        | take 7
        """

        response = client.query_workspace(
            workspace_id=workspace_id,
            query=query,
            timespan=timedelta(days=7)
        )

        # Process results into a clean JSON for React
        if response.status == LogsQueryStatus.SUCCESS and response.tables:
            rows = response.tables[0].rows
            if rows:
                # Get the most recent day's data for summary
                latest_row = rows[0]
                
                return {
                    "summary": {
                        "total_contracts_audited": latest_row.get("TotalAudits", 0),
                        "avg_cost_per_audit_tokens": int(latest_row.get("AvgTokens", 0)),
                        "groundedness_rate": (latest_row.get("GroundedSuccess", 0) / latest_row.get("TotalAudits", 1)) * 100 if latest_row.get("TotalAudits", 0) > 0 else 0,
                        "audit_success_rate": ((latest_row.get("TotalAudits", 0) - latest_row.get("NonCompliantCount", 0)) / latest_row.get("TotalAudits", 1)) * 100 if latest_row.get("TotalAudits", 0) > 0 else 0,
                        "avg_response_time_ms": latest_row.get("AvgLatency", 0)
                    },
                    "risk_alerts": {
                        "high_risk_clauses_detected": latest_row.get("NonCompliantCount", 0),
                        "compliance_issues": latest_row.get("NonCompliantCount", 0),
                        "critical_findings": max(0, latest_row.get("NonCompliantCount", 0) // 3)
                    },
                    "performance_metrics": {
                        "avg_response_time_ms": latest_row.get("AvgLatency", 0),
                        "cost_efficiency_score": min(100, 1000 / max(1, latest_row.get("AvgTokens", 1))),
                        "token_utilization_rate": min(100, (latest_row.get("AvgTokens", 0) / 2000) * 100)  # Assuming 2000 token limit
                    },
                    "trend_analysis": {
                        "daily_audits": [
                            {
                                "date": row["bin"].split("T")[0],  # Extract date part
                                "count": row["TotalAudits"]
                            }
                            for row in rows
                        ],
                        "groundedness_trend": [
                            {
                                "date": row["bin"].split("T")[0],
                                "score": (row.get("GroundedSuccess", 0) / row.get("TotalAudits", 1)) * 100 if row.get("TotalAudits", 0) > 0 else 0
                            }
                            for row in rows
                        ]
                    },
                    "compliance_breakdown": {
                        "fully_compliant": latest_row.get("TotalAudits", 0) - latest_row.get("NonCompliantCount", 0),
                        "partially_compliant": 0,  # Would need additional tracking
                        "non_compliant": latest_row.get("NonCompliantCount", 0),
                        "total_reviewed": latest_row.get("TotalAudits", 0),
                        "compliance_rate": ((latest_row.get("TotalAudits", 0) - latest_row.get("NonCompliantCount", 0)) / latest_row.get("TotalAudits", 1)) * 100 if latest_row.get("TotalAudits", 0) > 0 else 0
                    },
                    "data_source": "azure_monitor",
                    "last_updated": rows[0]["bin"] if rows else None
                }
        
        return {"error": "Failed to fetch management metrics", "details": str(response.status)}
        
    except Exception as e:
        logger.error(f"Failed to get management metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard Error: {str(e)}")

@router.get("/kusto-queries")
async def get_kusto_queries():
    """
    Get KQL queries for Azure Monitor dashboard creation.
    These queries are optimized for legal audit metrics.
    """
    return {
        "management_dashboard_queries": {
            "audit_overview": """
traces
| where name == "LegalQueryProcessed"
| extend d = customDimensions
| summarize 
    TotalAudits = count(),
    AvgTokens = avg(toint(d.tokens_used)),
    GroundedSuccess = countif(d.has_citations == "True"),
    NonCompliantCount = countif(d.compliance_status == "NON_COMPLIANT"),
    AvgLatency = avg(todouble(d.latency_ms))
by bin(timestamp, 1d)
| order by bin(timestamp, 1d) desc
| render timechart
            """.strip(),
            
            "groundedness_trend": """
traces
| where name == "LegalQueryProcessed"
| extend d = customDimensions
| extend groundedness_rate = (countif(d.has_citations == "True") * 100.0) / count()
| summarize AvgGroundedness = avg(groundedness_rate), MaxGroundedness = max(groundedness_rate), MinGroundedness = min(groundedness_rate)
by bin(timestamp, 1h)
| render timechart
            """.strip(),
            
            "compliance_analysis": """
traces
| where name == "LegalQueryProcessed"
| extend d = customDimensions
| extend compliance_rate = ((count() - countif(d.compliance_status == "NON_COMPLIANT")) * 100.0) / count()
| summarize AvgCompliance = avg(compliance_rate), TotalAudits = count(), NonCompliant = countif(d.compliance_status == "NON_COMPLIANT")
by bin(timestamp, 1d)
| render barchart
            """.strip(),
            
            "cost_analysis": """
traces
| where name == "LegalQueryProcessed"
| extend d = customDimensions
| extend cost_estimate = toint(d.tokens_used) * 0.00002  // $0.02 per 1K tokens
| summarize TotalCost = sum(cost_estimate), TotalTokens = sum(toint(d.tokens_used)), AvgCost = avg(cost_estimate)
by bin(timestamp, 1d)
| render timechart
            """.strip(),
            
            "performance_metrics": """
traces
| where name == "LegalQueryProcessed"
| extend d = customDimensions
| summarize 
    P95_Latency = percentile(todouble(d.latency_ms), 95),
    Avg_Latency = avg(todouble(d.latency_ms)),
    Request_Count = count()
by bin(timestamp, 1h)
| render timechart
            """.strip()
        },
        "dashboard_setup": {
            "instructions": [
                "1. Go to Azure Portal > Log Analytics Workspaces",
                "2. Select your workspace and open 'Logs'",
                "3. Copy any query above and paste it",
                "4. Click 'Run' to visualize the data",
                "5. Use 'Pin to dashboard' to create persistent views"
            ],
            "recommended_visualizations": [
                {
                    "name": "Legal Audit Volume",
                    "query": "audit_overview",
                    "chart_type": "timechart",
                    "business_value": "Shows system utilization and audit throughput"
                },
                {
                    "name": "Groundedness Score Trend",
                    "query": "groundedness_trend", 
                    "chart_type": "timechart",
                    "business_value": "Demonstrates RAG accuracy and reliability"
                },
                {
                    "name": "Compliance Analysis",
                    "query": "compliance_analysis",
                    "chart_type": "barchart", 
                    "business_value": "Tracks legal compliance detection rates"
                },
                {
                    "name": "Cost Efficiency",
                    "query": "cost_analysis",
                    "chart_type": "timechart",
                    "business_value": "Monitors operational costs and ROI"
                },
                {
                    "name": "Performance Metrics",
                    "query": "performance_metrics",
                    "chart_type": "timechart",
                    "business_value": "Tracks system responsiveness and reliability"
                }
            ]
        }
    }
