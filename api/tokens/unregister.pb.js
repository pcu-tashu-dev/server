routerAdd("POST", "/tokens/unregister", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  const { parse, requireFields } = require(`${__hooks}/lib/body.js`);
  try {
    if (!e.auth) return fail(e, "auth required", 401);
    const body = parse(e, { token: "" });
    requireFields(body, ["token"]);

    const col = $app.findCollectionByNameOrId("user_devices");
    const rec = $app.dao().findFirstRecordByData(col.id, "token", body.token);
    if (rec.get("user") !== e.auth.id) return fail(e, "forbidden", 403);

    $app.dao().deleteRecord(rec);
    return ok(e, { ok: true });
  } catch (err) {
    return fail(e, err.message);
  }
});
