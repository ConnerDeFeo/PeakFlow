import { Logo } from '../components/Logo'
import { NEON, NEON_GLOW } from '../constants'

export function Hero() {
  return (
    <section className="relative pt-36 pb-28 px-6 text-center overflow-hidden">
      {/* Background glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 60% 40% at 50% 30%, rgba(0,212,255,0.12) 0%, transparent 70%)',
        }}
      />
      <div className="relative max-w-4xl mx-auto">
        <div className="flex justify-center mb-8">
          <Logo size={88} />
        </div>
        <div
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold mb-6 border"
          style={{ borderColor: NEON, color: NEON }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: NEON, boxShadow: `0 0 6px ${NEON}` }}
          />
          AI Automation for Roofing Contractors
        </div>
        <h1 className="text-5xl md:text-7xl font-black leading-[1.05] tracking-tight mb-6">
          Automate Your Roofing<br />
          <span style={{ color: NEON }}>Business. Close More.</span>
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          PeakFlow builds custom AI systems that handle your leads, follow-ups,
          scheduling, and customer service — so you can focus on rooftops, not
          repetitive tasks.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="#contact"
            className="px-8 py-4 rounded-full text-base font-bold text-black transition-opacity hover:opacity-90"
            style={{
              background: NEON,
              boxShadow: `0 0 32px ${NEON_GLOW}`,
            }}
          >
            Get a Free Automation Audit →
          </a>
          <a
            href="#how-it-works"
            className="px-8 py-4 rounded-full text-base font-semibold border border-gray-700 text-gray-300 hover:border-gray-500 hover:text-white transition-colors"
          >
            See How It Works
          </a>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-20 max-w-2xl mx-auto">
          {[
            { val: '2–3×', label: 'More Leads Closed' },
            { val: '15+ hrs', label: 'Saved Per Week' },
            { val: '90 days', label: 'Average ROI Timeline' },
          ].map((s) => (
            <div
              key={s.label}
              className="border border-gray-800 rounded-2xl p-6"
              style={{ background: '#080808' }}
            >
              <div className="text-2xl md:text-3xl font-black" style={{ color: NEON }}>
                {s.val}
              </div>
              <div className="text-xs text-gray-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
