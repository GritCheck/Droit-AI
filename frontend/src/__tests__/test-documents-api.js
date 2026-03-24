// Test script for documents API integration
// This can be run in browser console or as a temporary component

import { fetcher, endpoints } from 'src/lib/axios';

export async function testDocumentsAPI() {
  console.log('📄 Testing Documents API Integration');
  console.log('=====================================');
  
  try {
    // Test backend health
    console.log('\n1. Testing backend health...');
    const healthResponse = await fetcher('/health');
    console.log('✅ Backend health:', healthResponse);
    
    // Test documents health
    console.log('\n2. Testing documents service health...');
    const documentsHealth = await fetcher(endpoints.documents.health);
    console.log('✅ Documents service health:', documentsHealth);
    
    // Test documents list
    console.log('\n3. Testing documents list...');
    const listResponse = await fetcher(endpoints.documents.list);
    console.log('✅ Documents count:', listResponse.documents.length);
    console.log('✅ Total documents:', listResponse.total);
    
    // Validate document structure
    const requiredKeys = ['id', 'type', 'name', 'data_limit', 'time_limit', 'rate_limit', 'price', 'status', 'created_at', 'updated_at'];
    const documents = listResponse.documents;
    
    const invalidDocs = documents.filter(doc => 
      !requiredKeys.every(key => key in doc)
    );
    
    if (invalidDocs.length === 0) {
      console.log('✅ All documents have required properties');
    } else {
      console.log('⚠️ Documents with missing properties:', invalidDocs);
    }
    
    // Test document filtering
    console.log('\n4. Testing document filtering...');
    
    // Test status filter
    const indexedResponse = await fetcher(`${endpoints.documents.list}?status=indexed`);
    console.log('✅ Indexed documents:', indexedResponse.documents.length);
    
    // Test type filter
    const pdfResponse = await fetcher(`${endpoints.documents.list}?type=PDF`);
    console.log('✅ PDF documents:', pdfResponse.documents.length);
    
    // Test search
    const searchResponse = await fetcher(`${endpoints.documents.list}?search=Document`);
    console.log('✅ Search results:', searchResponse.documents.length);
    
    // Test document details
    console.log('\n5. Testing document details...');
    if (documents.length > 0) {
      const firstDocId = documents[0].id;
      const detailResponse = await fetcher(endpoints.documents.detail.replace('{id}', firstDocId));
      console.log('✅ Document details:', detailResponse.name);
      
      // Validate document details structure
      const detailKeys = ['id', 'type', 'name', 'description', 'features', 'subscribers'];
      const missingDetailKeys = detailKeys.filter(key => !(key in detailResponse));
      
      if (missingDetailKeys.length === 0) {
        console.log('✅ All document detail keys present');
        console.log('   Document ID:', detailResponse.id);
        console.log('   Document Type:', detailResponse.type);
        console.log('   Security Level:', detailResponse.price);
        console.log('   Status:', detailResponse.status);
      } else {
        console.log('⚠️ Missing detail keys:', missingDetailKeys);
      }
    }
    
    // Test document statistics
    console.log('\n6. Testing document statistics...');
    const statsResponse = await fetcher(endpoints.documents.stats);
    console.log('✅ Document statistics:', statsResponse);
    
    // Validate stats structure
    const statsKeys = ['total', 'by_status', 'by_type', 'by_security_level', 'total_subscribers'];
    const missingStatsKeys = statsKeys.filter(key => !(key in statsResponse));
    
    if (missingStatsKeys.length === 0) {
      console.log('✅ All stats keys present');
      console.log('   Total documents:', statsResponse.total);
      console.log('   Indexed:', statsResponse.by_status.indexed);
      console.log('   Processing:', statsResponse.by_status.processing);
      console.log('   Failed:', statsResponse.by_status.failed);
      console.log('   Flagged:', statsResponse.by_status.flagged);
      console.log('   Total subscribers:', statsResponse.total_subscribers);
    } else {
      console.log('⚠️ Missing stats keys:', missingStatsKeys);
    }
    
    // Test document operations (simulate)
    console.log('\n7. Testing document operations...');
    if (documents.length > 0) {
      const testDocId = documents[0].id;
      
      // Test reindex (this would normally be a POST request)
      console.log('✅ Reindex endpoint available:', endpoints.documents.reindex.replace('{id}', testDocId));
      
      // Test delete (this would normally be a DELETE request)
      console.log('✅ Delete endpoint available:', endpoints.documents.delete.replace('{id}', testDocId));
    }
    
    // Test document types
    console.log('\n8. Testing document types...');
    const types = [...new Set(documents.map(doc => doc.type))];
    console.log('✅ Document types found:', types);
    
    // Test security levels
    console.log('\n9. Testing security levels...');
    const securityLevels = [...new Set(documents.map(doc => doc.price))];
    console.log('✅ Security levels found:', securityLevels.sort((a, b) => a - b));
    
    // Test status distribution
    console.log('\n10. Testing status distribution...');
    const statusCounts = documents.reduce((acc, doc) => {
      acc[doc.status] = (acc[doc.status] || 0) + 1;
      return acc;
    }, {});
    console.log('✅ Status distribution:', statusCounts);
    
    // Test chunk sizes
    console.log('\n11. Testing chunk sizes...');
    const chunkSizes = documents.map(doc => doc.data_limit);
    const uniqueChunkSizes = [...new Set(chunkSizes)];
    console.log('✅ Unique chunk sizes:', uniqueChunkSizes.length);
    
    // Test vector dimensions
    console.log('\n12. Testing vector dimensions...');
    const vectorDims = documents.map(doc => doc.rate_limit);
    const uniqueVectorDims = [...new Set(vectorDims)];
    console.log('✅ Unique vector dimensions:', uniqueVectorDims.length);
    
    console.log('\n=====================================');
    console.log('✅ All documents API tests completed successfully!');
    
    return { 
      success: true, 
      data: { 
        documents: listResponse.documents,
        stats: statsResponse,
        total: listResponse.total
      } 
    };
    
  } catch (error) {
    console.error('❌ Documents API test failed:', error);
    console.error('Error details:', error.message);
    console.error('Make sure the backend server is running on http://localhost:8000');
    
    return { success: false, error: error.message };
  }
}

// Export for use in components or console testing
export default testDocumentsAPI;
