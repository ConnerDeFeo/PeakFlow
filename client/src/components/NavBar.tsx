import { Link } from 'react-router-dom';
import { Logo } from './Logo';
import { NEON } from '../constants/colors';

export function NavBar() {
  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 border-b border-gray-900 bg-black/80 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Logo size={34} />
          <span className="text-lg text-white">PeakFlow</span>
        </div>
        <Link to="/contact" className={`text-sm font-medium text-gray-300 hover:text-${NEON}`}>
          Contact
        </Link>
      </div>
    </nav>
  )
}
