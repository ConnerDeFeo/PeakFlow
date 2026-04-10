export function Logo({ size = 2 }: { size?: number }) {
  return (
    <img
      src="/logo.svg"
      alt="PeakFlow logo"
      style={{width: `${size}rem`, height:`${size}rem`}}
    />
  )
}
