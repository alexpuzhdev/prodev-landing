import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Admin } from './admin/Admin'
import { ContentProvider } from './content'
import { Landing } from './sections/Landing'

export default function App() {
  return (
    <BrowserRouter>
      <ContentProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </ContentProvider>
    </BrowserRouter>
  )
}
