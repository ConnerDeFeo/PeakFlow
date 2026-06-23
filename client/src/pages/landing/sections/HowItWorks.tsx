import { NEON } from '../../../constants/colors'
const STEPS = [
  {
    num: '01',
    title: 'Discovery Call',
    desc: 'We start by taking a look at your business to define the best type of AI receptionist for your needs and goals.',
  },
  {
    num: '02',
    title: 'Custom Build',
    desc: 'Our engineers build AI systems tailored to your exact business — no off-the-shelf templates.',
  },
  {
    num: '03',
    title: 'Launch & Integration',
    desc: 'We deploy, test, and integrate with any existing software you use, ensuring a seamless transition and immediate impact.',
  },
  {
    num: '04',
    title: 'Optimise & Scale',
    desc: 'We monitor performance and continuously fine-tune automations as your business grows.',
  },
  {
    num: '05',
    title: 'Ongoing Support',
    desc: 'Our team is always on hand to provide support, updates, and new features as needed.',
  }
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-6 border-t border-gray-200">
      <div className="text-center mb-16">
        <h2 className="text-4xl md:text-5xl font-black mb-4">
          Simple Process.{' '}
          <span style={{ color: NEON }}>Powerful Results.</span>
        </h2>
        <p className="text-gray-600 text-lg">
          We handle everything — you see the results.
        </p>
      </div>
      <div className="space-y-4">
        {STEPS.map((step) => (
          <div
            key={step.num}
            className="flex gap-4 md:gap-6 items-start border border-gray-200 rounded-2xl p-5 md:p-8"
            style={{ background: 'linear-gradient(135deg,#fafafa,#f3f3f3)' }}
          >
            <div
              className="text-4xl font-black shrink-0 leading-none"
              style={{ color: NEON, opacity: 0.55 }}
            >
              {step.num}
            </div>
            <div>
              <h3 className="text-xl font-bold mb-2">{step.title}</h3>
              <p className="text-gray-600 leading-relaxed">{step.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
