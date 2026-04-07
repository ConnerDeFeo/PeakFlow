import { NEON, STEPS } from '../../../constants'

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-6 border-t border-gray-900">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-black mb-4">
            Simple Process.{' '}
            <span style={{ color: NEON }}>Powerful Results.</span>
          </h2>
          <p className="text-gray-400 text-lg">
            We handle everything — you see the results.
          </p>
        </div>
        <div className="space-y-4">
          {STEPS.map((step) => (
            <div
              key={step.num}
              className="flex gap-6 items-start border border-gray-800 rounded-2xl p-8"
              style={{ background: 'linear-gradient(135deg,#090909,#0d0d0d)' }}
            >
              <div
                className="text-4xl font-black shrink-0 leading-none"
                style={{ color: NEON, opacity: 0.55 }}
              >
                {step.num}
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                <p className="text-gray-400 leading-relaxed">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
