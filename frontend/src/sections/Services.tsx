import { useContent } from '../content'

const CARDS = [
  { icon: 'icon-circle', title: 'svc1Title', text: 'svc1Text' },
  { icon: 'icon-square-line', title: 'svc2Title', text: 'svc2Text' },
  { icon: 'icon-diamond', title: 'svc3Title', text: 'svc3Text' },
  { icon: 'icon-arch', title: 'svc4Title', text: 'svc4Text' },
]

export function Services() {
  const { t } = useContent()
  return (
    <section id="services" className="section">
      <div className="section-inner">
        <h2>{t('servicesTitle')}</h2>
        <div className="services-grid">
          {CARDS.map((c) => (
            <div className="service-card" key={c.title}>
              <span className={c.icon} aria-hidden="true"></span>
              <h3>{t(c.title)}</h3>
              <p>{t(c.text)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
