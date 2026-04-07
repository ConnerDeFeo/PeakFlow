import { Stars } from '../components/Stars'
import { NEON, TESTIMONIALS } from '../constants'

export function Testimonials() {
  return (
    <section id="results" className="py-24 px-6 border-t border-gray-900">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-black mb-4">
            Real Results from{' '}
            <span style={{ color: NEON }}>Real Roofers.</span>
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {TESTIMONIALS.map((t) => (
            <div
              key={t.name}
              className="border border-gray-800 rounded-2xl p-8 flex flex-col"
              style={{ background: 'linear-gradient(135deg,#090909,#0f0f0f)' }}
            >
              <Stars />
              <p className="text-gray-300 leading-relaxed flex-1 mb-6">
                "{t.quote}"
              </p>
              <div>
                <div className="font-semibold text-sm">{t.name}</div>
                <div className="text-xs text-gray-500">{t.company}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
