const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? window.location.origin
const wsBaseUrl = import.meta.env.VITE_WS_BASE ?? `ws//${window.location.host}`

export const fetchInitialDocument = async () => {
  const response = await fetch(`${apiBaseUrl}/test-db`)
  const data = await response.json()

  if (data.note) {
    return data.note.content
  }

  return ''
}

export const connectSocket = (onMessage: (value: string) => void) => {
  const socket = new WebSocket(`${wsBaseUrl}/ws`)

  socket.addEventListener('message', (event) => {
    try {
      const msg = JSON.parse(event.data)

      if (msg.type === 'init' && msg.note) {
        onMessage(msg.note.content)
      } else if (msg.type === 'text_change') {
        onMessage(msg.content)
      } else if (msg.type === 'db_change') {
        onMessage(msg.note.content)
        console.log(`Database ${msg.operation} detected`)
      }
    } catch (err) {
      console.error('Invalid JSON message:', event.data)
      console.error(err)
    }
  })

  socket.addEventListener('open', () => {
    console.log('WebSocket connected')
  })

  socket.addEventListener('close', () => {
    console.log('WebSocket closed')
  })

  socket.addEventListener('error', (err) => {
    console.error('WebSocket error', err)
  })

  return socket
}
