const handleList = (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  let DaoCtor = null;
  try {
    // PocketBase exposes Dao as a module
    const mod = require("dao");
    DaoCtor = mod && mod.Dao ? mod.Dao : mod;
  } catch (_) {}

  try {
    const stationId = e.request.pathValue("id");
    if (!stationId) return fail(e, "station id required", 400);

    let station;
    try {
      station = $app.findRecordById("stations", String(stationId));
    } catch (_) {
      return fail(e, "station not found", 404);
    }

    const query = e.request.url.query();
    const fromRaw = query.get("from") || "";
    const toRaw = query.get("to") || "";
    const limit = Math.min(
      Math.max(parseInt(query.get("limit") || "72", 10), 1),
      500
    );

    let filter = `station="${station.id}"`;

    if (fromRaw) {
      const fromDate = new Date(fromRaw);
      if (Number.isNaN(fromDate.getTime()))
        return fail(e, "invalid from date", 400);
      filter += ` && target_time >= "${fromDate.toISOString()}"`;
    }

    if (toRaw) {
      const toDate = new Date(toRaw);
      if (Number.isNaN(toDate.getTime()))
        return fail(e, "invalid to date", 400);
      filter += ` && target_time <= "${toDate.toISOString()}"`;
    }

    const col = $app.findCollectionByNameOrId("station_forecasts");
    // PocketBase hook helpers: use findRecordsByFilter to avoid direct Dao dependency
    const items = $app.findRecordsByFilter(
      col.id,
      filter,
      "target_time",
      1,
      limit
    );

    return ok(e, {
      station: {
        id: station.id,
        name: station.getString("name"),
      },
      items: items.map((r) =>
        typeof r.exportDefault === "function" ? r.exportDefault() : r
      ),
      limit,
    });
  } catch (err) {
    return fail(e, err.message);
  }
};

routerAdd("GET", "/stations/{id}/forecasts", handleList);
routerAdd("GET", "/api/stations/{id}/forecasts", handleList);
