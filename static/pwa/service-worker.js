const CACHE_NAME = "heartnote-v2";

const STATIC_ASSETS = [
    "/",
    "/dashboard/",
    "/static/pwa/manifest.json"
];

// INSTALL
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

// ACTIVATE (important for updates)
self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.map(key => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            )
        )
    );
    self.clients.claim();
});

// FETCH
self.addEventListener("fetch", event => {
    if (!event.request.url.includes("/api/")) {
        event.respondWith(
            caches.match(event.request).then(res => {
                return res || fetch(event.request).catch(() => {
                    return caches.match("/");
                });
            })
        );
    }
});
