import { useContent } from '../content'

export function About() {
  const { t } = useContent()
  return (
    <section id="about" className="section">
      <div className="section-inner about-grid">
        <div className="about-head">
          <h2>{t('aboutTitle')}</h2>
          <div className="about-shapes" aria-hidden="true">
            <span className="shape-circle-fill"></span>
            <span className="shape-circle-line"></span>
            <span className="shape-square-fill"></span>
            <span className="shape-square-line"></span>
          </div>
        </div>
        <div className="about-text">
          <p>{t('aboutP1')}</p>
          <p>{t('aboutP2')}</p>
        </div>
      </div>
    </section>
  )
}
