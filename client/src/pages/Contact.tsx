import { useState } from 'react'
import { NEON, NEON_GLOW } from '../constants/colors'
import { DEMO_NUMBER } from '../constants/demo'

const MISSED_CALLS_OPTIONS = [
  '0-2 calls',
  '3-5 calls',
  '6-10 calls',
  '10-20 calls',
  '20+ calls',
]

const INITIAL_FORM = {
  name: '',
  business_name: '',
  phone: '',
  email: '',
  missed_calls: '',
}

const Contact = () => {
  const [form, setForm] = useState(INITIAL_FORM)
  const [status, setStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault()
    setStatus('sending')
    try {
      const res = await fetch(import.meta.env.VITE_EMAIL_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (res.ok) {
        setStatus('success')
        setForm(INITIAL_FORM)
      } else {
        setStatus('error')
      }
    } catch {
      setStatus('error')
    }
  }

  return (
    <div className="bg-black text-white min-h-screen pt-28 pb-24 px-6">
      {/* Background glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 70% 45% at 50% 10%, rgba(0,212,255,0.09) 0%, transparent 70%)',
        }}
      />

      <div className="relative">
        {/* Heading */}
        <div className="text-center mb-10 md:mb-16">
          <h1 className="text-4xl md:text-6xl font-black leading-tight mb-4">
            Let's <span style={{ color: NEON }}>Talk.</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Call our AI receptionist to set up an appointment, or reach us directly below.
          </p>
        </div>

        {/* Contact cards */}
        <div className="grid md:grid-cols-3 gap-4 mb-16">
          {/* Demo line */}
          <a
            href="tel:3158733743"
            className="group flex flex-col items-center text-center gap-3 border border-gray-800 rounded-2xl p-8 transition-colors hover:border-[#00d4ff]/40"
            style={{ background: 'linear-gradient(135deg,#050505,#091318)' }}
          >
            <span
              className="text-3xl font-black"
              style={{ color: NEON, textShadow: `0 0 32px ${NEON_GLOW}` }}
            >
              AI Demo
            </span>
            <span className="text-xs font-semibold uppercase tracking-widest text-gray-500">
              Call to set up an appointment
            </span>
            <span
              className="text-2xl font-black tracking-tight group-hover:opacity-80 transition-opacity"
              style={{ color: NEON }}
            >
              {DEMO_NUMBER}
            </span>
          </a>

          {/* Direct phone */}
          <a
            href="tel:3158797067"
            className="group flex flex-col items-center text-center gap-3 border border-gray-800 rounded-2xl p-8 transition-colors hover:border-[#00d4ff]/40"
            style={{ background: 'linear-gradient(135deg,#050505,#091318)' }}
          >
            <span className="text-3xl font-black text-white">Direct Line</span>
            <span className="text-xs font-semibold uppercase tracking-widest text-gray-500">
              Call us directly
            </span>
            <span
              className="text-2xl font-black tracking-tight group-hover:opacity-80 transition-opacity"
              style={{ color: NEON }}
            >
              {DEMO_NUMBER}
            </span>
          </a>

          {/* Email */}
          <a
            href="mailto:peakflowaiautomations@gmail.com"
            className="group flex flex-col items-center text-center gap-3 border border-gray-800 rounded-2xl p-8 transition-colors hover:border-[#00d4ff]/40"
            style={{ background: 'linear-gradient(135deg,#050505,#091318)' }}
          >
            <span className="text-3xl font-black text-white">Email</span>
            <span className="text-xs font-semibold uppercase tracking-widest text-gray-500">
              Send us a message
            </span>
            <span
              className="text-base font-semibold break-all group-hover:opacity-80 transition-opacity"
              style={{ color: NEON }}
            >
              peakflowaiautomations<br />@gmail.com
            </span>
          </a>
        </div>

        {/* Lead capture form */}
        <div
          className="border border-gray-800 rounded-3xl px-5 md:px-14 py-10 md:py-14"
          style={{
            background: 'linear-gradient(135deg,#050505 0%,#091318 100%)',
            boxShadow: `inset 0 0 80px rgba(0,212,255,0.04)`,
          }}
        >
          <h2 className="text-3xl md:text-4xl font-black mb-2 text-center">
            Get a <span style={{ color: NEON }}>Free Consultation</span>
          </h2>
          <p className="text-gray-400 text-center mb-10">
            Fill out the form and we'll reach out within one business day.
          </p>

          {status === 'success' ? (
            <div className="text-center py-12">
              <p
                className="text-3xl font-black mb-3"
                style={{ color: NEON }}
              >
                You're all set!
              </p>
              <p className="text-gray-400">We'll be in touch soon.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid md:grid-cols-2 gap-5">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    Your Name
                  </label>
                  <input
                    type="text"
                    name="name"
                    required
                    value={form.name}
                    onChange={handleChange}
                    placeholder="John Smith"
                    className="bg-black/60 border border-gray-800 rounded-xl px-5 py-4 text-white placeholder-gray-600 focus:outline-none focus:border-[#00d4ff] transition-colors"
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    Business Name
                  </label>
                  <input
                    type="text"
                    name="business_name"
                    required
                    value={form.business_name}
                    onChange={handleChange}
                    placeholder="Smith Roofing LLC"
                    className="bg-black/60 border border-gray-800 rounded-xl px-5 py-4 text-white placeholder-gray-600 focus:outline-none focus:border-[#00d4ff] transition-colors"
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    required
                    value={form.phone}
                    onChange={handleChange}
                    placeholder="000-000-0000"
                    className="bg-black/60 border border-gray-800 rounded-xl px-5 py-4 text-white placeholder-gray-600 focus:outline-none focus:border-[#00d4ff] transition-colors"
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    Email Address
                  </label>
                  <input
                    type="email"
                    name="email"
                    required
                    value={form.email}
                    onChange={handleChange}
                    placeholder="john@smithroofing.com"
                    className="bg-black/60 border border-gray-800 rounded-xl px-5 py-4 text-white placeholder-gray-600 focus:outline-none focus:border-[#00d4ff] transition-colors"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                  How many calls do you miss per week?
                </label>
                <select
                  name="missed_calls"
                  required
                  value={form.missed_calls}
                  onChange={handleChange}
                  className="bg-black/60 border border-gray-800 rounded-xl px-5 py-4 text-white focus:outline-none focus:border-[#00d4ff] transition-colors appearance-none cursor-pointer"
                  style={{ colorScheme: 'dark' }}
                >
                  <option value="" disabled>Select an estimate…</option>
                  {MISSED_CALLS_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </div>

              {status === 'error' && (
                <p className="text-red-400 text-sm text-center">
                  Something went wrong. Please try again or email us directly.
                </p>
              )}

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={status === 'sending'}
                  className="cursor-pointer w-full py-5 rounded-full text-lg font-bold text-black transition-opacity hover:opacity-90 disabled:opacity-50"
                  style={{
                    background: NEON,
                    boxShadow: `0 0 48px ${NEON_GLOW}`,
                  }}
                >
                  {status === 'sending' ? 'Sending…' : 'Send My Info'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export default Contact;