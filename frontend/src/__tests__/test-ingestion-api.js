// Test script for ingestion API integration
// This can be run in browser console or as a temporary component

import { fetcher, endpoints } from 'src/lib/axios';

export async function testIngestionAPI() {
  console.log('🚀 Testing Ingestion API Integration');
  console.log('=====================================');
  
  try {
    // Test backend health
    console.log('\n1. Testing backend health...');
    const healthResponse = await fetcher('/health');
    console.log('✅ Backend health:', healthResponse);
    
    // Test ingestion health
    console.log('\n2. Testing ingestion health...');
    const ingestionHealth = await fetcher(endpoints.ingestion.health);
    console.log('✅ Ingestion health:', ingestionHealth);
    
    // Test ingestion overview
    console.log('\n3. Testing ingestion overview...');
    const overview = await fetcher(endpoints.ingestion.overview);
    console.log('✅ Ingestion overview keys:', Object.keys(overview));
    
    // Validate data structure
    const requiredKeys = ['summary', 'storage', 'activity', 'folders', 'recentFiles'];
    const missingKeys = requiredKeys.filter(key => !(key in overview));
    
    if (missingKeys.length === 0) {
      console.log('✅ All required keys present in ingestion data');
    } else {
      console.log('⚠️ Missing keys:', missingKeys);
    }
    
    // Test individual endpoints
    console.log('\n4. Testing individual endpoints...');
    
    const summary = await fetcher(endpoints.ingestion.summary);
    console.log('✅ Summary keys:', Object.keys(summary));
    
    const storage = await fetcher(endpoints.ingestion.storage);
    console.log('✅ Storage keys:', Object.keys(storage));
    
    const activity = await fetcher(endpoints.ingestion.activity);
    console.log('✅ Activity keys:', Object.keys(activity));
    
    // Validate summary structure
    const summaryKeys = ['adls', 'docling', 'aiSearch'];
    const missingSummaryKeys = summaryKeys.filter(key => !(key in summary));
    
    if (missingSummaryKeys.length === 0) {
      console.log('✅ All summary keys present');
    } else {
      console.log('⚠️ Missing summary keys:', missingSummaryKeys);
    }
    
    // Validate storage structure
    const storageKeys = ['totalGB', 'usedPercent', 'categories'];
    const missingStorageKeys = storageKeys.filter(key => !(key in storage));
    
    if (missingStorageKeys.length === 0) {
      console.log('✅ All storage keys present');
      console.log('   Storage categories count:', storage.categories.length);
    } else {
      console.log('⚠️ Missing storage keys:', missingStorageKeys);
    }
    
    // Validate activity structure
    const activityKeys = ['chartSeries'];
    const missingActivityKeys = activityKeys.filter(key => !(key in activity));
    
    if (missingActivityKeys.length === 0) {
      console.log('✅ All activity keys present');
      console.log('   Chart series count:', activity.chartSeries.length);
    } else {
      console.log('⚠️ Missing activity keys:', missingActivityKeys);
    }
    
    console.log('\n=====================================');
    console.log('✅ All ingestion API tests completed successfully!');
    
    return { 
      success: true, 
      data: { 
        overview, 
        summary, 
        storage, 
        activity 
      } 
    };
    
  } catch (error) {
    console.error('❌ Ingestion API test failed:', error);
    console.error('Error details:', error.message);
    console.error('Make sure the backend server is running on http://localhost:8000');
    
    return { success: false, error: error.message };
  }
}

// Export for use in components or console testing
export default testIngestionAPI;
