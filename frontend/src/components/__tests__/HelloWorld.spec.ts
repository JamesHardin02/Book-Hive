import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import HelloWorld from '../HelloWorld.vue'
import ApiStatus from '../ApiStatus.vue'

describe('HelloWorld', () => {
  it('renders properly', () => {
    const wrapper = mount(HelloWorld, { props: { msg: 'Hello Vitest' } })
    expect(wrapper.text()).toContain('Hello Vitest')
  })
})

describe('ApiStatus', () => {
  it('renders properly', () => {
    const wrapper = mount(ApiStatus)
    expect(wrapper.text()).toContain('Backend health:')
  })
})
