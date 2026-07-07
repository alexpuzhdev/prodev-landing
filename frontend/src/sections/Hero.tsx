import { useContent } from '../content'
import { tgLink } from './Header'

export function Hero() {
  const { t } = useContent()
  return (
    <section className="hero">
      <div className="hero-shape-ring" aria-hidden="true"></div>
      <div className="hero-shape-dot" aria-hidden="true"></div>
      <div className="hero-shape-square" aria-hidden="true"></div>
      <p className="hero-kicker">{t('kicker')}</p>
      <div className="hero-grid">
        <h1>{t('heroTitle')}</h1>
        <div className="hero-side">
          <p>{t('heroText')}</p>
          <div className="hero-cta">
            <a className="btn btn-dark btn-wide" href={tgLink(t)} target="_blank" rel="noopener">
              {t('ctaDiscuss')}
            </a>
            <a className="btn btn-outline btn-wide" href="#services">
              {t('ctaServices')}
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
