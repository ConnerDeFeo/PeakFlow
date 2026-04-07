import { Logo } from '../components/Logo'

export function Footer() {
  return (
    <footer className="border-t border-gray-900 py-10 px-6 bg-black">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="flex items-center gap-3">
          <Logo size={26} />
          <span className="font-black text-sm tracking-tight">PeakFlow</span>
        </div>
        <p className="text-gray-600 text-xs">© 2026 PeakFlow. All rights reserved.</p>
      </div>
    </footer>
  )
}
