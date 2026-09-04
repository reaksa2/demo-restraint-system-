import api from './api'

export async function login(email, password) {
  const { data } = await api.post('/auth/login', { email, password })
  localStorage.setItem('token', data.access_token)
  return data
}

export async function getMe() {
  const { data } = await api.get('/auth/me')
  return data
}

export function logout() {
  localStorage.removeItem('token')
}
