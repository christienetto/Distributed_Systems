export const fetchInitialDocument = async () => {
  // todo: replace with a real GET request to server
  await new Promise((resolve) => setTimeout(resolve, 1000))
  return 'Initial document text from server'
}

export const connectSocket = (onMessage: (value: string) => void) => {
  const socket = new WebSocket('ws://127.0.0.1:800') // todo: replace with real server URL

  socket.addEventListener('message', (event) => {
    onMessage(String(event.data ?? ''))
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
