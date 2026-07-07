import { useContent } from '../content'
import { tgLink } from './Header'

export function Footer() {
  const { t } = useContent()
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <span className="logo-dot"></span>
            <span>{t('brandName')}</span>
          </div>
          <div className="footer-meta">
            <span className="footer-copy">{t('footCopyright')}</span>
            <div className="footer-social">
              <a href={tgLink(t)} target="_blank" rel="noopener">
                Telegram
              </a>
              <a href="#top">GitHub</a>
              <a href="#top">LinkedIn</a>
            </div>
          </div>
        </div>
        <div className="footer-cols">
          <div className="footer-col">
            <span className="footer-col-title">{t('servicesTitle')}</span>
            <a href="#services">{t('svc1Title')}</a>
            <a href="#services">{t('svc2Title')}</a>
            <a href="#services">{t('svc3Title')}</a>
            <a href="#services">{t('svc4Title')}</a>
          </div>
          <div className="footer-col">
            <span className="footer-col-title">{t('footCompany')}</span>
            <a href="#about">{t('aboutTitle')}</a>
            <a href="#stack">{t('stackTitle')}</a>
            <a href="#top">{t('footTop')}</a>
          </div>
          <div className="footer-col">
            <span className="footer-col-title">{t('footContact')}</span>
            <a href={tgLink(t)} target="_blank" rel="noopener">
              {t('ctaHeader')}
            </a>
            <span className="footer-note">{t('footReply')}</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
