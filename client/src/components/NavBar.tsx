import { Logo } from './Logo'
import { NavLink } from './NavLink'
import { NEON } from '../constants'

export function NavBar() {
  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 border-b border-gray-900"
      style={{ background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(12px)' }}
    >
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Logo size={34} />
          <span className="text-lg font-black tracking-tight">PeakFlow</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <NavLink href="#services">Services</NavLink>
          <NavLink href="#how-it-works">How It Works</NavLink>
          <NavLink href="#results">Results</NavLink>
          <NavLink href="#faq">FAQ</NavLink>
        </div>
        <a
          href="#contact"
          className="hidden md:inline-block px-5 py-2 rounded-full text-sm font-bold text-black transition-opacity hover:opacity-80"
          style={{ background: NEON }}
        >
          Free Audit
        </a>
      </div>
    </nav>
  )
}
