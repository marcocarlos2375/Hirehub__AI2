export const useVoiceRecorder = () => {
  const isRecording = ref(false)
  const isPaused = ref(false)
  const recordingTime = ref(0)
  const audioBlob = ref<Blob | null>(null)

  let mediaRecorder: MediaRecorder | null = null
  let audioChunks: Blob[] = []
  let timerInterval: ReturnType<typeof setInterval> | null = null

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      // Create MediaRecorder
      mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      audioChunks = []

      // Handle data available event
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data)
        }
      }

      // Handle stop event
      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' })
        audioBlob.value = blob

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      // Start recording
      mediaRecorder.start()
      isRecording.value = true
      isPaused.value = false
      recordingTime.value = 0

      // Start timer
      timerInterval = setInterval(() => {
        if (!isPaused.value) {
          recordingTime.value += 1
        }
      }, 1000)
    } catch (error) {
      console.error('Error starting recording:', error)
      throw new Error('Failed to access microphone. Please grant permission.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
      isRecording.value = false
      isPaused.value = false

      if (timerInterval) {
        clearInterval(timerInterval)
        timerInterval = null
      }
    }
  }

  const pauseRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.pause()
      isPaused.value = true
    }
  }

  const resumeRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'paused') {
      mediaRecorder.resume()
      isPaused.value = false
    }
  }

  const cancelRecording = () => {
    stopRecording()
    audioChunks = []
    audioBlob.value = null
    recordingTime.value = 0
  }

  const reset = () => {
    audioChunks = []
    audioBlob.value = null
    recordingTime.value = 0
    isRecording.value = false
    isPaused.value = false
  }

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // Cleanup on unmount
  onUnmounted(() => {
    if (timerInterval) {
      clearInterval(timerInterval)
    }
    if (mediaRecorder) {
      stopRecording()
    }
  })

  return {
    isRecording: readonly(isRecording),
    isPaused: readonly(isPaused),
    recordingTime: readonly(recordingTime),
    audioBlob: readonly(audioBlob),
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    cancelRecording,
    reset,
    formatTime
  }
}
