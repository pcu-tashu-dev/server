routerAdd("POST", "/notifications", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  const { parse, requireFields } = require(`${__hooks}/lib/body.js`);

  try {
    if (!e.admin) return fail(e, "admin only", 403);

    const body = parse(e, {
      userId: "",
      title: "",
      body: "",
      type: "info",
      data: {},
    });
    requireFields(body, ["userId", "title", "body"]);

    const col = $app.findCollectionByNameOrId("notifications");
    const rec = new Record(col);
    rec.set("user", body.userId);
    rec.set("title", body.title);
    rec.set("body", body.body);
    rec.set("type", body.type || "info");
    rec.set("data", body.data || {});
    rec.set("read", false);

    $app.save(rec);
    return ok(e, { id: rec.id });
  } catch (err) {
    return fail(e, err.message);
  }
});
