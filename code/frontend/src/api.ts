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

      if (msg.type === 'init' && msg.notes) {
        const text = msg.notes
          .map((n: any) => `Title: ${n.title}\nContent: ${n.content}`)
          .join("\n\n");
        onMessage(text);
      } else if (msg.type === 'text_change') {
        onMessage(msg.content);
      } else if (msg.type === 'note_saved') {
        const text = `Title: ${msg.note.title}\nContent: ${msg.note.content}`;
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
