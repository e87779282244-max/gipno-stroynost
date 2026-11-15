// Гипно-стройность: офлайн-кэш. Сначала сеть (чтобы обновления приходили), без сети — из кэша.
const C='gipno-v1';
const FILES=['./','index.html','manifest.json','media/squat.jpg','media/pushup.jpg','media/plank.jpg','media/lunge.jpg','media/crunch.jpg','media/bottle.jpg','media/icon-180.png','media/icon-192.png','media/icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=='GET'||u.origin!==location.origin)return;
  e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r}).catch(()=>caches.match(e.request,{ignoreSearch:true}).then(r=>r||caches.match('index.html'))));
});
