import { Hero } from "./sections/Hero";
import { HowItWorks } from "./sections/HowItWorks";
import { FAQ } from "./sections/FAQ";
import { ContactCTA } from "./sections/ContactCTA";

const Landing = () => {
  return (
    <div className="text-white">
        <Hero/>
        <HowItWorks/>
        <FAQ/>
        <ContactCTA/>
    </div>
  )
}

export default Landing
