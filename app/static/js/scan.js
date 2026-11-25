(() => {
  'use strict';
  const root = document.getElementById('smartScan');
  if (!root) return;
  const get = id => document.getElementById(id);
  const form = get('scanForm'), status = get('scanStatus'), video = get('scanVideo');
  let selected = null, stream = null, previewUrl = null, generation = 0, busy = false;
  function stopCamera() {
    generation++;
    if (stream) stream.getTracks().forEach(track => track.stop());
    stream = null; if (video) video.srcObject = null;
    const c = get('scanCamera'); if (c) c.hidden = true;
  }
  async function select(file) {
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || !file.size || file.size > 8 * 1024 * 1024) {
      status.textContent = 'Selecciona JPEG, PNG o WebP de hasta 8 MB.'; return;
    }
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      previewUrl = url; selected = file;
      get('scanPreview').src = url; get('scanPreview').hidden = false;
      status.textContent = `${file.name} seleccionada. Lista para analizar.`;
    };
    image.onerror = () => { URL.revokeObjectURL(url); status.textContent = 'El archivo no contiene una imagen legible.'; };
    image.src = url;
  }
  get('scanLibrary')?.addEventListener('change', event => select(event.target.files[0]));
  get('scanCapture')?.addEventListener('change', event => select(event.target.files[0]));
  const camera = get('scanOpenCamera');
  if (camera) {
    camera.hidden = false;
    camera.addEventListener('click', async () => {
      if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
        status.textContent = 'La cámara del navegador requiere HTTPS y soporte getUserMedia.'; return;
      }
      stopCamera(); const current = generation;
      try {
        const acquired = await navigator.mediaDevices.getUserMedia({video: {facingMode: {ideal: 'environment'}}, audio: false});
        if (current !== generation || document.hidden) { acquired.getTracks().forEach(track => track.stop()); return; }
        stream = acquired; video.srcObject = stream; get('scanCamera').hidden = false; await video.play();
        status.textContent = 'Cámara activa. Captura cuando estés listo.';
      } catch (_) { stopCamera(); status.textContent = 'No se pudo abrir la cámara.'; }
    });
  }
  get('scanCloseCamera')?.addEventListener('click', stopCamera);
  get('scanTake')?.addEventListener('click', () => {
    if (!video.videoWidth || !video.videoHeight) { status.textContent = 'Espera a que la cámara muestre una imagen.'; return; }
    const canvas = document.createElement('canvas');
    const scale = Math.min(1, 2048 / Math.max(video.videoWidth, video.videoHeight));
    canvas.width = Math.round(video.videoWidth * scale); canvas.height = Math.round(video.videoHeight * scale);
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
      if (blob) select(new File([blob], 'smartscan.jpg', {type: 'image/jpeg'}));
      else status.textContent = 'No se pudo capturar la foto.';
    }, 'image/jpeg', 0.9);
    stopCamera();
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopCamera(); });
  window.addEventListener('pagehide', stopCamera);
  if (form) form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy) return;
    if (!selected) { status.textContent = 'Selecciona una imagen legible antes de analizar.'; return; }
    const body = new FormData(form); body.set('photo', selected);
    busy = true; get('scanSubmit').disabled = true; status.textContent = 'Analizando…';
    try {
      const response = await fetch(form.action || location.href, {method: 'POST', body, credentials: 'same-origin', headers: {'Accept': 'application/json'}});
      const data = await response.json();
      if (!response.ok || data.success !== true) throw new Error(data.error || 'No se completó el análisis.');
      const result = get('scanResult');
      if (data.html && result) {
        const parsed = new DOMParser().parseFromString(data.html, 'text/html');
        result.replaceChildren(...parsed.body.childNodes);
      }
      status.textContent = 'Análisis completado.';
    } catch (error) { status.textContent = error.message; }
    finally { busy = false; get('scanSubmit').disabled = false; }
  });
})();
