import type { ReactNode } from 'react'

export function NavLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      className="text-sm text-gray-400 hover:text-white transition-colors"
    >
      {children}
    </a>
  )
}
