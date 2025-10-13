routerAdd("GET", "/notifications", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  try {
    if (!e.auth) return fail(e, "auth required", 401);

    const userId = e.auth.id;
    const page = parseInt(e.queryParam("page") || "1", 10);
    const perPage = Math.min(
      parseInt(e.queryParam("perPage") || "20", 10),
      100
    );
    const unread = (e.queryParam("unread") || "false") === "true";

    const filter = `user="${userId}" ${unread ? "&& read = false" : ""}`;
    const items = $app
      .dao()
      .findRecordsByFilter("notifications", filter, "-created", page, perPage);
    const total = $app.dao().countRecordsByFilter("notifications", filter);

    return ok(e, {
      items: items.map((r) => r.exportDefault()),
      page,
      perPage,
      total,
    });
  } catch (err) {
    return fail(e, err.message);
  }
});
