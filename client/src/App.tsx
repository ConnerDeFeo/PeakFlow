import { Footer } from './components/Footer'
import { ContactCTA } from './pages/landing/sections/ContactCTA'
import { FAQ } from './pages/landing/sections/FAQ'
import { Testimonials } from './pages/landing/sections/Testimonials'
import { HowItWorks } from './pages/landing/sections/HowItWorks'
import { Services } from './pages/landing/sections/Services'
import { Hero } from './pages/landing/sections/Hero'
import { NavBar } from './components/NavBar'

function App() {
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

export default App
