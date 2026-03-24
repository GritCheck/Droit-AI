// Simple test to verify API integration
// This can be run in browser console or as a temporary component

import { fetcher , endpoints } from 'src/lib/axios';

export async function testDashboardAPI() {
  console.log('🚀 Testing Dashboard API Integration');
  console.log('=====================================');
  
  try {
    // Test backend health
    console.log('\n1. Testing backend health...');
    const healthResponse = await fetcher('/health');
    console.log('✅ Backend health:', healthResponse);
    
    // Test dashboard health
    console.log('\n2. Testing dashboard health...');
    const dashboardHealth = await fetcher(endpoints.dashboard.health);
    console.log('✅ Dashboard health:', dashboardHealth);
    
    // Test dashboard overview
    console.log('\n3. Testing dashboard overview...');
    const overview = await fetcher(endpoints.dashboard.overview);
    console.log('✅ Dashboard overview keys:', Object.keys(overview));
    
    // Validate data structure
    const requiredKeys = ['welcome', 'stats', 'charts', 'audit', 'widgets', 'recent'];
    const missingKeys = requiredKeys.filter(key => !(key in overview));
    
    if (missingKeys.length === 0) {
      console.log('✅ All required keys present in overview data');
    } else {
      console.log('⚠️ Missing keys:', missingKeys);
    }
    
    // Test individual endpoints
    console.log('\n4. Testing individual endpoints...');
    
    const stats = await fetcher(endpoints.dashboard.stats);
    console.log('✅ Stats keys:', Object.keys(stats));
    
    const charts = await fetcher(endpoints.dashboard.charts);
    console.log('✅ Charts keys:', Object.keys(charts));
    
    const widgets = await fetcher(endpoints.dashboard.widgets);
    console.log('✅ Widgets keys:', Object.keys(widgets));
    
    console.log('\n=====================================');
    console.log('✅ All API tests completed successfully!');
    
    return { success: true, data: { overview, stats, charts, widgets } };
    
  } catch (error) {
    console.error('❌ API test failed:', error);
    console.error('Error details:', error.message);
    console.error('Make sure the backend server is running on http://localhost:8000');
    
    return { success: false, error: error.message };
  }
}

// Export for use in components or console testing
export default testDashboardAPI;
