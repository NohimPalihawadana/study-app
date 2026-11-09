import "./App.css";

function App() {
  return (
    <div className="landing-page">
      <header className="navbar">
        <a href="/" className="brand">
          <span className="brand-icon">✦</span>
          study-app
        </a>
      </header>

      <main className="hero">
        <div className="hero-content">
          <span className="eyebrow">
            YOUR PERSONAL LEARNING COMPANION
          </span>

          <h1>
            Welcome to
            <span className="highlight"> study-app!</span>
          </h1>

          <p className="description">
            Study smarter, stay organized, and prepare
            confidently for every exam. Your personal
            study companion is here to help you achieve
            your academic goals.
          </p>

          <div className="buttons">
            <a href="/register" className="button primary">
              Get Started
            </a>

            <a href="/login" className="button secondary">
              Login
            </a>
          </div>

          <p className="hero-note">
            Your learning journey starts here.
          </p>
        </div>

        <div className="hero-visual" aria-hidden="true">
          <div className="visual-glow"></div>

          <div className="study-card">
            <div className="card-top">
              <span className="card-symbol">✦</span>
              <span className="card-status">Study space</span>
            </div>

            <h2>Make every study session count.</h2>

            <div className="progress-label">
              <span>Your learning journey</span>
              <span>In progress</span>
            </div>

            <div className="progress-track">
              <div className="progress-fill"></div>
            </div>

            <div className="mini-card">
              <span className="mini-icon">✓</span>
              <div>
                <strong>Learn with purpose</strong>
                <p>One topic at a time</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
