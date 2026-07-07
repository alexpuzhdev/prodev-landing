import { useEffect, useState } from 'react'

type Lead = {
  id: number
  username: string
  name: string
  task: string
  project_type: string
  timeline: string
  status: 'new' | 'done'
  created_at: string
}

const TYPE_LABELS: Record<string, string> = {
  mvp: 'MVP',
  landing: 'Лендинг',
  webapp: 'Веб-приложение',
  support: 'Поддержка',
}

export function Leads({ onAuthLost }: { onAuthLost: () => void }) {
  const [leads, setLeads] = useState<Lead[]>([])
  const [error, setError] = useState('')

  const load = async () => {
    const res = await fetch('/api/leads')
    if (res.status === 401) return onAuthLost()
    if (res.ok) setLeads(await res.json())
    else setError('Не удалось загрузить заявки')
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const toggle = async (lead: Lead) => {
    const res = await fetch(`/api/leads/${lead.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: lead.status === 'new' ? 'done' : 'new' }),
    })
    if (res.status === 401) return onAuthLost()
    if (res.ok) load()
  }

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {leads.length === 0 && !error && <p className="admin-hint">Заявок пока нет.</p>}
      {leads.map((lead) => (
        <div className={'admin-lead' + (lead.status === 'done' ? ' done' : '')} key={lead.id}>
          <div className="admin-lead-head">
            <b>{lead.name || 'Без имени'}</b>
            {lead.username && (
              <a href={`https://t.me/${lead.username}`} target="_blank" rel="noopener">
                @{lead.username}
              </a>
            )}
            <span>{TYPE_LABELS[lead.project_type] ?? lead.project_type}</span>
            <span>{new Date(lead.created_at).toLocaleString('ru-RU')}</span>
            <button onClick={() => toggle(lead)}>
              {lead.status === 'new' ? 'Обработана' : 'Вернуть в новые'}
            </button>
          </div>
          <p>{lead.task}</p>
          <p className="admin-hint">Сроки: {lead.timeline}</p>
        </div>
      ))}
    </div>
  )
}
