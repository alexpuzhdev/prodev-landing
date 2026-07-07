import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ContentProvider } from './content'
import { Landing } from './sections/Landing'

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
