routerAdd("POST", "/tokens/ping", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  const { parse, requireFields } = require(`${__hooks}/lib/body.js`);
  try {
    if (!e.auth) return fail(e, "auth required", 401);
    const body = parse(e, { token: "" });
    requireFields(body, ["token"]);
    const col = $app.findCollectionByNameOrId("user_devices");
    const rec = $app.dao().findFirstRecordByData(col.id, "token", body.token);
    if (rec.get("user") !== e.auth.id) return fail(e, "forbidden", 403);
    rec.set("is_active", true);
    rec.set("last_seen", new Date().toISOString());
    $app.save(rec);
    return ok(e, { id: rec.id });
  } catch (err) {
    return fail(e, err.message);
  }
});
