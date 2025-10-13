routerAdd("POST", "/notifications/:id/read", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  try {
    if (!e.auth) return fail(e, "auth required", 401);

    const id = e.request.pathParam("id");
    const rec = $app.findRecordById("notifications", id);

    if (rec.get("user") !== e.auth.id) return fail(e, "forbidden", 403);

    rec.set("read", true);
    $app.save(rec);

    return ok(e, { id: rec.id, read: true });
  } catch (err) {
    return fail(e, err.message);
  }
});
