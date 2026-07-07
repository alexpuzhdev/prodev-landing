import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { fetchContent, fetchTerminal } from '../content'
import type { ContentMap, TermLine } from '../content'

type Status = 'idle' | 'saving' | 'saved' | 'error'
type RowState = { ru: string; en: string; status: Status }
type TermRow = { id: number; kind: string; ru: string; en: string; status: Status }

const KIND_LABELS: Record<string, string> = {
  cmd: 'команда',
  ok: 'успех',
  info: 'процесс',
}

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
  const [termRows, setTermRows] = useState<TermRow[]>([])
  const [termError, setTermError] = useState('')

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
    fetchTerminal().then((lines: TermLine[]) => {
      setTermRows(
        lines.map((l) => ({ id: l.id ?? 0, kind: l.kind, ru: l.ru, en: l.en, status: 'idle' })),
      )
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

  const setTermRow = (id: number, patch: Partial<TermRow>) =>
    setTermRows((list) => list.map((r) => (r.id === id ? { ...r, ...patch } : r)))

  const saveTermRow = async (id: number) => {
    const row = termRows.find((r) => r.id === id)
    if (!row) return
    setTermRow(id, { status: 'saving' })
    const res = await fetch(`/api/terminal/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kind: row.kind, ru: row.ru, en: row.en }),
    })
    if (res.status === 401) {
      setAuthed(false)
      return
    }
    setTermRow(id, { status: res.ok ? 'saved' : 'error' })
  }

  const deleteTermRow = async (id: number) => {
    setTermError('')
    const res = await fetch(`/api/terminal/${id}`, { method: 'DELETE' })
    if (res.status === 401) {
      setAuthed(false)
      return
    }
    if (res.ok) setTermRows((list) => list.filter((r) => r.id !== id))
    else setTermError('Не удалось удалить строку')
  }

  const addTermRow = async () => {
    setTermError('')
    const res = await fetch('/api/terminal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kind: 'ok', ru: '', en: '' }),
    })
    if (res.status === 401) {
      setAuthed(false)
      return
    }
    if (res.ok) {
      const line: TermLine = await res.json()
      setTermRows((list) => [
        ...list,
        { id: line.id ?? 0, kind: line.kind, ru: line.ru, en: line.en, status: 'idle' },
      ])
    } else {
      setTermError('Не удалось добавить строку')
    }
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

      <section>
        <h2>Терминал: сценарий</h2>
        <p className="admin-hint">
          Строки печатаются по порядку. Тип "команда" выводится с $, "успех" с галочкой,
          "процесс" со стрелкой.
        </p>
        {termRows.map((row) => (
          <div className="admin-row admin-row-term" key={row.id}>
            <select
              value={row.kind}
              onChange={(e) => setTermRow(row.id, { kind: e.target.value, status: 'idle' })}
            >
              {Object.entries(KIND_LABELS).map(([kind, label]) => (
                <option key={kind} value={kind}>
                  {label}
                </option>
              ))}
            </select>
            <textarea
              rows={1}
              value={row.ru}
              onChange={(e) => setTermRow(row.id, { ru: e.target.value, status: 'idle' })}
            />
            <textarea
              rows={1}
              value={row.en}
              onChange={(e) => setTermRow(row.id, { en: e.target.value, status: 'idle' })}
            />
            <div className="admin-term-actions">
              <button onClick={() => saveTermRow(row.id)} disabled={row.status === 'saving'}>
                {row.status === 'saving' ? 'Сохраняю…' : 'Сохранить'}
              </button>
              <button className="admin-danger" onClick={() => deleteTermRow(row.id)}>
                Удалить
              </button>
              {row.status === 'saved' && <div className="admin-saved">Сохранено</div>}
              {row.status === 'error' && <div className="admin-error">Ошибка сохранения</div>}
            </div>
          </div>
        ))}
        <button className="admin-add" onClick={addTermRow}>
          Добавить строку
        </button>
        {termError && <div className="admin-error">{termError}</div>}
      </section>
    </div>
  )
}
