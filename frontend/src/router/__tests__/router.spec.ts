import { describe, it, expect } from 'vitest'
import router from '../index'

describe('router', () => {
  it('includes expected routes', () => {
    const paths = router.getRoutes().map((r) => r.path)

    expect(paths).toContain('/')
    expect(paths).toContain('/register')
    expect(paths).toContain('/dashboard')
    expect(paths).toContain('/search')
    expect(paths).toContain('/apistatus')
    expect(paths).toContain('/checkout')
  })
})
