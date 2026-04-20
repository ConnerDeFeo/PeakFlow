import { useNavigate } from 'react-router-dom';
import { NEON, NEON_GLOW } from '../../../constants/colors'

export function ContactCTA() {
  const navigate = useNavigate();
  return (
    <section id="contact" className="py-24 px-6 border-t border-gray-900">
      <div className="max-w-3xl mx-auto text-center">
        <div
          className="border border-gray-800 rounded-3xl px-6 py-12 md:px-10 md:py-16"
          style={{
            background: 'linear-gradient(135deg, #050505 0%, #091318 100%)',
            boxShadow: `inset 0 0 80px rgba(0,212,255,0.05)`,
          }}
        >
          <h2 className="text-4xl md:text-5xl font-black mb-5">
            Ready to Get<br />
            <span style={{ color: NEON }}>More Leads?</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-lg mx-auto mb-8 leading-relaxed">
            Contact us to schedule a 30-minute consultation.
          </p>
          <a
            href="mailto:jackdefeo@peakflowaiautomations.com"
            className="inline-block px-10 py-5 rounded-full text-lg font-bold text-black transition-opacity hover:opacity-90"
            style={{
              background: NEON,
              boxShadow: `0 0 48px ${NEON_GLOW}`,
            }}
            onClick={() => navigate('/contact')}
          >
            Contact Us
          </a>
        </div>
      </div>
    </section>
  )
}
