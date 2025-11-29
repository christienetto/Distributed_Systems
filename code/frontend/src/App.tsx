import { useEffect, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'

const fetchInitialDocument = async () => {
  // todo: replace with a real GET request to server
  await new Promise((resolve) => setTimeout(resolve, 1000))
  return 'Initial document text from server'
}

function App() {
  const [doc, setDoc] = useState('')

  useEffect(() => {
    void fetchInitialDocument().then((text) => {
      setDoc(text)
    })
  }, [])

  return (
    <main className="min-h-screen bg-stone-900 text-white flex justify-center py-52">
      <div className="w-full max-w-2xl space-y-4 px-6">
        <h1 className="text-2xl font-semibold">Type something below</h1>
        <div className="border border-white/10 rounded-md overflow-hidden shadow-lg">
          <CodeMirror
            height="320px"
            value={doc}
            className="text-black"
            basicSetup={{
              lineNumbers: false,
              highlightActiveLine: false,
              highlightActiveLineGutter: false,
              foldGutter: false,
            }}
          />
        </div>
      </div>
    </main>
  )
}

export default App
