import { Logo } from '../../../components/Logo'
import { NEON, NEON_GLOW } from '../../../constants/colors'

export function ContactCTA() {
  return (
    <section id="contact" className="py-24 px-6 border-t border-gray-900">
      <div className="max-w-3xl mx-auto text-center">
        <div
          className="border border-gray-800 rounded-3xl px-10 py-16"
          style={{
            background: 'linear-gradient(135deg, #050505 0%, #091318 100%)',
            boxShadow: `inset 0 0 80px rgba(0,212,255,0.05)`,
          }}
        >
          <div className="flex justify-center mb-6">
            <Logo size={64} />
          </div>
          <h2 className="text-4xl md:text-5xl font-black mb-5">
            Ready to Get<br />
            <span style={{ color: NEON }}>More Leads?</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-lg mx-auto mb-8 leading-relaxed">
            Book a 30-minute free consultation with our team.
          </p>
          <a
            href="mailto:hello@peakflow.ai"
            className="inline-block px-10 py-5 rounded-full text-lg font-bold text-black transition-opacity hover:opacity-90"
            style={{
              background: NEON,
              boxShadow: `0 0 48px ${NEON_GLOW}`,
            }}
          >
            Book Your Free Consultation
          </a>
          <p className="text-gray-600 text-xs mt-4">
            No commitment. No credit card. Just results.
          </p>
        </div>
      </div>
    </section>
  )
}
