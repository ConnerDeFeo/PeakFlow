import { NEON } from '../constants'

export function Logo({ size = 48 }: { size?: number }) {
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
