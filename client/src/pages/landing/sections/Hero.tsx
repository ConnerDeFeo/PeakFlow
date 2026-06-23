import { NEON } from '../../../constants/colors'
import { DEMO_NUMBER } from '../../../constants/demo'

export function Hero() {
  return (
    <section className="relative pt-28 pb-20 md:pt-36 md:pb-28 text-center overflow-hidden">
        {/* Background glow */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              'radial-gradient(ellipse 60% 40% at 50% 30%, rgba(0,212,255,0.12) 0%, transparent 70%)',
          }}
        />
        <div className="relative">
          <h1 className="text-4xl sm:text-5xl md:text-7xl font-black leading-[1.05] tracking-tight mb-6 md:mb-10">
            A Roofing Receptionist <br/><span style={{ color: NEON }}>That Never Sleeps.</span>
          </h1>

          {/* Demo number — first thing the user sees */}
          <div className="mb-10 md:mb-16">
            <a
              href={`tel:${DEMO_NUMBER.replace(/[^0-9]/g, '')}`}
              className="inline-block text-4xl sm:text-5xl md:text-7xl font-black tracking-tight transition-opacity hover:opacity-80"
              style={{ color: NEON }}
            >
              {DEMO_NUMBER}
            </a>
            <p className="text-xs md:text-sm font-semibold uppercase tracking-widest text-gray-500 my-3">
              Try our AI receptionist live — call the demo line
            </p>
          </div>

          <p className="text-lg px-6 md:px-0 md:text-xl text-gray-600 max-w-2xl mx-auto">
            PeakFlow's AI voice receptionist answers every call, qualifies every lead,
            and books appointments — 24/7, without you lifting a finger.
          </p>
        </div>
      </section>
  )
}
