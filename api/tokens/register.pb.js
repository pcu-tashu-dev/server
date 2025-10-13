routerAdd("POST", "/tokens/register", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  const { parse, requireFields } = require(`${__hooks}/lib/body.js`);
  try {
    if (!e.auth) return fail(e, "auth required", 401);
    const body = parse(e, {
      token: "",
      platform: "",
      provider: "fcm",
      app_version: "",
      locale: "",
    });
    requireFields(body, ["token", "platform", "provider"]);

    const col = $app.findCollectionByNameOrId("user_devices");
    let rec = null;
    try {
      rec = $app.dao().findFirstRecordByData(col.id, "token", body.token);
    } catch (_) {}

    if (rec) {
      if (rec.get("user") !== e.auth.id)
        return fail(e, "token already bound to another user", 409);
    } else {
      rec = new Record(col);
      rec.set("token", body.token);
    }

    rec.set("user", e.auth.id);
    rec.set("platform", body.platform);
    rec.set("provider", body.provider || "fcm");
    rec.set("app_version", body.app_version || "");
    rec.set("locale", body.locale || "");
    rec.set("is_active", true);
    rec.set("last_seen", new Date().toISOString());
    $app.save(rec);

    return ok(e, { id: rec.id });
  } catch (err) {
    return fail(e, err.message);
  }
});
