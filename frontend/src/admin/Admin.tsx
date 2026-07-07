import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { fetchContent } from '../content'
import type { ContentMap } from '../content'

type RowState = { ru: string; en: string; status: 'idle' | 'saving' | 'saved' | 'error' }

function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    })
    if (res.ok) onSuccess()
    else setError(res.status === 401 ? 'Неверный пароль' : 'Ошибка сервера, попробуйте ещё раз')
  }

  return (
    <form className="admin-login" onSubmit={submit}>
      <h1>Админка</h1>
      <input
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        autoFocus
      />
      <button type="submit">Войти</button>
      {error && <span className="admin-error">{error}</span>}
    </form>
  )
}

export function Admin() {
  const [authed, setAuthed] = useState<boolean | null>(null)
  const [texts, setTexts] = useState<ContentMap>({})
  const [rows, setRows] = useState<Record<string, RowState>>({})

  useEffect(() => {
    fetch('/api/auth/me').then((r) => setAuthed(r.ok))
  }, [])

  useEffect(() => {
    if (!authed) return
    fetchContent().then((data) => {
      setTexts(data)
      const init: Record<string, RowState> = {}
      for (const [key, v] of Object.entries(data)) {
        init[key] = { ru: v.ru, en: v.en, status: 'idle' }
      }
      setRows(init)
    })
  }, [authed])

  if (authed === null) return null
  if (!authed) return <LoginForm onSuccess={() => setAuthed(true)} />

  const setRow = (key: string, patch: Partial<RowState>) =>
    setRows((r) => ({ ...r, [key]: { ...r[key], ...patch } }))

  const save = async (key: string) => {
    setRow(key, { status: 'saving' })
    const { ru, en } = rows[key]
    const res = await fetch(`/api/content/${key}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ru, en }),
    })
    if (res.status === 401) {
      setAuthed(false)
      return
    }
    setRow(key, { status: res.ok ? 'saved' : 'error' })
  }

  const sections = new Map<string, string[]>()
  for (const [key, v] of Object.entries(texts)) {
    const s = v.section ?? ''
    if (!sections.has(s)) sections.set(s, [])
    sections.get(s)!.push(key)
  }

  return (
    <div className="admin">
      <h1>Тексты лендинга</h1>
      {[...sections.entries()].map(([section, keys]) => (
        <section key={section}>
          <h2>{section}</h2>
          {keys.map((key) => {
            const row = rows[key]
            if (!row) return null
            return (
              <div className="admin-row" key={key}>
                <div className="admin-label">
                  {texts[key].label}
                  <span className="admin-key">{key}</span>
                </div>
                <textarea
                  rows={2}
                  value={row.ru}
                  onChange={(e) => setRow(key, { ru: e.target.value, status: 'idle' })}
                />
                <textarea
                  rows={2}
                  value={row.en}
                  onChange={(e) => setRow(key, { en: e.target.value, status: 'idle' })}
                />
                <div>
                  <button onClick={() => save(key)} disabled={row.status === 'saving'}>
                    {row.status === 'saving' ? 'Сохраняю…' : 'Сохранить'}
                  </button>
                  {row.status === 'saved' && <div className="admin-saved">Сохранено</div>}
                  {row.status === 'error' && (
                    <div className="admin-error">Ошибка сохранения</div>
                  )}
                </div>
              </div>
            )
          })}
        </section>
      ))}
    </div>
  )
}
