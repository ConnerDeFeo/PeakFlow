import { Link, useNavigate } from 'react-router-dom';
import { Logo } from './Logo';
import { NEON } from '../constants/colors';

export function NavBar() {
  const navigation = useNavigate();
  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigation('/')}>
          <Logo/>
          <span className="text-lg text-black">Peak Flow</span>
        </div>
        <Link to="/contact" className={`text-lg font-medium text-gray-700 transition-colors duration-200 hover:text-[${NEON}]`}>
          Contact
        </Link>
      </div>
    </nav>
  )
}
