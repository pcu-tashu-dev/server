migrate(
  (app) => {
    try {
      const col = app.findCollectionByNameOrId("station_forecasts");
      const field = col.schema.getFieldByName("horizon_minutes");
      if (field) {
        field.required = false;
      }
      app.save(col);
    } catch (err) {
      console.log("[migration] horizon_minutes optional failed:", err);
    }
  },
  (app) => {
    try {
      const col = app.findCollectionByNameOrId("station_forecasts");
      const field = col.schema.getFieldByName("horizon_minutes");
      if (field) {
        field.required = true;
      }
      app.save(col);
    } catch (err) {
      console.log("[rollback] horizon_minutes rollback failed:", err);
    }
  }
);
