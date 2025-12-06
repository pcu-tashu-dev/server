migrate(
  (app) => {
    try {
      const col = app.findCollectionByNameOrId("station_forecasts");
      col.createRule = "";
      col.updateRule = "";
      col.deleteRule = "";
      app.save(col);
    } catch (err) {
      console.log("[migration] station_forecasts rule update failed:", err);
    }
  },
  (app) => {
    try {
      const col = app.findCollectionByNameOrId("station_forecasts");
      col.createRule = "@request.admin != null";
      col.updateRule = "@request.admin != null";
      col.deleteRule = "@request.admin != null";
      app.save(col);
    } catch (err) {
      console.log("[rollback] station_forecasts rule reset failed:", err);
    }
  }
);
