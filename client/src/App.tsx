import { useState } from 'react'

const NEON = '#00D4FF'
const NEON_GLOW = 'rgba(0, 212, 255, 0.25)'

function Logo({ size = 48 }: { size?: number }) {
  const h = Math.round(size * 0.87)
  return (
    <svg
      width={size}
      height={h}
      viewBox="0 0 100 87"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="PeakFlow logo"
      style={{ display: 'block', flexShrink: 0 }}
    >
      {/* Outer white triangle */}
      <polygon points="50,4 96,84 4,84" fill="white" />
      {/* Inner neon blue triangle — bottom flush with outer */}
      <polygon points="50,44 74,84 26,84" fill={NEON} />
      {/* Black border drawn last so it covers the inner triangle's base */}
      <polygon
        points="50,4 96,84 4,84"
        fill="none"
        stroke="black"
        strokeWidth="6"
        strokeLinejoin="miter"
      />
    </svg>
  )
}

const SERVICES = [
  {
    icon: '📞',
    title: 'Answers Every Call',
    desc: 'Never let a lead hit voicemail again. Our AI picks up instantly, any time of day or night.',
  },
  {
    icon: '✅',
    title: 'Qualifies Your Leads',
    desc: 'The AI asks the right questions — job type, timeline, location — and filters out tyre-kickers automatically.',
  },
  {
    icon: '📅',
    title: 'Books Appointments',
    desc: 'Hot leads get scheduled directly into your calendar without you lifting a finger.',
  },
  {
    icon: '💬',
    title: 'Sends Follow-Ups',
    desc: 'After every call, automated SMS and email follow-ups keep your leads warm and moving toward a close.',
  },
  {
    icon: '🕐',
    title: '24/7 Coverage',
    desc: 'Evenings, weekends, holidays — the AI never calls in sick and never misses a call.',
  },
  {
    icon: '📊',
    title: 'Call Summaries',
    desc: 'Get a full transcript and lead summary for every call delivered straight to your inbox.',
  },
]

const STEPS = [
  {
    num: '01',
    title: 'Customer Calls',
    desc: 'A potential customer calls your business number. Our AI answers instantly — no hold music, no voicemail.',
  },
  {
    num: '02',
    title: 'AI Qualifies the Lead',
    desc: 'The AI has a natural conversation, asks the right questions, and captures all the details you need to close.',
  },
  {
    num: '03',
    title: 'You Get Notified',
    desc: 'You receive a full call summary and transcript in real time, so you know exactly who to call back and why.',
  },
  {
    num: '04',
    title: 'Automatic Follow-Up',
    desc: 'The AI sends the caller an SMS confirmation and keeps following up until the job is booked.',
  },
]

const TESTIMONIALS = [
  {
    name: 'Marcus T.',
    company: 'Summit Roofing Co.',
    quote:
      'I used to miss 3–4 calls a day when I was on a job site. PeakFlow\'s AI answers every single one and sends me a summary. I haven\'t lost a lead since.',
  },
  {
    name: 'Derek H.',
    company: 'Highpoint Roofing',
    quote:
      'The AI receptionist saved us 15 hours a week. It answers every call, qualifies the lead, and books a consult — all without me touching anything.',
  },
  {
    name: 'Sandra M.',
    company: 'Ridge Masters LLC',
    quote:
      'We were nervous about an AI talking to our customers, but it sounds incredibly natural. Several clients didn\'t even know it wasn\'t a person.',
  },
]

const FAQS = [
  {
    q: 'Can I try the AI receptionist right now?',
    a: 'Yes — call 315-873-3743 and experience it yourself. It\'s live and ready to take your call.',
  },
  {
    q: 'How does it sound? Will my customers know it\'s an AI?',
    a: 'Our AI uses natural, conversational speech and handles interruptions smoothly. Most callers can\'t tell the difference.',
  },
  {
    q: 'How quickly can my business go live?',
    a: 'Most roofing contractors are fully set up within 48–72 hours of signing on.',
  },
  {
    q: 'What happens to the leads the AI captures?',
    a: 'You receive an instant call summary via email or SMS with the caller\'s details, job type, and next steps. We can also push leads directly into your CRM.',
  },
  {
    q: 'Does it work after hours and on weekends?',
    a: '100%. The AI never sleeps — it answers every call 24 hours a day, 7 days a week, 365 days a year.',
  },
]

function Stars() {
  return (
    <div className="flex gap-0.5 mb-4">
      {[...Array(5)].map((_, i) => (
        <span key={i} style={{ color: NEON, fontSize: '1rem' }}>★</span>
      ))}
    </div>
  )
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      className="text-sm text-gray-400 hover:text-white transition-colors"
    >
      {children}
    </a>
  )
}

function App() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  return (
    <div
      className="bg-black text-white min-h-screen"
      style={{ fontFamily: "'Inter', system-ui, -apple-system, sans-serif" }}
    >
      {/* ─── NAV ─── */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 border-b border-gray-900"
        style={{ background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(12px)' }}
      >
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Logo size={34} />
            <span className="text-lg font-black tracking-tight">PeakFlow</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <NavLink href="#services">Services</NavLink>
            <NavLink href="#how-it-works">How It Works</NavLink>
            <NavLink href="#results">Results</NavLink>
            <NavLink href="#faq">FAQ</NavLink>
          </div>
          <a
            href="tel:3158733743"
            className="hidden md:inline-block px-5 py-2 rounded-full text-sm font-bold text-black transition-opacity hover:opacity-80"
            style={{ background: NEON }}
          >
            Call Now
          </a>
        </div>
      </nav>

      {/* ─── HERO ─── */}
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
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <Logo size={88} />
          </div>

          <h1 className="text-5xl md:text-7xl font-black leading-[1.05] tracking-tight mb-10">
            A Receptionist <span style={{ color: NEON }}>That Never Sleeps.</span>
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
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            PeakFlow's AI voice receptionist answers every call, qualifies every lead,
            and books appointments — 24/7, without you lifting a finger.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
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
              { val: '100%', label: 'Calls Answered' },
              { val: '15+ hrs', label: 'Saved Per Week' },
              { val: '24/7', label: 'Always Available' },
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

      {/* ─── SERVICES ─── */}
      <section id="services" className="py-24 px-6 border-t border-gray-900">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-black mb-4">
              One Receptionist.{' '}
              <span style={{ color: NEON }}>Six Superpowers.</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-xl mx-auto">
              Our AI voice receptionist handles every part of the inbound call experience
              so you never miss a roofing lead again.
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

      {/* ─── HOW IT WORKS ─── */}
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

      {/* ─── TESTIMONIALS ─── */}
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

      {/* ─── FAQ ─── */}
      <section id="faq" className="py-24 px-6 border-t border-gray-900">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-4xl font-black mb-3">Common Questions</h2>
            <p className="text-gray-400">Everything you need to know before getting started.</p>
          </div>
          <div className="space-y-3">
            {FAQS.map((faq, i) => (
              <div
                key={i}
                className="border border-gray-800 rounded-xl overflow-hidden"
                style={{ background: '#090909' }}
              >
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex justify-between items-center px-6 py-5 text-left font-semibold text-sm hover:bg-gray-900 transition-colors"
                >
                  <span>{faq.q}</span>
                  <span
                    className="text-xl leading-none ml-4 shrink-0"
                    style={{ color: NEON }}
                  >
                    {openFaq === i ? '−' : '+'}
                  </span>
                </button>
                {openFaq === i && (
                  <div className="px-6 pb-5 text-sm text-gray-400 leading-relaxed border-t border-gray-800 pt-4">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── FINAL CTA ─── */}
      <section id="contact" className="py-24 px-6 border-t border-gray-900">
        <div className="max-w-3xl mx-auto text-center">
          <div
            className="border border-gray-800 rounded-3xl px-10 py-16"
            style={{
              background:
                'linear-gradient(135deg, #050505 0%, #091318 100%)',
              boxShadow: `inset 0 0 80px rgba(0,212,255,0.05)`,
            }}
          >
            <div className="flex justify-center mb-6">
              <Logo size={64} />
            </div>
            <h2 className="text-4xl md:text-5xl font-black mb-5">
              Hear It For<br />
              <span style={{ color: NEON }}>Yourself. Right Now.</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-lg mx-auto mb-8 leading-relaxed">
              Call <span style={{ color: NEON }} className="font-bold">315-873-3743</span> and speak to our AI receptionist live.
              Experience exactly what your customers will hear when they call your business.
            </p>
            <a
              href="tel:3158733743"
              className="inline-block px-10 py-5 rounded-full text-lg font-bold text-black transition-opacity hover:opacity-90"
              style={{
                background: NEON,
                boxShadow: `0 0 48px ${NEON_GLOW}`,
              }}
            >
              📞 Call 315-873-3743
            </a>
            <p className="text-gray-600 text-xs mt-4">
              Live demo. No sign-up required.
            </p>
          </div>
        </div>
      </section>


      {/* ─── FOOTER ─── */}
      <footer className="border-t border-gray-900 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-3">
            <Logo size={26} />
            <span className="font-black text-sm tracking-tight">PeakFlow</span>
          </div>
          <div className="flex gap-6 text-sm text-gray-500">
            <a href="#services" className="hover:text-white transition-colors">Services</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
            <a href="#results" className="hover:text-white transition-colors">Results</a>
            <a href="#contact" className="hover:text-white transition-colors">Contact</a>
          </div>
          <p className="text-gray-600 text-xs">© 2026 PeakFlow. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
