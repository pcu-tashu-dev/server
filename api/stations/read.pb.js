routerAdd("GET", "/stations/{id}", async (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  try {
    const id = e.request.pathValue("id");
    console.log("[stations/read] GET /stations/:id", id);

    try {
      const record = $app.findFirstRecordByData("stations", "id", id);
      const zoneRecord = $app.findFirstRecordByData(
        "daejeon_zones",
        "id",
        record.get("zone")
      );
      return ok(e, {
        station: record.publicExport(),
        zone: zoneRecord.publicExport(),
      });
    } catch (err) {
      console.log(String(err));
      return fail(e, "station not founded", 404);
    }
  } catch (err) {
    return fail(e, String(err), 500);
  }
});
