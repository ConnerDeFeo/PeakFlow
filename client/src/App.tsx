import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { NavBar } from './components/NavBar';
import { Footer } from './components/Footer';
import Contact from './pages/Contact';
import Landing from './pages/landing/Landing';

function App() {
  return (
    <BrowserRouter>
      <NavBar/>
      <div className='bg-black'>
         <div className='max-w-4xl mx-auto'>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </div>
      </div>
      <Footer/>
    </BrowserRouter>
  );
}

export default App;
