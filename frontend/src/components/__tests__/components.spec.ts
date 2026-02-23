import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import ApiStatus from '../ApiStatus.vue'
import BaseButton from '../BaseButton.vue'
import SiteNav from '../SiteNav.vue'
import PageHeader from '../PageHeader.vue'

describe('BaseButton', () => {
  it('renders default label when message is not provided', () => {
    const wrapper = mount(BaseButton)
    expect(wrapper.text()).toContain('Submit')
  })

  it('renders message when provided and uses the provided type', () => {
    const wrapper = mount(BaseButton, {
      props: { message: 'Search', type: 'button' },
    })
    expect(wrapper.text()).toContain('Search')
    expect(wrapper.get('button').attributes('type')).toBe('button')
  })
})

describe('SiteNav', () => {
  it('renders expected navigation links', () => {
    const wrapper = mount(SiteNav, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    const text = wrapper.text()
    expect(text).toContain('Login')
    expect(text).toContain('Dashboard')
    expect(text).toContain('Search')
    expect(text).toContain('Api Status')
    expect(text).toContain('Checkout')
  })
})

describe('PageHeader', () => {
  it('renders the page title and header shell', () => {
    const wrapper = mount(PageHeader, {
      props: { page: 'Dashboard' },
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('Book Hive - Dashboard')
  })
})

describe('ApiStatus', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => ({
        json: async () => ({ ok: true, db: 'connected' }),
      })) as unknown as typeof fetch,
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('shows OK when the health endpoint returns ok=true', async () => {
    const wrapper = mount(ApiStatus)

    // let the onMounted async work complete
    await Promise.resolve()
    await Promise.resolve()
    await nextTick()

    expect(wrapper.text()).toContain('Backend health:')
    expect(wrapper.text()).toContain('✅ OK')
    expect(wrapper.text()).toContain('"connected"')
  })
})
