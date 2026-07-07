import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import seed from '../../shared/seed_content.json'
import terminalSeed from '../../shared/seed_terminal.json'

export type Lang = 'ru' | 'en'
export type ContentMap = Record<
  string,
  { ru: string; en: string; label?: string; section?: string }
>
export type TermLine = { id?: number; position?: number; kind: string; ru: string; en: string }

export const defaults: ContentMap = seed as ContentMap
export const terminalDefaults: TermLine[] = terminalSeed as TermLine[]

export async function fetchTerminal(): Promise<TermLine[]> {
  const res = await fetch('/api/terminal')
  if (!res.ok) throw new Error(`API ${res.status}`)
  return res.json()
}

export async function fetchContent(): Promise<ContentMap> {
  const res = await fetch('/api/content')
  if (!res.ok) throw new Error(`API ${res.status}`)
  return res.json()
}

export function resolveTexts(remote: ContentMap | null): ContentMap {
  return remote && Object.keys(remote).length > 0 ? { ...defaults, ...remote } : defaults
}

type Ctx = {
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: string) => string
  texts: ContentMap
  terminal: TermLine[]
}

const ContentContext = createContext<Ctx | null>(null)

export function ContentProvider({ children }: { children: ReactNode }) {
  const [texts, setTexts] = useState<ContentMap>(defaults)
  const [terminal, setTerminal] = useState<TermLine[]>(terminalDefaults)
  const [lang, setLangState] = useState<Lang>(() =>
    localStorage.getItem('prodev_lang') === 'en' ? 'en' : 'ru',
  )

  useEffect(() => {
    fetchContent()
      .then((remote) => setTexts(resolveTexts(remote)))
      .catch(() => {})
    fetchTerminal()
      .then((lines) => {
        if (lines.length > 0) setTerminal(lines)
      })
      .catch(() => {})
  }, [])

  const setLang = (l: Lang) => {
    localStorage.setItem('prodev_lang', l)
    setLangState(l)
  }

  const t = (key: string) => texts[key]?.[lang] ?? defaults[key]?.[lang] ?? key

  return (
    <ContentContext.Provider value={{ lang, setLang, t, texts, terminal }}>
      {children}
    </ContentContext.Provider>
  )
}

export function useContent(): Ctx {
  const ctx = useContext(ContentContext)
  if (!ctx) throw new Error('useContent вне ContentProvider')
  return ctx
}
