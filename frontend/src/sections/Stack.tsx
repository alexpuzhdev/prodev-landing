import { useContent } from '../content'

const COLS = [
  { dot: 'stack-dot-accent', title: 'stackFront', items: 'stackFrontItems' },
  { dot: 'stack-dot-ink', title: 'stackBack', items: 'stackBackItems' },
  { dot: 'stack-dot-ring', title: 'stackInfra', items: 'stackInfraItems' },
]

export function Stack() {
  const { t } = useContent()
  return (
    <section id="stack" className="section">
      <div className="section-inner">
        <h2>{t('stackTitle')}</h2>
        <div className="stack-grid">
          {COLS.map((c) => (
            <div className="stack-col" key={c.title}>
              <h3>
                <span className={c.dot} aria-hidden="true"></span>
                <span>{t(c.title)}</span>
              </h3>
              <p>{t(c.items)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
