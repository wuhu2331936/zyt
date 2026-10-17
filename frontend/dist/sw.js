self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (event) {
  event.waitUntil((async function () {
    try { var k = await caches.keys(); await Promise.all(k.map(function (x) { return caches.delete(x); })); } catch (e) {}
    try { await self.registration.unregister(); } catch (e) {}
  })());
});
