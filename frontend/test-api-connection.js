// Test script to verify frontend can connect to backend APIs
const fetch = require('node-fetch');

const BASE_URL = 'http://localhost:8000';

async function testConnection() {
  console.log('🔍 Testing Frontend-Backend Connection...\n');
  
  const endpoints = [
    '/api/v1/dashboard/health',
    '/api/v1/dashboard/overview', 
    '/api/v1/dashboard/stats',
    '/api/v1/dashboard/charts',
    '/api/v1/dashboard/widgets'
  ];
  
  for (const endpoint of endpoints) {
    try {
      console.log(`📡 Testing: ${endpoint}`);
      const response = await fetch(`${BASE_URL}${endpoint}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ ${endpoint} - Status: ${response.status}`);
        
        // Show sample data for overview
        if (endpoint === '/api/v1/dashboard/overview') {
          console.log(`📊 Sample data: ${JSON.stringify({
            stats: Object.keys(data.stats || {}),
            charts: Object.keys(data.charts || {}),
            widgets: Object.keys(data.widgets || {})
          }, null, 2)}`);
        }
      } else {
        console.log(`❌ ${endpoint} - Status: ${response.status}`);
      }
    } catch (error) {
      console.log(`❌ ${endpoint} - Error: ${error.message}`);
    }
    console.log(''); // Empty line for readability
  }
  
  console.log('🎉 Connection test completed!');
  console.log('💡 If all endpoints show ✅, the frontend can consume the APIs');
}

testConnection().catch(console.error);
