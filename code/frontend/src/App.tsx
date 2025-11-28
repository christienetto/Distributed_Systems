import { useEffect, useRef } from 'react'
import { EditorView, basicSetup } from 'codemirror'

function App() {
  const editorRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!editorRef.current) return

    const view = new EditorView({
      parent: editorRef.current,
      doc: '...',
      extensions: [
        basicSetup,
        EditorView.theme({
          '&': { height: '320px' },
        }),
      ],
    })

    return () => view.destroy()
  }, [])

  return (
    <main className="min-h-screen bg-neutral-900 text-white flex justify-center py-52">
      <div className="w-full max-w-2xl space-y-4 px-6">
        <h1 className="text-2xl font-semibold">Type something below</h1>
        <div className="border border-white/10 rounded-md overflow-hidden shadow-lg">
          <div ref={editorRef} className="bg-white text-black" />
        </div>
      </div>
    </main>
  )
}

export default App
