import { Header } from './Header'
import { Hero } from './Hero'
import { ScrollSquare } from './ScrollSquare'
import { Terminal } from './Terminal'

export function Landing() {
  return (
    <div id="top">
      <ScrollSquare />
      <Header />
      <Hero />
      <Terminal />
    </div>
  )
}
