"""
Test script for dashboard API endpoints
"""

import asyncio
import aiohttp

async def test_dashboard_endpoints():
    """Test all dashboard API endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/health",
        "/api/v1/dashboard/health",
        "/api/v1/dashboard/overview",
        "/api/v1/dashboard/stats",
        "/api/v1/dashboard/charts",
        "/api/v1/dashboard/widgets"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            print(f"\nTesting {endpoint}...")
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {endpoint} - Status: {response.status}")
                        print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                        
                        # Validate overview endpoint structure
                        if endpoint == "/api/v1/dashboard/overview":
                            required_keys = ["welcome", "stats", "charts", "audit", "widgets", "recent"]
                            missing_keys = [key for key in required_keys if key not in data]
                            if missing_keys:
                                print(f"   ⚠️  Missing keys: {missing_keys}")
                            else:
                                print(f"   ✅ All required keys present")
                    else:
                        print(f"❌ {endpoint} - Status: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        
            except aiohttp.ClientError as e:
                print(f"❌ {endpoint} - Connection error: {e}")
            except Exception as e:
                print(f"❌ {endpoint} - Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Dashboard API Endpoints")
    print("=" * 50)
    
    try:
        asyncio.run(test_dashboard_endpoints())
        print("\n" + "=" * 50)
        print("✅ API testing completed")
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
