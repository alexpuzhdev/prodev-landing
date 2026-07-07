import { useContent } from '../content'
import { tgLink } from './Header'

export function Cta() {
  const { t } = useContent()
  return (
    <section className="cta-section">
      <div className="cta">
        <div className="cta-shape-ring" aria-hidden="true"></div>
        <div className="cta-shape-dot" aria-hidden="true"></div>
        <div className="cta-inner">
          <h2>{t('ctaTitle')}</h2>
          <p>{t('ctaText')}</p>
          <a className="btn btn-light btn-wide" href={tgLink(t)} target="_blank" rel="noopener">
            {t('ctaHeader')}
          </a>
        </div>
      </div>
    </section>
  )
}
