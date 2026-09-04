import { chromium } from 'playwright'

const API = 'http://localhost:8000/api'
const FRONTEND = 'http://localhost:5173'
const failures = []
const check = (label, cond) => { console.log(`[${cond ? 'PASS' : 'FAIL'}] ${label}`); if (!cond) failures.push(label) }

async function api(path, { method = 'GET', token, body } = {}) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`${method} ${path} -> ${res.status}: ${await res.text()}`)
  return res.status === 204 ? null : res.json()
}

// --- Seed data via API (fast, already proven correct by e2e_test.py) ---
const suffix = Date.now()
const { access_token: level1Token } = await api('/auth/login', { method: 'POST', body: { email: 'owner@example.com', password: 'change-me-now' } })
const group = await api('/groups', { method: 'POST', token: level1Token, body: { name: `UI Smoke Group ${suffix}` } })
const brand = await api('/brands', { method: 'POST', token: level1Token, body: { group_id: group.id, slug: `ui-smoke-brand-${suffix}`, name_en: 'UI Smoke Brand', name_kh: 'ម៉ាកសាកល្បង' } })
const zoneIn = await api(`/brands/${brand.id}/zones`, { method: 'POST', token: level1Token, body: { name_en: 'Inside', name_kh: 'ខាងក្នុង' } })
const zoneOut = await api(`/brands/${brand.id}/zones`, { method: 'POST', token: level1Token, body: { name_en: 'Outside', name_kh: 'ខាងក្រៅ' } })
const category = await api(`/brands/${brand.id}/categories`, { method: 'POST', token: level1Token, body: { name_en: 'Chicken', name_kh: 'មាន់' } })
const food = await api(`/brands/${brand.id}/foods`, {
  method: 'POST', token: level1Token,
  body: { category_id: category.id, name_en: 'Fried Chicken', name_kh: 'មាន់បំពង', description_en: 'Crispy and delicious', description_kh: 'ក្រូបនិងឆ្ងាញ់', is_available: true },
})
await api(`/brands/${brand.id}/foods/${food.id}/prices`, { method: 'PUT', token: level1Token, body: { zone_id: zoneIn.id, regular_price: '5.00' } })
await api(`/brands/${brand.id}/foods/${food.id}/prices`, { method: 'PUT', token: level1Token, body: { zone_id: zoneOut.id, regular_price: '4.00' } })
await api('/users', { method: 'POST', token: level1Token, body: { email: `smoke_inside_${suffix}@example.com`, password: 'password123', full_name: 'Smoke Inside', role: 'staff', brand_id: brand.id, zone_id: zoneIn.id } })
await api('/users', { method: 'POST', token: level1Token, body: { email: `smoke_outside_${suffix}@example.com`, password: 'password123', full_name: 'Smoke Outside', role: 'staff', brand_id: brand.id, zone_id: zoneOut.id } })
console.log('Seed data created via API.')

// --- Now verify the actual rendered UI ---
const browser = await chromium.launch()
const page = await browser.newPage()
page.on('pageerror', (err) => failures.push(`JS ERROR: ${err.message}`))
page.on('console', (msg) => { if (msg.type() === 'error') failures.push(`CONSOLE ERROR: ${msg.text()}`) })

// Level1 admin login + dashboard render
await page.goto(`${FRONTEND}/login`)
await page.fill('input[type=email]', 'owner@example.com')
await page.fill('input[type=password]', 'change-me-now')
await page.click('button[type=submit]')
await page.waitForURL('**/admin', { timeout: 8000 })
check('Level1 login reaches /admin', page.url().endsWith('/admin'))
await page.screenshot({ path: '/tmp/shot_dashboard.png' })

// Brand detail -> Foods tab renders both zone prices for admin
await page.goto(`${FRONTEND}/admin/brands/${brand.id}`)
await page.waitForSelector('text=Fried Chicken', { timeout: 8000 })
const adminBody = await page.textContent('body')
check('Brand detail page shows food name (Khmer)', adminBody.includes('មាន់បំពង'))
check('Admin Foods view shows Inside price $5.00', adminBody.includes('5.00'))
check('Admin Foods view shows Outside price $4.00', adminBody.includes('4.00'))
await page.screenshot({ path: '/tmp/shot_brand_foods.png' })

// Sign out, log in as Staff Inside -> menu shows ONLY 5.00
await page.click('text=Sign out')
await page.waitForURL('**/login', { timeout: 8000 })
await page.fill('input[type=email]', `smoke_inside_${suffix}@example.com`)
await page.fill('input[type=password]', 'password123')
await page.click('button[type=submit]')
await page.waitForURL('**/staff/menu', { timeout: 8000 })
await page.waitForSelector('text=Fried Chicken', { timeout: 8000 })
const insideBody = await page.textContent('body')
check('Staff Inside menu renders Khmer name', insideBody.includes('មាន់បំពង'))
check('Staff Inside menu shows $5.00', insideBody.includes('5.00'))
check('Staff Inside menu never shows $4.00', !insideBody.includes('4.00'))
await page.screenshot({ path: '/tmp/shot_staff_inside.png', fullPage: true })

// Sign out, log in as Staff Outside -> menu shows ONLY 4.00
await page.click('text=Sign out')
await page.waitForURL('**/login', { timeout: 8000 })
await page.fill('input[type=email]', `smoke_outside_${suffix}@example.com`)
await page.fill('input[type=password]', 'password123')
await page.click('button[type=submit]')
await page.waitForURL('**/staff/menu', { timeout: 8000 })
await page.waitForSelector('text=Fried Chicken', { timeout: 8000 })
const outsideBody = await page.textContent('body')
check('Staff Outside menu shows $4.00', outsideBody.includes('4.00'))
check('Staff Outside menu never shows $5.00', !outsideBody.includes('5.00'))
await page.screenshot({ path: '/tmp/shot_staff_outside.png', fullPage: true })

await browser.close()

console.log('\n' + '='.repeat(60))
if (failures.length) {
  console.log(`${failures.length} FAILURE(S):`)
  for (const f of failures) console.log(`  - ${f}`)
  process.exit(1)
} else {
  console.log('ALL UI SMOKE CHECKS PASSED')
}
