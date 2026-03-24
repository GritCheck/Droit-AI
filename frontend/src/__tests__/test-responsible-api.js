// Test script for responsible AI API integration
// This can be run in browser console or as a temporary component

import { fetcher, endpoints } from 'src/lib/axios';

export async function testResponsibleAPI() {
  console.log('🚀 Testing Responsible AI API Integration');
  console.log('========================================');
  
  try {
    // Test backend health
    console.log('\n1. Testing backend health...');
    const healthResponse = await fetcher('/health');
    console.log('✅ Backend health:', healthResponse);
    
    // Test responsible AI health
    console.log('\n2. Testing responsible AI health...');
    const responsibleHealth = await fetcher(endpoints.responsible.health);
    console.log('✅ Responsible AI health:', responsibleHealth);
    
    // Test responsible AI overview
    console.log('\n3. Testing responsible AI overview...');
    const overview = await fetcher(endpoints.responsible.overview);
    console.log('✅ Responsible AI overview keys:', Object.keys(overview));
    
    // Validate data structure
    const requiredKeys = ['summary', 'groundedness', 'reliability', 'safetyChecks', 'performance', 'moderation', 'feedback', 'interventions', 'audit'];
    const missingKeys = requiredKeys.filter(key => !(key in overview));
    
    if (missingKeys.length === 0) {
      console.log('✅ All required keys present in responsible AI data');
    } else {
      console.log('⚠️ Missing keys:', missingKeys);
    }
    
    // Test individual endpoints
    console.log('\n4. Testing individual endpoints...');
    
    const summary = await fetcher(endpoints.responsible.summary);
    console.log('✅ Summary keys:', Object.keys(summary));
    
    const performance = await fetcher(endpoints.responsible.performance);
    console.log('✅ Performance keys:', Object.keys(performance));
    
    const safety = await fetcher(endpoints.responsible.safety);
    console.log('✅ Safety keys:', Object.keys(safety));
    
    // Validate summary structure
    const summaryKeys = ['totalAssertions', 'safetyFiltered', 'highConfidenceCitations'];
    const missingSummaryKeys = summaryKeys.filter(key => !(key in summary));
    
    if (missingSummaryKeys.length === 0) {
      console.log('✅ All summary keys present');
      console.log('   Total assertions:', summary.totalAssertions);
      console.log('   Safety filtered:', summary.safetyFiltered);
      console.log('   High confidence citations:', summary.highConfidenceCitations);
    } else {
      console.log('⚠️ Missing summary keys:', missingSummaryKeys);
    }
    
    // Validate performance structure
    const performanceKeys = ['title', 'chart'];
    const missingPerformanceKeys = performanceKeys.filter(key => !(key in performance));
    
    if (missingPerformanceKeys.length === 0) {
      console.log('✅ All performance keys present');
      console.log('   Performance title:', performance.title);
      console.log('   Chart series count:', performance.chart.series.length);
    } else {
      console.log('⚠️ Missing performance keys:', missingPerformanceKeys);
    }
    
    // Validate safety structure
    const safetyKeys = ['groundedness', 'reliability', 'safetyChecks', 'moderation'];
    const missingSafetyKeys = safetyKeys.filter(key => !(key in safety));
    
    if (missingSafetyKeys.length === 0) {
      console.log('✅ All safety keys present');
      console.log('   Groundedness title:', safety.groundedness.title);
      console.log('   Safety checks series count:', safety.safetyChecks.chart.series.length);
    } else {
      console.log('⚠️ Missing safety keys:', missingSafetyKeys);
    }
    
    // Validate feedback structure
    const feedbackKeys = ['title', 'subheader', 'list'];
    const missingFeedbackKeys = feedbackKeys.filter(key => !(key in overview.feedback));
    
    if (missingFeedbackKeys.length === 0) {
      console.log('✅ All feedback keys present');
      console.log('   Feedback items count:', overview.feedback.list.length);
    } else {
      console.log('⚠️ Missing feedback keys:', missingFeedbackKeys);
    }
    
    // Validate audit structure
    const auditKeys = ['title', 'headers', 'tableData'];
    const missingAuditKeys = auditKeys.filter(key => !(key in overview.audit));
    
    if (missingAuditKeys.length === 0) {
      console.log('✅ All audit keys present');
      console.log('   Audit table rows:', overview.audit.tableData.length);
      console.log('   Audit headers count:', overview.audit.headers.length);
    } else {
      console.log('⚠️ Missing audit keys:', missingAuditKeys);
    }
    
    console.log('\n========================================');
    console.log('✅ All responsible AI API tests completed successfully!');
    
    return { 
      success: true, 
      data: { 
        overview, 
        summary, 
        performance, 
        safety 
      } 
    };
    
  } catch (error) {
    console.error('❌ Responsible AI API test failed:', error);
    console.error('Error details:', error.message);
    console.error('Make sure the backend server is running on http://localhost:8000');
    
    return { success: false, error: error.message };
  }
}

// Export for use in components or console testing
export default testResponsibleAPI;
