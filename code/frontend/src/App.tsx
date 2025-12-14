import { useEffect, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { connectSocket } from './api'

function App() {
  const [doc, setDoc] = useState('')
  const socketRef = useRef<WebSocket | null>(null)
  const [isUpdatingFromSocket, setIsUpdatingFromSocket] = useState(false)

  const saveTimeoutRef = useRef<number | null>(null)

  useEffect(() => {
    const socket = connectSocket((newContent) => {
      setIsUpdatingFromSocket(true)
      setDoc(newContent)
      setTimeout(() => setIsUpdatingFromSocket(false), 0)
    })
    
    socketRef.current = socket

    return () => {
      socket.close()
    }
  }, [])



  return (
    <main className="min-h-screen bg-stone-900 text-white flex justify-center py-52">
      <div className="w-full max-w-2xl space-y-4 px-6">
        <div className="flex justify-center items-center">
          <h1 className="text-2xl font-semibold">Collaborative Editor</h1>
        </div>
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
              if (!isUpdatingFromSocket) {
                setDoc(value)
                if (socketRef.current?.readyState === WebSocket.OPEN) {
                  socketRef.current.send(JSON.stringify({
                    type: 'text_change',
                    content: value
                  }))
                  
                  if (saveTimeoutRef.current) {
                    clearTimeout(saveTimeoutRef.current)
                  }
                  saveTimeoutRef.current = setTimeout(() => {
                    if (socketRef.current?.readyState === WebSocket.OPEN) {
                      socketRef.current.send(JSON.stringify({
                        type: 'save_note',
                        title: 'Shared Document',
                        content: value
                      }))
                    }
                  }, 2000)
                }
              }
            }}
          />
        </div>

      </div>
    </main>
  )
}

export default App
