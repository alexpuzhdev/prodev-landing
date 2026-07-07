import { useEffect, useRef } from 'react'

export function ScrollSquare() {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduceMotion) return
    const onScroll = () => {
      const el = ref.current
      if (!el) return
      const doc = document.documentElement
      const max = Math.max(1, doc.scrollHeight - window.innerHeight)
      const p = Math.min(1, Math.max(0, window.scrollY / max))
      el.style.transform = `rotate(${p * 540}deg)`
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return <div ref={ref} className="scroll-square" aria-hidden="true"></div>
}
