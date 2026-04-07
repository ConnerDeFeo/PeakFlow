import { Hero } from "./sections/Hero";
import { HowItWorks } from "./sections/HowItWorks";
import { FAQ } from "./sections/FAQ";
import { ContactCTA } from "./sections/ContactCTA";

const Landing = () => {
  return (
    <div
      className="bg-black text-white min-h-screen"
      style={{ fontFamily: "'Inter', system-ui, -apple-system, sans-serif" }}
    >
      <Hero/>
      <HowItWorks/>
      <FAQ/>
      <ContactCTA/>
    </div>
  )
}

export default Landing
