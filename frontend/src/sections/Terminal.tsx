import { useEffect, useMemo, useRef, useState } from 'react'
import type { ReactElement } from 'react'
import { useContent } from '../content'

type Line = { type: 'cmd' | 'ok' | 'info'; text: string }

const STATUS_COST = 12
const LOOP_PAUSE = 90
const TICK_MS = 45

export function terminalLines(t: (k: string) => string): Line[] {
  return [
    { type: 'cmd', text: 'git clone your-idea && cd your-idea' },
    { type: 'ok', text: t('termScope') },
    { type: 'cmd', text: 'npm run build' },
    { type: 'ok', text: t('termStack1') },
    { type: 'ok', text: t('termStack2') },
    { type: 'ok', text: t('termTests') },
    { type: 'cmd', text: 'npm run deploy --production' },
    { type: 'info', text: t('termDeploying') },
    { type: 'ok', text: t('termLive') },
  ]
}

function totalSteps(lines: Line[]): number {
  return lines.reduce((n, l) => n + (l.type === 'cmd' ? l.text.length : STATUS_COST), 0)
}

export function Terminal() {
  const { t, lang } = useContent()
  const [step, setStep] = useState(0)
  const bodyRef = useRef<HTMLDivElement>(null)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const lines = useMemo(() => terminalLines(t), [t, lang])
  const total = useMemo(() => totalSteps(lines), [lines])

  useEffect(() => {
    const id = setInterval(
      () => setStep((s) => (s >= total + LOOP_PAUSE ? 0 : s + 1)),
      TICK_MS,
    )
    return () => clearInterval(id)
  }, [total])

  const rows: ReactElement[] = []
  let consumed = 0
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const cost = line.type === 'cmd' ? line.text.length : STATUS_COST
    if (step <= consumed) break
    const avail = step - consumed
    const isLast = avail < cost
    if (line.type === 'cmd') {
      const txt = isLast ? line.text.slice(0, avail) : line.text
      rows.push(
        <div key={i}>
          <span className="t-prompt">$ </span>
          <span className="t-cmd">{txt}</span>
        </div>,
      )
    } else if (isLast) {
      break
    } else {
      rows.push(
        <div key={i}>
          <span className={`t-${line.type}`}>{'  ' + (line.type === 'ok' ? '✓ ' : '→ ')}</span>
          <span className="t-text">{line.text}</span>
        </div>,
      )
    }
    if (isLast) break
    consumed += cost
  }
  const blinkOn = Math.floor(step / 10) % 2 === 0

  useEffect(() => {
    const el = bodyRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [step])

  return (
    <section className="terminal-section">
      <div className="terminal">
        <div className="terminal-bar">
          <span className="light"></span>
          <span className="light"></span>
          <span className="light light-accent"></span>
          <span className="terminal-title">{t('termTitle')}</span>
        </div>
        <div className="terminal-body" aria-hidden="true" ref={bodyRef}>
          {rows}
          <span className={'terminal-cursor' + (blinkOn ? '' : ' off')}></span>
        </div>
      </div>
    </section>
  )
}
