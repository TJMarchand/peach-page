self.addEventListener("install", function (e) {
  console.log("Service Worker installed");
});

self.addEventListener("fetch", function (e) {
  console.log("Fetching: ", e.request.url);
});
