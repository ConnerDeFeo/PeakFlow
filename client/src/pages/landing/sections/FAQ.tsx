import { useState } from 'react'
import { NEON, FAQS } from '../../../constants'

export function FAQ() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  return (
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
  )
}
