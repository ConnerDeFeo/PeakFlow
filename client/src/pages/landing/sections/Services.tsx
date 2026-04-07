import { NEON, SERVICES } from '../../../constants'

export function Services() {
  return (
    <section id="services" className="py-24 px-6 border-t border-gray-900">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-black mb-4">
            Everything Automated.{' '}
            <span style={{ color: NEON }}>Nothing Missed.</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            From first contact to five-star review, PeakFlow automates every step
            of the roofing sales and service cycle.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {SERVICES.map((svc) => (
            <div
              key={svc.title}
              className="group border border-gray-800 rounded-2xl p-8 hover:border-gray-600 transition-colors cursor-default"
              style={{ background: 'linear-gradient(135deg,#090909,#0f0f0f)' }}
            >
              <div className="text-3xl mb-4">{svc.icon}</div>
              <h3
                className="text-base font-bold mb-2 transition-colors"
                style={{ color: 'white' }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = NEON)
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = 'white')
                }
              >
                {svc.title}
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed">{svc.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
