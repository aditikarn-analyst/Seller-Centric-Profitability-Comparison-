import axios from 'axios'

// One axios instance for the whole app. A single request interceptor attaches
// the JWT to every call, so no component ever handles the Authorization header
// itself (README §10).
const client = axios.create({ baseURL: '/api/v1' })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default client
