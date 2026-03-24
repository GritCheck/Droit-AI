// Test script for security groups API integration
// This can be run in browser console or as a temporary component

import { fetcher, endpoints } from 'src/lib/axios';

export async function testSecurityAPI() {
  console.log('🔐 Testing Security Groups API Integration');
  console.log('========================================');
  
  try {
    // Test backend health
    console.log('\n1. Testing backend health...');
    const healthResponse = await fetcher('/health');
    console.log('✅ Backend health:', healthResponse);
    
    // Test security health
    console.log('\n2. Testing security service health...');
    const securityHealth = await fetcher(endpoints.security.health);
    console.log('✅ Security service health:', securityHealth);
    
    // Test security groups
    console.log('\n3. Testing security groups...');
    const groupsResponse = await fetcher(endpoints.security.groups);
    console.log('✅ Security groups count:', groupsResponse.groups.length);
    
    // Validate data structure
    const requiredKeys = ['id', 'title', 'subheader', 'filter', 'clearanceLevel', 'description', 'members', 'created', 'modified'];
    const groups = groupsResponse.groups;
    
    const invalidGroups = groups.filter(group => 
      !requiredKeys.every(key => key in group)
    );
    
    if (invalidGroups.length === 0) {
      console.log('✅ All security groups have required properties');
    } else {
      console.log('⚠️ Groups with missing properties:', invalidGroups);
    }
    
    // Test RLS policies
    console.log('\n4. Testing RLS policies...');
    const policiesResponse = await fetcher(endpoints.security.rlsPolicies);
    console.log('✅ RLS policies count:', policiesResponse.policies.length);
    
    // Validate RLS policies structure
    const policyKeys = ['id', 'name', 'description', 'isActive', 'priority', 'conditions'];
    const policies = policiesResponse.policies;
    
    const invalidPolicies = policies.filter(policy => 
      !policyKeys.every(key => key in policy)
    );
    
    if (invalidPolicies.length === 0) {
      console.log('✅ All RLS policies have required properties');
    } else {
      console.log('⚠️ Policies with missing properties:', invalidPolicies);
    }
    
    // Test user clearance
    console.log('\n5. Testing user clearance...');
    const clearanceResponse = await fetcher(endpoints.security.userClearance);
    console.log('✅ User clearance data:', clearanceResponse);
    
    // Validate user clearance structure
    const clearanceKeys = ['userId', 'clearanceLevel', 'groups', 'department', 'lastUpdated'];
    const missingClearanceKeys = clearanceKeys.filter(key => !(key in clearanceResponse));
    
    if (missingClearanceKeys.length === 0) {
      console.log('✅ All user clearance keys present');
      console.log('   User ID:', clearanceResponse.userId);
      console.log('   Clearance Level:', clearanceResponse.clearanceLevel);
      console.log('   Groups:', clearanceResponse.groups);
      console.log('   Department:', clearanceResponse.department);
    } else {
      console.log('⚠️ Missing clearance keys:', missingClearanceKeys);
    }
    
    // Test specific security groups
    console.log('\n6. Testing specific security groups...');
    const expectedGroups = [
      'hr-all-staff',
      'legal-exec', 
      'finance-mgr',
      'ops-field',
      'medical-vetted',
      'board-only',
      'external-comm',
      'rnd-team'
    ];
    
    const foundGroups = groups.map(g => g.id);
    const missingGroups = expectedGroups.filter(id => !foundGroups.includes(id));
    
    if (missingGroups.length === 0) {
      console.log('✅ All expected security groups are present');
    } else {
      console.log('⚠️ Missing security groups:', missingGroups);
    }
    
    // Test clearance levels
    console.log('\n7. Testing clearance levels...');
    const clearanceLevels = groups.map(g => g.clearanceLevel);
    const uniqueLevels = [...new Set(clearanceLevels)].sort((a, b) => a - b);
    console.log('✅ Clearance levels found:', uniqueLevels);
    
    // Test member counts
    console.log('\n8. Testing member counts...');
    const totalMembers = groups.reduce((sum, group) => sum + group.members, 0);
    console.log('✅ Total members across all groups:', totalMembers);
    
    // Test active RLS policies
    console.log('\n9. Testing active RLS policies...');
    const activePolicies = policies.filter(policy => policy.isActive);
    console.log('✅ Active RLS policies:', activePolicies.length);
    
    console.log('\n========================================');
    console.log('✅ All security API tests completed successfully!');
    
    return { 
      success: true, 
      data: { 
        groups: groupsResponse.groups,
        policies: policiesResponse.policies,
        clearance: clearanceResponse
      } 
    };
    
  } catch (error) {
    console.error('❌ Security API test failed:', error);
    console.error('Error details:', error.message);
    console.error('Make sure the backend server is running on http://localhost:8000');
    
    return { success: false, error: error.message };
  }
}

// Export for use in components or console testing
export default testSecurityAPI;
