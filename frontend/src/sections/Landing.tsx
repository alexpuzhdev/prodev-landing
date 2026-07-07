import { About } from './About'
import { Cta } from './Cta'
import { Footer } from './Footer'
import { Header } from './Header'
import { Hero } from './Hero'
import { ScrollSquare } from './ScrollSquare'
import { Services } from './Services'
import { Stack } from './Stack'
import { Terminal } from './Terminal'

export function Landing() {
  return (
    <div id="top">
      <ScrollSquare />
      <Header />
      <Hero />
      <Terminal />
      <About />
      <Services />
      <Stack />
      <Cta />
      <Footer />
    </div>
  )
}
