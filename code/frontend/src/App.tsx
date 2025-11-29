import { useEffect, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { fetchInitialDocument, connectSocket } from './api'

function App() {
  const [doc, setDoc] = useState('')
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    void fetchInitialDocument().then((text) => {
      setDoc(text)
    })

    const socket = connectSocket(setDoc)
    socketRef.current = socket

    return () => {
      socket.close()
    }
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
            onChange={(value) => {
              setDoc(value)
              if (socketRef.current?.readyState === WebSocket.OPEN) {
                socketRef.current.send(value)
              }
            }}
          />
        </div>
      </div>
    </main>
  )
}

export default App
