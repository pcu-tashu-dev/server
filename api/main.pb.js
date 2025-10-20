// server/api/main.pb.js
try {
  require(`${__hooks}/users/index.pb.js`);
  console.log("[load] users ok");
} catch (e) {
  console.log("[load] users failed:", e);
}

try {
  require(`${__hooks}/notifications/index.pb.js`);
  console.log("[load] notifications ok");
} catch (e) {
  console.log("[load] notifications failed:", e);
}

try {
  require(`${__hooks}/stations/index.pb.js`);
  console.log("[load] stations ok");
} catch (e) {
  console.log("[load] stations failed:", e);
}

(() => {
  console.log("🎉 Tashu-dev application fired!");
})();
