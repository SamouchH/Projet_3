import { ImageLabeler } from './components/ImageLabeler/ImageLabeler'

function App() {
  return (
    <div className="w-full h-full bg-gray-100">
      <header className="bg-white shadow w-full">
        <div className="w-full py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Image Labeler
          </h1>
        </div>
      </header>
      <main className="w-full p-6">
        <ImageLabeler />
      </main>
    </div>
  )
}

export default App
