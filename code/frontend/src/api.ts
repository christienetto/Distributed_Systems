export const fetchInitialDocument = async () => {
  const response = await fetch("http://127.0.0.1:8000/test-db")
  const data = await response.json()
  
  if (data.note) {
    return `Title: ${data.note.title}\nContent: ${data.note.content}`;
  }

  return ""
}

export const connectSocket = (onMessage: (value: string) => void) => {
  const socket = new WebSocket('ws://localhost:8000/ws') 

  socket.addEventListener('message', (event) => {
    try {
      const msg = JSON.parse(event.data);

      if (msg.note) {
        const text = `Title: ${msg.note.title}\nContent:\n${msg.note.content}`
        onMessage(text);
      }
    } catch (err) {
      console.error("Invalid JSON message:", event.data);
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
