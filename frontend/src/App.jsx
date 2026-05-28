import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Explore } from './pages/Explore'
import { Submit } from './pages/Submit'

export function App() {
  const { pathname } = useLocation()
  return (
    <div className="app">
      <nav className="navbar">
        <span className="brand">BioMine</span>
        <div className="nav-links">
          <Link to="/" className={pathname === '/' ? 'active' : ''}>Explore</Link>
          <Link to="/submit" className={pathname === '/submit' ? 'active' : ''}>Submit Genome</Link>
        </div>
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<Explore />} />
          <Route path="/submit" element={<Submit />} />
        </Routes>
      </main>
    </div>
  )
}
