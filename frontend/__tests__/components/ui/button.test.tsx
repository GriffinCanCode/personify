import { Button } from '@/components/ui/button'
import { render, screen } from '@/lib/test-utils'
import { describe, expect, it } from 'vitest'

describe('Button', () => {
  it('should render with default variant', () => {
    render(<Button>Click me</Button>)
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeDefined()
  })

  it('should apply variant styles', () => {
    render(<Button variant="destructive">Delete</Button>)
    const button = screen.getByRole('button', { name: /delete/i })
    expect(button.className).toContain('destructive')
  })

  it('should handle disabled state', () => {
    render(<Button disabled>Disabled</Button>)
    const button = screen.getByRole('button', { name: /disabled/i })
    expect(button).toHaveProperty('disabled', true)
  })

  it('should apply custom className', () => {
    render(<Button className="custom-class">Custom</Button>)
    const button = screen.getByRole('button', { name: /custom/i })
    expect(button.className).toContain('custom-class')
  })

  it('should render different sizes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>)
    let button = screen.getByRole('button', { name: /small/i })
    expect(button.className).toContain('sm')

    rerender(<Button size="lg">Large</Button>)
    button = screen.getByRole('button', { name: /large/i })
    expect(button.className).toContain('lg')
  })
})
