import axios from 'axios'

// Simple test to verify API connectivity
async function testAPIConnection() {
  try {
    console.log('Testing API connection...')
    
    // Test health check endpoint
    const healthResponse = await axios.get('http://localhost:8000/health')
    console.log('✅ Health check:', healthResponse.data)
    
    // Test root endpoint
    const rootResponse = await axios.get('http://localhost:8000/')
    console.log('✅ Root endpoint:', rootResponse.data)
    
    // Test API v1 endpoints (without auth)
    try {
      const projectsResponse = await axios.get('http://localhost:8000/api/v1/projects')
      console.log('❌ Projects endpoint should require auth, but got:', projectsResponse.status)
    } catch (error) {
      if (error.response?.status === 401) {
        console.log('✅ Projects endpoint properly requires authentication')
      } else {
        console.log('❌ Unexpected error:', error.message)
      }
    }
    
    // Test OpenAPI docs availability
    try {
      const docsResponse = await axios.get('http://localhost:8000/docs')
      console.log('✅ API docs available')
    } catch (error) {
      console.log('⚠️ API docs may not be available:', error.message)
    }
    
    console.log('\n🎉 API integration test completed!')
    
  } catch (error) {
    console.error('❌ API connection failed:', error.message)
    
    if (error.code === 'ECONNREFUSED') {
      console.log('\n💡 Make sure the backend server is running:')
      console.log('   cd backend')
      console.log('   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload')
    }
  }
}

// Check if running in Node.js environment
if (typeof window === 'undefined') {
  testAPIConnection()
}

export { testAPIConnection }