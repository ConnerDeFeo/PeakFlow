import { NEON } from '../constants/colors'

export function Stars() {
  return (
    <div className="flex gap-0.5 mb-4">
      {[...Array(5)].map((_, i) => (
        <span key={i} style={{ color: NEON, fontSize: '1rem' }}>★</span>
      ))}
    </div>
  )
}
