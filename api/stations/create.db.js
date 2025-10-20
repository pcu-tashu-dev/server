routerAdd("POST", "/stations", async (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  try {
    if (!e.admin) return fail(e, "admin only", 403);
    const body = await e.request.json();

    const dzCol = $app.findCollectionByNameOrId("daejeon_zones");
    const zones = $app
      .dao()
      .findRecordsByExpr(dzCol.id, $app.dao().expr(null), 0, 0);

    function zoneFor(lat, lon) {
      for (const z of zones) {
        const min_lat = Number(z.get("min_lat"));
        const max_lat = Number(z.get("max_lat"));
        const min_lon = Number(z.get("min_lon"));
        const max_lon = Number(z.get("max_lon"));
        const eps = 1e-9;
        if (
          lat >= min_lat - eps &&
          lat <= max_lat + eps &&
          lon >= min_lon - eps &&
          lon <= max_lon + eps
        )
          return z.id;
      }
      return null;
    }

    const zId = zoneFor(Number(body.lat), Number(body.lon));
    if (!zId) return fail(e, "no matching zone for given lat/lon", 400);

    const col = $app.findCollectionByNameOrId("stations");
    const rec = new Record(col);
    rec.set("id", String(body.id));
    rec.set("name", String(body.name));
    rec.set("lat", Number(body.lat));
    rec.set("lon", Number(body.lon));
    rec.set("address", String(body.address || ""));
    rec.set("zone", [zId]);
    $app.save(rec);

    return ok(e, { id: rec.id, zone: zId });
  } catch (err) {
    return fail(e, String(err), 500);
  }
});
