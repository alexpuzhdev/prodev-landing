import { useContent } from '../content'

export function tgLink(t: (k: string) => string): string {
  return 'https://t.me/' + t('telegramHandle')
}

export function Header() {
  const { t, lang, setLang } = useContent()
  return (
    <header className="site-header">
      <a href="#top" className="logo">
        <span className="logo-dot"></span>
        <span>{t('brandName')}</span>
      </a>
      <nav className="site-nav">
        <a href="#about">{t('navAbout')}</a>
        <a href="#services">{t('navServices')}</a>
        <a href="#stack">{t('navStack')}</a>
      </nav>
      <div className="header-actions">
        <div className="lang-switch" role="group" aria-label="Language">
          <button type="button" className={lang === 'ru' ? 'active' : ''} onClick={() => setLang('ru')}>
            RU
          </button>
          <button type="button" className={lang === 'en' ? 'active' : ''} onClick={() => setLang('en')}>
            EN
          </button>
        </div>
        <a className="btn btn-dark" href={tgLink(t)} target="_blank" rel="noopener">
          {t('ctaHeader')}
        </a>
      </div>
    </header>
  )
}
