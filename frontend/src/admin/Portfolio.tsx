import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

type Item = {
  id: number
  position: number
  title: string
  text: string
  image_path: string
  enabled: boolean
}

export function Portfolio({ onAuthLost }: { onAuthLost: () => void }) {
  const [items, setItems] = useState<Item[]>([])
  const [error, setError] = useState('')

  const load = async () => {
    const res = await fetch('/api/portfolio?all=1')
    if (res.status === 401) return onAuthLost()
    if (res.ok) setItems(await res.json())
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const patch = (id: number, p: Partial<Item>) =>
    setItems((list) => list.map((it) => (it.id === id ? { ...it, ...p } : it)))

  const save = async (item: Item, file: File | null) => {
    setError('')
    const fd = new FormData()
    fd.set('title', item.title)
    fd.set('text', item.text)
    fd.set('position', String(item.position))
    fd.set('enabled', item.enabled ? '1' : '0')
    if (file) fd.set('image', file)
    const res = await fetch(`/api/portfolio/${item.id}`, { method: 'PUT', body: fd })
    if (res.status === 401) return onAuthLost()
    if (res.ok) load()
    else setError('Не удалось сохранить карточку')
  }

  const remove = async (id: number) => {
    setError('')
    const res = await fetch(`/api/portfolio/${id}`, { method: 'DELETE' })
    if (res.status === 401) return onAuthLost()
    if (res.ok) load()
  }

  const add = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    const form = e.currentTarget
    const res = await fetch('/api/portfolio', { method: 'POST', body: new FormData(form) })
    if (res.status === 401) return onAuthLost()
    if (res.ok) {
      form.reset()
      load()
    } else {
      setError('Не удалось добавить карточку')
    }
  }

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {items.length === 0 && !error && (
        <p className="admin-hint">Карточек пока нет. Добавьте первую ниже.</p>
      )}
      {items.map((item) => (
        <div className="admin-card" key={item.id}>
          <img src={item.image_path} alt="" />
          <div className="admin-card-fields">
            <input
              value={item.title}
              placeholder="Заголовок"
              onChange={(e) => patch(item.id, { title: e.target.value })}
            />
            <textarea
              rows={3}
              value={item.text}
              placeholder="Описание"
              onChange={(e) => patch(item.id, { text: e.target.value })}
            />
            <label>
              Порядок:
              <input
                type="number"
                value={item.position}
                onChange={(e) => patch(item.id, { position: Number(e.target.value) })}
              />
            </label>
            <label>
              <input
                type="checkbox"
                checked={item.enabled}
                onChange={(e) => patch(item.id, { enabled: e.target.checked })}
              />
              Показывать в боте
            </label>
            <label>
              Заменить картинку:
              <input type="file" accept=".png,.jpg,.jpeg,.webp" id={`file-${item.id}`} />
            </label>
            <div className="admin-term-actions">
              <button
                onClick={() => {
                  const el = document.getElementById(`file-${item.id}`) as HTMLInputElement
                  save(item, el?.files?.[0] ?? null)
                }}
              >
                Сохранить
              </button>
              <button className="admin-danger" onClick={() => remove(item.id)}>
                Удалить
              </button>
            </div>
          </div>
        </div>
      ))}

      <h2>Новая карточка</h2>
      <form className="admin-card-form" onSubmit={add}>
        <input name="title" placeholder="Заголовок" />
        <textarea name="text" rows={3} placeholder="Описание" />
        <label>
          Порядок:
          <input name="position" type="number" defaultValue={10} />
        </label>
        <input name="image" type="file" accept=".png,.jpg,.jpeg,.webp" required />
        <button type="submit">Добавить карточку</button>
      </form>
    </div>
  )
}
