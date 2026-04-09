import { NEON, NEON_GLOW } from '../../../constants/colors'

export function Hero() {
  return (
    <section className="relative pt-36 pb-28 text-center overflow-hidden">
        {/* Background glow */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              'radial-gradient(ellipse 60% 40% at 50% 30%, rgba(0,212,255,0.12) 0%, transparent 70%)',
          }}
        />
        <div>
          <h1 className="text-6xl md:text-7xl font-black leading-[1.05] tracking-tight mb-10">
            A Roofing Receptionist <br/><span style={{ color: NEON }}>That Never Sleeps.</span>
          </h1>

          {/* Demo number — prominent, right below headline */}
          <a
            href="tel:3158733743"
            className="group inline-flex flex-col items-center gap-1 mb-10"
          >
            <span className="text-xs font-semibold uppercase tracking-widest text-gray-500 mb-1">
              Hear our AI receptionist — call right now
            </span>
            <span
              className="text-4xl md:text-5xl font-black tracking-tight transition-opacity group-hover:opacity-80"
              style={{ color: NEON, textShadow: `0 0 40px ${NEON_GLOW}` }}
            >
              315-873-3743
            </span>
          </a>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
            PeakFlow's AI voice receptionist answers every call, qualifies every lead,
            and books appointments — 24/7, without you lifting a finger.
          </p>
        </div>
      </section>
  )
}
