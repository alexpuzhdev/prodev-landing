import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ContentProvider, useContent } from './content'

function Landing() {
  const { t } = useContent()
  return <h1>{t('heroTitle')}</h1>
}

export default function App() {
  return (
    <BrowserRouter>
      <ContentProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
        </Routes>
      </ContentProvider>
    </BrowserRouter>
  )
}
