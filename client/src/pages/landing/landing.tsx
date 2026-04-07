import { ContactCTA } from "./sections/ContactCTA"
import { FAQ } from "./sections/FAQ"
import { Hero } from "./sections/Hero"
import { HowItWorks } from "./sections/HowItWorks"
import { NavBar } from "../../components/NavBar"
import { Services } from "./sections/Services"
import { Testimonials } from "./sections/Testimonials"
import { Footer } from "../../components/Footer"

const Landing = () => {
  return (
    <div
      className="bg-black text-white min-h-screen"
      style={{ fontFamily: "'Inter', system-ui, -apple-system, sans-serif" }}
    >
      <NavBar/>
      <Hero/>
      <Services/>
      <HowItWorks/>
      <Testimonials/>
      <FAQ/>
      <ContactCTA />
      <Footer/>
    </div>
  )
}

export default Landing
